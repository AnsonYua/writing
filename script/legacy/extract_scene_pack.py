from __future__ import annotations

import argparse
from pathlib import Path

from storyboard_workspace import DEFAULT_SCENE_PACK_MD, DEFAULT_WORKSPACE_DIR, load_text, parse_scene_pack_markdown, save_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract scene-pack markdown into structured JSON.")
    parser.add_argument("--input", default=str(DEFAULT_SCENE_PACK_MD))
    parser.add_argument("--output", default=str(DEFAULT_WORKSPACE_DIR / "scene_pack.json"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    data = parse_scene_pack_markdown(load_text(input_path), source_path=input_path)
    save_json(output_path, data)
    print(f"[done] extracted scene pack -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
