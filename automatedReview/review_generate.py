#!/usr/bin/env python3
"""Generate ComfyUI shot images and review them with Codex CLI.

Run this script from WSL. It reads a linked shot prompt package, selects the
matching Qwen image-edit workflow from each shot's reference_assignment, queues
ComfyUI generations, and asks Codex CLI to review the generated image.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request


DEFAULT_INPUT_JSON = Path(
    "/mnt/c/Users/anson/Desktop/writing/out/舅父成日偷拍外甥女/output/output_linked_prompt.json"
)
DEFAULT_ANCHOR_DIR = Path(
    "/mnt/c/Users/anson/Desktop/writing/out/舅父成日偷拍外甥女/output/generated"
)
DEFAULT_OUTPUT_ROOT = Path("/mnt/c/Users/anson/Desktop/writing/out/automatedReview")
DEFAULT_COMFY_API = "http://127.0.0.1:8188"
DEFAULT_COMFY_INPUT_DIR = Path("/home/anson/comfy/ComfyUI/input")
DEFAULT_COMFY_OUTPUT_DIR = Path("/home/anson/comfy/ComfyUI/output")
DEFAULT_REVIEW_SKILL_PATH = Path("/mnt/c/Users/anson/Desktop/writing/out/general-start-image-review/SKILL.md")
WORKFLOW_TWO_REFS = Path(
    "/mnt/c/Users/anson/Desktop/comfyFlow/writing/writing-qwen-scene-character.json"
)
WORKFLOW_THREE_REFS = Path(
    "/mnt/c/Users/anson/Desktop/comfyFlow/writing/writing-qwen-multi-image-two-characters.json"
)

REQUIRED_NODE_TYPES = {
    "CLIPLoaderGGUF",
    "UnetLoaderGGUF",
    "VAELoader",
    "LoadImage",
    "TextEncodeQwenImageEditPlus",
    "SaveImage",
    "ImageScale",
}

SAFETY_SUFFIX = (
    "\n\nSafety and framing constraints: keep this as a non-sexual domestic "
    "drama evidence scene. Do not include nudity, sexualized posing, erotic "
    "framing, voyeuristic detail, glamorized danger, exposed body focus, or "
    "exploitative depiction. If suspicious photos are shown on a phone, keep "
    "them as small non-explicit evidence thumbnails or implied domestic-angle "
    "proof, not readable explicit content."
)

FORBIDDEN_PROMPT_TERMS = [
    "nude",
    "nudity",
    "naked",
    "erotic",
    "sexual",
    "sexy",
    "seductive",
    "lingerie",
    "underwear",
    "bathroom nude",
    "bedroom nude",
    "露點",
    "裸露",
    "裸體",
    "全裸",
    "半裸",
    "性感",
    "挑逗",
    "色情",
    "內衣",
    "床照",
    "走光",
    "露骨",
]


@dataclass(frozen=True)
class ShotJob:
    shot: dict[str, Any]
    shot_id: str
    workflow_path: Path
    workflow_label: str
    references: dict[str, str]
    anchor_ids: dict[str, str]
    warnings: list[str]


def eprint(*parts: object) -> None:
    print(*parts, file=sys.stderr)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    tmp.replace(path)


def api_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {body}") from exc


def api_get_json(url: str, timeout: int = 30) -> dict[str, Any]:
    with request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_object_info(api_url: str) -> dict[str, Any]:
    return api_get_json(f"{api_url}/object_info", timeout=30)


def find_node(workflow: dict[str, Any], node_type: str, title: str | None = None) -> dict[str, Any]:
    for node in workflow["nodes"]:
        if node["type"] != node_type:
            continue
        if title is not None and node.get("title") != title:
            continue
        return node
    raise KeyError(f"Could not find node type={node_type!r} title={title!r}")


def build_link_map(workflow: dict[str, Any]) -> dict[int, list[Any]]:
    return {link[0]: link for link in workflow["links"]}


def node_map(workflow: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {node["id"]: node for node in workflow["nodes"]}


def widget_inputs_for_node(node: dict[str, Any]) -> dict[str, Any]:
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
    if node_type == "RandomNoise":
        return {"noise_seed": values[0]}
    if node_type == "BasicScheduler":
        return {"scheduler": values[0], "steps": values[1], "denoise": values[2]}
    if node_type == "SamplerCustomAdvanced":
        return {}
    if node_type == "KSamplerSelect":
        return {"sampler_name": values[0]}
    return {}


def resolve_source_node(
    link_map: dict[int, list[Any]],
    nodes_by_id: dict[int, dict[str, Any]],
    node_id: int,
    output_index: int,
) -> tuple[int, int] | None:
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
    return resolve_source_node(link_map, nodes_by_id, input_link[1], input_link[2])


def ui_workflow_to_api_prompt(workflow: dict[str, Any], available_node_types: set[str]) -> dict[str, Any]:
    link_map = build_link_map(workflow)
    nodes_by_id = node_map(workflow)
    prompt: dict[str, Any] = {}
    skipped_nodes: dict[int, str] = {}

    for node in workflow["nodes"]:
        if node["type"] == "Reroute":
            continue
        if node["type"] not in available_node_types:
            skipped_nodes[node["id"]] = node["type"]
            continue

        inputs: dict[str, Any] = {}
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


def set_save_prefix(workflow: dict[str, Any], prefix: str) -> None:
    find_node(workflow, "SaveImage")["widgets_values"][0] = prefix


def set_output_image_size(workflow: dict[str, Any], width: int | None, height: int | None) -> None:
    if width is None or height is None:
        return
    for node in workflow["nodes"]:
        if node["type"] == "ImageScale":
            values = node.get("widgets_values", [])
            if len(values) >= 4:
                values[1] = width
                values[2] = height


def qwen_prompt_titles() -> set[str]:
    return {
        "Writing Multi-Image Instruction Prompt",
        "Writing Scene + Character Prompt",
    }


def find_qwen_instruction_node(workflow: dict[str, Any]) -> dict[str, Any]:
    for node in workflow["nodes"]:
        if node["type"] == "TextEncodeQwenImageEditPlus" and node.get("title") in qwen_prompt_titles():
            return node
    raise KeyError("Could not find the Qwen instruction prompt node.")


def find_qwen_negative_node(workflow: dict[str, Any]) -> dict[str, Any]:
    for node in workflow["nodes"]:
        if node["type"] == "TextEncodeQwenImageEditPlus" and node.get("title") not in qwen_prompt_titles():
            return node
    raise KeyError("Could not find the Qwen negative prompt node.")


def base_negative_prompt(workflow_path: Path) -> str:
    workflow = load_json(workflow_path)
    values = find_qwen_negative_node(workflow).get("widgets_values", [])
    return str(values[0] if values else "").strip()


def set_workflow_for_job(
    template: dict[str, Any],
    job: ShotJob,
    prompt: str,
    negative_prompt: str,
    save_prefix: str,
    width: int | None,
    height: int | None,
) -> dict[str, Any]:
    wf = copy.deepcopy(template)
    find_node(wf, "LoadImage", "Load Base Scene Image")["widgets_values"][0] = job.references["image1"]
    find_node(wf, "LoadImage", "Load Character 1 Reference Image")["widgets_values"][0] = job.references["image2"]
    if "image3" in job.references:
        find_node(wf, "LoadImage", "Load Character 2 Reference Image")["widgets_values"][0] = job.references["image3"]

    find_qwen_instruction_node(wf)["widgets_values"][0] = prompt
    find_qwen_negative_node(wf)["widgets_values"][0] = negative_prompt

    set_save_prefix(wf, save_prefix)
    set_output_image_size(wf, width, height)
    return wf


def queue_prompt(api_url: str, workflow: dict[str, Any], client_id: str, available_node_types: set[str]) -> str:
    payload = {"prompt": ui_workflow_to_api_prompt(workflow, available_node_types), "client_id": client_id}
    response = api_json(f"{api_url}/prompt", payload)
    return response["prompt_id"]


def wait_for_prompt(api_url: str, prompt_id: str, timeout: int, poll_interval: float) -> dict[str, Any]:
    start = time.time()
    while time.time() - start < timeout:
        history = api_get_json(f"{api_url}/history/{prompt_id}", timeout=30)
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(poll_interval)
    raise TimeoutError(f"Timed out waiting for prompt {prompt_id}")


def history_error_message(history_entry: dict[str, Any]) -> str | None:
    status = history_entry.get("status", {})
    if isinstance(status, dict):
        for message in status.get("messages") or []:
            if not isinstance(message, (list, tuple)) or len(message) < 2:
                continue
            if message[0] not in {"execution_error", "execution_interrupted"}:
                continue
            payload = message[1] if isinstance(message[1], dict) else {}
            node_id = payload.get("node_id")
            node_type = payload.get("node_type")
            exception_message = payload.get("exception_message")
            detail = f"ComfyUI execution failed for node {node_id}"
            if node_type:
                detail += f" ({node_type})"
            if exception_message:
                detail += f": {exception_message}"
            return detail
        if status.get("completed") is False:
            return f"ComfyUI did not complete prompt successfully: {status}"
    if history_entry.get("exception_message"):
        return str(history_entry["exception_message"])
    return None


def extract_output_image_paths(history_entry: dict[str, Any], comfy_output_dir: Path) -> list[Path]:
    paths: list[Path] = []
    for node_output in history_entry.get("outputs", {}).values():
        for img in node_output.get("images", []):
            filename = img.get("filename")
            if not filename:
                continue
            subfolder = img.get("subfolder") or ""
            img_type = img.get("type") or "output"
            if img_type != "output":
                continue
            paths.append(comfy_output_dir / subfolder / filename)
    return paths


def resolve_anchor_name(anchor_dir: Path, anchor_id: str) -> str:
    source = anchor_dir / f"{anchor_id}.png"
    if not source.exists():
        raise FileNotFoundError(f"Missing anchor image for {anchor_id}: {source}")
    return source.name


def copy_anchor_to_comfy_input(anchor_dir: Path, comfy_input_dir: Path, anchor_id: str) -> str:
    source = anchor_dir / resolve_anchor_name(anchor_dir, anchor_id)
    target = comfy_input_dir / source.name
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists() or source.stat().st_mtime > target.stat().st_mtime:
        shutil.copy2(source, target)
    return target.name


def load_shots(input_json: Path) -> list[dict[str, Any]]:
    data = load_json(input_json)
    try:
        shots = data["output_linked_prompt.json"]["shots"]
    except (KeyError, TypeError) as exc:
        raise ValueError('Input JSON must contain data["output_linked_prompt.json"]["shots"].') from exc
    if not isinstance(shots, list):
        raise ValueError("shots must be a list.")
    return shots


def is_scene_anchor(anchor_id: str) -> bool:
    return anchor_id.startswith("scene_anchor")


def build_job(shot: dict[str, Any], anchor_dir: Path, comfy_input_dir: Path, prepare_inputs: bool) -> ShotJob:
    shot_id = str(shot.get("shot_id") or f"shot_{uuid.uuid4().hex[:8]}")
    assignment = shot.get("reference_assignment")
    if not isinstance(assignment, list):
        raise ValueError(f"{shot_id}: reference_assignment must be a list.")

    usable: dict[str, str] = {}
    for item in assignment:
        if not isinstance(item, dict):
            continue
        slot = str(item.get("slot") or "").strip()
        anchor_id = str(item.get("anchor_id") or "").strip()
        if not slot or not anchor_id:
            continue
        if not re.fullmatch(r"image[1-9][0-9]*", slot):
            continue
        usable[slot] = anchor_id

    count = len(usable)
    if count == 2:
        workflow_path = WORKFLOW_TWO_REFS
        workflow_label = "writing-qwen-scene-character"
        required_slots = ["image1", "image2"]
    elif count == 3:
        workflow_path = WORKFLOW_THREE_REFS
        workflow_label = "writing-qwen-multi-image-two-characters"
        required_slots = ["image1", "image2", "image3"]
    else:
        raise ValueError(f"{shot_id}: expected 2 or 3 usable reference objects, got {count}.")

    missing = [slot for slot in required_slots if slot not in usable]
    if missing:
        raise ValueError(f"{shot_id}: missing required reference slots: {', '.join(missing)}.")

    warnings: list[str] = []
    if not is_scene_anchor(usable["image1"]):
        warnings.append(f"image1 is not a scene anchor: {usable['image1']}")

    references = {}
    for slot in required_slots:
        anchor_id = usable[slot]
        references[slot] = (
            copy_anchor_to_comfy_input(anchor_dir, comfy_input_dir, anchor_id)
            if prepare_inputs
            else resolve_anchor_name(anchor_dir, anchor_id)
        )
    return ShotJob(
        shot=shot,
        shot_id=shot_id,
        workflow_path=workflow_path,
        workflow_label=workflow_label,
        references=references,
        anchor_ids={slot: usable[slot] for slot in required_slots},
        warnings=warnings,
    )


def safety_findings(text: str) -> list[str]:
    lower = text.lower()
    return [term for term in FORBIDDEN_PROMPT_TERMS if term.lower() in lower]


def safe_generation_prompt(prompt: str) -> tuple[str, list[str]]:
    findings = safety_findings(prompt)
    if findings:
        raise ValueError(f"Prompt contains unsafe terms that need manual rewrite: {', '.join(findings)}")
    return prompt.rstrip() + SAFETY_SUFFIX, []


def merge_negative_prompt(current: str, improved: str) -> str:
    current = current.strip()
    improved = improved.strip()
    if not improved:
        return current
    if not current:
        return improved
    current_parts = [part.strip() for part in current.split(",") if part.strip()]
    seen = {part.casefold() for part in current_parts}
    for part in [item.strip() for item in improved.split(",") if item.strip()]:
        if part.casefold() not in seen:
            current_parts.append(part)
            seen.add(part.casefold())
    return ", ".join(current_parts)


def load_review_rules(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Review skill rules not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def build_review_prompt(
    shot: dict[str, Any],
    attempted_prompt: str,
    attempted_negative_prompt: str,
    max_score: int,
    review_rules: str,
) -> str:
    return f"""
You are reviewing one generated start-frame image for a short-drama storyboard.
Return ONLY strict JSON with this schema:
{{"accepted": true/false, "score": 0-10, "prompt_fit_score": 0-10, "start_image_quality_score": 0-10, "reason": "short concrete reason", "improved_start_image_prompt": "revised prompt if rejected, otherwise repeat the current prompt", "improved_negative_prompt": "targeted negative prompt if rejected, otherwise repeat the current negative prompt"}}

Accept only if score, prompt_fit_score, and start_image_quality_score are all at least {max_score}. Judge both whether the image fits the intended start_image_prompt and whether it is a good video first frame.

Original shot id: {shot.get("shot_id")}
Scene id: {shot.get("scene_id")}
Caption: {shot.get("caption", "")}
Reference assignment: {json.dumps(shot.get("reference_assignment", []), ensure_ascii=False)}

Current start_image_prompt:
{attempted_prompt}

Current negative prompt:
{attempted_negative_prompt}

General first-frame review rules:
{review_rules}

Story and prompt-fit review criteria:
- The image must be one stable first frame, not a sequence or completed action.
- It needs a clear first-eye center: evidence, reaction, pressure, help-seeking, handoff, confrontation, or blocked exit.
- Character positions, gaze targets, hand positions, prop ownership, and physical support must be logically visible.
- Phone/screen/album/black-screen state must be readable when it is the story evidence.
- The scene anchor should support the shot without stealing focus.
- The image must fit the prompt, not merely look attractive.
- Reject flat reactions, floating objects, too many focal points, abstract mood without visible cause, irrelevant props, wrong character count, missing required character, single-person crop when two people are required, over-cropped faces, wrong scene, wrong phone state, bad anatomy, identity drift, or unclear story function.
- For sensitive evidence shots, reject nudity, sexualized pose, voyeuristic detail, exposed body focus, or glamorized danger. Keep the image non-sexual and domestic-drama/evidence oriented.

If rejected, improve the start_image_prompt and/or negative prompt. Keep the same shot meaning, same references, same character count, and same story order. Make the positive prompt more visually concrete and logically grounded.

Negative prompt rules:
- Keep improved_negative_prompt short and targeted.
- Use it only for generation failure modes, not story content.
- Good additions include: no single-person crop, no missing second character, no cropped face, no only hands visible, no camera staring, no floating phone, no wrong hand contact, no screen content leaking into background, no completed action, no extra person.
- Do not put positive composition instructions only in the negative prompt; the positive prompt still owns what should appear.
""".strip()


def iter_json_candidates(text: str) -> list[dict[str, Any]]:
    decoder = json.JSONDecoder()
    candidates: list[dict[str, Any]] = []
    for match in re.finditer(r"\{", text):
        try:
            parsed, _end = decoder.raw_decode(text[match.start() :])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            candidates.append(parsed)
    return candidates


def extract_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        candidates = iter_json_candidates(text)
        if candidates:
            return candidates[-1]
        raise ValueError(f"Codex did not return a JSON object. Output was:\n{text[-2000:]}")
    if not isinstance(parsed, dict):
        raise ValueError(f"Codex returned JSON but not an object: {parsed!r}")
    return parsed


def run_codex_review(codex_cmd: str, image_path: Path, review_prompt: str, timeout: int) -> dict[str, Any]:
    cmd = [codex_cmd, "exec", "-i", str(image_path), "-", "--skip-git-repo-check"]
    proc = subprocess.run(cmd, input=review_prompt, text=True, capture_output=True, timeout=timeout)
    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if proc.returncode != 0:
        raise RuntimeError(f"Codex review failed with exit code {proc.returncode}:\n{combined[-4000:]}")
    review = extract_json_object(combined)
    if not isinstance(review.get("accepted"), bool):
        raise ValueError(f"Codex review missing boolean accepted: {review}")
    for key in ["score", "prompt_fit_score", "start_image_quality_score"]:
        try:
            review[key] = int(review.get(key))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Codex review missing numeric {key}: {review}") from exc
        if review[key] < 0 or review[key] > 10:
            raise ValueError(f"Codex review {key} must be between 0 and 10: {review}")
    if not isinstance(review.get("reason"), str):
        review["reason"] = str(review.get("reason", ""))
    if not isinstance(review.get("improved_start_image_prompt"), str):
        review["improved_start_image_prompt"] = ""
    if not isinstance(review.get("improved_negative_prompt"), str):
        review["improved_negative_prompt"] = ""
    return review


def load_state(state_path: Path) -> dict[str, Any]:
    if not state_path.exists():
        return {"shots": {}}
    state = load_json(state_path)
    if not isinstance(state, dict):
        return {"shots": {}}
    state.setdefault("shots", {})
    return state


def fresh_shot_state(existing: dict[str, Any], force: bool) -> dict[str, Any]:
    if not force:
        return existing
    if existing.get("status") == "accepted":
        return existing
    return {}


def mark_state_error(state: dict[str, Any], shot_id: str, message: str, state_path: Path) -> None:
    state["shots"][shot_id] = {
        **state["shots"].get(shot_id, {}),
        "status": "error",
        "error": message,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    write_json(state_path, state)


def preflight(args: argparse.Namespace, check_codex: bool) -> set[str]:
    if not args.input_json.exists():
        raise FileNotFoundError(f"Input JSON not found: {args.input_json}")
    if not args.anchor_dir.exists():
        raise FileNotFoundError(f"Anchor directory not found: {args.anchor_dir}")
    if not args.comfy_input_dir.exists():
        raise FileNotFoundError(f"ComfyUI input directory not found: {args.comfy_input_dir}")
    if not args.comfy_output_dir.exists():
        raise FileNotFoundError(f"ComfyUI output directory not found: {args.comfy_output_dir}")
    for workflow in [WORKFLOW_TWO_REFS, WORKFLOW_THREE_REFS]:
        if not workflow.exists():
            raise FileNotFoundError(f"Workflow not found: {workflow}")

    system_stats = api_get_json(f"{args.comfy_api}/system_stats", timeout=10)
    comfy_version = system_stats.get("system", {}).get("comfyui_version", "unknown")
    print(f"ComfyUI reachable: version {comfy_version}")

    object_info = get_object_info(args.comfy_api)
    available_node_types = set(object_info.keys())
    missing = sorted(REQUIRED_NODE_TYPES - available_node_types)
    if missing:
        raise RuntimeError(f"ComfyUI missing required node types: {', '.join(missing)}")

    if check_codex:
        codex_path = shutil.which(args.codex_cmd)
        if not codex_path:
            raise RuntimeError("WSL-side codex command not found. Install with: npm install -g @openai/codex")
        if codex_path.startswith("/mnt/c/Program Files/WindowsApps/"):
            raise RuntimeError(
                "codex resolves to the blocked Windows app binary inside WSL. "
                "Install the Linux/WSL CLI and put it earlier in PATH."
            )
        proc = subprocess.run(
            [args.codex_cmd, "--version"],
            text=True,
            capture_output=True,
            timeout=20,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"codex --version failed:\n{(proc.stdout + proc.stderr)[-2000:]}")
        print(f"Codex reachable: {(proc.stdout or proc.stderr).strip()}")
    return available_node_types


def plan_jobs(args: argparse.Namespace, shots: list[dict[str, Any]], state: dict[str, Any], state_path: Path) -> list[ShotJob]:
    jobs: list[ShotJob] = []
    for shot in shots:
        shot_id = str(shot.get("shot_id") or "unknown")
        if args.shot_id and shot_id != args.shot_id:
            continue
        existing = state.get("shots", {}).get(shot_id, {})
        if not args.force and existing.get("status") == "accepted":
            print(f"SKIP accepted {shot_id}: {existing.get('final_image')}")
            continue
        try:
            jobs.append(
                build_job(
                    shot,
                    args.anchor_dir,
                    args.comfy_input_dir,
                    prepare_inputs=not args.dry_run,
                )
            )
        except Exception as exc:
            print(f"ERROR planning {shot_id}: {exc}")
            if not args.dry_run:
                mark_state_error(state, shot_id, str(exc), state_path)
    return jobs


def run_comfy_generation(
    args: argparse.Namespace,
    available_node_types: set[str],
    job: ShotJob,
    prompt: str,
    negative_prompt: str,
    attempt: int,
) -> Path:
    template = load_json(job.workflow_path)
    safe_prompt, _warnings = safe_generation_prompt(prompt)
    prefix = f"automatedReview/{job.shot_id}/attempt_{attempt}"
    workflow = set_workflow_for_job(
        template=template,
        job=job,
        prompt=safe_prompt,
        negative_prompt=negative_prompt,
        save_prefix=prefix,
        width=args.width,
        height=args.height,
    )
    prompt_id = queue_prompt(args.comfy_api, workflow, args.client_id, available_node_types)
    history_entry = wait_for_prompt(args.comfy_api, prompt_id, args.timeout, args.poll_interval)
    err = history_error_message(history_entry)
    if err:
        raise RuntimeError(f"{err} [shot={job.shot_id}, attempt={attempt}, prompt_id={prompt_id}]")
    images = extract_output_image_paths(history_entry, args.comfy_output_dir)
    if not images:
        raise RuntimeError(f"No output images returned [shot={job.shot_id}, attempt={attempt}, prompt_id={prompt_id}]")
    source = images[0]
    if not source.exists():
        raise FileNotFoundError(f"ComfyUI reported image but file was not found: {source}")
    shot_dir = args.output_root / job.shot_id
    shot_dir.mkdir(parents=True, exist_ok=True)
    target = shot_dir / f"attempt_{attempt}{source.suffix.lower() or '.png'}"
    shutil.copy2(source, target)
    return target


def run_job(
    args: argparse.Namespace,
    available_node_types: set[str],
    state: dict[str, Any],
    state_path: Path,
    job: ShotJob,
) -> None:
    original_prompt = str(job.shot.get("start_image_prompt") or "").strip()
    if not original_prompt:
        mark_state_error(state, job.shot_id, "Missing start_image_prompt.", state_path)
        return

    existing_state = fresh_shot_state(state["shots"].get(job.shot_id, {}), args.force)
    review_rules = load_review_rules(args.review_skill_path)
    current_prompt = existing_state.get("final_prompt") or original_prompt
    original_negative_prompt = base_negative_prompt(job.workflow_path)
    current_negative_prompt = existing_state.get("final_negative_prompt") or original_negative_prompt
    shot_state = {
        **existing_state,
        "status": "running",
        "reference_assignment": job.shot.get("reference_assignment", []),
        "selected_workflow": job.workflow_label,
        "workflow_path": str(job.workflow_path),
        "references": job.references,
        "anchor_ids": job.anchor_ids,
        "original_prompt": original_prompt,
        "original_negative_prompt": original_negative_prompt,
        "warnings": job.warnings,
        "attempts": existing_state.get("attempts", []),
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    state["shots"][job.shot_id] = shot_state
    write_json(state_path, state)

    starting_attempt = len(shot_state["attempts"]) + 1
    for attempt in range(starting_attempt, args.max_attempts + 1):
        print(f"GENERATE {job.shot_id} attempt {attempt}/{args.max_attempts} via {job.workflow_label}")
        attempt_record: dict[str, Any] = {
            "attempt": attempt,
            "prompt": current_prompt,
            "negative_prompt": current_negative_prompt,
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
        try:
            image_path = run_comfy_generation(
                args,
                available_node_types,
                job,
                current_prompt,
                current_negative_prompt,
                attempt,
            )
            attempt_record["image"] = str(image_path)

            review_prompt = build_review_prompt(
                job.shot,
                current_prompt,
                current_negative_prompt,
                args.accept_score,
                review_rules,
            )
            review = run_codex_review(args.codex_cmd, image_path, review_prompt, args.codex_timeout)
            attempt_record["review"] = review
            accepted = (
                bool(review["accepted"])
                and int(review["score"]) >= args.accept_score
                and int(review["prompt_fit_score"]) >= args.accept_score
                and int(review["start_image_quality_score"]) >= args.accept_score
            )
            attempt_record["accepted"] = accepted

            shot_state["attempts"].append(attempt_record)
            if accepted:
                shot_state.update(
                    {
                        "status": "accepted",
                        "final_image": str(image_path),
                        "final_prompt": current_prompt,
                        "final_negative_prompt": current_negative_prompt,
                        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    }
                )
                write_json(state_path, state)
                print(
                    f"ACCEPT {job.shot_id}: score={review['score']} "
                    f"prompt_fit={review['prompt_fit_score']} "
                    f"start_image={review['start_image_quality_score']} image={image_path}"
                )
                return

            improved = review.get("improved_start_image_prompt", "").strip()
            improved_negative = review.get("improved_negative_prompt", "").strip()
            current_prompt = improved or current_prompt
            current_negative_prompt = merge_negative_prompt(current_negative_prompt, improved_negative)
            shot_state["final_prompt"] = current_prompt
            shot_state["final_negative_prompt"] = current_negative_prompt
            shot_state["status"] = "retrying"
            shot_state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
            write_json(state_path, state)
            print(
                f"RETRY {job.shot_id}: score={review['score']} "
                f"prompt_fit={review['prompt_fit_score']} "
                f"start_image={review['start_image_quality_score']} reason={review.get('reason', '')}"
            )
        except Exception as exc:
            attempt_record["error"] = str(exc)
            shot_state["attempts"].append(attempt_record)
            shot_state["status"] = "error"
            shot_state["error"] = str(exc)
            shot_state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
            write_json(state_path, state)
            print(f"ERROR {job.shot_id}: {exc}")
            return

    shot_state["status"] = "rejected"
    shot_state["final_prompt"] = current_prompt
    shot_state["final_negative_prompt"] = current_negative_prompt
    shot_state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    write_json(state_path, state)
    print(f"REJECT {job.shot_id}: reached max attempts")


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def score_threshold(value: str) -> int:
    parsed = positive_int(value)
    if parsed > 10:
        raise argparse.ArgumentTypeError("must be between 1 and 10")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate linked short-drama start images with ComfyUI and review them through Codex CLI."
    )
    parser.add_argument("--input-json", type=Path, default=DEFAULT_INPUT_JSON)
    parser.add_argument("--anchor-dir", type=Path, default=DEFAULT_ANCHOR_DIR)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--comfy-api", default=DEFAULT_COMFY_API)
    parser.add_argument("--comfy-input-dir", type=Path, default=DEFAULT_COMFY_INPUT_DIR)
    parser.add_argument("--comfy-output-dir", type=Path, default=DEFAULT_COMFY_OUTPUT_DIR)
    parser.add_argument("--review-skill-path", type=Path, default=DEFAULT_REVIEW_SKILL_PATH)
    parser.add_argument("--codex-cmd", default="codex")
    parser.add_argument("--shot-id", help="Run only one shot id.")
    parser.add_argument("--max-attempts", type=positive_int, default=5)
    parser.add_argument("--accept-score", type=score_threshold, default=8)
    parser.add_argument("--timeout", type=positive_int, default=3600, help="ComfyUI prompt timeout in seconds.")
    parser.add_argument("--codex-timeout", type=positive_int, default=900, help="Codex review timeout in seconds.")
    parser.add_argument("--poll-interval", type=float, default=2.0)
    parser.add_argument("--width", type=positive_int, default=None, help="Optional output resize width override.")
    parser.add_argument("--height", type=positive_int, default=None, help="Optional output resize height override.")
    parser.add_argument("--dry-run", action="store_true", help="Plan jobs and validate references without generation.")
    parser.add_argument("--force", action="store_true", help="Do not skip accepted shots.")
    parser.add_argument(
        "--skip-codex-check",
        action="store_true",
        help="Skip Codex preflight. Useful for dry-run parsing before WSL Codex is installed.",
    )
    parser.add_argument("--client-id", default=str(uuid.uuid4()))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.output_root.mkdir(parents=True, exist_ok=True)
    state_path = args.output_root / "state.json"

    try:
        available_node_types = preflight(args, check_codex=not args.skip_codex_check and not args.dry_run)
        state = load_state(state_path)
        shots = load_shots(args.input_json)
        jobs = plan_jobs(args, shots, state, state_path)

        if args.dry_run:
            print(f"Dry run planned {len(jobs)} job(s).")
            for job in jobs:
                warning = f" warnings={job.warnings}" if job.warnings else ""
                print(
                    f"{job.shot_id}: {job.workflow_label} refs={json.dumps(job.references, ensure_ascii=False)}{warning}"
                )
            return 0

        if not jobs:
            print("No jobs to run.")
            return 0

        for job in jobs:
            run_job(args, available_node_types, state, state_path, job)
        return 0
    except KeyboardInterrupt:
        eprint("Interrupted.")
        return 130
    except Exception as exc:
        eprint(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
