from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from storyboard_workspace import (
    default_workspace_dir,
    ensure_project_output_dirs,
    ensure_workspace_dirs,
    invoke_command_adapter,
    load_json,
    save_json,
)


def issue(issue_category: str, severity: str, decision: str, reason: str) -> dict[str, str]:
    return {
        "issue_category": issue_category,
        "severity": severity,
        "decision": decision,
        "reason": reason,
    }


def detect_shot_issues(shot: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    prompt_output = shot.get("prompt_output") or {}
    image_prompt = str(prompt_output.get("image_prompt", ""))
    panel_text_type = str(prompt_output.get("panelTextType", "none"))

    if not image_prompt:
        issues.append(issue("missing_field", "high", "rewrite_prompt_only", "缺少 image_prompt"))
    if len(image_prompt) > 260:
        issues.append(issue("overloaded_prompt", "medium", "rewrite_prompt_only", "image_prompt 過長，容易失焦"))
    if not str(shot.get("visual_focus", "")).strip():
        issues.append(issue("weak_planner_focus", "medium", "replan_shot", "planner 沒有清楚 visual_focus"))
    if panel_text_type not in {"dialogue", "caption", "inner_thought", "sfx", "none"}:
        issues.append(issue("invalid_panel_text_type", "medium", "rewrite_prompt_only", "panelTextType 不在允許值內"))
    return issues


def detect_scene_issues(shots: list[dict[str, Any]]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    previous_goal = ""
    previous_shot_id = ""
    for shot in shots:
        current_goal = str(shot.get("shot_goal", "")).strip()
        if current_goal and current_goal == previous_goal:
            issues.append(
                issue(
                    "duplicate_shot_function",
                    "medium",
                    "merge_with_previous",
                    f"{shot.get('shot_id')} 與 {previous_shot_id} 的 shot_goal 幾乎重覆",
                )
            )
        previous_goal = current_goal
        previous_shot_id = str(shot.get("shot_id", ""))
    return issues


def heuristic_review_shot(shot: dict[str, Any]) -> dict[str, Any]:
    issues = detect_shot_issues(shot)
    return {
        "result": "pass" if not issues else "fail",
        "review_level": "shot",
        "issues": issues,
        "hook_priority_notes": [],
        "final_continuity_risks": [],
        "operator_handoff_summary": "",
    }


def heuristic_review_scene(shots: list[dict[str, Any]], scene_id: str) -> dict[str, Any]:
    issues = detect_scene_issues(shots)
    return {
        "result": "pass" if not issues else "fail",
        "review_level": "scene",
        "scene_id": scene_id,
        "issues": issues,
        "hook_priority_notes": [],
        "final_continuity_risks": [],
        "operator_handoff_summary": "Scene review completed on lean shot schema.",
    }


def heuristic_review_board(shots: list[dict[str, Any]]) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    if not shots:
        issues.append(issue("missing_panels", "high", "replan_shot", "workspace 內沒有可 review 的 shot"))
    return {
        "result": "pass" if not issues else "fail",
        "review_level": "board",
        "issues": issues,
        "hook_priority_notes": [],
        "final_continuity_risks": [],
        "operator_handoff_summary": "Board review completed on image_prompt / panelText payload.",
    }


def review_shot(shot: dict[str, Any], workspace_dir: Path, executor: str, command_template: str) -> dict[str, Any]:
    if executor == "heuristic":
        review = heuristic_review_shot(shot)
    else:
        workspace_paths = ensure_workspace_dirs(workspace_dir)
        request_path = workspace_paths["requests"] / f"{shot['shot_id']}_review_request.json"
        response_path = workspace_paths["responses"] / f"{shot['shot_id']}_review_response.json"
        request_payload = {
            "mode": "shot_review",
            "item_id": shot["shot_id"],
            "skill": "short-drama-start-image-review",
            "shot": shot,
        }
        review = invoke_command_adapter(command_template, request_payload, request_path, response_path)

    updated = dict(shot)
    updated["review_result"] = review
    updated["review_status"] = review.get("result", "fail")
    updated["status"] = "approved" if review.get("result") == "pass" else "reviewed"
    updated["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    return updated


def review_scene(scene_shots: list[dict[str, Any]], scene_id: str, workspace_dir: Path, executor: str, command_template: str) -> dict[str, Any]:
    if executor == "heuristic":
        return heuristic_review_scene(scene_shots, scene_id)
    workspace_paths = ensure_workspace_dirs(workspace_dir)
    request_path = workspace_paths["requests"] / f"{scene_id}_scene_review_request.json"
    response_path = workspace_paths["responses"] / f"{scene_id}_scene_review_response.json"
    request_payload = {
        "mode": "scene_review",
        "item_id": scene_id,
        "skill": "short-drama-start-image-review",
        "scene_id": scene_id,
        "shots": scene_shots,
    }
    return invoke_command_adapter(command_template, request_payload, request_path, response_path)


def review_board(all_shots: list[dict[str, Any]], workspace_dir: Path, executor: str, command_template: str) -> dict[str, Any]:
    if executor == "heuristic":
        return heuristic_review_board(all_shots)
    workspace_paths = ensure_workspace_dirs(workspace_dir)
    request_path = workspace_paths["requests"] / "board_review_request.json"
    response_path = workspace_paths["responses"] / "board_review_response.json"
    request_payload = {
        "mode": "board_review",
        "item_id": "board",
        "skill": "short-drama-start-image-review",
        "shots": all_shots,
    }
    return invoke_command_adapter(command_template, request_payload, request_path, response_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review storyboard prompts and assembled board readiness.")
    parser.add_argument("--project-dir", default="")
    parser.add_argument("--workspace-dir", default="")
    parser.add_argument("--executor", choices=["heuristic", "command"], default="heuristic")
    parser.add_argument("--command-template", default="")
    parser.add_argument("--level", choices=["shot", "scene", "board", "all"], default="shot")
    parser.add_argument("--shot-id", action="append")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir) if args.project_dir else Path.cwd()
    ensure_project_output_dirs(project_dir)
    workspace_dir = Path(args.workspace_dir) if args.workspace_dir else default_workspace_dir(project_dir)
    ensure_workspace_dirs(workspace_dir)
    selected_ids = set(args.shot_id or [])

    if args.level in {"shot", "all"}:
        for shot_path in sorted((workspace_dir / "shots").glob("*.json")):
            shot = load_json(shot_path)
            if selected_ids and shot.get("shot_id") not in selected_ids:
                continue
            if not args.force and shot.get("review_status") in {"pass", "fail"}:
                continue
            if shot.get("status") not in {"prompt_generated", "reviewed", "approved", "assembled"}:
                continue
            reviewed = review_shot(shot, workspace_dir, args.executor, args.command_template)
            save_json(shot_path, reviewed)
            print(f"[done] reviewed {reviewed['shot_id']} -> {reviewed['review_result']['result']}")

    if args.level in {"scene", "all"}:
        scene_groups: dict[str, list[dict[str, Any]]] = {}
        all_shots = [load_json(path) for path in sorted((workspace_dir / "shots").glob("*.json"))]
        for shot in all_shots:
            scene_groups.setdefault(str(shot.get("scene_id", "")), []).append(shot)
        for scene_id, scene_shots in scene_groups.items():
            review = review_scene(scene_shots, scene_id, workspace_dir, args.executor, args.command_template)
            workspace_paths = ensure_workspace_dirs(workspace_dir)
            save_json(workspace_paths["reviews"] / f"{scene_id}_scene_review.json", review)
            print(f"[done] scene review {scene_id} -> {review['result']}")

    if args.level in {"board", "all"}:
        all_shots = [load_json(path) for path in sorted((workspace_dir / "shots").glob("*.json"))]
        review = review_board(all_shots, workspace_dir, args.executor, args.command_template)
        workspace_paths = ensure_workspace_dirs(workspace_dir)
        save_json(workspace_paths["reviews"] / "board_review.json", review)
        print(f"[done] board review -> {review['result']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
