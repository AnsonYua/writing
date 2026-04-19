---
name: short-drama-reference-linker
description: Convert one assembled storyboard shot into a downstream-ready multi-reference image-edit prompt after storyboard.json is built. Use when Codex needs to read the canonical storyboard shot, decide what image1/image2/image3 each represent from actual runtime reference mappings, and output a clean reference-linked prompt for Qwen or Comfy image-edit workflows.
---

# Short Drama Reference Linker

Use this skill after storyboard assembly:

`storyboard.json` -> `short-drama-reference-linker` -> linked prompt package

## Main Goal

Take one already-assembled storyboard shot and turn its canonical `image_prompt` into one downstream-ready reference-linked prompt.

Use the assembled shot as the source of truth for panel meaning.

Use the runtime reference mapping as the source of truth for actual image slots.

## Hard Boundary

Do not change the storyline.

Do not:

- redesign the shot
- rewrite the dramatic function
- move beats between panels
- add new plot facts
- replace the canonical `image_prompt`
- review the whole board

Only resolve downstream reference linking for the current shot.

## Not My Job

- I do not plan shots.
- I do not rewrite storyboard structure.
- I do not do assembled-board pacing review.
- I do not replace the canonical storyboard prompt.

## Required Input Shape

Expect:

- `shot`
- `actual_reference_map`
- `project_context` optional

## Required Output Fields

- `resolved_image_prompt`
- `reference_assignment`
- `linking_note`

## Linking Rules

### Canonical Prompt Preservation Rule

Treat the incoming `image_prompt` as the canonical panel meaning.

Do not replace its story intent.

Only rewrite it into a cleaner downstream multi-reference edit prompt.

### Assignment Rule

Assign each actual image slot one clear preserve job.

Typical jobs:

- main character appearance
- support character appearance
- scene layout or room direction
- prop identity or state
- previous-shot carry-over

Do not let multiple image slots do the same vague job.

### Natural Reference Language Rule

Write natural Traditional Chinese.

Use concrete wording such as:

- 以圖1保留李美珍的臉型、年齡感和素色家居服
- 以圖2保留臥室門口與房內的方向關係
- 以圖3保留同一部黑色手機的機身和黑屏狀態

Do not write raw markers or placeholder preserve language.

### Preserve And Change Balance Rule

The linked prompt must answer both:

- what stays stable from each reference
- what the new panel now looks like

Do not let preserve wording overwhelm the panel itself.

### Missing Reference Rule

If the runtime map is missing a needed reference:

- still produce the best usable linked prompt
- state the risk briefly in `linking_note`
- do not invent a fake file

### Output Shape Rule

`reference_assignment` should map each image slot to:

- `path`
- `job`
- `preserve`

Keep it short and machine-friendly.

## Self-Check

Before returning:

- the current shot meaning is unchanged
- each image slot has one distinct job
- raw ref markers are gone
- preserve wording is concrete
- `resolved_image_prompt` still reads like one drawable panel
- `linking_note` is empty unless a real risk exists
