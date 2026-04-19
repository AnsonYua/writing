from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from storyboard_workspace import (
    build_reference_context,
    build_previous_shot_summary,
    build_scene_context_summary,
    build_shot_workspace_path,
    build_workflow_reference_plan,
    default_workspace_dir,
    ensure_project_output_dirs,
    ensure_workspace_dirs,
    invoke_command_adapter,
    load_json,
    normalize_prompt_output,
    project_shot_to_prompt_input,
    save_json,
)


DEFAULT_SKILL_NAME = "short-drama-shot-prompt"


def validate_prompt_output(prompt_output: dict[str, object]) -> None:
    required = ["image_prompt", "panelTextType", "panelText"]
    missing = [field for field in required if field not in prompt_output]
    if missing:
        raise RuntimeError(f"Prompt output missing fields: {', '.join(missing)}")
    image_prompt = str(prompt_output.get("image_prompt", "")).strip()
    if not image_prompt:
        raise RuntimeError("Prompt output image_prompt is empty.")
    banned_markers = ["scene_ref", "character_ref", "second_character_ref", "prop_ref"]
    lowered = image_prompt.lower()
    found = [marker for marker in banned_markers if marker in lowered]
    if found:
        raise RuntimeError(f"Prompt output still contains raw reference markers: {', '.join(found)}")


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
    previous_shot = load_json(previous_path)
    return build_previous_shot_summary(previous_shot)


def load_scene_context(workspace_dir: Path, shot: dict[str, object]) -> dict[str, object]:
    scene_path = workspace_dir / f"scene_{shot['scene_id']}_shots.json"
    if scene_path.exists():
        return load_json(scene_path)
    return {
        "scene_id": shot.get("scene_id", ""),
        "scene_number": shot.get("scene_number", ""),
        "scene_goal": shot.get("scene_goal", ""),
        "scene_key_image": "",
        "scene_end_hook": "",
        "characters_present": "",
        "location": "",
        "time_feel": "",
        "continuity_notes": [],
    }


def build_adapter_prompt(*, prompt_input: dict[str, object]) -> str:
    return (
        f"Use skill `{DEFAULT_SKILL_NAME}`.\n"
        "You are in Qwen-style shot-level image prompt writing mode.\n"
        "Think like a prompt enhancement step for image edit, but return JSON only.\n"
        "Required JSON fields:\n"
        "- image_prompt\n- panelTextType\n- panelText\n- sfxText\n\n"
        "Rules:\n"
        "- Write one polished still-image prompt only.\n"
        "- Do not output start_image_prompt.\n"
        "- Do not output comfy_image_prompt.\n"
        "- Do not output dialogueText or captionText.\n"
        "- Do not redesign shot structure.\n"
        "- First infer what each reference must preserve.\n"
        "- Separate appearance preservation from semantic scene preservation.\n"
        "- Never write raw markers like scene_ref, character_ref, second_character_ref, prop_ref in the final prompt.\n"
        "- Never write placeholder wording like 保留參考重點 or 同一角色 identity.\n"
        "- Use natural Traditional Chinese sentences.\n"
        "- The final prompt must read like one drawable still panel, not an engineering memo.\n\n"
        f"Prompt input JSON:\n{prompt_input}\n"
    )


def generate_for_shot(shot: dict[str, object], project_dir: Path, workspace_dir: Path, command_template: str) -> dict[str, object]:
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

    workspace_paths = ensure_workspace_dirs(workspace_dir)
    request_path = workspace_paths["requests"] / f"{shot['shot_id']}_prompt_request.json"
    response_path = workspace_paths["responses"] / f"{shot['shot_id']}_prompt_response.json"
    request_payload = {
        "mode": "shot_prompt",
        "item_id": shot["shot_id"],
        "skill": DEFAULT_SKILL_NAME,
        **prompt_input,
        "adapter_prompt": build_adapter_prompt(prompt_input=prompt_input),
    }
    prompt_output = normalize_prompt_output(
        invoke_command_adapter(command_template, request_payload, request_path, response_path)
    )
    validate_prompt_output(prompt_output)

    updated = {key: value for key, value in shot.items() if key != "prompt_output"}
    updated["prompt_output"] = prompt_output
    updated["status"] = "prompt_generated"
    updated["updated_at"] = datetime.now(timezone.utc).isoformat()
    return updated


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate storyboard shot prompts via LLM only.")
    parser.add_argument("--project-dir", default="")
    parser.add_argument("--workspace-dir", default="")
    parser.add_argument("--executor", choices=["command", "heuristic"], default="command")
    parser.add_argument("--command-template", default="")
    parser.add_argument("--shot-id", action="append")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--allow-debug-heuristic", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.executor != "command":
        if not args.allow_debug_heuristic:
            raise RuntimeError("LLM-only mode is required. Use --executor command, or add --allow-debug-heuristic only for local debugging.")
        raise RuntimeError("Debug heuristic mode is no longer implemented for prompt generation.")
    if not args.command_template.strip():
        raise RuntimeError("Missing --command-template. LLM-only prompt generation requires a Codex/MCP command bridge.")

    project_dir = Path(args.project_dir) if args.project_dir else Path.cwd()
    ensure_project_output_dirs(project_dir)
    workspace_dir = Path(args.workspace_dir) if args.workspace_dir else default_workspace_dir(project_dir)
    ensure_workspace_dirs(workspace_dir)
    selected_ids = set(args.shot_id or [])

    for shot_path in sorted((workspace_dir / "shots").glob("*.json")):
        shot = load_json(shot_path)
        if selected_ids and shot.get("shot_id") not in selected_ids:
            continue
        if not args.force and shot.get("status") in {"prompt_generated", "approved", "assembled"}:
            continue
        if shot.get("review_status") == "fail":
            continue
        if shot.get("review_result", {}).get("decision") in {"merge_with_previous", "delete_shot"}:
            continue
        generated = generate_for_shot(shot, project_dir, workspace_dir, args.command_template)
        save_json(shot_path, generated)
        print(f"[done] prompt-generated {generated['shot_id']} via {DEFAULT_SKILL_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
