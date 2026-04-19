from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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


def load_previous_summary(workspace_dir: Path, current_shot: dict[str, Any]) -> dict[str, Any] | None:
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


def load_scene_context(workspace_dir: Path, shot: dict[str, Any]) -> dict[str, Any]:
    scene_path = workspace_dir / f"scene_{shot['scene_id']}_shots.json"
    if scene_path.exists():
        return load_json(scene_path)
    return {
        "scene_goal": shot.get("scene_goal", ""),
        "scene_key_image": shot.get("scene_key_image", ""),
        "scene_end_hook": shot.get("scene_end_hook", ""),
        "characters_present": shot.get("characters_present", ""),
    }


def detect_issue(shot: dict[str, Any], previous_summary: dict[str, Any] | None) -> tuple[str, str, str, dict[str, Any] | None]:
    visual_focus = str(shot.get("visual_focus", "")).strip()
    description = str(shot.get("shot_description", "")).strip()
    must_show = [str(item).strip() for item in shot.get("must_show", []) if str(item).strip()]
    goal = str(shot.get("shot_goal", "")).strip()

    if not visual_focus:
        return "fail", "rewrite_shot", "focus_missing", {
            "visual_focus": description[:24] or goal[:24],
        }

    if len(must_show) > 4:
        return "fail", "rewrite_shot", "must_show_overload", {
            "must_show": must_show[:4],
        }

    reaction_markers = ["反應", "擊中", "僵住", "停住", "發白", "驚", "怕"]
    if any(marker in goal or marker in visual_focus for marker in reaction_markers):
        trigger_markers = ["手機", "畫面", "照片", "相", "內容", "證據", "proof"]
        if not any(marker in description or marker in " ".join(must_show) for marker in trigger_markers):
            rewrite = {
                "visual_focus": f"{visual_focus}，因為手上內容不對勁" if "內容" not in visual_focus else visual_focus,
                "shot_description": f"{description.rstrip('。')}，看得出她是被手上的內容當場擊中。" if description else "",
            }
            return "fail", "rewrite_shot", "reaction_trigger_missing", rewrite

    if previous_summary:
        prev_summary = str(previous_summary.get("summary", "")).strip()
        if prev_summary and visual_focus and visual_focus in prev_summary:
            return "fail", "merge_with_previous", "duplicate_function", None

    if "、" in description and description.count("，") >= 3:
        rewritten = "，".join(description.split("，")[:2]).rstrip("。") + "。"
        return "fail", "rewrite_shot", "continuity_memo_smell", {
            "shot_description": rewritten,
        }

    return "pass", "keep", "none", None


def heuristic_review(shot: dict[str, Any], scene_context: dict[str, Any], previous_summary: dict[str, Any] | None) -> dict[str, Any]:
    result, decision, issue_category, rewrite = detect_issue(shot, previous_summary)
    reason_map = {
        "none": "Shot task is clear enough to enter prompt generation.",
        "focus_missing": "這格缺少清楚 visual focus。",
        "must_show_overload": "這格 must_show 太多，主次未分清。",
        "reaction_trigger_missing": "這格只看見反應結果，未看得出角色是被什麼擊中。",
        "duplicate_function": "這格與上一格功能過於接近，像重複 panel。",
        "continuity_memo_smell": "這格 description 比較像 continuity memo，不夠像單格畫面。",
    }
    return {
        "result": result,
        "decision": decision,
        "issue_category": issue_category,
        "reason": reason_map.get(issue_category, "Shot review flagged a structural issue."),
        "rewrite": rewrite or {},
    }


def build_adapter_prompt(review_input: dict[str, Any]) -> str:
    return (
        f"Use skill `{DEFAULT_SKILL_NAME}`.\n"
        "You are reviewing one planned storyboard shot before prompt generation.\n"
        "Return JSON only with these fields:\n"
        "- result\n- decision\n- issue_category\n- reason\n- rewrite\n\n"
        "Allowed decisions: keep, rewrite_shot, merge_with_previous, delete_shot.\n"
        "Do not rewrite the whole scene.\n"
        "Do not write image prompts.\n\n"
        f"Review input JSON:\n{review_input}\n"
    )


def apply_rewrite(shot: dict[str, Any], review: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if review.get("decision") != "rewrite_shot":
        return shot, False
    rewrite = review.get("rewrite") or {}
    if not isinstance(rewrite, dict) or not rewrite:
        return shot, False
    updated = dict(shot)
    for key in ["shot_goal", "visual_focus", "shot_description", "must_show"]:
        if key in rewrite and rewrite[key]:
            updated[key] = rewrite[key]
    return updated, True


def review_shot(shot: dict[str, Any], workspace_dir: Path, executor: str, command_template: str) -> dict[str, Any]:
    previous_summary = load_previous_summary(workspace_dir, shot)
    scene_context = load_scene_context(workspace_dir, shot)
    review_input = {
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
        },
        "scene_context_summary": build_scene_context_summary(scene_context),
        "previous_shot_summary": previous_summary,
    }

    if executor == "heuristic":
        review = heuristic_review(shot, scene_context, previous_summary)
    else:
        workspace_paths = ensure_workspace_dirs(workspace_dir)
        request_path = workspace_paths["requests"] / f"{shot['shot_id']}_planned_review_request.json"
        response_path = workspace_paths["responses"] / f"{shot['shot_id']}_planned_review_response.json"
        request_payload = {
            "mode": "shot_planned_review",
            "item_id": shot["shot_id"],
            "skill": DEFAULT_SKILL_NAME,
            **review_input,
            "adapter_prompt": build_adapter_prompt(review_input),
        }
        review = invoke_command_adapter(command_template, request_payload, request_path, response_path)

    updated, applied = apply_rewrite(shot, review)
    updated["review_result"] = review
    updated["review_status"] = review.get("result", "fail")
    updated["review_applied"] = applied
    updated["status"] = "planned" if review.get("decision") in {"merge_with_previous", "delete_shot"} else "reviewed"
    updated["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    return updated


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review lean planned shots before prompt generation.")
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
            raise RuntimeError("LLM-first review is required. Use --executor command, or add --allow-debug-heuristic only for local debugging.")
    elif not args.command_template.strip():
        raise RuntimeError("Missing --command-template. Planned-shot review requires a Codex/MCP command bridge.")

    project_dir = Path(args.project_dir) if args.project_dir else Path.cwd()
    ensure_project_output_dirs(project_dir)
    workspace_dir = Path(args.workspace_dir) if args.workspace_dir else default_workspace_dir(project_dir)
    workspace_paths = ensure_workspace_dirs(workspace_dir)
    selected_ids = set(args.shot_id or [])

    for shot_path in sorted((workspace_dir / "shots").glob("*.json")):
        shot = load_json(shot_path)
        if selected_ids and shot.get("shot_id") not in selected_ids:
            continue
        if not args.force and shot.get("review_status") in {"pass", "fail"}:
            continue
        reviewed = review_shot(shot, workspace_dir, args.executor, args.command_template)
        save_json(shot_path, reviewed)
        save_json(workspace_paths["reviews"] / f"{reviewed['shot_id']}_planned_review.json", reviewed["review_result"])
        print(f"[done] planned-shot review {reviewed['shot_id']} -> {reviewed['review_result']['decision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
