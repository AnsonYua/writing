---
name: short-drama-director-pack
description: Assemble a final director-ready pack from a short-drama script, character pack, scene pack, storyboard, and image prompts without changing the storyline. Use when Codex needs to merge the upstream writing and planning assets into one practical production handoff.
---

# Short Drama Director Pack

Assemble the final production-facing pack for a short-drama episode.

This skill is the last bridge before generation or shooting. Use it after the upstream assets already exist.

Read [director-pack-rules.md](C:\Users\anson\Desktop\writing\out\short-drama-director-pack\references\director-pack-rules.md) before assembling.
Read [negative-rules.md](C:\Users\anson\Desktop\writing\out\short-drama-director-pack\references\negative-rules.md) before finalizing.

## Hard Boundary

Do not change the storyline.

That means:

- do not rewrite plot
- do not alter scene order unless the user explicitly asks
- do not add new reveals
- do not add actor blocking that changes scene meaning

This skill is for assembly and handoff, not rewriting.

## Main Goal

Merge the upstream assets into one pack that tells the next stage:

- what the episode is about
- how characters must stay consistent
- what each scene must communicate
- what the key images and shots are
- what the hook delivery is

## Default Output

When the user gives the needed upstream files, produce:

1. Director Pack Summary
2. Episode Intent
3. Character Execution Notes
4. Scene Execution Grid
5. Hook Priority Notes
6. Global Negative Prompt Strategy
7. Final Continuity Risks

## Workflow

1. Read script
2. Read character pack
3. Read scene pack
4. Read storyboard if available
5. Read image prompts if available
6. Merge only the needed production facts
7. Remove duplicated wording
8. Run negative-rule check

## Assembly Rule

Prefer merged clarity over file-by-file repetition.

Bad:

- repeating the same character description in four sections

Good:

- one character execution note plus scene references where it matters

## Output Format

### Director Pack Summary

- story title
- episode covered
- source files used
- missing dependencies if any

### Episode Intent

- opening hook goal
- central emotional pain
- episode-end hook goal
- what the viewer should feel by the end

### Character Execution Notes

For each key character:

- visual lock
- performance lock
- what must not drift

### Scene Execution Grid

For each scene:

- scene number
- dramatic job
- must-have image
- must-have shot or framing
- key prop
- key performance note
- continuity caution

### Hook Priority Notes

Include:

- first 3-second hook
- proof beat
- strongest emotional beat
- cliffhanger beat

### Global Negative Prompt Strategy

Summarize what all downstream image/video steps should avoid.

Include:

- character drift
- age drift
- wrong prop or location class signal
- over-stylization against the story tone
- accidental early reveal of later facts
- generic villain framing that ruins false-normality pressure
- glamour or sexualization problems
- collage / text / watermark / malformed anatomy issues if image generation is involved

### Final Continuity Risks

List the top risks before generation or shooting.

## Negative Rule Check

Fail the pack and rewrite the affected section if it:

- repeats upstream files without adding handoff value
- drops an important continuity warning
- hides the central proof object
- turns performance notes into new plot
- over-specifies missing details as if they were canon
- omits a usable negative-prompt strategy for downstream teams

## Tone

Be concise, practical, and ready for production.

Do not write for readers. Write for the next operator.
