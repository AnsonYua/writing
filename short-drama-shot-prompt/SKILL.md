---
name: short-drama-shot-prompt
description: Write one Qwen-Image-ready still-image prompt plus one carried-forward panel caption for one approved storyboard shot JSON without changing the storyline. Use when Codex needs to turn one already-planned shot into one clear single-panel image prompt that trusts existing anchors, writes from camera/image space rather than story-summary space, and preserves planner-provided caption text.
---

# Short Drama Shot Prompt

Use this skill for the prompt-writing pass of the storyboard pipeline:

`output/storyboard-workspace/shots/*.json` -> `short-drama-shot-prompt` -> `output/storyboard-workspace/prompts/*.prompt.json`

Read [shot-value-rules.md](C:\Users\anson\Desktop\writing\out\short-drama-shot-prompt\references\shot-value-rules.md) before prompt writing when the current shot depends on proof, chemistry, humiliation, danger, reversal, or a strong thumbnail read.
Read [shot-fail-patterns.md](C:\Users\anson\Desktop\writing\out\short-drama-shot-prompt\references\shot-fail-patterns.md) when a prompt feels technically correct but visually flat, generic, or too safe.
Read [prompt-example.md](C:\Users\anson\Desktop\writing\out\short-drama-shot-prompt\examples\prompt-example.md) when the user needs a concrete before-and-after style target.

## Main Goal

Take one approved planner shot and write one clean Qwen-Image prompt for that shot only.

Planner output is the source of truth.

This skill does one job:

- convert one approved shot task into one still-image prompt that reads like a camera-facing image request

Success condition:

- someone reading the prompt can imagine the exact panel without extra explanation
- the prompt reads like an image-generation prompt, not a story note
- the prompt stays focused on what the camera sees in this one frame
- the prompt preserves the panel's strongest dramatic payload instead of flattening it

## Core Proposition

Use the current shot as a task card:

- `shot_task` answers: why this panel exists
- `shot_description` answers: what the frozen frame visibly is
- `anchor_mapping` answers: what stable elements already exist downstream
- optional `audience_read` answers: what the viewer should get in one glance
- `image_prompt` answers: how to render this panel as one image

`shot_task` helps decide image priority.

`shot_description` is the main writing base.

`anchor_mapping` is not the main subject of the prompt. Its value is that it lets the prompt stay shorter and cleaner.

If a sentence does not change what the image looks like, do not keep it in the prompt.

If a stable scene, character, or item already exists in `anchor_mapping`, do not treat the prompt as a place to complete that missing setup again.

## Hard Boundary

Do not change the storyline.

Do not:

- question shot count
- merge or split shots
- move a beat to another scene
- redesign shot structure
- invent new plot information
- write image1 / image2 / image3 assignment
- write reference-linking plans
- write preserve-clause engineering language
- output workflow notes inside the prompt
- answer for neighboring shots

If the shot itself is weak, still write the best prompt for the current shot. Do not silently replan it.

## Not My Job

- I do not redesign shot structure.
- I do not merge or delete shots.
- I do not review assembled board pacing.
- I do not design reference binding.
- I do not write multi-image assignment.
- I do not output post-storyboard linked prompts.
- I do not add continuity burdens not already justified by the shot itself.
- I do not invent dialogue or caption that the planner did not provide.
- I do not write SFX fields.

## Required Input Shape

Expect the current shot payload to primarily provide:

- `scene_id`
- `scene_number`
- `shot_id`
- `shot_number`
- `shot_task`
- `shot_description`
- `caption`
- `anchor_mapping`

Optional support input:

- `audience_read`
- `scene_context_summary`
- `previous_shot_summary`

Treat `anchor_mapping` as compression support, not as prompt cargo.

Treat `anchor_mapping` as existence proof for stable scene, character, and item information that downstream can already resolve.

When an anchored person, place, or item does need to be named in the prompt, use the exact `object_name` wording from `anchor_mapping` instead of inventing a new synonym.

## Required Output Fields

- `shot_id`
- `image_prompt`
- `caption`

## Output Placement

Default output location:

- `output/storyboard-workspace/prompts/`

Default filename pattern:

- `{shot_id}.prompt.json`

Example:

- `output/storyboard-workspace/prompts/S1_SH1.prompt.json`

Default behavior:

- create the prompt result in the prompts folder
- if `{shot_id}.prompt.json` already exists, overwrite it with the newest accepted result
- do not write prompt results back into the original shot JSON by default

This skill should assume the prompt file is the canonical output artifact for one shot prompt pass.

## Internal Work Order

Before writing the final JSON, do this internally:

1. read `shot_task` and optional `audience_read`
2. choose the panel's first-look center
3. choose the panel's commercial payload
4. choose the visual priority order
5. read `shot_description` and identify the visible subject, framing, action, prop state, and space cue
6. check `anchor_mapping` and suppress any stable look, stable space, or stable item re-description that the image does not need
7. write one prompt from camera/viewpoint language
8. carry forward the planner-provided `caption`
9. self-check for:
   - story-summary voice
   - re-describing stable anchored looks
   - re-describing stable anchored scene or item setup
   - workflow memo smell
   - two time steps in one prompt
   - weak first-look center
   - flat neutral description where the panel should feel charged
   - caption does not repeat the whole image prompt

Only output the final JSON.

## Priority Lock

Before wording the prompt, explicitly decide internally:

- what the viewer sees first
- what the image is selling
- what must stay most legible

Default priority order:

1. main dramatic center
2. visible emotional state
3. proof, prop, or person relation
4. room cue
5. light or atmosphere only if it sharpens the read

If a later detail weakens an earlier priority, cut the later detail.

## Prompt Rules

### One Shot One Image Rule

One shot = one image.

Do not treat one shot like a mini-sequence.

Write the image as an already-established state, not as a transition that is still unfolding.

### First-Look Bait Rule

The first readable area of the image should carry the story payload.

If the panel sells proof, the proof should read first or nearly first.
If the panel sells humiliation, the exposed power relation should read first.
If the panel sells chemistry, the charged spacing or gaze should read first.
If the panel sells danger, the threat relation should read first.

Do not bury the real hook behind neutral setup detail.

### Image Space Rule

Write from image space, not story space.

Start from what the lens sees:

- framing
- subject
- visible action or pose
- key prop or proof position
- minimum readable room cue

Do not start from:

- what the author wants to say
- what the audience should feel
- what this beat means in the overall story

### Camera POV Rule

Think in shot perspective.

The prompt should feel like a frozen camera view, not a recap of events.

Prefer wording that helps visualize:

- shot distance
- where the subject sits in frame
- what the body is doing
- what object or proof is visible
- what part of the room is readable

Prefer plain visual language over technical camera jargon.

### No Flat Prompt Rule

Do not write neutral descriptive prompts for panels whose point is:

- tension
- shame
- desire
- fear
- revelation
- reversal

If the panel depends on emotional charge, make that charge visible through:

- distance
- posture
- gaze
- pressure
- blocking
- prop contact
- who controls the center of frame

### Dramatic Compression Rule

Use the fewest details needed to make the panel hit hard.

Keep:

- what sells the panel
- what keeps it legible
- what keeps it specific

Cut:

- nice-to-have set dressing
- stable identity recap already handled by anchors
- decorative atmosphere that weakens the main read

### Charged Framing Rule

If the beat is intimate or confrontational, use distance, blockage, negative space, overlap, or asymmetry to sharpen it.

### Emotional Body Rule

Express emotion through visible body state, not mood labels.

Prefer:

- fingers paused on the phone edge
- shoulders locked
- chin slightly lifted in refusal
- body half-turned but eyes still fixed on him
- one step too close for comfort

### Trust Anchors Rule

If `anchor_mapping` already provides stable character, scene, or prop anchors, trust them.

Do not re-describe stable looks unless the feature is necessary to make this specific frame readable.

Do not re-describe stable scene setup or stable item identity unless the frame cannot be understood without it.

### Anchor-Backed Omission Rule

If a scene, character, or item is already supported by `anchor_mapping`, and this frame does not depend on its detailed appearance, omit that detail.

Anchor existence is a reason to shorten the prompt.

### Exact Object Name Rule

If the prompt needs to name an anchored person, place, or item, prefer the exact `object_name` already declared in `anchor_mapping`.

### Shot Task Priority Rule

Use `shot_task` and optional `audience_read` only to decide what should dominate the image.

Do not restate them mechanically.

### Shot Description Base Rule

`shot_description` is the main base of the prompt.

Translate it into clearer image language when needed, but do not replace it with a different panel idea.

### Frame First Rule

Build the prompt in this priority order:

1. framing or camera distance
2. main subject
3. visible action, pose, or proof
4. key prop state if needed
5. minimum room cue
6. visible light or atmosphere only if it changes the image

### Visible Only Rule

Only write what can be seen in the image.

Translate abstract emotion into visible image language such as:

- gaze direction
- hand position
- body stillness or tension
- prop position
- distance from another person

### Established State Rule

Describe what the viewer sees as the frame already exists now.

Prefer:

- the screen shows
- the phone is on
- the hand rests on the screen edge
- the face is turned toward the phone

### Single-Frame Multiplicity Rule

If a panel needs to communicate several items, repeated instances, or repeated evidence, express that through one visible layout or simultaneous arrangement inside the frame.

### Arrangement Over Process Rule

When the panel meaning depends on multiple elements being present, write how they are visibly arranged in the frame, not how they emerge over time.

### Visible Pattern Rule

If the image meaning depends on recognizing repetition, sameness, or shared source, name the repeated visible cues that make that pattern readable.

### Collection State Rule

When the panel centers on a collection of related items, write the frame as one stable collection state rather than a browsing process.

### Proof Legibility Rule

If the panel depends on evidence, the evidence must be visually legible in the prompt, not buried.

Name the exact visible arrangement when helpful:

- several photos tiled on the phone screen
- the incriminating message thread open in one view
- a lipstick mark on the white shirt collar near the throat

Avoid story-summary explanation of what the evidence means.

### Reaction Rule

If the panel is reaction-driven, keep the visible link between:

- what the character is seeing or holding
- how the reaction lands on the body or face

Do not let the image become a generic stunned pose.

Preserve hand, eye, and object continuity.

### Chemistry Rule

If the panel is chemistry-driven, prioritize:

- charged spacing
- gaze
- interruption
- asymmetry
- near-contact
- blocked contact

Describe the relation between bodies, not only each person separately.

### Humiliation And Confrontation Rule

If the panel is humiliation-driven or confrontation-driven, make the social power relation readable.

Use:

- crowd placement
- body angle
- eye-line imbalance
- center ownership
- exposure versus isolation

### Support Character Rule

If a second character is visible, only include the amount of detail needed to keep the frame readable.

Do not let support-character description overpower the intended main center.

### Stable Look Suppression Rule

If a character or room is already stable through anchors, do not spend prompt space reintroducing full appearance.

Only mention a stable element again when this frame needs it for:

- readability
- role distinction
- prop recognition
- proof clarity

### Natural Qwen Prompt Rule

Write natural Traditional Chinese short sentences.

The result should feel like one coherent image request.

Prefer simple visual wording that ordinary readers can picture immediately.

### Caption Rule

Carry the planner-provided `caption` forward into the output.

Default caption format:

- `[Character]: line`
- `[Character心聲]: line`

If planner input gives:

- `""`

then return:

- `""`

Do not invent a new caption when planner input does not provide one.

## Output Rule

`image_prompt` is the only creative product of this skill.

Return only:

- `shot_id`
- `image_prompt`
- `caption`

## Anti-Pattern Warnings

Do not write prompts like this:

- story summary disguised as image prompt
- "this panel should express ..."
- "create a feeling of ..."
- anchor exists but full character appearance is re-described anyway
- anchor exists but full room setup is re-described anyway
- anchor exists but item identity is over-explained anyway
- workflow note disguised as prompt
- video-style action chain
- wording built around a state-change that only makes sense over time
- reaction visible but trigger invisible
- a proof frame where the evidence is named too vaguely to picture
- a chemistry frame that reads like neutral posing
- a charged scene flattened into tasteful but low-tension description

## Prompt Self-Check

Before returning the shot result, check:

- the prompt reads like one still image, not a sequence
- the prompt describes an established visible state, not an unfolding change
- the first-look center is clear
- the prompt's first readable area carries the intended payload
- the wording starts from what the camera sees
- the prompt does not retell the story
- stable anchored looks are not re-described without need
- stable anchored scene or item setup is not re-described without need
- proof-heavy prompts keep evidence legible
- reaction-heavy prompts keep trigger and body state linked
- chemistry-heavy prompts preserve charged spacing, asymmetry, or blocked contact
- humiliation and confrontation prompts keep power imbalance visible
- the caption is short and uses `[Character]: line` format when present
- if the caption is inner voice, it keeps `[Character心聲]: line` format
