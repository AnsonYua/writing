---
name: short-drama-shot-review
description: Review one lean storyboard shot task or one generated single-panel image prompt without changing the storyline. Use when Codex needs to check whether a planned shot is readable as one frozen panel, whether a generated prompt thinks in image space instead of story-summary space, and whether the prompt wrongly re-describes stable anchored looks.
---

# Short Drama Shot Review

Use this skill in two places:

`scene-pack.md` -> `short-drama-shot-planner` -> `short-drama-shot-review`

and

`short-drama-shot-prompt` -> `short-drama-shot-review` -> assemble

## Main Goal

Review whether one shot is good enough for the next stage.

In planned-shot mode, check:

- is the panel readable on its own
- does the shot read like one frozen image rather than notes
- is the trigger readable if this is a reaction shot
- is the proof visible if this is a proof shot
- is the panel center clear
- does the shot avoid unnecessary story-explanation burden
- is `caption` truly necessary if present
- is `caption` short enough to behave like panel text rather than dialogue coverage
- if a reaction panel leads into active checking, does the panel already show why the character stays on the object
- does `shot_task` read like human creative planning instead of analyst wording
- if `caption` uses a pronoun, is the referent still clear enough
- if `caption` is inner voice, does it sound like immediate thought rather than summary

In prompt-review mode, check:

- does the prompt think in image space instead of story space
- does the wording start from what the camera sees
- does the prompt trust anchors instead of re-describing stable looks
- does the prompt avoid re-completing stable scene, character, and item setup already backed by anchors
- is the prompt free of workflow memo, preserve memo, and operator-note smell
- does the prompt still read like one single panel
- does the prompt describe an already-established visible state rather than an unfolding transition

## Hard Boundary

Do not change the storyline.

Do not:

- add new plot beats
- move reveals earlier
- redesign the whole scene
- rewrite neighboring shots
- silently merge scene structure

Review only the current shot.

## Not My Job

- I do not write a brand-new storyboard.
- I do not review assembled-board pacing.
- I do not rewrite the whole scene.
- I do not assign image1 / image2 / image3 order.
- I do not perform reference-linking.

## Review Modes

### Planned-Shot Mode

Review target is a lean shot task.

Expected shape:

- `shot_task`
- `shot_description`
- `caption`
- `anchor_mapping`

Allowed rewrite keys:

- `shot_task`
- `shot_description`
- `caption`

### Prompt-Review Mode

Review target is one generated prompt result.

Expected shape:

- `shot_id`
- `image_prompt`
- `caption`

Allowed rewrite keys:

- `image_prompt`
- `caption`

Do not use prompt review mode to silently redesign structure.

## Core Checks

### Single Panel Readability Check

Check whether the current shot reads as one understandable frozen panel.

If a reader still cannot imagine what is in frame, the shot is not ready.

### Established State Check

Fail the prompt if it is mainly written around a change still happening over time instead of the visible state that already exists in this one frame.

Bad smell examples:

- lights up
- starts to
- suddenly
- is about to
- turns and then

Rewrite toward the stable visible result that the viewer can actually see in one still image.

### Process Language In Still Frame Check

Fail if a still-image prompt uses sequential, unfolding, or browsing language to carry meaning that should instead be readable in one simultaneous frame.

- If several items matter, they should be visible together, not described as if they arrive one by one.
- If the wording sounds like revealing, scrolling, continuing, or gradually showing, reject it.
- Rewrite toward one stable arrangement the viewer can understand in one glance.

### Unseen Inference Check

Fail if the prompt depends on the viewer inferring sameness, repetition, shared source, or one repeated pattern without naming the visible repeated cues.

- If the panel meaning depends on one shared source, one repeated pattern, or one repeated place, the prompt must state what repeated visible cues make that readable.
- If the meaning lives mainly in interpretation rather than visible evidence, reject it.

### Collection Layout Clarity Check

Fail if a prompt centers on a collection, list, grid, grouped screen, grouped page, or any one-view set of related items, but does not define that collection as one stable readable arrangement.

- The viewer should understand the collection state in one glance.
- The wording should describe what is visible together now, not the process of moving through the collection.

### Image Space Check

Reject wording that thinks in story-summary space rather than image space.

Bad smell examples:

- explaining what the beat means
- explaining what the audience should feel
- explaining why the scene matters

Accept only wording that helps visualize the frame.

### Camera POV Check

Check whether the shot or prompt feels like a camera-facing frozen view.

The panel should be understandable through:

- framing
- subject placement
- visible action or pose
- proof or prop position
- minimum room cue

If the wording reads like recap, not lens view, fail it.

### Reaction Trigger Check

If this is a reaction shot, confirm the reader can tell what hit the character.

Do not accept:

- froze for no clear reason
- stared without clear trigger
- visible reaction with no readable cause

### Reaction To Checking Gap Check

If the current panel is reaction-driven and the next panel turns into active checking of the same object or proof, check whether the current panel already shows why that continuation is natural.

Good signs:

- the character still keeps eyes on the trigger
- the character still holds the object
- the hand or finger still stays close to the proof source
- the body is frozen but attention clearly has not left the object

Fail the shot if the next panel would only make sense because of extra explanation outside the image.

### Result-Only Reaction Check

Fail reaction shots that only present stunned result but do not show continued attachment to the trigger when the next panel depends on further checking.

Do not accept:

- generic frozen pose
- generic shocked stare
- reaction wording that forgets the object will remain the next panel's center

### Proof Visibility Check

If this is a proof shot, confirm the proof is visible at first glance.

Do not accept proof that only exists in explanation outside the panel.

### Panel Center Check

Check whether the shot or prompt has one first-look center.

If multiple things compete as the main subject, rewrite it.

### Continuity Memo Smell Check

Reject a shot or prompt that reads like a continuity memo instead of a panel.

Bad smell examples:

- too many reminders about same room or same prop
- too much next-step logic
- too much explanation of why the shot exists

### Analyst Language Check

Fail the shot if surfaced planner wording reads like tagged analysis rather than creative dramatic planning.

Bad smell examples:

- event-classification wording
- evidence taxonomy wording
- review-language labels
- commentary that sounds like system notes instead of storyboard language

## Prompt-Specific Checks

### Trust Anchors Check

If anchors already exist for character, room, or prop, the prompt should trust them.

Reject prompts that re-describe stable looks or stable space without a frame-specific reason.

Anchor value should be:

- shorter prompt
- cleaner prompt
- less repeated appearance description

Anchor value should not become:

- repeated character-sheet description
- repeated room-setting description
- repeated prop identity explanation
- repeated setup completion

### Anchor-Backed Omission Check

If `anchor_mapping` already supports a scene, character, or item, ask whether the extra description is truly needed for this frame.

Reject prompt wording that exists only to complete background setup already covered by anchors.

Ask:

- if this sentence is removed, does the frame still stand
- if yes, is this sentence just repeating what the anchor already covers
- if yes, remove it

### Exact Object Name Consistency Check

If a prompt names an anchored person, place, or item, check whether it keeps the exact `object_name` already declared in `anchor_mapping` when that name is already clear and usable.

Fail the prompt if it casually renames anchored elements in a way that weakens:

- wording stability
- downstream reference linking
- cross-shot consistency

### Stable Look Re-Description Check

Reject prompts that spend too much space reintroducing:

- full face description
- full hairstyle description
- full room appearance
- full object identity

when those things are already stable through anchors and are not the current frame's visual need.

### Over-Completion Check

Reject prompts when setup completion becomes louder than the actual panel event.

Common failures:

- background setup is longer than the key interaction
- room description is longer than the action
- item explanation is longer than the proof or handoff
- prompt spends more words rebuilding context than showing the current image

### Story-Space Voice Check

Reject prompts that sound like:

- story summary
- director intent
- audience guidance
- emotional interpretation instead of visible image language

Bad examples:

- this panel should express ...
- create a feeling of ...
- normal and plain, not horror-like

### Engineering Smell Check

Reject prompts that feel like operator notes rather than image prompts.

Bad smell examples:

- preserve memo language
- workflow language
- reference management language
- stacked tool instructions

### Prompt Rewrite Smell Check

Reject prompts that are:

- repetitive
- over-explained
- scattered
- carrying too many secondary details
- built around transition verbs instead of a frozen visible state

The final prompt should feel like one sharpened still-image request.

### Caption Check

If `caption` is present, check whether it helps the panel instead of repeating it.

Accept captions only when they are:

- short
- readable
- in `[Character]: line` format
- or `[Character心聲]: line` format for inner voice
- adding one useful line rather than explaining the whole story

### Caption Referent Clarity Check

Fail the caption if a pronoun or vague reference could reasonably point to more than one person, object, or source in the panel.

Rewrite toward the clearest concrete referent needed for the panel to read immediately.

### Inner Caption Authenticity Check

If the caption is heart-voice, fail it when it sounds like analysis, summary, or explanation rather than immediate human thought.

Accept only if it feels like something the character would actually think in that exact moment.

Reject captions that are:

- narration paragraph
- full scene explanation
- repeating the image prompt in words
- missing speaker label when dialogue is clearly spoken

### Caption Is Doing Image Job Check

Fail the shot if `caption` is being used to explain a transition that the image itself should already show.

Typical failures:

- caption explains why the character now keeps checking
- caption carries object continuity that the frame did not make visible
- caption becomes the real bridge between two panels

## Allowed Decisions

- `keep`
- `rewrite_shot`
- `merge_with_previous`
- `delete_shot`

## Required Output Shape

- `result`
- `decision`
- `issue_category`
- `reason`
- `rewrite`

Only include `rewrite` when the decision is `rewrite_shot`.

Keep rewrite minimal and local to the current shot.

In planned-shot mode, `rewrite` should only include:

- `shot_task`
- `shot_description`
- `caption`

In prompt-review mode, `rewrite` should only include:

- `image_prompt`
- `caption`

## Anti-Pattern Warnings

Do not accept shots or prompts like this:

- reaction is clear but trigger is missing
- proof is implied but not visible
- the wording tells story more than image
- the wording sounds like recap more than camera view
- `shot_task` sounds like analyst labeling instead of story-facing planning
- anchors exist but stable looks are fully re-described anyway
- anchors exist but scene setup is rebuilt anyway
- anchors exist but item identity is over-explained anyway
- setup text is longer than the main interaction
- engineering language takes more space than the panel itself
- continuity reminders overpower the actual frame
- caption repeats the whole image instead of adding one useful line
- the next checking panel only works because of tiny off-panel justification
- caption is doing the transition work that the image should have done
- caption uses a vague pronoun that weakens clarity
- inner caption reads like explanation instead of thought
- several items are supposed to matter but the prompt describes them as a sequence
- a repeated pattern is claimed but the repeated visible cues are missing
- a collection is central to the panel but the collection state is not readable in one view
- the image depends on a time-change verb such as `亮起` instead of a stable visible state

