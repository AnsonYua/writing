---
name: general-start-image-review
description: General review rules for judging whether an image works as a video start_image / first frame. Use for image-to-video prompt review across stories, not for one specific plot.
---

# General Start Image Review

Use this skill when reviewing whether a generated image is a good `start_image`
for video generation.

A good `start_image` is not just a pretty still image. It is the first frame of
a video: a clear paused moment that can naturally continue into motion.

Core rule:

`good start_image = single focus + visible image logic + reasonable gaze + physical logic + clear space + unfinished action + natural video continuation`

## General Rules

- The image must be a video first frame, not just an attractive picture.
- The image should show one clear paused moment.
- The image should have one first-eye center.
- Everything important should be visible, not abstract.
- Character gaze must have a reason; characters should not default to looking at camera.
- Character body direction should fit the action, attention, or pressure in the frame.
- Props should have one clear visible state: outside appearance, content, screen, reflection, or simple held object.
- Camera angle must make the visible information possible.
- Hand/object contact and physical support must be clear.
- Multi-person scenes should simplify stance, distance, gaze, and the main contact point.
- The action should not be completed too early.
- The frame should leave a motion runway for the `video_prompt`.
- Space relationships should be stable: foreground/background, left/right, near/far, entrance, table edge, wall, window, seat, or path.
- Sound, dialogue, or offscreen events should become visible reactions, such as turning, stopping, looking toward a direction, gripping an object, or holding still.
- The image should not include the next shot, the full process, or too much background explanation.
- Negative constraints should be added when needed: no camera staring, no floating object, no wrong hand logic, no screen content leaking into the background, no completed action.

## Review Questions

Ask these before accepting:

1. What does the viewer see first?
2. Is there only one main visual purpose?
3. Where should each character look, and is that gaze natural?
4. Is the object showing its outside, its content, or only its held state?
5. Are hands, body positions, contact points, and object support physically logical?
6. Has the image already completed the action that the video should perform?
7. Can the `video_prompt` naturally begin from this exact frame?
8. Are too many people, props, background details, or emotion signals competing for focus?

## Acceptance Standard

Accept only when the image is readable as a first frame and can naturally lead
into motion. Reject or request a prompt rewrite when the image is pretty but
lacks a clear paused moment, has no motion runway, has illogical gaze or hand
contact, shows impossible camera information, completes the action too early,
or mixes too many focal points.
