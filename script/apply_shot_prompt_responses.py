from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from storyboard_workspace import (
    default_workspace_dir,
    ensure_project_output_dirs,
    ensure_workspace_dirs,
    load_json,
    normalize_prompt_output,
    save_json,
)


def validate_prompt_output(prompt_output: dict[str, object]) -> None:
    required = ["image_prompt", "panelTextType", "panelText"]
    missing = [field for field in required if field not in prompt_output]
    if missing:
        raise RuntimeError(f"Prompt output missing fields: {', '.join(missing)}")
    image_prompt = str(prompt_output.get("image_prompt", "")).strip()
    if not image_prompt:
        raise RuntimeError("Prompt output image_prompt is empty.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply generated prompt responses back into shot JSON files.")
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
        response_path = workspace_paths["responses"] / f"{shot_id}_prompt_response.json"
        if not response_path.exists():
            continue
        prompt_output = normalize_prompt_output(load_json(response_path))
        validate_prompt_output(prompt_output)
        updated = dict(shot)
        updated["prompt_output"] = prompt_output
        updated["status"] = "prompt_generated"
        updated["updated_at"] = datetime.now(timezone.utc).isoformat()
        save_json(shot_path, updated)
        print(f"[done] applied prompt response {shot_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
