---
name: short-drama-script
description: Generate polished viral short-drama scripts from a topic or one-line premise. Use when Codex needs to turn an idea, trope, title, character setup, or rough concept into a short-form serialized script with fast hooks, de-AI rewriting, and built-in self-review.
---

# Short Drama Script

Turn a loose idea into a platform-native short-drama script.

Default to a commercially sharp, emotionally charged style suitable for short-video drama platforms. Focus on scriptwriting only. Do not output image prompts, storyboard prompts, or video prompts unless the user explicitly asks for them.

Read [genre-packs.md](C:\Users\anson\Desktop\writing\out\short-drama-script\references\genre-packs.md) when the user names a genre or when the premise clearly maps to one of the included packs.
Read [de-ai-audit.md](C:\Users\anson\Desktop\writing\out\short-drama-script\references\de-ai-audit.md) when the draft feels generic, over-explanatory, or repetitive.
Read [negative-rules.md](C:\Users\anson\Desktop\writing\out\short-drama-script\references\negative-rules.md) before locking the premise, before writing Episode 1, and during self-review.

## Default Output

When the user gives only a topic or one-line premise, produce:

1. Upgraded one-line hook
2. Core cast
3. Eight-episode outline
4. Full Episode 1 script
5. Episode-end continuity snapshot
6. Brief self-review summary

If the user explicitly asks for only one part, provide only that part.

## Workflow

Follow this workflow internally before you answer:

1. Upgrade the premise
2. Stress-test premise logic like a skeptical viewer
3. Reject fake reversals before drafting
4. Build the conflict engine
5. Build the episode emotion engine
6. Draft the outline
7. Convert Episode 1 into 3-5 concrete beats
8. Write the script
9. Remove AI-like language
10. Audit the draft
11. Revise once based on the audit
12. Run the negative-rule check

Do not dump the internal chain-of-thought. Only present the polished output.

## Premise Upgrade

Preserve the user's core idea, then strengthen it with at least two of:

- identity gap
- public humiliation
- betrayal
- secret
- reversal
- revenge
- contract relationship
- class gap
- misunderstanding
- hidden power

If the idea is too flat, make it more marketable without changing the genre beyond recognition.

Before locking the upgraded premise, challenge it like a skeptical audience member.

- Ask what the viewer will question first
- Ask whether the hook sounds natural in spoken language
- Ask whether the reversal is earned or just forced
- Ask whether the setting uses the right word for the situation
- If the premise sounds fake, awkward, or over-engineered, rewrite the premise instead of defending it

## Reversal Gate

Do not call something a reversal unless the audience's understanding meaningfully changes.

Not a reversal:

- bad news followed by worse news
- pressure followed by more pressure
- "it is even more tragic than before"
- a dramatic sentence that does not change the audience's understanding

A valid reversal must do at least one of these:

- reveal that the audience understood the situation wrongly
- flip who has power in the moment
- turn humiliation into leverage
- turn weakness into hidden value
- turn a loss into a new path, weapon, or bargaining chip

Hard rule:

- "worse than before" is escalation, not reversal
- do not label escalation as reversal
- if the hook only makes the protagonist more miserable, rewrite it until it creates a new audience understanding

## Protagonist Emphasis

Highlight the protagonist's pain point early and clearly.

- Make the audience instantly understand what the protagonist is losing
- Make the humiliation concrete, not abstract
- Make the pressure visible in work, money, family, status, or love
- Make the protagonist's wound easy to feel within seconds
- Make the eventual payoff hit the exact place that hurt earlier

When choosing between a clever twist and a sharper protagonist pain point, prefer the sharper pain point.

## Script Rules

Write like a short-drama writer, not a novelist.

- Hook the audience in the first 3 seconds
- Keep scenes few and efficient
- Push conflict in every scene
- Make dialogue short, sharp, and speakable
- Prefer action, reaction, interruption, and subtext over explanation
- End on a strong cliffhanger
- Make scene description show how a person acts, not only what happens
- Keep Episode 1 dense: it should feel like several ordinary scenes' worth of plot packed into one short episode

## Action-Presentable Rule

Write actions as things actors can perform and cameras can capture.

Avoid author-summary wording such as:

- 找借口
- 想办法
- 试图
- 打算
- 为了不让别人发现

when the line should really show a visible action.

Bad:

- `周晓晴找借口把李美珍拉进卧室`

Why this is weak:

- `找借口` is not a drawable action
- the audience cannot immediately picture what she actually does
- it sounds like writer explanation, not drama happening in front of us

Prefer:

- `周晓晴把李美珍拉进卧室，反手把门关上`
- `周晓晴一把拉住母亲，直接把她拽进卧室`
- `周晓晴把手机塞进母亲手里，转身把门关上`

Hard rule:

- if a line contains the intent but not the visible move, rewrite it into the visible move
- priority goes to what the body does, what the hand does, what the door does, what the prop does

## Scene Logic Rule

Build scenes around motivated behavior, not arbitrary coverage chunks.

When a discovery scene depends on a private window, write the private window explicitly into the script.

Common useful motivations:

- someone leaves the space for a believable reason
- someone asks the protagonist to help with a small task
- control of the key prop changes hands for a natural reason
- the protagonist is briefly left alone in the same room

Do not let important discoveries happen in a vacuum.

If the protagonist suddenly gets time to inspect a phone, room, message, or object, the script should already have given a reason why:

- that prop is now in their hand
- the other person is no longer watching directly
- the action still feels socially natural

## Evidence Object Precision Rule

Name the proof object by its actual media type.

Do not casually swap between:

- 相
- 截图
- 相簿缩图
- 影片封面
- 录屏
- 聊天记录截图

These are not interchangeable.

Use:

- `相` or `照片`
  - when the girl is looking at an original偷拍照片 in the gallery or photo list
- `相簿缩图` or `影片封面`
  - when she is seeing multiple gallery items at once
- `截图`
  - only when the story really means an image captured from another screen, interface, or device state

Hard rule:

- if the story logic is "the phone itself contains the偷拍照片", do not call the image a `截图`
- if the viewer is supposed to understand "someone took this photo", use photo language, not screenshot language

Why this matters:

- `截图` changes how viewers imagine the source
- it weakens偷拍感 if the evidence should feel like a directly taken image
- it can make the phone interaction logic feel fake

## Evidence Description Naturalness Rule

When writing the first strange image or first proof image, describe it in the order a person would feel it, not the order a camera technician would map it.

Prefer this order:

1. this is clearly inside our home
2. this is an image that should not exist
3. only then add the specific spatial clue if needed

Bad:

- `看见家里走廊对准洗手间门口的截图`
- `画面正对洗手间门口`
- `从走廊角度对准房门拍摄`

Why these fail:

- `对准` sounds like surveillance analysis, not first shock
- the information order is too mechanical
- it makes the line feel like camera setup notes instead of lived discovery

Prefer lines like:

- `看见一张拍着自家洗手间门口的怪相`
- `看见手机里有一张家里洗手间门口的偷拍相`
- `那张相一看就是家里门口拍的`

Hard rule:

- first discovery language should trigger recognition and偷拍感 first
- spatial geometry is secondary, only add enough to keep the image specific

## Scene Boundary Rule

Do not split scenes only because the proof becomes deeper.

Keep actions in the same scene when all of these remain true:

- same physical space
- same prop
- same uninterrupted handling of the prop
- same immediate pressure situation
- same motivated line of action

Example:

- uncle prepares to sleep or leaves the girl's immediate space
- he asks her to help take or charge the phone
- she sees one strange image
- while still handling the same phone in the same domestic moment, she opens it again to confirm

This can still be one scene.

Create a new scene when one of these truly changes:

- new room or tactical position
- new social pressure configuration
- action purpose changes from discovery to hiding, confrontation, escape, or help-seeking
- the protagonist must re-enter the action under a different risk structure

## Single-Function Beat Rule

Every scene should have one dominant dramatic job.
Every beat inside the scene should also have one dominant function.

Strong scene jobs:

- establish danger
- confirm suspicion
- escalate proof
- seek help
- land confrontation
- end on hook

Strong beat functions:

- proof image
- reaction
- threat presence
- reversal
- handoff into next scene

Do not stack multiple equal-priority jobs into the same beat if they can be separated more cleanly.

Do not keep multiple beats that do the same job without escalation.

If two beats both only show fear, keep the stronger one.
If two beats both only deepen proof in the same way, merge them.

## Adjacent Scene Compression Rule

If two adjacent scenes are both doing the same main dramatic job, compress them.

Examples:

- Scene A: the protagonist asks for help and gets shut down
- Scene B: the same help is still being shut down, just with one extra pressure reminder

This usually means the draft should become:

- one stronger scene where help fails and outside pressure lands before the scene ends

Do not stretch one dramatic function across two scenes unless the second scene truly adds a new layer of conflict.

Ask:

- does Scene B change the function, or only extend the mood
- if I merge these scenes, do I lose any real story information
- is the second scene a new turn, or only a slower echo of the first one

If it is only a slower echo, merge it.

## Presence Continuity Rule

If a dangerous person is physically present in the same space, do not let the script pretend they vanish unless the story gives a reason.

When writing linked beats like:

- protagonist reaction
- threat reverse shot

make sure the first beat already plants the second person in the space when useful.

That second person may appear as:

- background presence
- half body
- side-frame pressure
- off-screen voice with clear spatial relation

The point is to keep human presence and pressure logically continuous.

Default pacing:

- 8 episodes
- 45-90 seconds per episode
- 2-4 scenes for Episode 1 unless the user asks otherwise

## Episode Emotion Engine

For each episode, lock in:

- 1 core emotion
- 1 supporting emotion
- 1 ending hook

Use at least one of these per episode:

- shock point
- pain point
- payoff point

Common payoff formula:

- suppression
- reversal
- public reaction
- gain

Do not pile every emotion into the same beat. Sequence them.

## Episode 1 Opening Rules

Default to these unless the user asks for a slower opening:

- Open in crisis, not setup
- Reveal relationship pressure fast
- Establish the protagonist's immediate goal
- Introduce information asymmetry
- Include at least one reversal
- Set a larger long-term goal before the end of Episode 1
- Make the protagonist's pain point unmistakable before the first major twist

## Dialogue Voice Lock

Run this test before finalizing:

- If you hide character names, can the reader still tell who is speaking?

Different characters should differ in:

- aggression level
- vocabulary
- directness
- rhythm
- emotional control

## De-AI Rewrite Rules

Before finalizing, remove obvious AI flavor.

- Cut abstract summary language
- Cut moralizing or lecture-like phrasing
- Cut repetitive emotional labels
- Replace explanation with behavior, silence, interruption, or gesture
- Make character voices less uniform
- Shorten lines that sound over-written
- Avoid formulaic transition words used too often
- Avoid too many paragraphs with near-identical length
- Avoid consecutive sentences with the same opening pattern
- Avoid hedge-heavy language like "it seems / maybe / perhaps" unless uncertainty is dramatically necessary

Bad pattern:

- "She felt extremely shocked and did not know how to respond."

Better pattern:

- "Her fingers froze around the phone. 'Say that again.'"

## Self-Review Standard

Audit the script like a normal viewer first, then like a writer.

Viewer-first questions:

- If the user reacted "this makes no sense", would the script survive that criticism?
- Is the core setup believable enough for mass viewers to accept in one hearing?
- Is any key term unnatural for the situation, even if technically explainable?
- Is any claimed reversal actually just escalation?
- Is any reversal present only because the writer wanted a twist?
- Will viewers ask "why would it work like that?" before they feel emotion?
- Will viewers feel the protagonist's pain quickly enough?
- Is the protagonist's suffering specific, embarrassing, unfair, or expensive enough to trigger emotion?
- When the protagonist is hurt, will viewers immediately know what they want back?
- Will a viewer say "that hurts" or only "I get the plot"?
- Is the hook special enough, or does it sound like a standard-answer workplace comeback?
- Is the story sharp enough, or only technically workable?
- Is the hook hitting money, status, family, dignity, public humiliation, or another concrete pain point strongly enough?
- Will viewers be able to predict the whole shape too easily after hearing one sentence?
- Is the story's most memorable angle truly distinctive, or just familiar "he was underestimated" material?

Writer-side questions:
- Is the opening hook immediate enough?
- Does the protagonist want something concrete?
- Is the antagonist pressure clear?
- Does each scene escalate conflict?
- Are any lines too explanatory?
- Do any characters sound interchangeable?
- Is there at least one strong reversal?
- Is the cliffhanger sharp enough to pull the next episode?
- Does the script read like a shootable short drama rather than prose?
- Are paragraph lengths varied enough to avoid machine-like rhythm?
- Are transition words, hedge words, or repeated sentence openings exposing AI patterns?

If major issues appear, revise before presenting the final draft.
Do not try to "argue for" a weak premise. Fix it.
If the problem is in the premise, hook, core reversal, or story logic, restart from the beginning:

1. rewrite the premise
2. rebuild the outline
3. rewrite Episode 1
4. run self-review again

Do not apply only small local edits when the foundation is wrong.

## Negative Rule Check

Fail the draft if it contains obvious weak-pattern writing.

Treat these as red flags:

- fake reversal that is only more suffering
- sudden inheritance, hidden identity, miracle comeback, or elite connection without enough setup
- protagonist only wins because everyone else becomes stupid
- generic "everyone underestimated him" setup with no fresh angle
- public humiliation that feels copied, weightless, or interchangeable
- abstract pain with no concrete loss in money, status, family, work, dignity, or safety
- every episode-end hook using the same beat shape
- exposition disguised as dialogue
- characters explaining motive instead of showing pressure
- lines that sound like summaries instead of spoken drama
- conflict that could be solved if two people spoke one normal sentence

If any red flag appears in the premise, hook, outline, or Episode 1, revise before presenting.

## Output Format

Use this default structure:

### Hook

One upgraded logline.

### Characters

List the main cast with:

- name
- role
- outward image
- desire
- weakness
- conflict link

### Episode Outline

For Episodes 1-8, include:

- episode title
- opening hook
- core conflict
- ending cliffhanger

### Episode 1 Script

For each scene, include:

- scene number
- location
- characters present
- action
- dialogue
- emotional turn
- scene hook

### Episode-End Continuity Snapshot

Include:

- who knows what by the end of Episode 1
- where the main proof or leverage currently is
- what emotional pressure is still unresolved
- what question must carry into Episode 2
- what must not be resolved too early

### Self-Review

Keep this short. Include:

- the protagonist's main pain point and whether it is sharp enough on screen
- the main viewer-style complaint the draft could trigger
- the top logic or plausibility challenge a skeptical viewer would raise
- whether the main hook contains a real reversal or only escalation
- whether the hook feels distinctive or too standard
- what makes this story special, and if nothing makes it special, say so and rebuild it
- the top 3 problems found in the first pass
- what was revised
- why the final draft is stronger

## Tone Selection

Infer the most likely commercial tone from the prompt unless the user specifies one:

- urban romance
- school drama
- wealthy family conflict
- revenge melodrama
- hidden-identity romance
- suspense romance

If the user names a specific tone, obey it.

When genre fit is obvious, apply matching prohibitions and language rules from the genre pack.

## When Information Is Missing

Make reasonable assumptions instead of stopping.

Assume:

- modern setting
- vertical short-drama pacing
- mass-market emotional clarity

Only ask a clarifying question if the missing detail would substantially change the genre or audience.
