from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_PROJECT_DIR = Path.cwd()


def project_output_dir(project_dir: Path) -> Path:
    return project_dir / "output"


def default_scene_pack_md(project_dir: Path) -> Path:
    return project_dir / "scene-pack.md"


def default_character_pack_md(project_dir: Path) -> Path:
    return project_dir / "角色包.md"


def default_workspace_dir(project_dir: Path) -> Path:
    return project_output_dir(project_dir) / "storyboard-workspace"


def default_storyboard_json(project_dir: Path) -> Path:
    return project_output_dir(project_dir) / "storyboard.json"


def default_storyboard_md(project_dir: Path) -> Path:
    return project_output_dir(project_dir) / "storyboard.md"


def default_logs_dir(project_dir: Path) -> Path:
    return project_output_dir(project_dir) / "logs"


def default_debug_dir(project_dir: Path) -> Path:
    return project_output_dir(project_dir) / "debug"


def default_generated_dir(project_dir: Path) -> Path:
    return project_output_dir(project_dir) / "generated"


def default_generated_videos_dir(project_dir: Path) -> Path:
    return default_generated_dir(project_dir) / "videos"


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def save_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8-sig")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def ensure_project_output_dirs(project_dir: Path) -> dict[str, Path]:
    dirs = {
        "project_output": project_output_dir(project_dir),
        "logs": default_logs_dir(project_dir),
        "debug": default_debug_dir(project_dir),
        "generated": default_generated_dir(project_dir),
        "videos": default_generated_videos_dir(project_dir),
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs


def ensure_workspace_dirs(workspace_dir: Path) -> dict[str, Path]:
    dirs = {
        "root": workspace_dir,
        "shots": workspace_dir / "shots",
        "log": workspace_dir / "log",
        "requests": workspace_dir / "log" / "requests",
        "responses": workspace_dir / "log" / "responses",
        "reviews": workspace_dir / "log" / "reviews",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs


def normalize_key(label: str) -> str:
    cleaned = label.strip().lower()
    cleaned = cleaned.replace("/", "_")
    cleaned = cleaned.replace(" ", "_").replace("-", "_")
    cleaned = re.sub(r"[^a-z0-9_\u4e00-\u9fff]+", "", cleaned)
    return cleaned


def bullet_indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def parse_bullet_value(line: str) -> tuple[str, str] | None:
    match = re.match(r"^\s*-\s+([^:]+):\s*(.*)$", line)
    if not match:
        return None
    return match.group(1).strip(), match.group(2).strip()


def parse_plain_bullets(lines: list[str]) -> list[str]:
    items: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return items


def parse_key_value_block(lines: list[str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        item = parse_bullet_value(line)
        if not item:
            index += 1
            continue
        key, value = item
        normalized = normalize_key(key)
        current_indent = bullet_indent(line)
        if value:
            result[normalized] = value
            index += 1
            continue

        index += 1
        nested: list[str] = []
        while index < len(lines):
            nested_line = lines[index]
            if not nested_line.strip():
                index += 1
                continue
            if bullet_indent(nested_line) <= current_indent:
                break
            stripped = nested_line.strip()
            if stripped.startswith("- "):
                nested.append(stripped[2:].strip())
            index += 1
        result[normalized] = nested
    return result


def split_sections(lines: list[str]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current_title = ""
    current_lines: list[str] = []
    for line in lines:
        if line.startswith("## "):
            if current_title:
                sections[current_title] = current_lines
            current_title = line[3:].strip()
            current_lines = []
            continue
        if current_title:
            current_lines.append(line)
    if current_title:
        sections[current_title] = current_lines
    return sections


def split_h3_blocks(lines: list[str]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current_title = ""
    current_lines: list[str] = []
    for line in lines:
        if line.startswith("### "):
            if current_title:
                sections[current_title] = current_lines
            current_title = line[4:].strip()
            current_lines = []
            continue
        if current_title:
            current_lines.append(line)
    if current_title:
        sections[current_title] = current_lines
    return sections


def split_characters(raw: str) -> list[str]:
    parts = re.split(r"[、,，/／\s]+", raw)
    return [part.strip() for part in parts if part.strip()]


def parse_scene_cards(lines: list[str]) -> list[dict[str, Any]]:
    scenes: list[dict[str, Any]] = []
    blocks = split_h3_blocks(lines)
    for title, block_lines in blocks.items():
        scene_match = re.search(r"(\d+)", title)
        scene_number = scene_match.group(1) if scene_match else title
        data = parse_key_value_block(block_lines)
        scene = {
            "scene_number": scene_number,
            "scene_id": f"S{scene_number}",
            "location": data.get("location", ""),
            "time_feel": data.get("time_feel", ""),
            "characters_present": data.get("characters_present", ""),
            "characters_present_list": split_characters(str(data.get("characters_present", ""))),
            "scene_purpose": data.get("scene_purpose", ""),
            "visible_action": data.get("visible_action", []),
            "core_conflict": data.get("core_conflict", ""),
            "emotional_turn": data.get("emotional_turn", ""),
            "key_image": data.get("key_image", ""),
            "end_hook": data.get("end_hook", ""),
            "continuity_notes": data.get("continuity_notes", []),
        }
        scenes.append(scene)
    return sorted(scenes, key=lambda item: int(str(item["scene_number"])))


def parse_scene_pack_markdown(text: str, source_path: Path | None = None) -> dict[str, Any]:
    lines = text.splitlines()
    title = ""
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break
    sections = split_sections(lines)
    summary = parse_key_value_block(sections.get("Scene Pack Summary", []))
    continuity_blocks = {
        name: parse_plain_bullets(block_lines)
        for name, block_lines in split_h3_blocks(sections.get("Continuity Notes", [])).items()
    }
    downstream_blocks = {
        name: parse_plain_bullets(block_lines)
        for name, block_lines in split_h3_blocks(sections.get("Downstream Handoff Notes", [])).items()
    }
    end_state = parse_key_value_block(sections.get("Episode End State Snapshot", []))
    return {
        "workspace_version": "1",
        "story_title": summary.get("story_title", title.replace("Scene Pack", "").strip()).strip(),
        "source_scene_pack": str(source_path) if source_path else "",
        "episode": summary.get("episode_coverage", ""),
        "summary": summary,
        "episode_scene_table": parse_plain_bullets(sections.get("Episode Scene Table", [])),
        "scenes": parse_scene_cards(sections.get("Detailed Scene Cards", [])),
        "continuity_notes": continuity_blocks,
        "episode_end_state_snapshot": end_state,
        "negative_prompt_handoff": parse_plain_bullets(sections.get("Negative Prompt Handoff", [])),
        "downstream_handoff_notes": downstream_blocks,
    }


def parse_character_pack_markdown(text: str, source_path: Path | None = None) -> dict[str, Any]:
    lines = text.splitlines()
    title = ""
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break
    sections = split_sections(lines)
    cards: list[dict[str, Any]] = []
    for card_title, block_lines in split_h3_blocks(sections.get("Character Cards", [])).items():
        data = parse_key_value_block(block_lines)
        cards.append(
            {
                "name": card_title.strip(),
                "role_in_story": data.get("role_in_story", ""),
                "age_or_age_band": data.get("age_or_age_band", ""),
                "story_function": data.get("story_function", ""),
                "core_appearance": data.get("core_appearance", []),
                "clothing_system": data.get("clothing_system", []),
                "visual_anchors": data.get("visual_anchors", []),
                "behavior_and_emotional_habits": data.get("behavior_and_emotional_habits", []),
                "continuity_locks": data.get("continuity_locks", []),
                "quick_prompt_version": data.get("quick_prompt_version", []),
            }
        )
    return {
        "title": title,
        "source_character_pack": str(source_path) if source_path else "",
        "cards": cards,
    }


def scene_sort_key(scene: dict[str, Any]) -> tuple[int, str]:
    return int(str(scene.get("scene_number", "0"))), str(scene.get("scene_id", ""))


def shot_sort_key(shot: dict[str, Any]) -> tuple[int, int, str]:
    return (
        int(str(shot.get("scene_number", "0"))),
        int(str(shot.get("shot_number", "0"))),
        str(shot.get("shot_id", "")),
    )


def build_scene_workspace_path(workspace_dir: Path, scene_id: str) -> Path:
    return workspace_dir / f"scene_{scene_id}_shots.json"


def build_shot_workspace_path(workspace_dir: Path, shot_id: str) -> Path:
    return workspace_dir / "shots" / f"{shot_id}.json"


def summarize_shot_for_context(shot: dict[str, Any]) -> dict[str, Any]:
    return {
        "shot_id": shot.get("shot_id", ""),
        "shot_goal": shot.get("shot_goal", ""),
        "visual_focus": shot.get("visual_focus", ""),
        "shot_description": shot.get("shot_description", ""),
        "support_character_mode": shot.get("support_character_mode", "none"),
        "image_prompt": (shot.get("prompt_output") or {}).get("image_prompt", ""),
        "panelTextType": (shot.get("prompt_output") or {}).get("panelTextType", "none"),
    }


def build_scene_context_summary(scene_json: dict[str, Any]) -> dict[str, Any]:
    return {
        "scene_goal": scene_json.get("scene_goal", ""),
        "scene_key_image": scene_json.get("scene_key_image", ""),
        "scene_end_hook": scene_json.get("scene_end_hook", ""),
        "characters_present": scene_json.get("characters_present", ""),
        "location": scene_json.get("location", ""),
        "time_feel": scene_json.get("time_feel", ""),
    }


def build_previous_shot_summary(prev_shot_json: dict[str, Any] | None) -> dict[str, Any] | None:
    if not prev_shot_json:
        return None
    shot_id = str(prev_shot_json.get("shot_id", ""))
    visual_focus = str(prev_shot_json.get("visual_focus", "")).strip()
    image_prompt = str((prev_shot_json.get("prompt_output") or {}).get("image_prompt", "")).strip()
    shot_description = str(prev_shot_json.get("shot_description", "")).strip()
    support_mode = str(prev_shot_json.get("support_character_mode", "none")).strip()
    summary_parts = [part for part in [visual_focus, shot_description or image_prompt] if part]
    return {
        "shot_id": shot_id,
        "summary": "；".join(summary_parts[:2]),
        "support_character_mode": support_mode,
    }


def _first_items(values: Any, *, limit: int = 2) -> list[str]:
    if isinstance(values, list):
        return [str(item).strip() for item in values if str(item).strip()][:limit]
    if values:
        return [str(values).strip()]
    return []


def load_character_pack(project_dir: Path) -> dict[str, Any]:
    path = default_character_pack_md(project_dir)
    if not path.exists():
        return {"title": "", "source_character_pack": "", "cards": []}
    return parse_character_pack_markdown(load_text(path), path)


def find_character_card(character_pack: dict[str, Any], name: str) -> dict[str, Any] | None:
    target = name.strip()
    if not target:
        return None
    for card in character_pack.get("cards", []):
        card_name = str(card.get("name", "")).strip()
        if target == card_name:
            return card
    for card in character_pack.get("cards", []):
        card_name = str(card.get("name", "")).strip()
        if card_name and (card_name in target or target in card_name):
            return card
    return None


def infer_shot_characters(shot: dict[str, Any], scene_context: dict[str, Any], character_pack: dict[str, Any]) -> list[str]:
    haystack = " ".join(
        str(value)
        for value in [
            shot.get("visual_focus", ""),
            shot.get("shot_description", ""),
            scene_context.get("characters_present", ""),
        ]
    )
    matches: list[str] = []
    for card in character_pack.get("cards", []):
        name = str(card.get("name", "")).strip()
        if name and name in haystack:
            matches.append(name)
    return matches


def build_reference_context(
    project_dir: Path,
    shot: dict[str, Any],
    scene_context: dict[str, Any],
    previous_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    character_pack = load_character_pack(project_dir)
    matched = infer_shot_characters(shot, scene_context, character_pack)
    main_card = find_character_card(character_pack, matched[0]) if matched else None
    second_card = find_character_card(character_pack, matched[1]) if len(matched) > 1 else None

    scene_preserve = _first_items(scene_context.get("continuity_notes", []), limit=2)
    if scene_context.get("location"):
        scene_preserve.insert(0, f"同一場景位置：{scene_context.get('location')}")
    if scene_context.get("time_feel"):
        scene_preserve.append(f"時間與氣氛：{scene_context.get('time_feel')}")

    def character_context(card: dict[str, Any] | None) -> dict[str, Any]:
        if not card:
            return {}
        return {
            "name": card.get("name", ""),
            "appearance_cues": _first_items(card.get("core_appearance", []), limit=2),
            "clothing_cues": _first_items(card.get("clothing_system", []), limit=2),
            "visual_anchors": _first_items(card.get("visual_anchors", []), limit=2),
            "continuity_locks": _first_items(card.get("continuity_locks", []), limit=2),
            "quick_prompt_version": "；".join(_first_items(card.get("quick_prompt_version", []), limit=1)),
        }

    prop_preserve = ""
    if "prop_ref" in shot.get("reference_needs", []):
        prop_preserve = "同一道具的身份、屏幕狀態、手持方向與誰在拿都要保持連續。"

    return {
        "scene_reference_context": {
            "preserve": scene_preserve,
            "scene_goal": scene_context.get("scene_goal", ""),
            "scene_key_image": scene_context.get("scene_key_image", ""),
        },
        "character_reference_context": character_context(main_card),
        "second_character_reference_context": character_context(second_card),
        "prop_reference_context": {
            "preserve": prop_preserve,
            "must_show_details": _first_items(shot.get("must_show", []), limit=3),
        },
        "previous_shot_carry": previous_summary or {},
    }


def build_workflow_reference_plan(
    shot: dict[str, Any],
    previous_summary: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    plan: list[dict[str, str]] = []
    if "scene_ref" in shot.get("reference_needs", []):
        plan.append(
            {
                "reference_type": "scene_ref",
                "preserve_role": "semantic_frame",
                "preserve_target": "空間方向、房門與家具位置、光線與同一場景壓力",
            }
        )
    if "character_ref" in shot.get("reference_needs", []):
        plan.append(
            {
                "reference_type": "character_ref",
                "preserve_role": "appearance",
                "preserve_target": "主角色臉型、髮型、年齡感、體態與辨識度",
            }
        )
    if "second_character_ref" in shot.get("reference_needs", []):
        plan.append(
            {
                "reference_type": "second_character_ref",
                "preserve_role": "appearance",
                "preserve_target": "支援角色的可讀身份、穿著輪廓與入鏡辨識 cue",
            }
        )
    if "prop_ref" in shot.get("reference_needs", []):
        plan.append(
            {
                "reference_type": "prop_ref",
                "preserve_role": "prop_continuity",
                "preserve_target": "同一道具身份、屏幕狀態、手持關係與使用邏輯",
            }
        )
    if previous_summary and previous_summary.get("summary"):
        plan.append(
            {
                "reference_type": "previous_shot_summary",
                "preserve_role": "carry_over",
                "preserve_target": "上一格連續性只作輔助，不可壓過本格主畫面",
            }
        )
    return plan


def project_shot_to_prompt_input(
    shot: dict[str, Any],
    scene_context: dict[str, Any],
    previous_summary: dict[str, Any] | None,
    reference_context: dict[str, Any] | None = None,
    workflow_reference_plan: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    prompt_shot = {
        "scene_id": shot.get("scene_id", ""),
        "scene_number": shot.get("scene_number", ""),
        "shot_id": shot.get("shot_id", ""),
        "shot_number": shot.get("shot_number", ""),
        "shot_goal": shot.get("shot_goal", ""),
        "visual_focus": shot.get("visual_focus", ""),
        "shot_description": shot.get("shot_description", ""),
        "must_show": shot.get("must_show", []),
        "reference_needs": shot.get("reference_needs", []),
        "prompt_workflow": shot.get("prompt_workflow", "single_edit"),
        "support_character_mode": shot.get("support_character_mode", "none"),
    }
    return {
        "shot": prompt_shot,
        "scene_context_summary": build_scene_context_summary(scene_context),
        "previous_shot_summary": previous_summary,
        "reference_context": reference_context or {},
        "workflow_reference_plan": workflow_reference_plan or [],
    }


def normalize_prompt_output(response: dict[str, Any]) -> dict[str, Any]:
    panel_text_type = str(response.get("panelTextType", "none") or "none")
    panel_text = str(response.get("panelText", "") or "")
    sfx_text = str(response.get("sfxText", "") or "")
    return {
        "image_prompt": str(response.get("image_prompt", "") or ""),
        "panelTextType": panel_text_type,
        "panelText": panel_text,
        "sfxText": sfx_text,
    }


def invoke_command_adapter(
    command_template: str,
    request_payload: dict[str, Any],
    request_path: Path,
    response_path: Path,
) -> dict[str, Any]:
    save_json(request_path, request_payload)
    command = command_template.format(
        request=str(request_path),
        response=str(response_path),
        item_id=str(request_payload.get("item_id", "")),
        mode=str(request_payload.get("mode", "")),
    )
    subprocess.run(command, shell=True, check=True)
    if not response_path.exists():
        raise FileNotFoundError(f"Adapter did not create response file: {response_path}")
    return load_json(response_path)


def compute_dialogue_summary(shots: list[dict[str, Any]]) -> dict[str, list[str]]:
    summary = {
        "spoken_panels": [],
        "thought_panels": [],
        "caption_panels": [],
        "sfx_panels": [],
        "silent_panels": [],
    }
    mapping = {
        "dialogue": "spoken_panels",
        "spoken": "spoken_panels",
        "inner_thought": "thought_panels",
        "thought": "thought_panels",
        "caption": "caption_panels",
        "sfx": "sfx_panels",
        "none": "silent_panels",
    }
    for shot in shots:
        prompt_output = shot.get("prompt_output") or {}
        bucket = mapping.get(str(prompt_output.get("panelTextType", "none")), "silent_panels")
        summary[bucket].append(str(shot.get("shot_id", "")))
    return summary
