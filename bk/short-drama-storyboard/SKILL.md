---
name: short-drama-storyboard
description: Legacy reference-only short-drama storyboard skill. Historical rule library for image-first storyboard planning and still-image prompting. Do not use as the main pipeline skill; use only when Codex needs to inspect old storyboard rules and migrate their strengths into short-drama-shot-planner, short-drama-shot-prompt, or short-drama-start-image-review.
---

# Short Drama Storyboard

This is a legacy reference skill.

Do not use it as the main pipeline entry.

The active pipeline is:

`scene-pack.md` -> `short-drama-shot-planner` -> `short-drama-shot-prompt` -> `storyboard.json` / `storyboard.md` -> `short-drama-start-image-review`

## What This Legacy Skill Still Preserves

- comic-panel / frozen-frame thinking
- shot economy and scene-job boundary rules
- emotion-to-image translation
- reference / anchor / Qwen-Comfy prompt practices

## Mapping To Active Skills

- structural rules -> `short-drama-shot-planner`
- still-image prompt rules -> `short-drama-shot-prompt`
- assembled board review and handoff thinking -> `short-drama-start-image-review`

## Not For Main Pipeline Use

Do not use this skill as:

- the planner
- the shot prompt writer
- the assembled storyboard reviewer

Use it only as a historical rule library when auditing or migrating old logic.
