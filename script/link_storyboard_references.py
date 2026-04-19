from __future__ import annotations

import argparse
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from storyboard_workspace import default_storyboard_json, ensure_project_output_dirs, load_json, save_json


DEFAULT_SKILL_NAME = "short-drama-reference-linker"


def default_reference_link_root(project_dir: Path) -> Path:
    return project_dir / "output" / "reference-linking"


def default_linked_storyboard_json(project_dir: Path) -> Path:
    return project_dir / "output" / "linked-storyboard.json"


def ensure_reference_link_dirs(project_dir: Path) -> dict[str, Path]:
    root = default_reference_link_root(project_dir)
    dirs = {
        "root": root,
        "requests": root / "requests",
        "responses": root / "responses",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export/apply post-storyboard reference-linking requests.")
    parser.add_argument("--project-dir", default="")
    parser.add_argument("--storyboard-json", default="")
    parser.add_argument("--output-json", default="")
    parser.add_argument("--requests-dir", default="")
    parser.add_argument("--responses-dir", default="")
    parser.add_argument("--actual-reference-map", default="")
    parser.add_argument("--shot-id", action="append")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def infer_character_names(shot: dict[str, Any]) -> list[str]:
    shot_description = str(shot.get("shot_description", "")).strip()
    haystack = " ".join(
        [
            str(shot.get("visual_focus", "")),
            shot_description,
            str(shot.get("image_prompt", "")),
        ]
    )
    positions: list[tuple[int, str]] = []
    for candidate in ["周曉晴", "李美珍", "陳國強", "周晓晴", "李美珍", "陈国强"]:
        index = haystack.find(candidate)
        if index != -1:
            positions.append((index, candidate))
    positions.sort(key=lambda item: item[0])
    names: list[str] = []
    for _, candidate in positions:
        if candidate not in names:
            names.append(candidate)
    leading = re.match(r"^([\u4e00-\u9fff]{2,4})", shot_description)
    if leading:
        lead_name = leading.group(1)
        if lead_name in names:
            names = [lead_name] + [name for name in names if name != lead_name]
    return names


def infer_reference_defaults(shot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    names = infer_character_names(shot)
    refs: dict[str, dict[str, Any]] = {}

    if "character_ref" in shot.get("reference_needs", []):
        main_name = names[0] if names else ""
        refs["character_ref"] = {
            "slot": "image1",
            "path": "",
            "job": "main_character_appearance",
            "preserve": f"保留{main_name}的外觀與辨識特徵" if main_name else "保留主角外觀與辨識特徵",
            "available": False,
        }

    if "scene_ref" in shot.get("reference_needs", []):
        used = {item["slot"] for item in refs.values()}
        slot = "image2" if "image2" not in used else "image3"
        refs["scene_ref"] = {
            "slot": slot,
            "path": "",
            "job": "scene_layout",
            "preserve": "保留房間方向、門口位置、室內光線與空間關係",
            "available": False,
        }

    if "prop_ref" in shot.get("reference_needs", []):
        used = {item["slot"] for item in refs.values()}
        slot = "image3" if "image3" not in used else "image4"
        refs["prop_ref"] = {
            "slot": slot,
            "path": "",
            "job": "prop_continuity",
            "preserve": "保留同一道具身份與當前狀態",
            "available": False,
        }

    if "second_character_ref" in shot.get("reference_needs", []):
        secondary_name = names[1] if len(names) > 1 else ""
        used = {item["slot"] for item in refs.values()}
        slot = "image4"
        for candidate in ["image2", "image3", "image4"]:
            if candidate not in used:
                slot = candidate
                break
        refs["second_character_ref"] = {
            "slot": slot,
            "path": "",
            "job": "support_character_appearance",
            "preserve": f"保留{secondary_name}的外觀與可讀性" if secondary_name else "保留支援角色外觀與可讀性",
            "available": False,
        }

    return refs


def load_reference_map(path: str) -> dict[str, Any]:
    if not path:
        return {}
    return load_json(Path(path))


def resolve_actual_reference_map(shot: dict[str, Any], full_map: dict[str, Any]) -> dict[str, dict[str, Any]]:
    resolved = infer_reference_defaults(shot)
    shot_id = str(shot.get("shot_id", ""))
    shot_map = full_map.get(shot_id, {}) if isinstance(full_map.get(shot_id, {}), dict) else {}
    for key, payload in shot_map.items():
        if not isinstance(payload, dict):
            continue
        current = dict(resolved.get(key, {}))
        current.update(payload)
        current["available"] = bool(current.get("path"))
        if not current.get("slot"):
            current["slot"] = f"image{len(resolved) + 1}"
        resolved[key] = current
    return resolved


def build_adapter_prompt(shot: dict[str, Any], actual_reference_map: dict[str, Any]) -> str:
    payload = {
        "shot": shot,
        "actual_reference_map": actual_reference_map,
        "project_context": {
            "goal": "把 canonical storyboard prompt 轉成 downstream-ready multi-reference linked prompt",
            "language": "Traditional Chinese",
        },
    }
    return (
        f"Use skill `{DEFAULT_SKILL_NAME}`.\n"
        "Return JSON only for the current shot.\n"
        "Required JSON fields:\n"
        "- resolved_image_prompt\n- reference_assignment\n- linking_note\n\n"
        "Do not change storyline or shot function.\n"
        "Keep the canonical image_prompt meaning intact.\n"
        "Use actual_reference_map to decide clear image1/image2/image3 jobs.\n"
        "Write natural Traditional Chinese.\n"
        "If a needed reference is missing, keep the prompt usable and explain briefly in linking_note.\n\n"
        f"Linking input JSON:\n{payload}\n"
    )


def validate_response(response: dict[str, Any]) -> dict[str, Any]:
    required = ["resolved_image_prompt", "reference_assignment", "linking_note"]
    missing = [field for field in required if field not in response]
    if missing:
        raise RuntimeError(f"Reference-link response missing fields: {', '.join(missing)}")
    if not str(response.get("resolved_image_prompt", "")).strip():
        raise RuntimeError("Reference-link response resolved_image_prompt is empty.")
    if not isinstance(response.get("reference_assignment"), dict):
        raise RuntimeError("Reference-link response reference_assignment must be an object.")
    return {
        "resolved_image_prompt": str(response.get("resolved_image_prompt", "")).strip(),
        "reference_assignment": response.get("reference_assignment", {}),
        "linking_note": str(response.get("linking_note", "") or "").strip(),
    }


def export_request(request_path: Path, shot: dict[str, Any], actual_reference_map: dict[str, Any]) -> None:
    payload = {
        "mode": "reference_link",
        "item_id": shot.get("shot_id", ""),
        "skill": DEFAULT_SKILL_NAME,
        "shot": shot,
        "actual_reference_map": actual_reference_map,
        "adapter_prompt": build_adapter_prompt(shot, actual_reference_map),
    }
    save_json(request_path, payload)


def build_linked_storyboard(
    storyboard: dict[str, Any],
    applied: dict[str, dict[str, Any]],
    actual_maps: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    linked = deepcopy(storyboard)
    linked["linked_output"] = {
        "skill": DEFAULT_SKILL_NAME,
        "resolved_shots": sorted(applied.keys()),
    }
    for scene in linked.get("scenes", []):
        for shot in scene.get("shots", []):
            shot_id = str(shot.get("shot_id", ""))
            shot["reference_link_status"] = "linked" if shot_id in applied else "pending"
            shot["actual_reference_map"] = actual_maps.get(shot_id, {})
            if shot_id in applied:
                shot["resolved_image_prompt"] = applied[shot_id]["resolved_image_prompt"]
                shot["reference_assignment"] = applied[shot_id]["reference_assignment"]
                shot["linking_note"] = applied[shot_id]["linking_note"]
    return linked


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir) if args.project_dir else Path.cwd()
    ensure_project_output_dirs(project_dir)
    link_dirs = ensure_reference_link_dirs(project_dir)
    storyboard_json = Path(args.storyboard_json) if args.storyboard_json else default_storyboard_json(project_dir)
    output_json = Path(args.output_json) if args.output_json else default_linked_storyboard_json(project_dir)
    requests_dir = Path(args.requests_dir) if args.requests_dir else link_dirs["requests"]
    responses_dir = Path(args.responses_dir) if args.responses_dir else link_dirs["responses"]
    requests_dir.mkdir(parents=True, exist_ok=True)
    responses_dir.mkdir(parents=True, exist_ok=True)
    selected_ids = set(args.shot_id or [])

    storyboard = load_json(storyboard_json)
    full_reference_map = load_reference_map(args.actual_reference_map)
    applied: dict[str, dict[str, Any]] = {}
    actual_maps: dict[str, dict[str, Any]] = {}

    for scene in storyboard.get("scenes", []):
        for shot in scene.get("shots", []):
            shot_id = str(shot.get("shot_id", ""))
            if selected_ids and shot_id not in selected_ids:
                continue
            actual_map = resolve_actual_reference_map(shot, full_reference_map)
            actual_maps[shot_id] = actual_map
            request_path = requests_dir / f"{shot_id}_reference_link_request.json"
            response_path = responses_dir / f"{shot_id}_reference_link_response.json"
            if args.force or not request_path.exists():
                export_request(request_path, shot, actual_map)
                print(f"[done] exported reference-link request {shot_id}")
            if response_path.exists():
                applied[shot_id] = validate_response(load_json(response_path))
                print(f"[done] applied reference-link response {shot_id}")

    save_json(output_json, build_linked_storyboard(storyboard, applied, actual_maps))
    print(f"[done] wrote linked storyboard -> {output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
