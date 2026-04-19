from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from storyboard_workspace import (
    default_workspace_dir,
    ensure_project_output_dirs,
    ensure_workspace_dirs,
    load_json,
    save_json,
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply generated prompt review responses back into shot JSON files.")
    parser.add_argument("--project-dir", default="")
    parser.add_argument("--workspace-dir", default="")
    parser.add_argument("--shot-id", action="append")
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
        response_path = workspace_paths["responses"] / f"{shot_id}_prompt_review_response.json"
        if not response_path.exists():
            continue
        review = load_json(response_path)
        updated, applied = apply_prompt_rewrite(shot, review)
        updated["prompt_review_result"] = review
        updated["prompt_review_status"] = review.get("result", "fail")
        updated["prompt_review_applied"] = applied
        updated["status"] = "approved" if review.get("decision") not in {"merge_with_previous", "delete_shot"} else "prompt_generated"
        updated["prompt_reviewed_at"] = datetime.now(timezone.utc).isoformat()
        save_json(shot_path, updated)
        print(f"[done] applied prompt review response {shot_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
