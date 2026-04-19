from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = [
    "image_prompt",
    "panelTextType",
    "panelText",
    "sfxText",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def extract_first_json_object(text: str) -> dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise RuntimeError("Adapter could not find JSON object in Codex response.")
    payload = json.loads(text[start : end + 1])
    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing:
        raise RuntimeError(f"Adapter JSON missing required fields: {', '.join(missing)}")
    return payload


def run_codex_command(prompt: str) -> str:
    command = os.environ.get("CODEX_MCP_COMMAND", "").strip()
    if not command:
        raise RuntimeError("Missing CODEX_MCP_COMMAND. Set it to a command that reads stdin, calls Codex MCP, and prints JSON.")
    completed = subprocess.run(command, input=prompt, text=True, shell=True, capture_output=True, check=True)
    return completed.stdout.strip() or completed.stderr.strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bridge shot-prompt requests to Codex MCP.")
    parser.add_argument("--request", required=True)
    parser.add_argument("--response", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    request_payload = load_json(Path(args.request))
    adapter_prompt = str(request_payload.get("adapter_prompt", "")).strip()
    if not adapter_prompt:
        raise RuntimeError("Request payload missing adapter_prompt.")
    response_text = run_codex_command(adapter_prompt)
    response_payload = extract_first_json_object(response_text)
    save_json(Path(args.response), response_payload)
    print(f"[done] adapter wrote {args.response}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
