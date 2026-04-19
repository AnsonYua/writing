---
name: short-drama-start-image-review
description: Review an assembled image-first storyboard or linked-storyboard output at shot, scene, or board level without changing the storyline. Use when Codex needs a production-facing editorial check on panel readability, continuity, proof escalation, hook hierarchy, linked multi-reference clarity, and handoff readiness after storyboard assembly.
---

# Short Drama Start Image Review

Use this skill after storyboard assembly:

`storyboard.json` / `storyboard.md` / `linked-storyboard.json` -> `short-drama-start-image-review`

I am the storyboard-assembled, high-level production/editorial reviewer.

## Main Goal

Review whether the assembled storyboard is actually ready to hand off to the next operator.

Check:

- shot prompt quality
- panel readability
- scene sequence pacing
- duplication / drag
- proof readability
- emotional beat placement
- continuity of people, props, and space
- linked prompt clarity when downstream multi-reference prompts exist
- production readiness for the next image / production step

## Review Modes

- `shot`
- `scene`
- `board`

## Board Review Order

When reviewing at board level, check in this order:

1. hook hierarchy
2. proof readability
3. emotional beat placement
4. continuity risks
5. operator readiness

## Hard Boundary

Do not change the storyline.

Do not:

- add plot events
- move reveals earlier
- invent props that become story facts
- silently rewrite story logic while pretending to do prompt cleanup

## Not My Job

- I do not review script-level commercial potential only.
- I do not replace the second-review skill.
- I do not silently rewrite story logic while pretending to do prompt cleanup.

## Core Review Lenses

### Hook Priority Check

Check whether:

- the first 3-second hook is truly the earliest strong pull
- the strongest proof panel is clear enough and placed early enough
- the strongest emotional beat lands on the right panel
- the final cliffhanger is strong enough to hand off to the next step

### Panel Readability Check

Check whether each panel reads even before the full script is explained.

Ask:

- can a reader tell what is happening now
- is the visual center obvious
- is the panel still-image readable rather than video-instructional

### Adjacent Panel Bridge Check

Check whether neighboring panels feel like the same continuous dramatic moment instead of disconnected generated images.

### Proof Escalation Check

Check whether proof grows in strength instead of repeating the same evidence too many times or revealing too much too early.

### Continuity Risk Check

Check for:

- character drift
- prop drift
- room / layout drift
- support-character in / out logic problems
- reference burden that is too dependent on text only
- linked prompt reference assignment that is vague or overlapping
- false-normality danger being pushed into obvious villain-face framing

### Operator Handoff Check

Check whether:

- the assembled storyboard is already usable for the next image / production step
- the board is missing high-risk warnings
- the handoff reads like a practical operator brief, not a recap

## Allowed Decisions

- `keep`
- `rewrite_prompt_only`
- `replan_shot`
- `merge_with_previous`
- `move_to_next_scene`
- `delete_shot`

## Required Output Shape

- `result`
- `review_level`
- `issues`
- `rewritten_prompt`
- `reference_strategy_correction`
- `sequence_note`
- `hook_priority_notes`
- `final_continuity_risks`
- `operator_handoff_summary`

Use `rewrite_prompt_only` when wording is the only problem.

Use structural decisions when the real problem is pacing, placement, duplication, continuity, or handoff safety.
