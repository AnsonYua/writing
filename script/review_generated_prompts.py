from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from storyboard_workspace import (
    build_previous_shot_summary,
    build_shot_workspace_path,
    build_scene_context_summary,
    default_workspace_dir,
    ensure_project_output_dirs,
    ensure_workspace_dirs,
    invoke_command_adapter,
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
        "Review target is the current shot prompt only.\n"
        "Allowed decisions: keep, rewrite_shot, merge_with_previous, delete_shot.\n"
        "In prompt-review mode, rewrite may include image_prompt, panelTextType, panelText, sfxText.\n"
        "Do not redesign the scene.\n"
        "Reject raw reference markers, placeholder preserve wording, engineering memo language, or weak preserve/change clarity.\n\n"
        f"Review input JSON:\n{review_input}\n"
    )


def apply_prompt_rewrite(shot: dict[str, object], review: dict[str, object]) -> tuple[dict[str, object], bool]:
    if review.get("decision") != "rewrite_shot":
        return shot, False
    rewrite = review.get("rewrite") or {}
    if not isinstance(rewrite, dict) or not rewrite:
        return shot, False
    updated = dict(shot)
    prompt_output = dict(updated.get("prompt_output") or {})
    changed = False
    for key in ["image_prompt", "panelTextType", "panelText", "sfxText"]:
        value = rewrite.get(key)
        if value is not None and str(value).strip():
            prompt_output[key] = value
            changed = True
    if changed:
        updated["prompt_output"] = prompt_output
    return updated, changed


def review_prompt(shot: dict[str, object], workspace_dir: Path, command_template: str) -> dict[str, object]:
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

    workspace_paths = ensure_workspace_dirs(workspace_dir)
    request_path = workspace_paths["requests"] / f"{shot['shot_id']}_prompt_review_request.json"
    response_path = workspace_paths["responses"] / f"{shot['shot_id']}_prompt_review_response.json"
    request_payload = {
        "mode": "shot_prompt_review",
        "item_id": shot["shot_id"],
        "skill": DEFAULT_SKILL_NAME,
        **review_input,
        "adapter_prompt": build_adapter_prompt(review_input),
    }
    review = invoke_command_adapter(command_template, request_payload, request_path, response_path)

    updated, applied = apply_prompt_rewrite(shot, review)
    updated["prompt_review_result"] = review
    updated["prompt_review_status"] = review.get("result", "fail")
    updated["prompt_review_applied"] = applied
    updated["status"] = "approved" if review.get("decision") not in {"merge_with_previous", "delete_shot"} else "prompt_generated"
    updated["prompt_reviewed_at"] = datetime.now(timezone.utc).isoformat()
    return updated


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review generated shot prompts for Qwen cleanliness and preserve/change clarity.")
    parser.add_argument("--project-dir", default="")
    parser.add_argument("--workspace-dir", default="")
    parser.add_argument("--command-template", default="")
    parser.add_argument("--shot-id", action="append")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.command_template.strip():
        raise RuntimeError("Missing --command-template. Prompt review requires a Codex/MCP command bridge.")

    project_dir = Path(args.project_dir) if args.project_dir else Path.cwd()
    ensure_project_output_dirs(project_dir)
    workspace_dir = Path(args.workspace_dir) if args.workspace_dir else default_workspace_dir(project_dir)
    workspace_paths = ensure_workspace_dirs(workspace_dir)
    selected_ids = set(args.shot_id or [])

    for shot_path in sorted((workspace_dir / "shots").glob("*.json")):
        shot = load_json(shot_path)
        if selected_ids and shot.get("shot_id") not in selected_ids:
            continue
        if shot.get("status") not in {"prompt_generated", "approved"}:
            continue
        if not args.force and shot.get("prompt_review_status") in {"pass", "fail"}:
            continue
        reviewed = review_prompt(shot, workspace_dir, args.command_template)
        save_json(shot_path, reviewed)
        save_json(workspace_paths["reviews"] / f"{reviewed['shot_id']}_prompt_review.json", reviewed["prompt_review_result"])
        print(f"[done] prompt review {reviewed['shot_id']} -> {reviewed['prompt_review_result']['decision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
