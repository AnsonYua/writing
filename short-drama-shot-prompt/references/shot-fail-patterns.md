# Shot Fail Patterns

Use this file when a prompt sounds correct but still feels weak.

## Common Failures

### Flat proof prompt

Weak:

- 她看著手機裡的內容，表情震驚。

Why it fails:

- the evidence is not visually specified
- the image center is split
- the prompt explains emotion but not proof

### Flat reaction prompt

Weak:

- 她站在原地，神情僵住。

Why it fails:

- no visible trigger
- no next-action continuity
- could belong to any scene

### Flat chemistry prompt

Weak:

- 兩人站在走廊裡互相看著對方。

Why it fails:

- no charged spacing
- no asymmetry
- no reason this frame matters more than a generic two-shot

### Pretty but empty prompt

Weak:

- 光線漂亮的房間裡，人物站在窗邊。

Why it fails:

- atmosphere replaces payload
- no proof, charge, pressure, or hook

## Recovery Questions

Before locking a prompt, ask:

- what should the viewer see first
- what exactly is the image selling
- what visible relation makes this frame specific
- would this still work when small
- did I accidentally flatten a charged panel into neutral description
