from __future__ import annotations

import argparse
from pathlib import Path

from storyboard_workspace import (
    build_reference_context,
    build_previous_shot_summary,
    build_shot_workspace_path,
    build_workflow_reference_plan,
    default_workspace_dir,
    ensure_project_output_dirs,
    ensure_workspace_dirs,
    load_json,
    project_shot_to_prompt_input,
    save_json,
)


DEFAULT_SKILL_NAME = "short-drama-shot-prompt"


def load_previous_summary(workspace_dir: Path, current_shot: dict[str, object]) -> dict[str, object] | None:
    try:
        shot_number = int(str(current_shot.get("shot_number", "1")))
    except ValueError:
        return None
    if shot_number <= 1:
        return None
    previous_id = f"{current_shot['scene_id']}_SH{shot_number - 1}"
    previous_path = build_shot_workspace_path(workspace_dir, previous_id)
    if not previous_path.exists():
        return None
    return build_previous_shot_summary(load_json(previous_path))


def load_scene_context(workspace_dir: Path, shot: dict[str, object]) -> dict[str, object]:
    scene_path = workspace_dir / f"scene_{shot['scene_id']}_shots.json"
    if scene_path.exists():
        return load_json(scene_path)
    return {
        "scene_goal": shot.get("scene_goal", ""),
        "scene_key_image": shot.get("scene_key_image", ""),
        "scene_end_hook": shot.get("scene_end_hook", ""),
        "characters_present": shot.get("characters_present", ""),
        "location": "",
        "time_feel": "",
        "continuity_notes": [],
    }


def build_adapter_prompt(prompt_input: dict[str, object]) -> str:
    return (
        f"Use skill `{DEFAULT_SKILL_NAME}`.\n"
        "Return JSON only for the current shot.\n"
        "Required JSON fields:\n"
        "- image_prompt\n- panelTextType\n- panelText\n- sfxText\n\n"
        "This is a Qwen-style still-image prompt writing task.\n"
        "First infer what each reference must preserve.\n"
        "Separate appearance preservation from semantic scene preservation and prop continuity.\n"
        "Never output raw markers like scene_ref, character_ref, second_character_ref, prop_ref in the final prompt.\n"
        "Never use placeholder wording like 保留參考重點 or 同一角色 identity.\n"
        "Write natural Traditional Chinese.\n"
        "Keep one drawable still panel with one clear visual center.\n\n"
        f"Prompt input JSON:\n{prompt_input}\n"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export per-shot prompt requests for MCP-in-chat workflow.")
    parser.add_argument("--project-dir", default="")
    parser.add_argument("--workspace-dir", default="")
    parser.add_argument("--shot-id", action="append")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir) if args.project_dir else Path.cwd()
    ensure_project_output_dirs(project_dir)
    workspace_dir = Path(args.workspace_dir) if args.workspace_dir else default_workspace_dir(project_dir)
    workspace_paths = ensure_workspace_dirs(workspace_dir)
    selected_ids = set(args.shot_id or [])

    for shot_path in sorted((workspace_dir / "shots").glob("*.json")):
        shot = load_json(shot_path)
        shot_id = str(shot.get("shot_id", ""))
        if selected_ids and shot_id not in selected_ids:
            continue
        if shot.get("review_status") == "fail":
            continue
        if shot.get("review_result", {}).get("decision") in {"merge_with_previous", "delete_shot"}:
            continue
        request_path = workspace_paths["requests"] / f"{shot_id}_prompt_request.json"
        if request_path.exists() and not args.force:
            continue
        previous_summary = load_previous_summary(workspace_dir, shot)
        scene_context = load_scene_context(workspace_dir, shot)
        reference_context = build_reference_context(project_dir, shot, scene_context, previous_summary)
        workflow_reference_plan = build_workflow_reference_plan(shot, previous_summary)
        prompt_input = project_shot_to_prompt_input(
            shot,
            scene_context,
            previous_summary,
            reference_context=reference_context,
            workflow_reference_plan=workflow_reference_plan,
        )
        request_payload = {
            "mode": "shot_prompt",
            "item_id": shot_id,
            "skill": DEFAULT_SKILL_NAME,
            **prompt_input,
            "adapter_prompt": build_adapter_prompt(prompt_input),
        }
        save_json(request_path, request_payload)
        print(f"[done] exported prompt request {shot_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
