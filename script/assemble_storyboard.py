from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from storyboard_workspace import (
    compute_dialogue_summary,
    default_storyboard_json,
    default_storyboard_md,
    default_workspace_dir,
    ensure_project_output_dirs,
    ensure_workspace_dirs,
    load_json,
    save_json,
    save_text,
    shot_sort_key,
)


def collect_shots(workspace_dir: Path) -> list[dict[str, Any]]:
    shots = [load_json(path) for path in (workspace_dir / "shots").glob("*.json")]
    return sorted(shots, key=shot_sort_key)


def assembled_shot(shot: dict[str, Any]) -> dict[str, Any]:
    prompt_output = dict(shot.get("prompt_output") or {})
    image_prompt = str(prompt_output.get("image_prompt", ""))
    panel_text_type = str(prompt_output.get("panelTextType", "none"))
    panel_text = str(prompt_output.get("panelText", ""))
    sfx_text = str(prompt_output.get("sfxText", ""))
    return {
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
        "image_prompt": image_prompt,
        "panelTextType": panel_text_type,
        "panelText": panel_text,
        "sfxText": sfx_text,
    }


def scene_groups(shots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for shot in shots:
        grouped.setdefault(str(shot["scene_id"]), []).append(shot)
    result: list[dict[str, Any]] = []
    for scene_id in sorted(grouped.keys(), key=lambda value: int(value[1:])):
        scene_shots = grouped[scene_id]
        first = scene_shots[0]
        result.append(
            {
                "scene_number": first.get("scene_number", scene_id[1:]),
                "scene_id": scene_id,
                "meta": {
                    "scene_goal": first.get("scene_goal", ""),
                    "key_image": first.get("scene_key_image", ""),
                    "end_hook": first.get("scene_end_hook", ""),
                    "characters_present": first.get("characters_present", ""),
                },
                "shots": [assembled_shot(shot) for shot in scene_shots],
            }
        )
    return result


def shot_markdown_block(shot: dict[str, Any]) -> list[str]:
    refs = ", ".join(f"`{item}`" for item in shot.get("reference_needs", [])) or "none"
    panel_text = shot.get("panelText", "") or "none"
    sfx_text = shot.get("sfxText", "") or "none"
    return [
        f"#### `{shot['shot_id']}`",
        "",
        f"- shot goal: {shot.get('shot_goal', '')}",
        f"- visual focus: {shot.get('visual_focus', '')}",
        f"- workflow: `{shot.get('prompt_workflow', '')}`",
        f"- refs: {refs}",
        f"- panel text: `{shot.get('panelTextType', 'none')}` | {panel_text}",
        f"- sfx: {sfx_text}",
        "- image prompt:",
        f"  - {shot.get('image_prompt', '')}",
        "",
    ]


def build_storyboard_markdown(data: dict[str, Any]) -> str:
    lines = [
        f"# {data['story_title']} Storyboard",
        "",
        "## Storyboard Summary",
        "",
        f"- story title: {data['story_title']}",
        f"- episode: {data.get('episode', '')}",
        f"- total scenes: {data['summary'].get('total_scenes', 0)}",
        f"- total panels: {data['summary'].get('total_panels', 0)}",
        f"- first 3-second hook: `{data['summary'].get('first_3_second_hook', '')}`",
        f"- strongest proof panel: `{data['summary'].get('strongest_proof_panel', '')}`",
        f"- final cliffhanger panel: `{data['summary'].get('final_cliffhanger_panel', '')}`",
        "",
        "## Panel Dialogue Notes",
        "",
    ]
    for label, values in data.get("panel_dialogue_notes", {}).items():
        rendered = ", ".join(f"`{value}`" for value in values) if values else "none"
        lines.append(f"- {label}: {rendered}")
    lines.extend(["", "## Scene-by-Scene Shot List", ""])
    for scene in data.get("scenes", []):
        lines.extend(
            [
                f"### Scene {scene['scene_number']}",
                "",
                f"- scene goal: {scene['meta'].get('scene_goal', '')}",
                f"- key image: {scene['meta'].get('key_image', '')}",
                f"- end hook: {scene['meta'].get('end_hook', '')}",
                "",
            ]
        )
        for shot in scene.get("shots", []):
            lines.extend(shot_markdown_block(shot))
    return "\n".join(lines).strip() + "\n"


def choose_first_hook_panel(flat_shots: list[dict[str, Any]]) -> str:
    if not flat_shots:
        return ""
    strong_markers = ("proof", "可疑", "證據", "怪照片", "黑屏手機", "手機螢幕")
    for shot in flat_shots:
        haystacks = [
            str(shot.get("shot_goal", "")),
            str(shot.get("visual_focus", "")),
            str(shot.get("image_prompt", "")),
        ]
        if any(marker in text for text in haystacks for marker in strong_markers):
            return str(shot.get("shot_id", ""))
    return str(flat_shots[0].get("shot_id", ""))


def assemble_storyboard(scene_pack: dict[str, Any], shots: list[dict[str, Any]]) -> dict[str, Any]:
    ready_shots = [shot for shot in shots if shot.get("status") in {"prompt_generated", "reviewed", "approved", "assembled"}]
    scenes = scene_groups(ready_shots)
    flat_shots = [shot for scene in scenes for shot in scene["shots"]]
    return {
        "story_title": scene_pack.get("story_title", ""),
        "episode": scene_pack.get("episode", ""),
        "format": "image-first comic storyboard",
        "language": "Traditional Chinese",
        "summary": {
            "total_scenes": len(scenes),
            "total_panels": len(flat_shots),
            "first_3_second_hook": choose_first_hook_panel(flat_shots),
            "strongest_proof_panel": next((shot["shot_id"] for shot in flat_shots if "proof" in shot.get("shot_goal", "").lower()), ""),
            "final_cliffhanger_panel": flat_shots[-1]["shot_id"] if flat_shots else "",
        },
        "panel_dialogue_notes": compute_dialogue_summary(ready_shots),
        "negative_prompt_handoff": scene_pack.get("negative_prompt_handoff", []),
        "scenes": scenes,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assemble workspace shots into storyboard.json and storyboard.md.")
    parser.add_argument("--project-dir", default="")
    parser.add_argument("--workspace-dir", default="")
    parser.add_argument("--output-json", default="")
    parser.add_argument("--output-md", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir) if args.project_dir else Path.cwd()
    ensure_project_output_dirs(project_dir)
    workspace_dir = Path(args.workspace_dir) if args.workspace_dir else default_workspace_dir(project_dir)
    output_json = Path(args.output_json) if args.output_json else default_storyboard_json(project_dir)
    output_md = Path(args.output_md) if args.output_md else default_storyboard_md(project_dir)
    ensure_workspace_dirs(workspace_dir)
    scene_pack = load_json(workspace_dir / "scene_pack.json")
    shots = collect_shots(workspace_dir)
    assembled = assemble_storyboard(scene_pack, shots)
    save_json(output_json, assembled)
    save_text(output_md, build_storyboard_markdown(assembled))
    for shot_path in (workspace_dir / "shots").glob("*.json"):
        shot = load_json(shot_path)
        if shot.get("status") in {"prompt_generated", "reviewed", "approved"}:
            shot["status"] = "assembled"
            save_json(shot_path, shot)
    print(f"[done] assembled storyboard -> {output_json}")
    print(f"[done] assembled markdown -> {output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
