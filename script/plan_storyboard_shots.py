from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from storyboard_workspace import (
    build_scene_workspace_path,
    build_shot_workspace_path,
    default_scene_pack_md,
    default_workspace_dir,
    ensure_project_output_dirs,
    ensure_workspace_dirs,
    invoke_command_adapter,
    load_text,
    parse_scene_pack_markdown,
    save_json,
    scene_sort_key,
)


DEFAULT_SKILL_NAME = "short-drama-shot-planner"


def scene_context(scene: dict[str, Any]) -> dict[str, Any]:
    return {
        "scene_number": scene["scene_number"],
        "scene_id": scene["scene_id"],
        "scene_goal": scene.get("scene_purpose", ""),
        "scene_key_image": scene.get("key_image", ""),
        "scene_end_hook": scene.get("end_hook", ""),
        "characters_present": scene.get("characters_present", ""),
    }


def build_shot(
    scene: dict[str, Any],
    *,
    shot_number: int,
    shot_goal: str,
    visual_focus: str,
    shot_description: str,
    must_show: list[str],
    reference_needs: list[str],
    prompt_workflow: str,
    support_character_mode: str,
    shot_decision_note: str = "",
    merge_or_delete_risk: str = "",
) -> dict[str, Any]:
    return {
        **scene_context(scene),
        "shot_number": str(shot_number),
        "shot_id": f"{scene['scene_id']}_SH{shot_number}",
        "shot_goal": shot_goal,
        "visual_focus": visual_focus,
        "shot_description": shot_description,
        "must_show": must_show,
        "reference_needs": reference_needs,
        "prompt_workflow": prompt_workflow,
        "support_character_mode": support_character_mode,
        "shot_decision_note": shot_decision_note,
        "merge_or_delete_risk": merge_or_delete_risk,
        "status": "planned",
    }


def generic_plan_scene(scene: dict[str, Any]) -> list[dict[str, Any]]:
    actions = list(scene.get("visible_action", []))
    if not actions:
        return []
    shots: list[dict[str, Any]] = []
    limit = min(4, len(actions))
    for index, action in enumerate(actions[:limit], start=1):
        focus = action[:24]
        shots.append(
            build_shot(
                scene,
                shot_number=index,
                shot_goal=action,
                visual_focus=focus,
                shot_description=action,
                must_show=[scene.get("key_image", "") or action],
                reference_needs=["scene_ref", "character_ref"],
                prompt_workflow="single_edit",
                support_character_mode="none",
                shot_decision_note="fallback heuristic shot",
            )
        )
    return shots


def plan_scene_1(scene: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        build_shot(
            scene,
            shot_number=1,
            shot_goal="先交代手機 handoff，建立危險從正常晚飯後生活裡冒出來。",
            visual_focus="舅父遞手機給曉晴",
            shot_description="晚飯後客廳餐桌邊中景，陳國強把快沒電的黑色手機遞向周曉晴，曉晴站在桌邊伸手接過，白色充電線已在另一隻手裡。",
            must_show=["同一部黑色手機", "白色充電線", "晚飯後餐桌", "舅父只是自然交手機"],
            reference_needs=["scene_ref", "character_ref", "second_character_ref", "prop_ref"],
            prompt_workflow="multi_edit",
            support_character_mode="readable_actor",
            shot_decision_note="先種下 prop handoff，再讓 proof 成立。",
        ),
        build_shot(
            scene,
            shot_number=2,
            shot_goal="交出第一個可疑 proof。",
            visual_focus="手機螢幕上的古怪照片",
            shot_description="手機插入特寫，剛亮起的黑色手機螢幕上跳出一張明顯來自家中空間的古怪照片，照片角度帶出偷拍感。",
            must_show=["手機螢幕可讀", "照片像同一個家", "偷拍感", "同一部手機"],
            reference_needs=["prop_ref", "scene_ref"],
            prompt_workflow="single_edit",
            support_character_mode="none",
            shot_decision_note="proof panel 只做 proof，不混 reaction。",
        ),
        build_shot(
            scene,
            shot_number=3,
            shot_goal="交出曉晴第一次被擊中的身體反應。",
            visual_focus="曉晴拿著手機僵住",
            shot_description="客廳餐桌邊中景，周曉晴右手握著剛亮起的手機，左手白色充電線還停在插口前，整個接線動作突然停住。",
            must_show=["曉晴是主體", "手機仍在手上", "充電線未插上", "晚飯後客廳延續"],
            reference_needs=["scene_ref", "character_ref", "prop_ref"],
            prompt_workflow="multi_edit",
            support_character_mode="pressure_presence",
            shot_decision_note="proof 後立即落身體反應，不重複 proof。",
        ),
        build_shot(
            scene,
            shot_number=4,
            shot_goal="把 proof 升級成不是單一巧合。",
            visual_focus="手機裡更多可疑內容",
            shot_description="手機近距離特寫，畫面不再只是一張照片，而是能看出有更多同類偷拍內容的入口或縮圖排列。",
            must_show=["同一部手機", "可疑內容不只一張", "仍然是家中空間線索"],
            reference_needs=["prop_ref", "scene_ref"],
            prompt_workflow="single_edit",
            support_character_mode="none",
            shot_decision_note="升級 proof，但仍留一手給下一場。",
        ),
    ]


def plan_scene_2(scene: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        build_shot(
            scene,
            shot_number=1,
            shot_goal="把求助動作建立清楚，翻入母女空間。",
            visual_focus="曉晴把李美珍拉進房",
            shot_description="李美珍臥室門口中景，周曉晴一手抓住母親往房裡帶，另一手還拿著同一部黑色手機，動作急但不誇張。",
            must_show=["同一部手機", "母女進入臥室", "求助動作直接", "空間已離開客廳"],
            reference_needs=["scene_ref", "character_ref", "second_character_ref", "prop_ref"],
            prompt_workflow="multi_edit",
            support_character_mode="readable_actor",
            shot_decision_note="先把求助動作交代清楚，再進入情緒戲。",
        ),
        build_shot(
            scene,
            shot_number=2,
            shot_goal="把證據直接塞到母親面前。",
            visual_focus="李美珍手上的手機",
            shot_description="臥室裡的中近景，李美珍被迫接過手機，螢幕上的可疑內容正對著她，周曉晴站在旁邊盯著她反應。",
            must_show=["母親已拿到手機", "證據對著母親", "母女同框但主體是手機與母親反應"],
            reference_needs=["scene_ref", "character_ref", "second_character_ref", "prop_ref"],
            prompt_workflow="multi_edit",
            support_character_mode="readable_actor",
            shot_decision_note="先讓證據落到母親手上，才有後面的沉默。",
        ),
        build_shot(
            scene,
            shot_number=3,
            shot_goal="交出母親看完後的恐懼與退縮。",
            visual_focus="李美珍發白的臉和握緊手機的手",
            shot_description="李美珍臥室中近景，李美珍盯著手機後臉色發白，手指緊緊扣住手機，周曉晴在一旁等她開口。",
            must_show=["母親恐懼", "手機仍在母親手上", "曉晴在旁等待", "不是大喊而是壓住"],
            reference_needs=["scene_ref", "character_ref", "second_character_ref", "prop_ref"],
            prompt_workflow="multi_edit",
            support_character_mode="readable_actor",
            shot_decision_note="情緒 payoff 落在母親退縮，而不是額外加新證據。",
        ),
        build_shot(
            scene,
            shot_number=4,
            shot_goal="場尾 hook 把屏幕裡的危險壓回門外現實。",
            visual_focus="黑屏手機和房門壓力",
            shot_description="李美珍臥室中景，李美珍本能把手機按黑握在手裡，母女一起看住房門方向，門外傳來自然平靜的要手機聲音。",
            must_show=["黑屏手機", "房門方向壓力", "母女不敢出聲", "危險回到現實空間"],
            reference_needs=["scene_ref", "character_ref", "second_character_ref", "prop_ref"],
            prompt_workflow="multi_edit",
            support_character_mode="readable_actor",
            shot_decision_note="以現實壓力收尾，不再另開新 confrontation。",
        ),
    ]


def heuristic_plan_scene(scene: dict[str, Any]) -> list[dict[str, Any]]:
    if scene.get("scene_id") == "S1":
        return plan_scene_1(scene)
    if scene.get("scene_id") == "S2":
        return plan_scene_2(scene)
    return generic_plan_scene(scene)


def merge_shot_defaults(scene: dict[str, Any], shot: dict[str, Any]) -> dict[str, Any]:
    merged = dict(shot)
    merged.setdefault("scene_number", scene["scene_number"])
    merged.setdefault("scene_id", scene["scene_id"])
    merged.setdefault("scene_goal", scene.get("scene_purpose", ""))
    merged.setdefault("scene_key_image", scene.get("key_image", ""))
    merged.setdefault("scene_end_hook", scene.get("end_hook", ""))
    merged.setdefault("characters_present", scene.get("characters_present", ""))
    merged.setdefault("must_show", [])
    merged.setdefault("reference_needs", [])
    merged.setdefault("prompt_workflow", "single_edit")
    merged.setdefault("support_character_mode", "none")
    merged.setdefault("shot_decision_note", "")
    merged.setdefault("merge_or_delete_risk", "")
    merged.setdefault("status", "planned")
    return merged


def build_adapter_prompt(scene: dict[str, Any]) -> str:
    return (
        f"Use skill `{DEFAULT_SKILL_NAME}`.\n"
        "Return JSON only for the current scene.\n"
        "Plan the minimum useful shot skeletons.\n"
        "Each shot must only contain these fields:\n"
        "- scene_id\n- scene_number\n- shot_id\n- shot_number\n- shot_goal\n- visual_focus\n- shot_description\n- must_show\n- reference_needs\n- prompt_workflow\n- support_character_mode\n- shot_decision_note optional\n- merge_or_delete_risk optional\n\n"
        "Do not write prompts.\n"
        "Do not write continuity_in or continuity_out.\n"
        "Do not change the storyline.\n\n"
        f"Current scene JSON:\n{scene}\n"
    )


def plan_scene(scene: dict[str, Any], executor: str, workspace_dir: Path, command_template: str) -> list[dict[str, Any]]:
    if executor == "heuristic":
        return heuristic_plan_scene(scene)
    workspace_paths = ensure_workspace_dirs(workspace_dir)
    request_path = workspace_paths["requests"] / f"{scene['scene_id']}_planner_request.json"
    response_path = workspace_paths["responses"] / f"{scene['scene_id']}_planner_response.json"
    request_payload = {
        "mode": "shot_planner",
        "item_id": scene["scene_id"],
        "skill": DEFAULT_SKILL_NAME,
        "scene": scene,
        "adapter_prompt": build_adapter_prompt(scene),
    }
    response = invoke_command_adapter(command_template, request_payload, request_path, response_path)
    shots = response.get("shots", [])
    if not isinstance(shots, list) or not shots:
        raise RuntimeError(f"Planner adapter returned no shots for {scene['scene_id']}")
    return [merge_shot_defaults(scene, shot) for shot in shots]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create lean storyboard shot skeletons directly from scene-pack markdown.")
    parser.add_argument("--project-dir", default="")
    parser.add_argument("--scene-pack-md", default="")
    parser.add_argument("--workspace-dir", default="")
    parser.add_argument("--executor", choices=["heuristic", "command"], default="heuristic")
    parser.add_argument("--command-template", default="")
    parser.add_argument("--scene-id", action="append")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir) if args.project_dir else Path.cwd()
    ensure_project_output_dirs(project_dir)
    scene_pack_path = Path(args.scene_pack_md) if args.scene_pack_md else default_scene_pack_md(project_dir)
    workspace_dir = Path(args.workspace_dir) if args.workspace_dir else default_workspace_dir(project_dir)
    ensure_workspace_dirs(workspace_dir)
    scene_pack = parse_scene_pack_markdown(load_text(scene_pack_path), source_path=scene_pack_path)
    save_json(workspace_dir / "scene_pack.json", scene_pack)
    selected_scene_ids = set(args.scene_id or [])
    for scene in sorted(scene_pack.get("scenes", []), key=scene_sort_key):
        if selected_scene_ids and scene["scene_id"] not in selected_scene_ids:
            continue
        shots = plan_scene(scene, args.executor, workspace_dir, args.command_template)
        save_json(build_scene_workspace_path(workspace_dir, scene["scene_id"]), {**scene_context(scene), "shots": shots})
        for shot in shots:
            save_json(build_shot_workspace_path(workspace_dir, shot["shot_id"]), shot)
        print(f"[done] planned {scene['scene_id']} -> {len(shots)} shots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
