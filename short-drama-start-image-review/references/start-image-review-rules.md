# Start Image Review Rules

Use this file when reviewing `startImagePrompt` quality.

## What A Good Start Image Prompt Does

- freezes one precise visual moment
- tells you the subject immediately
- keeps room geography understandable
- names the key prop or screen state when relevant
- preserves character age, look, costume, and emotional energy
- bridges naturally from previous shot to next shot
- gives enough composition detail that a stranger can imagine the frame layout

## What It Should Not Do

- narrate time passing like a video prompt
- describe three actions happening in sequence
- rely on abstract mood words instead of visible details
- assume the reader already knows the whole plot
- swap room orientation casually
- forget which hand holds the phone or where the door is if those matter for continuity
- explain the function of the shot without describing what the frame looks like
- call something a phone close-up, insert, or tight close-up while stuffing in more body and room information than that framing can realistically hold

## Stranger Read Test

A stranger reading the prompt should still be able to imagine:

- the frame composition
- the emotional beat
- the key object
- the likely immediate context
- where the key object is in relation to the subject
- what sits in foreground versus background

If not, the prompt is too inside-baseball and needs revision.

## Framing Consistency Test

The prompt must respect the shot size it claims.

Examples:

- if it is a phone insert or phone close-up, the phone should dominate the frame and only a small amount of hand / body / background information should remain
- if it needs seated posture, both hands, table edge, and room context, it is probably a near shot or medium close-up, not a phone insert
- if it needs both door geography and two people, it is probably not a tight close-up

If the framing word and the described visual information cannot coexist naturally, mark it as a review failure.

## Continuity Review Lens

Check:

- same phone, same clothing, same hair, same room
- same side of door / bed / table / sofa when that spatial logic matters
- same screen state if the previous shot handed off a specific image
- same emotional beat level unless the shot is supposed to escalate

## Safe Fix Pattern

When a prompt is weak, improve it by adding:

- clearer subject placement
- clearer prop state
- clearer room anchor
- clearer frozen emotional read
- clearer carry-over from previous shot
- clearer setup for next shot
- one or two concrete foreground/background anchors
- visible objects instead of summary words like "ordinary feeling" or "danger"
- a framing description that actually fits the amount of visible information

Do not improve it by inventing new plot facts.

## Strong Prompt Signals

- "still holding the same charging phone"
- "standing half-hidden at the kitchen doorway with the living room behind her"
- "mother still gripping the phone, daughter facing her from one step away"
- "same bedroom door in frame, uncle still outside"

## Weak Prompt Signals

- "a tense domestic moment"
- "she feels uneasy"
- "something dangerous is happening"
- "a suspicious atmosphere"
- "normal life surface with danger underneath"
- "daily feeling still there"
- "near phone close-up" followed by a full seated-body description
- "tight close-up" followed by doorway, sofa, table, and second-character geography all at once

If the reader cannot see it, the prompt is not ready.
