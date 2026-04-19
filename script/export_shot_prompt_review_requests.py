from __future__ import annotations

import argparse
from pathlib import Path

from storyboard_workspace import (
    build_previous_shot_summary,
    build_shot_workspace_path,
    build_scene_context_summary,
    default_workspace_dir,
    ensure_project_output_dirs,
    ensure_workspace_dirs,
    load_json,
    save_json,
)


DEFAULT_SKILL_NAME = "short-drama-shot-review"


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
    }


def build_adapter_prompt(review_input: dict[str, object]) -> str:
    return (
        f"Use skill `{DEFAULT_SKILL_NAME}`.\n"
        "You are reviewing one generated still-image prompt for Qwen image edit readiness.\n"
        "Return JSON only with these fields:\n"
        "- result\n- decision\n- issue_category\n- reason\n- rewrite\n\n"
        "In prompt-review mode, rewrite may include image_prompt, panelTextType, panelText, sfxText.\n"
        "Do not redesign the scene.\n"
        "Reject raw reference markers, placeholder preserve wording, engineering memo language, or weak preserve/change clarity.\n\n"
        f"Review input JSON:\n{review_input}\n"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export prompt-review requests for MCP-in-chat workflow.")
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
        if shot.get("status") not in {"prompt_generated", "approved"}:
            continue
        request_path = workspace_paths["requests"] / f"{shot_id}_prompt_review_request.json"
        if request_path.exists() and not args.force:
            continue
        previous_summary = load_previous_summary(workspace_dir, shot)
        scene_context = load_scene_context(workspace_dir, shot)
        review_input = {
            "review_level": "shot_prompt",
            "shot": {
                "scene_id": shot.get("scene_id", ""),
                "scene_number": shot.get("scene_number", ""),
                "shot_id": shot.get("shot_id", ""),
                "shot_number": shot.get("shot_number", ""),
                "shot_goal": shot.get("shot_goal", ""),
                "visual_focus": shot.get("visual_focus", ""),
                "shot_description": shot.get("shot_description", ""),
                "must_show": shot.get("must_show", []),
                "reference_needs": shot.get("reference_needs", []),
                "prompt_workflow": shot.get("prompt_workflow", ""),
                "support_character_mode": shot.get("support_character_mode", "none"),
                "prompt_output": shot.get("prompt_output", {}),
            },
            "scene_context_summary": build_scene_context_summary(scene_context),
            "previous_shot_summary": previous_summary,
        }
        request_payload = {
            "mode": "shot_prompt_review",
            "item_id": shot_id,
            "skill": DEFAULT_SKILL_NAME,
            **review_input,
            "adapter_prompt": build_adapter_prompt(review_input),
        }
        save_json(request_path, request_payload)
        print(f"[done] exported prompt review request {shot_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
