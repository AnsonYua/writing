import argparse
import json
import re
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent

DEFAULT_STORYBOARD_PATH = PROJECT_DIR / "storyboard.md"
DEFAULT_GENERATED_DIR = PROJECT_DIR / "generated"
DEFAULT_JSON_PATH = PROJECT_DIR / "storyboard.json"
DEFAULT_CHECKLIST_PATH = PROJECT_DIR / "storyboard-checklist.md"


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def save_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8-sig")


def parse_bullet_value(line: str) -> tuple[str, str] | None:
    match = re.match(r"^\s*-\s+([^:]+):\s*(.*)$", line)
    if not match:
        return None
    return match.group(1).strip(), match.group(2).strip()


def normalize_key(label: str) -> str:
    normalized = label.lower().replace(" ", "_").replace("-", "_")
    aliases = {
        "production_type": "production_type",
        "reference_character": "reference_character",
        "must_show_detail": "must_show_detail",
        "continuity_in": "continuity_in",
        "continuity_out": "continuity_out",
        "startimageprompt": "start_image_prompt",
        "videoprompt": "video_prompt",
        "finalprompt": "video_prompt",
    }
    return aliases.get(normalized, normalized)


def parse_storyboard(text: str) -> dict:
    lines = text.splitlines()
    title = ""
    summary = {}
    scenes = []
    notes = {}

    current_scene = None
    current_shot = None
    current_notes_section = None
    in_summary = False
    in_shot_list = False
    in_notes = False

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped.startswith("# "):
            title = stripped[2:].strip()
            continue

        if stripped == "## Storyboard Summary":
            in_summary = True
            in_shot_list = False
            in_notes = False
            current_scene = None
            current_shot = None
            current_notes_section = None
            continue

        if stripped == "## Scene-by-Scene Shot List":
            in_summary = False
            in_shot_list = True
            in_notes = False
            current_scene = None
            current_shot = None
            current_notes_section = None
            continue

        if stripped.startswith("## ") and stripped not in {
            "## Storyboard Summary",
            "## Scene-by-Scene Shot List",
        }:
            in_summary = False
            in_shot_list = False
            in_notes = True
            current_scene = None
            current_shot = None
            current_notes_section = stripped[3:].strip()
            notes[current_notes_section] = []
            continue

        if in_summary:
            item = parse_bullet_value(line)
            if item:
                summary[normalize_key(item[0])] = item[1]
            continue

        if in_shot_list and stripped.startswith("#### Scene "):
            scene_number = stripped.replace("#### Scene ", "").strip()
            current_scene = {
                "scene_number": scene_number,
                "scene_id": f"S{scene_number}",
                "meta": {},
                "shots": [],
            }
            scenes.append(current_scene)
            current_shot = None
            continue

        if in_shot_list and stripped.startswith("- shot "):
            if current_scene is None:
                continue
            shot_number = stripped.replace("- shot ", "").strip()
            current_shot = {
                "shot_number": shot_number,
                "shot_id": f"{current_scene['scene_id']}_SH{shot_number}",
            }
            current_scene["shots"].append(current_shot)
            continue

        item = parse_bullet_value(line)
        if not item:
            continue

        key, value = item
        normalized_key = normalize_key(key)

        if in_shot_list and current_shot is not None:
            current_shot[normalized_key] = value
            continue

        if in_shot_list and current_scene is not None:
            current_scene["meta"][normalized_key] = value
            continue

        if in_notes and current_notes_section is not None:
            notes[current_notes_section].append({"label": key, "value": value})

    total_shots = sum(len(scene["shots"]) for scene in scenes)
    summary_total_shots = summary.get("total_shots")
    summary_total_shots_int = None
    if summary_total_shots and summary_total_shots.isdigit():
        summary_total_shots_int = int(summary_total_shots)
    return {
        "title": title,
        "summary": summary,
        "scene_count": len(scenes),
        "shot_count": total_shots,
        "summary_total_shots": summary_total_shots_int,
        "summary_shot_count_matches": summary_total_shots_int == total_shots if summary_total_shots_int is not None else None,
        "scenes": scenes,
        "notes": notes,
    }


def build_expected_image_name(scene_id: str, shot_number: str) -> str:
    return f"ep1_s{scene_id[1:]}_sh{shot_number}"


def find_matching_image(generated_dir: Path, scene_id: str, shot_number: str) -> str | None:
    prefix = build_expected_image_name(scene_id, shot_number)
    for path in sorted(generated_dir.glob(f"{prefix}*.png")):
        return path.name
    return None


def build_checklist(data: dict, generated_dir: Path) -> str:
    lines = []
    title = data["title"]
    if title.endswith(" Storyboard"):
        title = title[: -len(" Storyboard")]
    lines.append(f"# {title} Storyboard Checklist")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- total scenes: {data['scene_count']}")
    lines.append(f"- total shots: {data['shot_count']}")
    if data.get("summary_total_shots") is not None:
        lines.append(f"- storyboard summary says total shots: {data['summary_total_shots']}")
        lines.append(f"- summary matches parsed shot count: {data['summary_shot_count_matches']}")
    lines.append(f"- generated image folder: {generated_dir}")
    lines.append("")
    lines.append("## Shot Coverage")
    lines.append("")

    for scene in data["scenes"]:
        lines.append(f"### {scene['scene_id']}")
        lines.append("")
        scene_goal = scene["meta"].get("scene_goal", "")
        key_image = scene["meta"].get("key_image", "")
        end_hook = scene["meta"].get("end_hook", "")
        if scene_goal:
            lines.append(f"- scene goal: {scene_goal}")
        if key_image:
            lines.append(f"- key image: {key_image}")
        if end_hook:
            lines.append(f"- end hook: {end_hook}")
        lines.append("")

        for shot in scene["shots"]:
            image_name = find_matching_image(generated_dir, scene["scene_id"], shot["shot_number"])
            status = "OK" if image_name else "MISSING"
            duration = shot.get("duration", "")
            framing = shot.get("framing", "")
            camera = shot.get("camera", "")
            production_type = shot.get("production_type", "")
            reference_character = shot.get("reference_character", "")
            subject = shot.get("subject", "")
            action = shot.get("action", "")
            must_show_detail = shot.get("must_show_detail", "")
            continuity_in = shot.get("continuity_in", "")
            continuity_out = shot.get("continuity_out", "")
            purpose = shot.get("purpose", "")
            start_image_prompt = shot.get("start_image_prompt", "") or shot.get("startimageprompt", "")
            video_prompt = (
                shot.get("video_prompt", "")
                or shot.get("videoprompt", "")
                or shot.get("final_prompt", "")
                or shot.get("finalprompt", "")
            )

            lines.append(f"- [{status}] {shot['shot_id']}")
            if duration:
                lines.append(f"  duration: {duration}")
            if framing:
                lines.append(f"  framing: {framing}")
            if camera:
                lines.append(f"  camera: {camera}")
            if production_type:
                lines.append(f"  production type: {production_type}")
            if reference_character:
                lines.append(f"  reference character: {reference_character}")
            if subject:
                lines.append(f"  subject: {subject}")
            if action:
                lines.append(f"  action: {action}")
            if must_show_detail:
                lines.append(f"  must-show detail: {must_show_detail}")
            if continuity_in:
                lines.append(f"  continuity-in: {continuity_in}")
            if continuity_out:
                lines.append(f"  continuity-out: {continuity_out}")
            if purpose:
                lines.append(f"  purpose: {purpose}")
            if start_image_prompt:
                lines.append(f"  startImagePrompt: {start_image_prompt}")
            if video_prompt:
                lines.append(f"  videoPrompt: {video_prompt}")
            lines.append(f"  image: {image_name or 'not generated yet'}")
            lines.append("")

    missing = 0
    present = 0
    for scene in data["scenes"]:
        for shot in scene["shots"]:
            if find_matching_image(generated_dir, scene["scene_id"], shot["shot_number"]):
                present += 1
            else:
                missing += 1

    lines.append("## Coverage Totals")
    lines.append("")
    lines.append(f"- matched shots: {present}")
    lines.append(f"- missing shots: {missing}")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build structured storyboard outputs and shot coverage checklist from storyboard.md."
    )
    parser.add_argument("--storyboard", default=str(DEFAULT_STORYBOARD_PATH))
    parser.add_argument("--generated-dir", default=str(DEFAULT_GENERATED_DIR))
    parser.add_argument("--json-out", default=str(DEFAULT_JSON_PATH))
    parser.add_argument("--checklist-out", default=str(DEFAULT_CHECKLIST_PATH))
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    storyboard_path = Path(args.storyboard)
    generated_dir = Path(args.generated_dir)
    json_out = Path(args.json_out)
    checklist_out = Path(args.checklist_out)

    if not storyboard_path.exists():
        raise FileNotFoundError(f"Storyboard not found: {storyboard_path}")
    if not generated_dir.exists():
        generated_dir.mkdir(parents=True, exist_ok=True)

    data = parse_storyboard(load_text(storyboard_path))
    for scene in data["scenes"]:
        for shot in scene["shots"]:
            image_name = find_matching_image(generated_dir, scene["scene_id"], shot["shot_number"])
            shot["image_status"] = "OK" if image_name else "MISSING"
            shot["image_name"] = image_name
    save_text(json_out, json.dumps(data, ensure_ascii=False, indent=2))
    save_text(checklist_out, build_checklist(data, generated_dir))

    print(f"Saved JSON to {json_out}")
    print(f"Saved checklist to {checklist_out}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        raise SystemExit(130)
