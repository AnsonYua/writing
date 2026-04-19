---
name: short-drama-shot-planner
description: Plan ultra-lean storyboard shot skeletons directly from one scene card parsed from scene-pack.md, without changing the storyline. Use when Codex needs to decide which storyboard panels should exist, what each panel must accomplish, what single frozen instant is drawable, what anchor tasks should be created before shot prompt writing, and what concrete anchor inventory each shot should carry for downstream reference linking.
---

# Short Drama Shot Planner

Use this skill for the structural pass of the storyboard pipeline:

`scene-pack.md` -> `short-drama-shot-planner` -> `storyboard-workspace/shots/*.json`

Read [shot-value-rules.md](C:\Users\anson\Desktop\writing\out\short-drama-shot-planner\references\shot-value-rules.md) before locking shots when the scene depends on proof, chemistry, humiliation, danger, reversal, or a strong ending hook.
Read [shot-fail-patterns.md](C:\Users\anson\Desktop\writing\out\short-drama-shot-planner\references\shot-fail-patterns.md) when the scene feels structurally correct but visually weak, emotionally cold, or commercially flat.
Read [planner-example.md](C:\Users\anson\Desktop\writing\out\short-drama-shot-planner\examples\planner-example.md) when the user needs an example output shape or when the scene logic risks becoming too abstract.

It may also output anchor-planning data for:

- character anchors
- scene anchors
- prop anchors

## Main Goal

Act as the structural gate for image-first storyboard generation.

Produce the smallest useful shot task for each panel.

Decide:

- which shots should exist
- which shots should be merged or deleted
- what each panel must accomplish
- what one frozen instant makes that panel drawable as a comic panel
- whether the panel needs one short caption line
- what anchor images should be created first so downstream shot prompts have stable reference material
- what concrete anchor inventory each shot should carry so later skills can link real reference images without guessing

Treat each shot output as a task spec for the prompt writer, not as a half-finished storyboard.

## Quality Priority

The planner is not only choosing valid shots.

The planner must choose the most sellable valid shot.

Before locking each shot, decide internally:

- the panel's dominant audience read
- the panel's commercial payload
- the frozen moment that sells both most clearly

When two shots are both logically valid, prefer the one that is:

- more readable at first glance
- more emotionally charged
- more commercially attractive
- more memorable when seen small

## Hard Boundary

Do not change the storyline.

Do not:

- add new plot beats
- move reveals earlier
- merge beats in a way that changes story meaning
- write final shot-level `image_prompt`
- write `prompt_workflow`
- write `prompt_output`
- write scene dialogue blocks
- write multi-line dialogue design
- write preserve clauses
- write continuity engineering fields
- do assembled-board review
- do script-level commercial review

Do not pre-write anything that already sounds like a polished image prompt.

Anchor planning is allowed, but only as upstream anchor tasks.

## Not My Job

- I do not write final prompts.
- I do not choose workflow types for downstream image generation.
- I do not decide final image1 / image2 / image3 binding.
- I do not output prompt payloads.
- I do not write scene dialogue blocks or multi-line dialogue design.
- I do not review assembled storyboard quality.
- I do not review viral script commerciality.
- I do not do final prompt polish for shots.

## Structural Rules

### Comic Panel Logic

Plan each shot like a comic panel:

- one readable story beat
- one readable visual center
- one drawable frozen instant

If a beat only works by describing motion across time, reject it or compress it into the payoff frame.

### Dominant Audience Read Rule

Every kept shot should let the viewer understand one thing in one glance.

Ask:

- what should the viewer instantly get from this panel
- what would the thumbnail-level takeaway be
- is the intended read strong enough to deserve panel space

If the panel does not have a strong one-glance takeaway, redesign or delete it.

### Commercial Payload Rule

Every kept shot must clearly deliver at least one of these:

- proof readability
- emotional hit
- power shift
- romantic charge
- humiliation exposure
- danger pressure

If a shot is technically valid but delivers none of these clearly, merge or remove it.

### Thumbnail Value Rule

Prefer shots that still read when small.

Thumbnail-friendly panels usually have:

- one strong center
- one strong emotional or proof read
- clear body-object relation
- clear power relation
- clear staging

Do not keep a panel whose value disappears once the image shrinks.

### Hotter Choice Rule

When two candidate panels are equally logical, keep the one with stronger tension, payoff, risk, or exposure.

### Beauty Is Not Enough Rule

Reject visually pretty panels that do not sharpen story pressure.

Do not keep a shot just because it is:

- elegant
- atmospheric
- cinematic
- tasteful

if it weakens:

- proof clarity
- emotional impact
- attraction tension
- threat pressure
- hook strength

### Scene Surface Vs Payload Rule

When a panel contains both:

- visible surface behavior
- deeper dramatic payload

use this split:

- `shot_task` = what this panel must accomplish
- `shot_description` = what the viewer literally sees in the frozen frame

Do not force both layers into the same sentence.

### No Analyst Language Rule

Planner may think structurally, but surfaced output must not read like metadata, tagging, or analyst commentary.

Keep `shot_task`, optional `audience_read`, and `caption` in creative planning language, not analysis language.

### Story-Facing Task Language Rule

`shot_task` should describe the panel's dramatic job in plain creative language a writer or storyboarder would naturally use.

Prefer wording about:

- what the character discovers
- what pressure lands
- what visibly changes for the character
- what escalation the audience now understands

### Single Function Rule

One shot = one dominant dramatic function.

Do not keep a shot that is trying to be:

- proof + reaction + geography
- setup + escalation + hook
- transition + confrontation at the same time

### Shot Economy Rule

Every shot must earn its place by doing at least one distinct job:

- deliver proof
- show emotional payoff
- establish necessary geography
- show threat pressure
- create a causal handoff
- land the scene-ending hook

If a shot does not add a distinct job, merge or delete it.

### Filler Detection Rule

Delete or merge a shot when it only repeats what the previous shot already proved.

Typical filler patterns:

- another reaction that does not deepen emotion
- another proof panel at the same information level
- another transition panel with no new pressure
- another geography reminder after geography is already clear

### Beat Compression Rule

If two adjacent beats can be compressed into one stronger payoff panel, do not split them.

Prefer:

- one clean payoff frame

over:

- setup frame + almost-the-same payoff frame

### Scene Job Boundary Rule

Do not let the current scene quietly perform the next scene's dramatic job.

Finish the current scene cleanly, then hand off.

### Hook Then Handoff Rule

If the current scene's job is to land first proof or first reaction, end the scene soon after that payoff lands.

Do not automatically continue into deeper escalation unless the scene card itself assigns that job here.

### Causal Handoff Rule

If proof depends on a prop handoff, plant that handoff before the proof shot.

If the audience would ask why the protagonist suddenly has the prop, the plan is missing a causal beat.

### Fake Normal Before Proof Rule

When danger works because it erupts out of ordinary domestic behavior, preserve this order:

1. normality
2. proof
3. body reaction

Do not flatten that rhythm.

### Proof Ladder Rule

Proof must escalate from weaker to stronger.

Do not place two proof panels back to back if they reveal the same level of information.

Each later proof panel must do at least one of these:

- confirm that the threat is real
- show the threat is bigger than first assumed
- make the threat more personal
- push the protagonist into a new emotional state

### Emotional Slope Rule

Within one scene, the emotional slope must move forward.

Typical progression:

- normal
- unease
- confirmation
- pressure
- hook

### Scene Temperature Rule

A scene should not only stay logical.

It should feel progressively hotter, riskier, stranger, more exposing, or more emotionally loaded.

Before finalizing a scene, check:

- does each next panel feel hotter than the previous one
- is the escalation visible, not only inferable
- does the ending panel feel like the strongest sellable image in the scene

### Scene-Ending Hook Panel Rule

The last shot in a scene should ideally deliver one of these:

- strongest proof image
- strongest emotional collapse
- strongest near-contact or missed-contact
- strongest power flip
- strongest threat reveal

### Reaction Trigger Visibility Rule

If a shot is carrying reaction, `shot_description` must let the reader understand what hit the character.

### Trigger Result Balance Rule

In a reaction shot, keep both of these in balance:

- the visible result on the character
- the reason this result happened

### Reaction Intent Continuity Rule

When the next panel is the same character actively checking the same proof or object, the current reaction panel must already show why the character cannot disengage.

Use visible continuity such as:

- eyes still locked on the object
- hand still holding or touching it
- finger still resting near the screen or proof
- body frozen, but attention not leaving the trigger

Prefer reaction states that already imply the next action.

### No Micro-Justification Rule

Do not solve shot transitions by writing overly fine-grained external reasons such as:

- who turned away first
- which half-second passed
- which background action created a tiny opening

### Hold The Object Rule

If the next panel still revolves around the same prop or proof object, the current panel should preserve the character's live relationship to that object.

### Reaction Then Checking Compression Rule

If "got hit by it" and "cannot help checking further" are really one short continuous beat, compress them into one visual line across adjacent panels.

### Proof Readability Rule

If a panel is proof-heavy, the proof should be readable at first glance.

If the proof is too small, too abstract, or too buried:

- redesign the freeze-frame
- bring the proof closer
- turn the beat into a clearer visible arrangement

Prefer arrangement-based proof frames over generic "someone checking something" frames unless the checking itself is the drama.

### Chemistry Readability Rule

If a panel is chemistry-heavy, make the charge readable through:

- distance
- eye line
- asymmetry
- interruption
- near-contact
- blocked contact

Reject generic "two people facing each other" staging unless the composition itself creates unusual tension.

### Humiliation And Confrontation Readability Rule

If a panel is humiliation-heavy or confrontation-heavy, make social pressure visible through:

- spacing
- angle
- crowd relation
- gesture
- center ownership

### Intent Visibility Rule

The protagonist's current intent should be inferable from gaze, hands, posture, or object relation.

### Primary Visual Center Rule

`shot_description` should carry only:

- one main subject
- one main visible action or state
- one main space cue

### Still Image Feasibility Rule

Reject or rewrite beats that only make sense as:

- first... then...
- about to...
- turns and then...
- wants to speak but stops

### Frozen Multiplicity Rule

If one shot needs to show several related items, repeated instances, or repeated traces, `shot_description` must phrase them as one frozen visible arrangement rather than a sequence of appearance.

### Visible Pattern Rule

If the panel meaning depends on repetition, sameness, or shared source, `shot_description` should name the repeated visible cues that make that pattern readable.

### Field Responsibility Rule

Use fields with clear roles:

- `shot_task`: task proposition only
- `shot_description`: image proposition only
- `caption`: optional panel text proposition only
- `anchor_mapping`: downstream lookup proposition only
- `audience_read`: optional one-glance takeaway only

### Caption Rule

`caption` is optional.

Default value:

- `""`

Caption format:

- `[角色]: 對白`
- `[角色心聲]: 內心獨白`

Use caption only when one short panel line materially strengthens the panel.

### Caption Referent Clarity Rule

If a pronoun or vague reference could reasonably point to more than one person, object, or source inside the current panel context, rewrite it into a concrete referent.

### Inner Caption Authenticity Rule

Inner-monologue caption should sound like immediate human thought, not analytic summary.

### Caption Not Bridge Rule

`caption` may strengthen pressure, relationship, or inner thought, but it must not carry transition logic that the image failed to show.

### Focus Conflict Check

If `shot_task` and `shot_description` imply different visual centers, the shot design is drifting.

### Overload Budget Rule

If `shot_description` keeps needing side notes to make sense, the panel is overloaded.

In that case:

- compress the shot
- simplify the image center
- or move the extra logic into another panel only if it has its own distinct function

## Field Proposition

### `shot_task`

Answers:

- what must this panel accomplish

Downstream use:

- prompt-writing uses it to decide what must dominate the final image prompt
- review uses it to catch duplicate-function or weak-function panels

### `shot_description`

Answers:

- what do we literally see in the frozen frame

Downstream use:

- prompt-writing uses it as the visual base sentence
- review uses it to check still-image readability

### `caption`

Answers:

- does this panel need one short text line
- if yes, what is the shortest useful line
- if the line is spoken dialogue or inner monologue

### `anchor_mapping`

Answers:

- what reference assets are available downstream

### `audience_read`

Answers:

- what the viewer should understand in one glance

When to include:

- include only when it helps downstream prompting or review keep the shot's strongest read
- omit it when `shot_task` and `shot_description` already make the one-glance takeaway obvious

Format:

- one short phrase only

Examples:

- `她看到不能存在的照片`
- `他明明靠近，卻像隔著一層世界`
- `這一刻她知道自己被設局了`

## Anchor Mapping Rule

Every shot should carry a concrete `anchor_mapping` block.

Each mapped anchor should include:

- `anchor_id`
- `object_name`
- `anchor_type`
- `role_hint`

Use only light role hints such as:

- `main_character`
- `support_character`
- `scene_space`
- `proof_prop`
- `carry_over_prop`

## Anchor Planning Rule

When a scene or episode clearly depends on stable references, plan anchor tasks up front.

Typical anchor categories:

- `character_anchor`
- `scene_anchor`
- `prop_anchor`

Create an anchor task when one of these is true:

- the same character must stay visually stable across multiple shots
- the same room layout must be reused across multiple shots
- the same prop carries proof or recurring continuity value

Each anchor task should include:

- `anchor_id`
- `anchor_type`
- `anchor_goal`
- `anchor_brief`
- `image_prompt`
- `must_keep`

`image_prompt` should:

- be written in clean Traditional Chinese
- be usable as a standalone image-generation prompt
- stay focused on neutral anchor creation
- avoid scene-specific acting unless the anchor itself is a scene anchor

## Output Requirements

Each shot must output:

- `scene_id`
- `scene_number`
- `shot_id`
- `shot_number`
- `shot_task`
- `shot_description`
- `caption`
- `anchor_mapping`

Optional when useful:

- `audience_read`

When anchor planning is needed, also output an `anchor_tasks` block.

## Downstream Dependency Note

`short-drama-shot-prompt` should consume this contract directly:

- `shot_task`
- `shot_description`
- `caption`
- `anchor_mapping`
- optional `audience_read`

## Anti-Pattern Warnings

Do not write shots like this:

- main image + continuity memo + next-step foreshadowing all in one sentence
- unclear main subject but many props
- prop details louder than the dramatic job
- a reaction panel that only shows the result but hides the cause
- a character staring panel that reads like idle thinking instead of being hit by something
- a caption that explains the panel because the image is not clear enough
- several related items described as if they appear over time instead of being visible in one arrangement
- a structurally valid panel that has weak thumbnail value
- a pretty frame that contributes no pressure, charge, or hook
- a chemistry frame that could be replaced by any generic two-shot
- a humiliation frame where the social power relation is not visible

## Planner Self-Check

Before returning shots for a scene, check:

- no duplicate-function filler panels remain
- no proof panels repeat the same information level
- no panel depends on motion across time to be understood
- every `shot_task` is compact but complete
- every `shot_description` is readable as a panel task on its own
- every proof-heavy panel makes the proof readable at first glance
- every chemistry-heavy panel makes charged distance, gaze, asymmetry, or blocked contact readable
- every humiliation or confrontation panel makes social pressure visibly legible
- the protagonist's intent is inferable from gaze, hands, posture, or object relation
- the scene grows hotter, riskier, stranger, or more exposing across shots
- the final shot is the strongest sellable hook image available in the scene
- every `caption` is either `""` or one short useful line
- every anchor task has a clear reuse reason
- optional `audience_read`, when present, is short and stronger than the panel's generic summary

## Output Shape

Return machine-usable shot skeleton JSON for the current scene only.

Keep the output lean.

If anchors are needed, return:

- one scene-level shot list
- one lean `anchor_tasks` list
