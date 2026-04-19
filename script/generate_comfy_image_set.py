import argparse
import copy
import json
import re
import shutil
import struct
import sys
import time
import uuid
from pathlib import Path
from urllib import error, request

from storyboard_workspace import default_generated_dir, default_logs_dir, default_storyboard_json


DEFAULT_API_URL = "http://127.0.0.1:8188"
DEFAULT_WSL_DISTRO = "Ubuntu"
DEFAULT_WSL_COMFY_ROOT = "/home/anson/comfy/ComfyUI"

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = Path.cwd()
DEFAULT_OUTPUT_ROOT = PROJECT_DIR / "output"
DEFAULT_LOGS_DIR = DEFAULT_OUTPUT_ROOT / "logs"
DEFAULT_DEBUG_DIR = DEFAULT_OUTPUT_ROOT / "debug"
DEFAULT_OUTPUT_DIR = DEFAULT_OUTPUT_ROOT / "generated"
DEFAULT_STORYBOARD_JSON = DEFAULT_OUTPUT_ROOT / "storyboard.json"
DEFAULT_IMAGE_PROMPTS_PATH = PROJECT_DIR / "image-prompts.md"
DEFAULT_TEMPLATES_DIR = Path(r"C:\Users\anson\Desktop\comfyFlow\writing")
DEFAULT_WIDTH = 480
DEFAULT_HEIGHT = 720

TEXT2IMG_TEMPLATE = "writing-qwen-text-to-image.json"
SINGLE_EDIT_TEMPLATE = "writing-qwen-single-image-edit.json"
MULTI_EDIT_TEMPLATE = "writing-qwen-multi-image-edit.json"

SCENE_POSITIVE_FALLBACK = (
    "domestic realism, Chinese family apartment, restrained emotional pressure, natural indoor lighting, "
    "short-drama frame, believable contemporary household setting"
)
SCENE_NEGATIVE_FALLBACK = (
    "luxury house, fantasy lighting, cartoon style, collage, watermark, text overlay, extra limbs, "
    "bad hands, distorted anatomy, glam styling, overdesigned horror"
)



# Override any garbled source keys above with the intended character names.
CHARACTER_ANCHOR_BY_NAME = {
    "\u5468\u6653\u6674": "character_ref_zhou_xiaoqing.png",
    "\u6653\u6674": "character_ref_zhou_xiaoqing.png",
    "\u674e\u7f8e\u73cd": "character_ref_li_meizhen.png",
    "\u5988\u5988": "character_ref_li_meizhen.png",
    "\u6bcd\u4eb2": "character_ref_li_meizhen.png",
    "\u9648\u56fd\u5f3a": "character_ref_chen_guoqiang.png",
    "\u8205\u7236": "character_ref_chen_guoqiang.png",
    "\u8205\u8205": "character_ref_chen_guoqiang.png",
}



ANCHOR_JOBS = [
    {
        "id": "character_ref_zhou_xiaoqing",
        "workflow": "text2img",
        "positive": "17-year-old Chinese high school girl, slim build, short ponytail, sensitive watchful eyes, plain school uniform, front face or slight three-quarter view, calm guarded expression, full face visible, restrained posture, quiet alert energy, domestic realism, natural indoor lighting, medium portrait shot",
        "negative": "adult-looking teenage girl, glamorous makeup, sexualized schoolgirl styling, mature face, fashion model, luxury background, fantasy lighting, text, watermark, collage, extra fingers, bad hands, distorted anatomy",
        "save_prefix": "character_ref_zhou_xiaoqing",
        "copy_to_input": "character_ref_zhou_xiaoqing.png",
    },
    {
        "id": "character_ref_li_meizhen",
        "workflow": "text2img",
        "positive": "Chinese middle-aged housewife, tired face, plain home clothes, slightly stooped shoulders, front face or slight three-quarter view, neutral tired expression, full face visible, low-key family-home appearance, practical domestic realism, indoor lighting, medium portrait shot",
        "negative": "glamorous mother, villain styling, luxury housewife, heavy makeup, fashion shoot, polished celebrity face, text, watermark, collage, bad hands, distorted anatomy",
        "save_prefix": "character_ref_li_meizhen",
        "copy_to_input": "character_ref_li_meizhen.png",
    },
    {
        "id": "character_ref_chen_guoqiang",
        "workflow": "text2img",
        "positive": "Chinese middle-aged man, ordinary clean appearance, casual polo or plain homewear, front face or slight three-quarter view, slight everyday smile, full face visible, socially smooth family-insider energy, normal-face danger, domestic realism, indoor lighting, medium portrait shot",
        "negative": "monster face, horror villain, cartoon evil man, gangster styling, luxury boss look, exaggerated creepy expression, text, watermark, collage, distorted anatomy",
        "save_prefix": "character_ref_chen_guoqiang",
        "copy_to_input": "character_ref_chen_guoqiang.png",
    },
]

SCENE_ANCHOR_TITLE_HINTS = {
    "1": "晚飯後客廳與餐桌",
    "2": "廚房門口望向客廳",
    "3": "臥室內部空間",
    "4": "臥室門口與走廊",
}

SCENE_ANCHOR_SPATIAL_PROMPTS = {
    "1": (
        "modest Chinese family living room after dinner, dining table edge, sofa position, warm ceiling light, "
        "unfinished bowls and plates, clear apartment layout, domestic realism, no people, empty room anchor, "
        "stable room geography, vertical short-drama frame"
    ),
    "2": (
        "narrow kitchen doorway looking toward a modest family living room, visible doorframe, compressed apartment depth, "
        "clear direction from kitchen to living room, domestic realism, no people, empty room anchor, "
        "stable room geography, vertical short-drama frame"
    ),
    "3": (
        "small family bedroom interior, bed edge, plain wall, bedroom door position, low-key household lighting, "
        "modest domestic realism, no people, empty room anchor, stable room geography, vertical short-drama frame"
    ),
    "4": (
        "bedroom doorway facing a narrow apartment hallway, clear inside-outside door relationship, hallway light spill, "
        "doorframe pressure, modest domestic realism, no people, empty room anchor, stable room geography, vertical short-drama frame"
    ),
}


def wsl_unc_path(distro: str, wsl_path: str) -> Path:
    clean = wsl_path.strip("/").replace("/", "\\")
    return Path(rf"\\wsl$\{distro}\{clean}")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def save_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def api_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {body}") from exc


def api_get_json(url: str) -> dict:
    with request.urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))


def api_get_object_info(api_url: str) -> dict:
    return api_get_json(f"{api_url}/object_info")


def find_node(workflow: dict, node_type: str, title: str | None = None) -> dict:
    for node in workflow["nodes"]:
        if node["type"] != node_type:
            continue
        if title is not None and node.get("title") != title:
            continue
        return node
    raise KeyError(f"Could not find node type={node_type!r} title={title!r}")


def build_link_map(workflow: dict) -> dict[int, list]:
    return {link[0]: link for link in workflow["links"]}


def widget_inputs_for_node(node: dict) -> dict:
    node_type = node["type"]
    values = node.get("widgets_values", [])

    if node_type == "CLIPTextEncode":
        return {"text": values[0]}
    if node_type == "TextEncodeQwenImageEditPlus":
        return {"prompt": values[0]}
    if node_type == "CLIPLoaderGGUF":
        return {"clip_name": values[0], "type": values[1]}
    if node_type == "UnetLoaderGGUF":
        return {"unet_name": values[0]}
    if node_type == "VAELoader":
        return {"vae_name": values[0]}
    if node_type == "EmptySD3LatentImage":
        return {"width": values[0], "height": values[1], "batch_size": values[2]}
    if node_type == "ModelSamplingAuraFlow":
        return {"shift": values[0]}
    if node_type == "CFGNorm":
        return {"strength": values[0]}
    if node_type == "KSampler":
        return {
            "seed": values[0],
            "steps": values[2],
            "cfg": values[3],
            "sampler_name": values[4],
            "scheduler": values[5],
            "denoise": values[6],
        }
    if node_type == "SaveImage":
        return {"filename_prefix": values[0]}
    if node_type == "LoadImage":
        return {"image": values[0]}
    if node_type == "ImageScale":
        return {
            "upscale_method": values[0],
            "width": values[1],
            "height": values[2],
            "crop": values[3],
        }
    if node_type == "FluxKontextMultiReferenceLatentMethod":
        return {"reference_latents_method": values[0]}
    return {}


def node_map(workflow: dict) -> dict[int, dict]:
    return {node["id"]: node for node in workflow["nodes"]}


def resolve_source_node(link_map: dict[int, list], nodes_by_id: dict[int, dict], node_id: int, output_index: int) -> tuple[int, int] | None:
    node = nodes_by_id[node_id]
    if node["type"] != "Reroute":
        return node_id, output_index

    input_link = None
    for node_input in node.get("inputs", []):
        if node_input.get("link") is not None:
            input_link = link_map[node_input["link"]]
            break

    if input_link is None:
        return None

    upstream_node_id = input_link[1]
    upstream_output_index = input_link[2]
    return resolve_source_node(link_map, nodes_by_id, upstream_node_id, upstream_output_index)


def ui_workflow_to_api_prompt(workflow: dict, available_node_types: set[str]) -> dict:
    link_map = build_link_map(workflow)
    nodes_by_id = node_map(workflow)
    prompt = {}
    skipped_nodes = {}

    for node in workflow["nodes"]:
        if node["type"] == "Reroute":
            continue
        if node["type"] not in available_node_types:
            skipped_nodes[node["id"]] = node["type"]
            continue

        inputs = {}

        for node_input in node.get("inputs", []):
            link_id = node_input.get("link")
            if link_id is None:
                continue
            link = link_map[link_id]
            resolved = resolve_source_node(link_map, nodes_by_id, link[1], link[2])
            if resolved is None:
                continue
            src_node_id, src_output_index = resolved
            if src_node_id in skipped_nodes:
                raise RuntimeError(
                    "Workflow input depends on a non-executable node "
                    f"{src_node_id} ({skipped_nodes[src_node_id]})."
                )
            inputs[node_input["name"]] = [str(src_node_id), src_output_index]

        inputs.update(widget_inputs_for_node(node))

        prompt[str(node["id"])] = {
            "inputs": inputs,
            "class_type": node["type"],
            "_meta": {"title": node.get("title") or node["type"]},
        }

    return prompt


def set_save_prefix(workflow: dict, prefix: str) -> None:
    find_node(workflow, "SaveImage")["widgets_values"][0] = prefix


def set_latent_size(workflow: dict, width: int, height: int) -> None:
    for node in workflow["nodes"]:
        if node["type"] == "EmptySD3LatentImage":
            node["widgets_values"][0] = width
            node["widgets_values"][1] = height


def set_output_image_size(workflow: dict, width: int, height: int) -> None:
    for node in workflow["nodes"]:
        if node["type"] == "ImageScale" and node.get("title") == "Output Resize":
            node["widgets_values"][1] = width
            node["widgets_values"][2] = height


def set_ksampler_steps(workflow: dict, steps: int) -> None:
    for node in workflow["nodes"]:
        if node["type"] == "KSampler":
            node["widgets_values"][2] = steps


def set_text2img(workflow: dict, positive: str, negative: str, prefix: str, width: int, height: int, steps: int) -> dict:
    wf = copy.deepcopy(workflow)
    find_node(wf, "CLIPTextEncode", "Writing Positive Prompt")["widgets_values"][0] = positive
    find_node(wf, "CLIPTextEncode", "Writing Negative Prompt")["widgets_values"][0] = negative
    set_latent_size(wf, width, height)
    set_ksampler_steps(wf, steps)
    set_save_prefix(wf, prefix)
    return wf


def set_single_edit(
    workflow: dict, input_image: str, instruction: str, negative: str, prefix: str, steps: int, width: int, height: int
) -> dict:
    wf = copy.deepcopy(workflow)
    find_node(wf, "LoadImage", "Load Input Image")["widgets_values"][0] = input_image
    find_node(wf, "TextEncodeQwenImageEditPlus", "Writing Instruction Prompt")["widgets_values"][0] = instruction
    find_node(wf, "TextEncodeQwenImageEditPlus", "Writing Negative Prompt")["widgets_values"][0] = negative
    set_output_image_size(wf, width, height)
    set_ksampler_steps(wf, steps)
    set_save_prefix(wf, prefix)
    return wf


def set_multi_edit(
    workflow: dict,
    base_image: str,
    ref_image: str,
    instruction: str,
    negative: str,
    prefix: str,
    steps: int,
    width: int,
    height: int,
) -> dict:
    wf = copy.deepcopy(workflow)
    find_node(wf, "LoadImage", "Load Base Scene Image")["widgets_values"][0] = base_image
    find_node(wf, "LoadImage", "Load Character Reference Image")["widgets_values"][0] = ref_image
    find_node(wf, "TextEncodeQwenImageEditPlus", "Writing Multi-Image Instruction Prompt")["widgets_values"][0] = instruction

    negative_node = None
    for node in wf["nodes"]:
        if node["type"] == "TextEncodeQwenImageEditPlus" and node.get("title") != "Writing Multi-Image Instruction Prompt":
            negative_node = node
            break
    if negative_node is None:
        raise KeyError("Could not find multi-image negative prompt node")
    negative_node["widgets_values"][0] = negative
    set_output_image_size(wf, width, height)
    set_ksampler_steps(wf, steps)
    set_save_prefix(wf, prefix)
    return wf


def queue_prompt(api_url: str, workflow: dict, client_id: str, available_node_types: set[str]) -> str:
    payload = {"prompt": ui_workflow_to_api_prompt(workflow, available_node_types), "client_id": client_id}
    response = api_json(f"{api_url}/prompt", payload)
    return response["prompt_id"]


def wait_for_prompt(api_url: str, prompt_id: str, timeout: int = 3600, poll_interval: float = 2.0) -> dict:
    start = time.time()
    while time.time() - start < timeout:
        history = api_get_json(f"{api_url}/history/{prompt_id}")
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(poll_interval)
    raise TimeoutError(f"Timed out waiting for prompt {prompt_id}")


def history_error_message(history_entry: dict) -> str | None:
    status = history_entry.get("status", {})
    if isinstance(status, dict):
        completed = status.get("completed")
        status_messages = status.get("messages") or []
        for message in status_messages:
            if not isinstance(message, (list, tuple)) or len(message) < 2:
                continue
            payload = message[1]
            if not isinstance(payload, dict):
                continue
            if message[0] in {"execution_error", "execution_interrupted"}:
                exception_message = payload.get("exception_message")
                node_type = payload.get("node_type")
                node_id = payload.get("node_id")
                parts = [f"ComfyUI execution failed for node {node_id}"]
                if node_type:
                    parts[-1] += f" ({node_type})"
                if exception_message:
                    parts.append(exception_message)
                return ": ".join(parts)
        if completed is False:
            return f"ComfyUI did not complete prompt successfully: {status}"

    if history_entry.get("exception_message"):
        return str(history_entry["exception_message"])

    return None


def extract_output_images(history_entry: dict) -> list[str]:
    images = []
    outputs = history_entry.get("outputs", {})
    for node_output in outputs.values():
        for img in node_output.get("images", []):
            images.append(img["filename"])
    return images


def copy_from_output_to_input(output_dir: Path, input_dir: Path, filename: str, target_name: str) -> Path:
    source = output_dir / filename
    if not source.exists():
        raise FileNotFoundError(f"Output image not found: {source}")
    target = input_dir / target_name
    shutil.copy2(source, target)
    return target


def copy_to_project(output_dir: Path, filename: str, project_output_dir: Path, target_name: str | None = None) -> Path:
    source = output_dir / filename
    if not source.exists():
        raise FileNotFoundError(f"Output image not found: {source}")
    project_output_dir.mkdir(parents=True, exist_ok=True)
    target = project_output_dir / (target_name or filename)
    shutil.copy2(source, target)
    return target


def find_latest_output_by_prefix(output_dir: Path, prefix: str) -> Path | None:
    matches = sorted(
        output_dir.glob(f"{prefix}_*.png"),
        key=lambda path: (path.stat().st_mtime, path.name),
        reverse=True,
    )
    return matches[0] if matches else None


def recover_existing_output(
    job: dict,
    comfy_output_dir: Path,
    comfy_input_dir: Path,
    project_output_dir: Path,
    width: int,
    height: int,
) -> dict | None:
    existing_output = find_latest_output_by_prefix(comfy_output_dir, job["save_prefix"])
    if existing_output is None:
        return None

    copied_input = None
    target_name = job.get("copy_to_input") or existing_output.name
    project_target = project_output_dir / target_name

    if job.get("copy_to_input"):
        input_target = comfy_input_dir / job["copy_to_input"]
        if not input_target.exists():
            copied_input = copy_from_output_to_input(
                comfy_output_dir,
                comfy_input_dir,
                existing_output.name,
                job["copy_to_input"],
            )
            ensure_expected_image_size(copied_input, width, height)
        else:
            copied_input = input_target

    if not project_target.exists():
        project_copy = copy_to_project(
            comfy_output_dir,
            existing_output.name,
            project_output_dir,
            target_name=target_name,
        )
    else:
        project_copy = project_target

    ensure_expected_image_size(existing_output, width, height)
    ensure_expected_image_size(project_copy, width, height)
    return {
        "job_id": job["id"],
        "status": "recovered_existing_output",
        "first_image": existing_output.name,
        "copied_input": str(copied_input) if copied_input else None,
        "project_copy": str(project_copy),
        "workflow": job["workflow"],
        "image_size": f"{width}x{height}",
        "all_images": [existing_output.name],
        "candidate_copies": None,
    }


def is_anchor_job(job: dict) -> bool:
    return (
        job["id"].startswith("character_ref_")
        or job["id"].startswith("scene_anchor_s")
        or job["id"].startswith("prop_ref_")
    )


def existing_anchor_path(job: dict, comfy_input_dir: Path) -> Path | None:
    target_name = job.get("copy_to_input")
    if not target_name:
        return None
    candidate = comfy_input_dir / target_name
    if candidate.exists():
        return candidate
    return None


def anchor_jobs_to_run(comfy_input_dir: Path, regenerate_anchors: bool, skip_anchors: bool) -> list[dict]:
    if skip_anchors:
        return []
    if regenerate_anchors:
        return list(ANCHOR_JOBS)
    pending = []
    for job in ANCHOR_JOBS:
        if existing_anchor_path(job, comfy_input_dir) is None:
            pending.append(job)
    return pending


def scene_anchor_filename(scene_number: str) -> str:
    return f"scene_anchor_s{scene_number}.png"


def scene_anchor_input_path(scene_number: str, comfy_input_dir: Path) -> Path:
    return comfy_input_dir / scene_anchor_filename(scene_number)


def existing_scene_anchor_path(scene_number: str, comfy_input_dir: Path) -> Path | None:
    candidate = scene_anchor_input_path(scene_number, comfy_input_dir)
    if candidate.exists():
        return candidate
    return None


def build_prop_anchor_job(prop_anchor: dict) -> dict:
    anchor_id = str(prop_anchor["anchor_id"]).strip()
    positive = sanitize_generation_prompt(prop_anchor.get("anchor_prompt", ""))
    negative = sanitize_generation_prompt(prop_anchor.get("negative_prompt", SCENE_NEGATIVE_FALLBACK))
    if not positive:
        raise ValueError(f"Prop anchor {anchor_id} is missing anchor_prompt")
    return {
        "id": Path(anchor_id).stem,
        "workflow": "text2img",
        "positive": positive,
        "negative": negative,
        "save_prefix": Path(anchor_id).stem,
        "copy_to_input": anchor_id,
    }


def prop_anchor_jobs(
    storyboard_json: Path,
    comfy_input_dir: Path,
    project_output_dir: Path,
    regenerate_anchors: bool,
    skip_anchors: bool,
) -> list[dict]:
    if skip_anchors or not storyboard_json.exists():
        return []

    storyboard_data = load_json(storyboard_json)
    jobs = []
    for prop_anchor in storyboard_data.get("prop_anchor_plan", []):
        job = build_prop_anchor_job(prop_anchor)
        if not regenerate_anchors:
            existing_input = existing_anchor_path(job, comfy_input_dir)
            if existing_input is not None:
                continue
            if (project_output_dir / job["copy_to_input"]).exists():
                continue
        jobs.append(job)
    return jobs


def save_all_candidates(output_dir: Path, filenames: list[str], candidate_dir: Path, job_id: str) -> list[str]:
    candidate_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for index, filename in enumerate(filenames, start=1):
        suffix = Path(filename).suffix or ".png"
        target_name = f"{job_id}_candidate_{index}{suffix}"
        saved_path = copy_to_project(output_dir, filename, candidate_dir, target_name=target_name)
        saved.append(str(saved_path))
    return saved


def parse_scene_image_prompts(markdown_text: str) -> dict[str, dict]:
    scene_map = {}
    current_data = None

    for raw_line in markdown_text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if stripped.startswith("#### Scene "):
            scene_number = stripped.replace("#### Scene ", "").strip()
            current_data = {}
            scene_map[scene_number] = current_data
            continue
        if not current_data:
            continue
        match = re.match(r"^\s*-\s+([^:]+):\s*(.*)$", line)
        if match:
            key = match.group(1).strip().lower().replace(" ", "_").replace("-", "_")
            current_data[key] = match.group(2).strip()
    return scene_map


def build_scene_anchor_positive(scene: dict, scene_prompt_data: dict | None) -> str:
    scene_number = str(scene.get("scene_number", "")).strip()
    location_hint = SCENE_ANCHOR_TITLE_HINTS.get(scene_number, "家庭室內空間")
    scene_positive = SCENE_ANCHOR_SPATIAL_PROMPTS.get(scene_number, SCENE_POSITIVE_FALLBACK)

    pieces = [
        scene_positive,
        f"{location_hint}，垂直短劇分鏡定場畫面",
        "空間方向清楚，門口、桌面、沙發或床位關係穩定",
        "no people, no character, no readable face, no human figure",
    ]
    pieces.append("不要人物，不要角色，不要任何正在發生的劇情動作，優先穩定空間和家居現實感")
    return "，".join(piece for piece in pieces if piece)


def build_scene_anchor_job(scene: dict, scene_prompt_data: dict | None) -> dict:
    scene_number = str(scene["scene_number"])
    scene_negative = scene_prompt_data.get("negative_prompt", SCENE_NEGATIVE_FALLBACK) if scene_prompt_data else SCENE_NEGATIVE_FALLBACK
    filename = scene_anchor_filename(scene_number)
    return {
        "id": Path(filename).stem,
        "workflow": "text2img",
        "positive": build_scene_anchor_positive(scene, scene_prompt_data),
        "negative": (
            f"{scene_negative}, person, people, human figure, character, readable face, portrait, "
            "unstable room geography, unclear doorway direction, floating furniture, identity drift, glamour look, "
            "overdramatic horror, unreadable phone, cluttered composition"
        ),
        "save_prefix": Path(filename).stem,
        "copy_to_input": filename,
    }


def scene_anchor_jobs(
    storyboard_json: Path,
    image_prompts_path: Path,
    comfy_input_dir: Path,
    project_output_dir: Path,
    regenerate_scene_anchors: bool,
    skip_scene_anchors: bool,
    selected_shots: set[str] | None = None,
) -> list[dict]:
    if skip_scene_anchors or not storyboard_json.exists():
        return []

    storyboard_data = load_json(storyboard_json)
    scene_prompt_map = parse_scene_image_prompts(load_text(image_prompts_path)) if image_prompts_path.exists() else {}
    jobs = []
    for scene in storyboard_data.get("scenes", []):
        if selected_shots:
            scene_has_selected = any(shot.get("shot_id") in selected_shots for shot in scene.get("shots", []))
            if not scene_has_selected:
                continue
        scene_number = str(scene["scene_number"])
        filename = scene_anchor_filename(scene_number)
        if not regenerate_scene_anchors:
            if existing_scene_anchor_path(scene_number, comfy_input_dir) is not None:
                continue
            if (project_output_dir / filename).exists():
                continue
        jobs.append(build_scene_anchor_job(scene, scene_prompt_map.get(scene_number)))
    return jobs


def infer_anchor_image(*texts: str) -> str | None:
    for text in texts:
        for key, value in CHARACTER_ANCHOR_BY_NAME.items():
            if key in text:
                return value
    return None


def shot_anchor_image(shot: dict) -> str | None:
    return infer_anchor_image(
        str(shot.get("reference_character", "")),
        str(shot.get("subject", "")),
        str(shot.get("action", "")),
        str(shot.get("purpose", "")),
    )


def first_non_empty(mapping: dict, *keys: str) -> str:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def normalize_ref_type(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def sanitize_generation_prompt(text: str) -> str:
    cleaned = (text or "").replace("？", "").replace("?", "").strip()

    noise_markers = [
        "同时为下一拍",
        "下一 shot",
        "下一场",
        "后方只需要留出客厅沙发区",
        "保持他表面正常的松弛感",
        "重点是门外有人逼近",
    ]
    cut_index = len(cleaned)
    for marker in noise_markers:
        index = cleaned.find(marker)
        if index != -1:
            cut_index = min(cut_index, index)
    cleaned = cleaned[:cut_index]

    if cleaned.startswith("12"):
        cleaned = cleaned[2:]

    while "。。" in cleaned:
        cleaned = cleaned.replace("。。", "。")
    cleaned = cleaned.replace("。，", "，").replace("；，", "；")
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ，；。")

    if cleaned and cleaned[-1] not in "。！？":
        cleaned += "。"

    return cleaned


def reference_keep_text(reference_character: str, framing: str, reference_mode: str) -> str:
    name = str(reference_character or "").split(",")[0].split("，")[0].strip()
    insert_like = str(framing or "").lower() == "insert"

    if reference_mode in {"scene_ref", "scene_ref_fallback"}:
        return "保留参考图里已经建立的空间朝向、道具位置和画面连续性。"
    if reference_mode == "scene_plus_character":
        if name:
            return f"保留图1里已经建立的空间连续性，并保留图2里{name}的身份感、年龄感和外形连续性。"
        return "保留图1里已经建立的空间连续性，并保留图2里人物的身份感和外形连续性。"

    if not name:
        return ""

    if insert_like:
        if "周晓晴" in name:
            return "保留参考图里周晓晴作为同一个手机使用者的学生年龄感、手持习惯和手部关系。"
        if "李美珍" in name:
            return "保留参考图里李美珍作为同一个持机者的手部状态、疲惫气质和持机关系。"
        if "陈国强" in name:
            return "保留参考图里陈国强普通家人式的年龄感和日常气质。"
    else:
        if "周晓晴" in name:
            return "保留参考图里周晓晴的脸型、短马尾、学生年龄感和拘紧警觉的气质。"
        if "李美珍" in name:
            return "保留参考图里李美珍疲惫的脸型、素面家居感、微驼体态和压着情绪说话的母亲气质。"
        if "陈国强" in name:
            return "保留参考图里陈国强普通家人式的脸型、年龄感、表面正常的神态和看似无害的日常气质。"

    return f"保留参考图里{name}的身份感、年龄感和外形连续性。"


def parse_int(value: str) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return 0


def default_scene_reference(scene: dict, project_output_dir: Path) -> str | None:
    scene_anchor = scene_anchor_filename(str(scene["scene_number"]))
    if (project_output_dir / scene_anchor).exists():
        return scene_anchor
    return None


def previous_shot_reference(scene: dict, shot: dict, project_output_dir: Path) -> str | None:
    current_number = parse_int(shot.get("shot_number", "0"))
    best_candidate = None
    for candidate in scene.get("shots", []):
        candidate_number = parse_int(candidate.get("shot_number", "0"))
        if candidate_number >= current_number:
            continue
        image_name = candidate.get("image_name") or f"ep1_s{scene['scene_number']}_sh{candidate.get('shot_number')}.png"
        if (project_output_dir / image_name).exists():
            best_candidate = image_name
    return best_candidate


def choose_scene_reference(scene: dict, shot: dict, project_output_dir: Path) -> str | None:
    continuity_in = str(shot.get("continuity_in", ""))
    must_show_detail = str(shot.get("must_show_detail", ""))
    carry_state_keywords = ["同一部手機", "同一手機", "承接上一", "接住上一", "同一姿勢", "螢幕狀態", "手指", "拇指"]
    needs_previous_shot = any(keyword in continuity_in or keyword in must_show_detail for keyword in carry_state_keywords)

    if needs_previous_shot:
        return previous_shot_reference(scene, shot, project_output_dir) or default_scene_reference(scene, project_output_dir)
    return default_scene_reference(scene, project_output_dir) or previous_shot_reference(scene, shot, project_output_dir)


def is_insert_like_shot(shot: dict) -> bool:
    framing = str(shot.get("framing", "")).lower()
    production_type = str(shot.get("production_type", "")).lower()
    subject = str(shot.get("subject", "")).lower()
    action = str(shot.get("action", "")).lower()
    phone_keywords = ["手机", "屏幕", "界面", "相册", "thumb", "phone", "screen"]
    return (
        production_type == "insert"
        or framing == "insert"
        or any(keyword in subject for keyword in phone_keywords)
        or any(keyword in action for keyword in phone_keywords)
    )


def should_prefer_multi_edit(shot: dict, anchor_image: str | None, scene_ref: str | None) -> bool:
    if not anchor_image or not scene_ref:
        return False
    if is_insert_like_shot(shot):
        return False
    framing = str(shot.get("framing", "")).lower()
    production_type = str(shot.get("production_type", "")).lower()
    return production_type in {"master", "derived"} or framing in {"medium", "medium over-shoulder", "close-up", "close", "medium close-up"}


def should_prefer_single_character_edit(shot: dict, anchor_image: str | None) -> bool:
    if not anchor_image:
        return False
    if is_insert_like_shot(shot):
        return False
    return True


def should_prefer_single_scene_edit(shot: dict, scene_ref: str | None) -> bool:
    if not scene_ref:
        return False
    return is_insert_like_shot(shot) or str(shot.get("production_type", "")).lower() in {"video-only", "insert"}


def png_size(path: Path) -> tuple[int, int] | None:
    if path.suffix.lower() != ".png" or not path.exists():
        return None
    with path.open("rb") as fh:
        if fh.read(8) != b"\x89PNG\r\n\x1a\n":
            return None
        length = struct.unpack(">I", fh.read(4))[0]
        chunk_type = fh.read(4)
        if chunk_type != b"IHDR" or length < 8:
            return None
        width, height = struct.unpack(">II", fh.read(8))
        return width, height


def ensure_expected_image_size(path: Path, width: int, height: int) -> None:
    measured = png_size(path)
    if measured is None:
        return
    if measured != (width, height):
        raise RuntimeError(f"Unexpected image size for {path.name}: got {measured[0]}x{measured[1]}, expected {width}x{height}")


def latest_output_for_reference_name(comfy_output_dir: Path, reference_name: str) -> Path | None:
    exact = comfy_output_dir / reference_name
    if exact.exists():
        return exact
    stem = Path(reference_name).stem
    return find_latest_output_by_prefix(comfy_output_dir, stem)


def ensure_reference_image_ready(
    reference_name: str,
    comfy_input_dir: Path,
    comfy_output_dir: Path,
    project_output_dir: Path,
) -> Path:
    input_candidate = comfy_input_dir / reference_name
    if png_size(input_candidate) is not None:
        return input_candidate

    project_candidate = project_output_dir / reference_name
    if png_size(project_candidate) is not None:
        shutil.copy2(project_candidate, input_candidate)
        return input_candidate

    output_candidate = latest_output_for_reference_name(comfy_output_dir, reference_name)
    if output_candidate is not None and png_size(output_candidate) is not None:
        shutil.copy2(output_candidate, input_candidate)
        return input_candidate

    if input_candidate.exists():
        raise RuntimeError(
            f"Reference image exists but is not a valid PNG: {input_candidate}. "
            "Delete it and regenerate the matching anchor/ref image."
        )
    raise FileNotFoundError(
        f"Missing reference image '{reference_name}' in ComfyUI input. "
        f"Looked in {input_candidate}, {project_candidate}, and ComfyUI output."
    )


def ensure_job_references_ready(
    job: dict,
    comfy_input_dir: Path,
    comfy_output_dir: Path,
    project_output_dir: Path,
) -> list[str]:
    required_refs: list[str] = []
    if job["workflow"] == "single_edit":
        required_refs.append(job["input_image"])
    elif job["workflow"] == "multi_edit":
        required_refs.extend([job["base_image"], job["reference_image"]])

    prepared: list[str] = []
    for reference_name in required_refs:
        ready_path = ensure_reference_image_ready(
            reference_name=reference_name,
            comfy_input_dir=comfy_input_dir,
            comfy_output_dir=comfy_output_dir,
            project_output_dir=project_output_dir,
        )
        prepared.append(str(ready_path))
    return prepared


def fallback_instruction_text(
    scene: dict,
    shot: dict,
    start_image_prompt: str,
    prompt_workflow: str,
    reference_mode: str,
    prev_action: str,
    next_action: str,
) -> str:
    reference_character = shot.get("reference_character", "")
    subject = shot.get("subject", "")
    framing = shot.get("framing", "")
    must_show_detail = shot.get("must_show_detail", "")
    continuity_in = shot.get("continuity_in", prev_action) or ""

    keep_line = reference_keep_text(reference_character, framing, reference_mode)

    focus_line = ""
    if must_show_detail:
        focus_line = f"重点让观众一眼看清{must_show_detail}。"

    continuity_line = ""
    if continuity_in:
        continuity_line = f"当前画面必须延续上一拍已建立的状态: {continuity_in}。"

    return (
        f"{keep_line} "
        f"{start_image_prompt} "
        f"{focus_line} "
        f"{continuity_line} "
        f"这是一格{framing}画面，主体是{subject}。"
    ).strip()


def resolve_reference_plan(scene: dict, shot: dict, project_output_dir: Path) -> tuple[str, str | None, str | None, str]:
    prompt_workflow = first_non_empty(shot, "prompt_workflow", "promptWorkflow")
    primary_ref_type = normalize_ref_type(first_non_empty(shot, "primary_reference_type", "primaryReferenceType"))
    primary_ref_image = first_non_empty(shot, "primary_reference_image", "primaryReferenceImage")
    secondary_ref_type = normalize_ref_type(first_non_empty(shot, "secondary_reference_type", "secondaryReferenceType"))
    secondary_ref_image = first_non_empty(shot, "secondary_reference_image", "secondaryReferenceImage")
    scene_anchor_image = default_scene_reference(scene, project_output_dir) or ""
    previous_ref_image = previous_shot_reference(scene, shot, project_output_dir) or ""

    if primary_ref_type == "scene_anchor" and not primary_ref_image:
        primary_ref_image = scene_anchor_image
    if secondary_ref_type == "scene_anchor" and not secondary_ref_image:
        secondary_ref_image = scene_anchor_image
    if primary_ref_type == "last_shot_ref" and not primary_ref_image:
        primary_ref_image = previous_ref_image
    if secondary_ref_type == "last_shot_ref" and not secondary_ref_image:
        secondary_ref_image = previous_ref_image

    if primary_ref_type == "character_ref" and not primary_ref_image:
        primary_ref_image = shot_anchor_image(shot) or ""
    if secondary_ref_type == "character_ref" and not secondary_ref_image:
        secondary_ref_image = shot_anchor_image(shot) or ""

    scene_ref = choose_scene_reference(scene, shot, project_output_dir) or ""
    if primary_ref_type == "scene_ref" and not primary_ref_image:
        primary_ref_image = scene_ref
    if secondary_ref_type == "scene_ref" and not secondary_ref_image:
        secondary_ref_image = scene_ref

    if prompt_workflow == "multi_edit":
        if primary_ref_image and secondary_ref_image:
            return "multi_edit", primary_ref_image, secondary_ref_image, primary_ref_type or secondary_ref_type
        if primary_ref_image:
            return "single_edit", primary_ref_image, None, primary_ref_type or "fallback_single"
        if secondary_ref_image:
            return "single_edit", secondary_ref_image, None, secondary_ref_type or "fallback_single"
        return "text2img", None, None, "fallback_text2img"

    if prompt_workflow == "single_edit":
        if primary_ref_image:
            return "single_edit", primary_ref_image, None, primary_ref_type or "single_edit"
        if secondary_ref_image:
            return "single_edit", secondary_ref_image, None, secondary_ref_type or "fallback_single"
        return "text2img", None, None, "fallback_text2img"

    if prompt_workflow == "text2img":
        return "text2img", None, None, "text2img"

    anchor_image = shot_anchor_image(shot)

    if scene_anchor_image and anchor_image and not is_insert_like_shot(shot):
        return "multi_edit", scene_anchor_image, anchor_image, "scene_anchor_plus_character"
    if should_prefer_multi_edit(shot, anchor_image, scene_ref):
        return "multi_edit", scene_ref, anchor_image, "scene_plus_character"
    if should_prefer_single_character_edit(shot, anchor_image):
        return "single_edit", anchor_image, None, "character_ref"
    if should_prefer_single_scene_edit(shot, scene_ref):
        return "single_edit", scene_ref, None, "scene_ref"
    if anchor_image:
        return "single_edit", anchor_image, None, "character_ref_fallback"
    if scene_anchor_image:
        return "single_edit", scene_anchor_image, None, "scene_anchor_fallback"
    if scene_ref:
        return "single_edit", scene_ref, None, "scene_ref_fallback"
    return "text2img", None, None, "none"


def previous_and_next_context(scene: dict, shot_number: str) -> tuple[str, str]:
    prev_action = ""
    next_action = ""
    shots = scene.get("shots", [])
    for index, candidate in enumerate(shots):
        if candidate.get("shot_number") != shot_number:
            continue
        if index > 0:
            prev_action = shots[index - 1].get("shot_description", "") or shots[index - 1].get("action", "")
        if index + 1 < len(shots):
            next_action = shots[index + 1].get("shot_description", "") or shots[index + 1].get("action", "")
        break
    return prev_action, next_action


def build_storyboard_prompt_job(scene: dict, shot: dict, scene_prompt_data: dict | None, project_output_dir: Path) -> dict:
    subject = shot.get("visual_focus", "") or shot.get("subject", "")
    framing = shot.get("framing", "")
    start_image_prompt = shot.get("image_prompt", "") or shot.get("start_image_prompt", "") or shot.get("shot_description", "")
    prev_action, next_action = previous_and_next_context(scene, shot.get("shot_number", ""))

    scene_positive = scene_prompt_data.get("positive_prompt", SCENE_POSITIVE_FALLBACK) if scene_prompt_data else SCENE_POSITIVE_FALLBACK
    scene_negative = scene_prompt_data.get("negative_prompt", SCENE_NEGATIVE_FALLBACK) if scene_prompt_data else SCENE_NEGATIVE_FALLBACK

    image_name = shot.get("image_name") or f"ep1_s{scene['scene_number']}_sh{shot['shot_number']}.png"
    stem = Path(image_name).stem
    prompt_workflow, primary_reference_image, secondary_reference_image, reference_mode = resolve_reference_plan(
        scene, shot, project_output_dir
    )
    comfy_image_prompt = first_non_empty(shot, "image_prompt", "comfy_image_prompt", "comfyImagePrompt")
    if not comfy_image_prompt:
        comfy_image_prompt = fallback_instruction_text(
            scene,
            shot,
            start_image_prompt,
            prompt_workflow,
            reference_mode,
            prev_action,
            next_action,
        )
    comfy_image_prompt = sanitize_generation_prompt(comfy_image_prompt)

    negative = (
        f"{scene_negative}, inconsistent phone prop, wrong age, wrong room, wrong costume, "
        "identity drift, cluttered composition, unreadable action, weak emotional beat"
    )

    if prompt_workflow == "multi_edit" and primary_reference_image and secondary_reference_image:
        return {
            "id": stem,
            "workflow": "multi_edit",
            "base_image": primary_reference_image,
            "reference_image": secondary_reference_image,
            "instruction": comfy_image_prompt,
            "negative": negative,
            "save_prefix": stem,
            "copy_to_input": image_name,
        }

    if prompt_workflow == "single_edit" and primary_reference_image:
        return {
            "id": stem,
            "workflow": "single_edit",
            "input_image": primary_reference_image,
            "instruction": comfy_image_prompt,
            "negative": negative,
            "save_prefix": stem,
            "copy_to_input": image_name,
        }

    return {
        "id": stem,
        "workflow": "text2img",
        "positive": comfy_image_prompt or sanitize_generation_prompt(
            f"{scene_positive}, {start_image_prompt}, framing: {framing}, subject focus: {subject}, "
            f"must show detail: {'; '.join(shot.get('must_show', [])) if shot.get('must_show') else shot.get('must_show_detail', '')}, continuity in: {prev_action}, "
            "stable continuity, single short-drama frame"
        ),
        "negative": negative,
        "save_prefix": stem,
        "copy_to_input": image_name,
    }


def storyboard_jobs(
    storyboard_json: Path,
    image_prompts_path: Path,
    project_output_dir: Path,
    only_missing: bool = True,
    selected_shots: set[str] | None = None,
    force_existing: bool = False,
) -> list[dict]:
    if not storyboard_json.exists():
        return []

    storyboard_data = load_json(storyboard_json)
    scene_prompt_map = parse_scene_image_prompts(load_text(image_prompts_path)) if image_prompts_path.exists() else {}

    jobs = []
    for scene in storyboard_data.get("scenes", []):
        scene_prompt_data = scene_prompt_map.get(scene["scene_number"])
        for shot in scene.get("shots", []):
            if selected_shots and shot.get("shot_id") not in selected_shots:
                continue
            image_name = shot.get("image_name") or f"ep1_s{scene['scene_number']}_sh{shot['shot_number']}.png"
            if only_missing and not force_existing and shot.get("image_status") == "OK":
                continue
            if only_missing and not force_existing and (project_output_dir / image_name).exists():
                continue
            jobs.append(build_storyboard_prompt_job(scene, shot, scene_prompt_data, project_output_dir))
    return jobs


def run_job(
    job: dict,
    templates: dict,
    api_url: str,
    client_id: str,
    available_node_types: set[str],
    comfy_input_dir: Path,
    comfy_output_dir: Path,
    project_output_dir: Path,
    width: int,
    height: int,
    text2img_steps: int,
    edit_steps: int,
    preserve_existing_anchors: bool = True,
    allow_anchor_first_image: bool = False,
    dry_run: bool = False,
) -> dict:
    if job["workflow"] == "text2img":
        workflow = set_text2img(
            templates["text2img"], job["positive"], job["negative"], job["save_prefix"], width, height, text2img_steps
        )
    elif job["workflow"] == "single_edit":
        workflow = set_single_edit(
            templates["single_edit"],
            job["input_image"],
            job["instruction"],
            job["negative"],
            job["save_prefix"],
            edit_steps,
            width,
            height,
        )
    elif job["workflow"] == "multi_edit":
        workflow = set_multi_edit(
            templates["multi_edit"],
            job["base_image"],
            job["reference_image"],
            job["instruction"],
            job["negative"],
            job["save_prefix"],
            edit_steps,
            width,
            height,
        )
    else:
        raise ValueError(f"Unknown workflow type: {job['workflow']}")

    if preserve_existing_anchors and is_anchor_job(job):
        existing_path = existing_anchor_path(job, comfy_input_dir)
        if existing_path is not None:
            return {
                "job_id": job["id"],
                "status": "skipped_existing_anchor",
                "existing_input": str(existing_path),
            }

    if dry_run:
        return {"job_id": job["id"], "status": "dry_run"}

    recovered = recover_existing_output(
        job,
        comfy_output_dir=comfy_output_dir,
        comfy_input_dir=comfy_input_dir,
        project_output_dir=project_output_dir,
        width=width,
        height=height,
    )
    if recovered is not None:
        return recovered

    prepared_references = ensure_job_references_ready(
        job,
        comfy_input_dir=comfy_input_dir,
        comfy_output_dir=comfy_output_dir,
        project_output_dir=project_output_dir,
    )

    prompt_id = queue_prompt(api_url, workflow, client_id, available_node_types)
    history_entry = wait_for_prompt(api_url, prompt_id)
    execution_error = history_error_message(history_entry)
    if execution_error:
        raise RuntimeError(f"{execution_error} [job={job['id']}, prompt_id={prompt_id}]")

    images = extract_output_images(history_entry)
    if not images:
        raise RuntimeError(f"No images returned for job {job['id']} (prompt_id={prompt_id})")

    candidate_copies = None
    if is_anchor_job(job) and len(images) > 1 and not allow_anchor_first_image:
        candidate_copies = save_all_candidates(
            comfy_output_dir,
            images,
            project_output_dir / "anchor-candidates",
            job["id"],
        )
        raise RuntimeError(
            f"Anchor job {job['id']} returned {len(images)} images. "
            "Candidates were saved for review, but no canonical ref was promoted automatically."
        )

    first_image = images[0]
    copied_input = None
    if job.get("copy_to_input"):
        copied_input = copy_from_output_to_input(comfy_output_dir, comfy_input_dir, first_image, job["copy_to_input"])
        ensure_expected_image_size(copied_input, width, height)

    project_copy = copy_to_project(
        comfy_output_dir,
        first_image,
        project_output_dir,
        target_name=job.get("copy_to_input") or first_image,
    )
    ensure_expected_image_size(comfy_output_dir / first_image, width, height)
    ensure_expected_image_size(project_copy, width, height)
    return {
        "job_id": job["id"],
        "prompt_id": prompt_id,
        "first_image": first_image,
        "copied_input": str(copied_input) if copied_input else None,
        "project_copy": str(project_copy),
        "workflow": job["workflow"],
        "image_size": f"{width}x{height}",
        "all_images": images,
        "candidate_copies": candidate_copies,
        "prepared_references": prepared_references or None,
    }


def phase_jobs(phase: str) -> list[dict]:
    if phase == "anchors":
        return list(ANCHOR_JOBS)
    if phase == "prop_anchors":
        raise ValueError("prop_anchors phase requires storyboard context and should be assembled in main().")
    if phase == "scene_anchors":
        raise ValueError("scene_anchors phase requires storyboard context and should be assembled in main().")
    raise ValueError(f"Unknown phase: {phase}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch-generate the short-drama image set through ComfyUI.")
    parser.add_argument("--phase", choices=["anchors", "prop_anchors", "scene_anchors", "missing", "full", "all"], default="full")
    parser.add_argument("--api-url", default=DEFAULT_API_URL)
    parser.add_argument("--wsl-distro", default=DEFAULT_WSL_DISTRO)
    parser.add_argument("--wsl-comfy-root", default=DEFAULT_WSL_COMFY_ROOT)
    parser.add_argument("--templates-dir", default=str(DEFAULT_TEMPLATES_DIR))
    parser.add_argument("--project-dir", default="")
    parser.add_argument("--project-output-dir", default="")
    parser.add_argument("--storyboard-json", default="")
    parser.add_argument("--image-prompts", default="")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    parser.add_argument("--text2img-steps", type=int, default=40)
    parser.add_argument("--edit-steps", type=int, default=20)
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--turbo", action="store_true")
    parser.add_argument("--shots", nargs="*")
    parser.add_argument("--force-existing", action="store_true")
    parser.add_argument("--skip-anchors", action="store_true")
    parser.add_argument("--skip-scene-anchors", action="store_true")
    parser.add_argument("--regenerate-anchors", action="store_true")
    parser.add_argument("--regenerate-scene-anchors", action="store_true")
    parser.add_argument("--allow-anchor-first-image", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    templates_dir = Path(args.templates_dir)
    project_dir = Path(args.project_dir) if args.project_dir else Path.cwd()
    project_output_dir = Path(args.project_output_dir) if args.project_output_dir else default_generated_dir(project_dir)
    storyboard_json = Path(args.storyboard_json) if args.storyboard_json else default_storyboard_json(project_dir)
    image_prompts_path = Path(args.image_prompts) if args.image_prompts else (project_dir / "image-prompts.md")
    selected_shots = set(args.shots or [])
    width = args.width
    height = args.height
    text2img_steps = args.text2img_steps
    edit_steps = args.edit_steps
    if args.fast:
        text2img_steps = min(text2img_steps, 24)
        edit_steps = min(edit_steps, 12)
    if args.turbo:
        text2img_steps = min(text2img_steps, 16)
        edit_steps = min(edit_steps, 8)
    comfy_input_dir = wsl_unc_path(args.wsl_distro, f"{args.wsl_comfy_root}/input")
    comfy_output_dir = wsl_unc_path(args.wsl_distro, f"{args.wsl_comfy_root}/output")

    if not args.dry_run:
        for path in [templates_dir, project_dir, comfy_input_dir, comfy_output_dir]:
            if not path.exists():
                raise FileNotFoundError(f"Path not found: {path}")

    templates = {
        "text2img": load_json(templates_dir / TEXT2IMG_TEMPLATE),
        "single_edit": load_json(templates_dir / SINGLE_EDIT_TEMPLATE),
        "multi_edit": load_json(templates_dir / MULTI_EDIT_TEMPLATE),
    }
    available_node_types = set(api_get_object_info(args.api_url).keys())

    effective_skip_scene_anchors = args.skip_scene_anchors or args.skip_anchors
    prop_anchor_phase_jobs = prop_anchor_jobs(
        storyboard_json,
        comfy_input_dir,
        project_output_dir,
        regenerate_anchors=args.regenerate_anchors,
        skip_anchors=args.skip_anchors,
    )

    scene_anchor_phase_jobs = scene_anchor_jobs(
        storyboard_json,
        image_prompts_path,
        comfy_input_dir,
        project_output_dir,
        regenerate_scene_anchors=args.regenerate_scene_anchors,
        skip_scene_anchors=effective_skip_scene_anchors,
        selected_shots=selected_shots or None,
    )

    if args.phase == "missing":
        jobs = storyboard_jobs(
            storyboard_json,
            image_prompts_path,
            project_output_dir,
            only_missing=True,
            selected_shots=selected_shots,
            force_existing=args.force_existing,
        )
        if not args.skip_anchors:
            jobs = prop_anchor_phase_jobs + scene_anchor_phase_jobs + jobs
    elif args.phase == "prop_anchors":
        jobs = prop_anchor_phase_jobs
    elif args.phase == "scene_anchors":
        jobs = scene_anchor_phase_jobs
    elif args.phase in {"full", "all"}:
        storyboard_phase_jobs = storyboard_jobs(
            storyboard_json,
            image_prompts_path,
            project_output_dir,
            only_missing=False,
            selected_shots=selected_shots or None,
            force_existing=args.force_existing,
        )
        jobs = (
            anchor_jobs_to_run(comfy_input_dir, args.regenerate_anchors, args.skip_anchors)
            + prop_anchor_phase_jobs
            + scene_anchor_phase_jobs
            + storyboard_phase_jobs
        )
    else:
        jobs = phase_jobs(args.phase)
    client_id = str(uuid.uuid4())
    results = []

    for job in jobs:
        print(f"[run] {job['id']}")
        result = run_job(
            job=job,
            templates=templates,
            api_url=args.api_url,
            client_id=client_id,
            available_node_types=available_node_types,
            comfy_input_dir=comfy_input_dir,
            comfy_output_dir=comfy_output_dir,
            project_output_dir=project_output_dir,
            width=width,
            height=height,
            text2img_steps=text2img_steps,
            edit_steps=edit_steps,
            preserve_existing_anchors=not args.regenerate_anchors,
            allow_anchor_first_image=args.allow_anchor_first_image,
            dry_run=args.dry_run,
        )
        results.append(result)
        print(f"[done] {job['id']}")

    logs_dir = default_logs_dir(project_dir)
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "last_run_results.json"
    save_text(log_path, json.dumps(results, indent=2, ensure_ascii=False))
    print(f"Saved run log to {log_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        raise SystemExit(130)
