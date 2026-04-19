from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from storyboard_workspace import (
    default_scene_pack_md,
    default_storyboard_json,
    default_storyboard_md,
    default_workspace_dir,
    ensure_project_output_dirs,
)


SCRIPT_DIR = Path(__file__).resolve().parent


def run_python(script_name: str, *extra_args: str) -> None:
    subprocess.run(["python", str(SCRIPT_DIR / script_name), *extra_args], check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run planner -> shot review -> shot prompt -> prompt review -> assemble as one storyboard pipeline.")
    parser.add_argument("--project-dir", default="")
    parser.add_argument("--scene-pack-md", default="")
    parser.add_argument("--workspace-dir", default="")
    parser.add_argument("--output-json", default="")
    parser.add_argument("--output-md", default="")
    parser.add_argument("--executor", choices=["command", "heuristic"], default="command")
    parser.add_argument("--command-template", default="")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--scene-id", action="append")
    parser.add_argument("--shot-id", action="append")
    parser.add_argument("--allow-debug-heuristic", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.executor != "command":
        if not args.allow_debug_heuristic:
            raise RuntimeError("The formal storyboard pipeline is LLM-only. Use --executor command, or add --allow-debug-heuristic only for local debugging.")
    elif not args.command_template.strip():
        raise RuntimeError("Missing --command-template. The formal storyboard pipeline requires a Codex/MCP command bridge.")

    project_dir = Path(args.project_dir) if args.project_dir else Path.cwd()
    ensure_project_output_dirs(project_dir)
    scene_pack_md = args.scene_pack_md or str(default_scene_pack_md(project_dir))
    workspace_dir = args.workspace_dir or str(default_workspace_dir(project_dir))
    output_json = args.output_json or str(default_storyboard_json(project_dir))
    output_md = args.output_md or str(default_storyboard_md(project_dir))

    planner_args = ["--project-dir", str(project_dir), "--scene-pack-md", scene_pack_md, "--workspace-dir", workspace_dir, "--executor", args.executor]
    if args.command_template:
        planner_args.extend(["--command-template", args.command_template])
    for scene_id in args.scene_id or []:
        planner_args.extend(["--scene-id", scene_id])
    run_python("plan_storyboard_shots.py", *planner_args)

    shot_review_args = ["--project-dir", str(project_dir), "--workspace-dir", workspace_dir, "--executor", args.executor]
    if args.command_template:
        shot_review_args.extend(["--command-template", args.command_template])
    if args.force:
        shot_review_args.append("--force")
    if args.allow_debug_heuristic:
        shot_review_args.append("--allow-debug-heuristic")
    for shot_id in args.shot_id or []:
        shot_review_args.extend(["--shot-id", shot_id])
    run_python("review_planned_shots.py", *shot_review_args)

    prompt_args = ["--project-dir", str(project_dir), "--workspace-dir", workspace_dir, "--executor", args.executor]
    if args.command_template:
        prompt_args.extend(["--command-template", args.command_template])
    if args.force:
        prompt_args.append("--force")
    if args.allow_debug_heuristic:
        prompt_args.append("--allow-debug-heuristic")
    for shot_id in args.shot_id or []:
        prompt_args.extend(["--shot-id", shot_id])
    run_python("generate_storyboard_shot_prompts.py", *prompt_args)

    prompt_review_args = ["--project-dir", str(project_dir), "--workspace-dir", workspace_dir]
    if args.command_template:
        prompt_review_args.extend(["--command-template", args.command_template])
    if args.force:
        prompt_review_args.append("--force")
    for shot_id in args.shot_id or []:
        prompt_review_args.extend(["--shot-id", shot_id])
    run_python("review_generated_prompts.py", *prompt_review_args)

    run_python(
        "assemble_storyboard.py",
        "--project-dir",
        str(project_dir),
        "--workspace-dir",
        workspace_dir,
        "--output-json",
        output_json,
        "--output-md",
        output_md,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
