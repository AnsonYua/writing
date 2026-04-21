---
name: short-drama-reference-linker
description: 將一格 storyboard shot 轉成多參考圖的 image-edit prompt，且不改動故事線。用於根據實際 reference mappings，決定 image1/image2/image3 各自代表什麼，並產出一條 reference-aware 的 shot prompt。
---

# 短劇 Reference Linker

當一格 shot prompt 需要具體 reference assignment 時，就使用這個 skill：

shot meaning + actual reference map -> `short-drama-reference-linker` -> reference-aware shot prompt

這個 skill 是獨立的。

它不需要 `linked-storyboard.json`，也不需要獨立的 reference-linking pass。

## Main Goal

Take one storyboard shot and turn its `image_prompt` into one reference-linked prompt.

Use the current shot as the prompt meaning reference.

Use the runtime reference mapping as the reference for actual image slots.

## Hard Boundary

Do not change the storyline.

Do not:

- redesign the shot
- rewrite the dramatic function
- move beats between shots
- add new plot facts
- replace the shot `image_prompt` with a different dramatic meaning
- review the whole board

Only resolve downstream reference linking for the current shot.

## Not My Job

- I do not plan shots.
- I do not rewrite storyboard structure.
- I do not do assembled-board pacing review.
- I do not replace the shot prompt's meaning.

## Required Input Shape

Expect:

- `shot`
- `actual_reference_map`
- `project_context` optional

## Required Output Fields

- `image_prompt`
- `reference_assignment`
- `linking_note`

## Linking Rules

### Prompt Preservation Rule

Treat the incoming `image_prompt` as the shot meaning.

Do not replace its story intent.

Only rewrite it into a cleaner multi-reference edit prompt and return that as the final `image_prompt`.

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
- what the new shot now looks like

Do not let preserve wording overwhelm the shot itself.

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
- returned `image_prompt` still reads like one drawable shot image
- `linking_note` is empty unless a real risk exists
