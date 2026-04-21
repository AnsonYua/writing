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
- If the prompt requires two or more people, the image must show the required people as readable figures. A cropped hand, shoulder, or offscreen implication does not count unless the intended shot is explicitly POV, hidden-view, or partial-reveal.
- In multi-person relationship shots, props must not replace the relationship. If a phone, document, bed, door, mirror, or table makes one person disappear, the composition has failed even if the prop looks correct.
- Portrait / vertical frames have limited horizontal capacity. If the image needs two readable people, do not also require a full doorway, foreground furniture, a readable prop, detailed room geography, and precise gaze logic. Pick the two-person relation first, then reduce the scene to one simple background cue.
- The action should not be completed too early.
- The frame should leave a motion runway for the `video_prompt`.
- Space relationships should be stable: foreground/background, left/right, near/far, entrance, table edge, wall, window, seat, or path.
- Sound, dialogue, or offscreen events should become visible reactions, such as turning, stopping, looking toward a direction, gripping an object, or holding still.
- Dialogue-like actions such as whispering, asking, shouting, or speaking are not reliable video motion instructions. Review suggestions should convert them into visible body behavior: leaning closer, lips barely moving, gaze fixed on the other person, the other person avoiding eye contact, or both characters freezing.
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
9. If the prompt asks for a relationship, are all required people actually visible and placed in a readable relation?
10. If the image failed, would adding more detail fix it, or should the prompt be simplified into a clearer layout?

## Acceptance Standard

Accept only when the image is readable as a first frame and can naturally lead
into motion. Reject or request a prompt rewrite when the image is pretty but
lacks a clear paused moment, has no motion runway, has illogical gaze or hand
contact, shows impossible camera information, completes the action too early,
or mixes too many focal points.

## Review Output

Return the review in a structure the retry loop can use:

- `accepted`: true only when the image can work as the video first frame.
- `score`: overall usefulness as a start image, 1-10.
- `prompt_fit_score`: whether the image matches the requested first-frame content, 1-10.
- `start_image_quality_score`: whether the image is visually stable enough for image-to-video, 1-10.
- `reason`: short diagnosis using visible failures, not story explanation.
- `improved_start_image_prompt`: if rejected, a compact implementation-ready rewrite; if accepted, leave empty or only suggest a tiny optional refinement.

When rejected, the `reason` should name the root failure first. Examples: missing required person, wrong first-eye center, completed action too early, gaze target wrong, hand/object contact unclear, prop content impossible from camera angle, scene drift, or over-cropped vertical composition.

## Prompt Implementation Suggestions

When rejecting an image, the review should not only describe what is wrong. It should suggest how to implement the next prompt in a short, usable structure.

The suggested rewrite should fix the root visual failure first:

- Missing required person: start with the people count and layout.
- Wrong focus: name the one first-eye center and demote everything else.
- Completed action: reset the frame to a paused pre-action state.
- Gaze problem: state the visible gaze target.
- Hand/object problem: state who holds the object, which hand if needed, and where the contact point is.
- Scene drift: name only the few stable space anchors needed for this shot.
- Repeated same failure after two attempts: stop adding clauses. Simplify the layout and add one targeted negative constraint for the repeated failure.

Use compact structure instead of accumulating detail:

```text
shot size + location + character A position + character B position + core prop state + gaze/distance + unfinished motion runway
```

For a two-person shot, a useful implementation suggestion should look like:

```text
Use a medium shot. Put character A on the left and character B on the right, both visible from face or upper body. Keep the prop small in character A's hand. Make both characters look toward each other or toward the same pressure point. Leave the action paused before the handoff / confrontation / turn.
```

If the previous attempts became longer but did not fix the image, explicitly recommend shortening the prompt to 3-5 direct sentences. Do not paste the whole previous improved prompt and keep adding clauses. Extract the failure reason, then rewrite the visual layout.

For repeated missing-person or over-crop failures, recommend this order:

1. Medium shot or medium close-up, not close-up.
2. Required people visible first.
3. One relation cue: gaze, distance, hand contact, or shared pressure point.
4. One prop state if needed.
5. One background anchor only.
6. Targeted negative prompt, such as `no missing second character, no single-person crop, no only hands visible, no cropped face`.

Suggested `improved_start_image_prompt` should be implementation-ready:

- Say what to keep from references, if references exist.
- Say what the new first frame should show.
- Use visible nouns and positions, not story explanation.
- If references exist, keep the image reference bound to the character in the rewrite. Prefer `畫面左側圖2的女孩` and `畫面右側圖3的中年女性` over generic phrases like `畫面左側的女孩` or `畫面右側的中年女性`.
- Do not include internal labels such as `first frame`, `two-person first frame`, `use a medium two-person first frame`, `改成近距離雙人第一幀`, `使用中景雙人第一幀`, or `生成一張...`.
- Start the rewritten prompt with the visible composition itself, such as `Bedroom medium shot, character A on the left...` or `臥室中景，角色A在畫面左側...`.
- Avoid generic phrases such as `more dramatic`, `more tense`, `keep consistent`, or `same as before`.
- Add a negative constraint only for the specific likely failure, such as `avoid cropping out the second character`, `avoid characters looking at camera`, or `avoid turning the phone screen into the whole background`.
