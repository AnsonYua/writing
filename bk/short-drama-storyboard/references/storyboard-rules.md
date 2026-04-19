# Storyboard Rules

Use this file when breaking scene packs into shots.

## Prefer These

- 3-6 shots for a short scene unless complexity demands more
- one reveal shot
- one reaction shot
- one hook-ending shot
- simple framing language
- concrete visual carry-over from shot to shot
- shot descriptions that tell downstream generation what must still be on screen

## Avoid These

- overcoverage
- repeating the same close-up five times
- camera moves with no dramatic reason
- turning still tension scenes into action coverage

## Useful Framing Labels

- wide
- medium
- close-up
- insert
- over-shoulder
- doorway frame

## Hook Logic

- first hook: what grabs the eye
- middle proof: what confirms the danger
- ending hook: what keeps the next click alive
- bridge logic: each middle shot should inherit something visible from the previous shot and prepare one visible change for the next shot

## Per-Shot Minimum

Every shot should make these answerable:

- what exactly is visible right now
- how the camera is placed and what it is doing
- which recurring character identity the downstream prompt should lock to
- what detail must still match the previous shot
- what new detail prepares the next shot
- what should not accidentally disappear between shots
- whether this shot really needs its own standalone still image
- what the starting still image should look like before any motion starts

## Camera Description Rule

Use short practical camera language such as:

- eye-level locked-off
- slight handheld pressure
- slow push-in
- over-shoulder from behind subject
- static insert

Do not describe the camera in vague poetic terms.

## Start Image Prompt Output Rule

Every shot should have a Chinese `startImagePrompt` that:

- is optimized for storyboard still generation
- freezes the best connected frame for that shot
- keeps character identity and prop continuity stable
- preserves room geography and eyeline logic
- helps the next shot feel like it comes from the same continuous moment

Good `startImagePrompt` traits:

- names the frozen moment clearly
- keeps the same phone / door / table / sofa / bedroom orientation when needed
- favors stable body pose over motion wording
- describes what must already be in frame before the next beat happens
- makes the frame picturable even for a reader who has not seen the script
- names concrete image anchors such as hand position, table edge, lamp, doorway, bed, sofa, corridor, screen area

Use this mental test:

- if the prompt were given alone to an illustrator, could they sketch a first-pass frame without asking where things are

If not, it is too vague.

Do not write `startImagePrompt` like a generic scene summary.

Bad:

- a dangerous clue appears during an ordinary family moment

Better:

- near phone close-up at the dining table, the girl's right hand has just taken a black phone while her left hand still holds a white charging cable, the bright screen shows the home's narrow corridor facing the bathroom door, warm dinner light and uncollected bowls remain blurred behind

## Video Prompt Output Rule

Every shot should have a Chinese `videoPrompt` that:

- reads like a real usable image-generation prompt
- reflects the shot's dramatic function
- keeps continuity with nearby shots
- emphasizes what must be seen in this frame

Do not build `videoPrompt` by mechanically concatenating metadata fields.

Interpret first, then write.

## Production Type Logic

- `master`: use for the key image, strongest proof beat, strongest reaction beat, or a new scene-defining setup
- `derived`: use when the shot is basically the same moment as a nearby master with a small angle or pose change
- `insert`: use for phone screens, hands, props, doors, and other detail beats
- `video-only`: use when the shot can be covered by reframing, motion, or a light variant of an existing still

Do not default every shot to a full standalone still.

## Good Negative Prompt Handoff Topics

- do not overexpose the proof object before the intended reveal shot
- do not switch the emotional center away from the protagonist
- do not glamorize fear scenes
- do not flatten subtle pressure into generic yelling coverage
