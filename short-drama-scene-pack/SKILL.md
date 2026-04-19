---
name: short-drama-scene-pack
description: Turn an existing short-drama script, outline, or episode draft into a shootable scene pack without changing the storyline. Use when Codex needs to bridge from scriptwriting into production planning by locking scene order, locations, characters, visible actions, emotional turns, key images, and continuity notes for later image, storyboard, or director work.
---

# Short Drama Scene Pack

Convert a locked short-drama script into a production-ready scene pack.

This skill is for scene breakdown, not story regeneration. Keep the original storyline intact and make the material easier to shoot, visualize, and continue into later stages.

Read [scene-pack-rules.md](C:\Users\anson\Desktop\writing\out\short-drama-scene-pack\references\scene-pack-rules.md) before building the pack.
Read [negative-rules.md](C:\Users\anson\Desktop\writing\out\short-drama-scene-pack\references\negative-rules.md) before finalizing the pack.

If the user also provides a character pack, use it to lock visual continuity.

## Hard Boundary

Do not change the storyline.

That means:

- do not rewrite plot
- do not add scenes that change cause and effect
- do not invent a new twist
- do not change who knows what
- do not change relationships
- do not quietly move a reveal earlier if that breaks Episode 2 continuity

You may:

- split an existing episode into clearer scene units
- sharpen scene purpose
- name visible key images
- lock emotional turn and scene hook
- add continuity notes
- point out missing production details as missing, not invented

If a scene is unclear, preserve the story and label the uncertainty.

## Main Goal

Turn script material into a stable scene-by-scene package that can be reused for:

- image prompt generation
- storyboard generation
- shot list planning
- director prompt generation
- continuity control
- production review before visual work

This skill should now support structured downstream parsing.

Write the scene pack so it can cleanly feed a JSON workspace pipeline:

- scene-level fields should stay stable and explicit
- `scene purpose`, `visible action`, `key image`, `end hook`, and `continuity notes` should be easy to parse into scene JSON
- do not bury scene-defining information inside long prose paragraphs if a fielded bullet can hold it more clearly

## Default Output

When the user gives a script or episode draft, produce:

1. Scene Pack Summary
2. Episode Scene Table
3. Detailed Scene Cards
4. Continuity Notes
5. Episode End State Snapshot
6. Negative Prompt Handoff
7. Downstream Handoff Notes

If the user asks for only one episode, only pack that episode.

## Workflow

Follow this workflow internally before answering:

1. Identify the locked storyline
2. Identify the episode boundary
3. Split into the minimum clear scene units
4. Lock scene purpose
5. Lock visible action
6. Lock emotional turn
7. Lock scene-end hook
8. Add continuity notes
9. Run negative-rule check

Do not present chain-of-thought. Only present the finished pack.

## Scene Splitting Rules

Split by actual dramatic unit, not by sentence count.

Create a new scene when one of these changes:

- location
- active character set
- dramatic objective
- power balance
- time jump that affects the beat

Do not oversplit.
Do not turn one simple beat into three fake scenes.
Do not merge two different emotional beats if they need different visuals downstream.

## No Duplicate Scene Function Rule

Do not keep adjacent scenes if they are mainly performing the same dramatic function.

Examples of duplicate scene function:

- one scene already completes `求助失败`, and the next scene only repeats `事情还是被压下去`
- one scene already lands `危险确认`, and the next scene only restates the same danger without a new turn
- one scene already puts pressure back on the protagonist, and the next scene only repeats that pressure in a slightly different container

When two neighboring scenes are both doing the same core job, prefer:

- merging them into one stronger scene
- or cutting the weaker one

Use a new scene only if it adds a genuinely new function such as:

- proof becomes clearer in a qualitatively new way
- help-seeking turns into failed protection
- private fear turns into public pressure
- internal conflict turns into external interruption

Hard rule:

- a new location corner or doorway is not enough reason by itself
- a new speaker is not enough reason by itself
- if the dominant dramatic function is unchanged, do not split

## What Each Scene Must Lock

Each scene card must clearly state:

- scene number
- location
- time feel if known
- characters present
- scene purpose
- visible action
- core conflict
- emotional turn
- key image
- end hook
- continuity notes

Prefer visible and shootable language over abstract explanation.

## Proof Object Naming Rule

Lock the evidence object with the correct media type.

Do not blur together:

- 偷拍相 / 照片
- 相簿缩图
- 影片封面
- 截图

Use precise wording in scene cards.

Examples:

- if the phone gallery contains original偷拍照片, write `偷拍相` or `照片`
- if the girl sees multiple items in album view, write `相簿缩图` or `影片封面`
- only write `截图` when the story truly means an image captured from another screen or interface

If the wrong object name would change how downstream storyboard or image generation reads the scene, treat that as a production error and correct it.

## First-Proof Wording Rule

When locking the scene's first strange image, write it as immediate recognition, not technical angle analysis.

Prefer:

- home first
- wrongness second
- exact spatial clue third

Bad:

- `家里走廊对准洗手间门口的相`
- `正对门口的画面`
- `对准洗手间门口拍摄`

Better:

- `一张拍着自家洗手间门口的怪相`
- `一张明显是家里门口偷拍的照片`
- `手机里跳出一张家里洗手间门口的偷拍相`

The scene pack should help later stages feel the beat quickly:

- `这就是我家`
- `这张相不该出现在这里`

Do not write the key image like a CCTV installation memo.

Weak:

- she feels afraid of the future

Strong:

- she freezes with the phone in hand when the hidden-recording screenshot slides across the lock screen

## Visible Action Rule

`visible action` must be physically presentable on screen.

Do not fill scene cards with writer-summary language that explains intention without showing action.

Weak:

- 她找借口把妈妈带进房间
- 她想办法避开舅父
- 她试图冷静下来

Better:

- 她一把拉住母亲进卧室，反手把门关上
- 她拿着手机站到厨房门口，背对客厅继续翻
- 她盯着手机，手指停住，半天没有把充电线插上

If the audience cannot tell what the actor is doing with body, prop, or space, the line is not yet production-ready.

## Abstract Emotion Translation Rule

Do not leave key beats in abstract emotional shorthand when they will later need storyboard, image, or performance use.

If the script says things like:

- she freezes
- she cannot believe it
- he acts normal
- the mother is scared
- tension rises

translate that into visible stageable behavior before finalizing the scene pack.

Preferred translation targets:

- hand stops before finishing an action
- shoulder, neck, or jaw suddenly locks
- eyes pin to the phone, door, or person
- breath shortens, catches, or is forced quiet
- the person first looks at the door before speaking
- the person lowers the voice instead of answering directly
- a prop is gripped tighter, hidden, pressed dark, or not handed back

Bad:

- `她整個人先卡住`
- `曉晴不敢相信`
- `李美珍很害怕`

Better:

- `她手裡的充電線停在插口前，肩膀一下僵住，眼睛釘在螢幕上`
- `她盯住母親，像等對方立刻開口處理，卻只等到一句壓低聲音的「先不要講出去」`
- `李美珍先看門，再把聲音壓低，握手機的手指節慢慢發白`

Use emotional labels only as a secondary summary after the visible behavior is already clear.

## Continuity Rule

Always protect continuation into the next episode.

Check:

- does this scene hand the right question into the next scene?
- does this episode end on the same hook already established in the script?
- does any clarification accidentally reduce suspense needed for Episode 2?

If a stronger production note would weaken continuity, keep continuity.

## Character Usage Rule

If a character pack is available:

- use the locked role and energy
- keep visual anchors stable
- respect age band and class markers
- do not blur two characters together

If no character pack is available:

- only use details explicit in the script
- label careful inferences as inferred from context

## Scene-Pack Priorities

Prioritize these in order:

1. clarity of what happens on screen
2. emotional readability
3. hook readability
4. location efficiency
5. downstream usefulness for visual tools

Do not pad with literary description.

## Output Format

Use this structure:

### Scene Pack Summary

- story title
- source material used
- episode coverage
- total scenes packed
- any missing production details

### Episode Scene Table

For each scene, give one line with:

- scene number
- location
- main conflict
- end hook

### Detailed Scene Cards

For each scene, output:

#### Scene X

- location
- time feel
- characters present
- scene purpose
- visible action
- core conflict
- emotional turn
- key image
- end hook
- continuity notes

### Continuity Notes

Include:

- character continuity locks
- prop continuity locks
- location continuity locks
- information reveal locks
- what must not be shown too clearly yet

### Episode End State Snapshot

Include:

- who knows what by episode end
- where the main proof or object is
- what relationship state changed
- what unresolved pressure carries into the next episode
- what later stages must avoid revealing too early

### Negative Prompt Handoff

List what downstream visual stages should avoid for this episode.

Cover:

- age drift
- over-glam styling
- villain-face exaggeration
- wrong home/class signals
- prop drift
- revealing later-episode facts too early
- turning subtle family pressure into loud melodrama visuals

### Downstream Handoff Notes

Include short notes for:

- image generation
- storyboard
- directing / shot listing
- optional structured field names if the user wants JSON later
- optional asset/reference slot names if the user wants to build a ref index later

When useful, explicitly distinguish:

- scene number
- actual room identity
- suggested room anchor key

Do not assume these are the same thing.

Example:

- scene number: 2
- actual room: mother bedroom
- suggested room anchor key: `bedroom_interior_anchor`

not:

- `scene 2 = scene_anchor_s2` by default

## Negative Rule Check

Fail the pack and rewrite the affected section if it does any of these:

- retells the plot without helping downstream production
- changes the order or meaning of events
- explains emotion without naming visible action
- leaves key beats in abstract emotional shorthand instead of body / prop / space behavior
- uses vague scene purpose like "build tension" without specific conflict
- loses the episode-end hook
- makes every scene card sound identical
- adds visual details that contradict the character pack or story
- quietly assumes downstream room anchors can be inferred from scene numbering alone

## Tone

Be practical, visual, and production-facing.

Do not overwrite the writer.
Do not become a novelist.
Do not create fake precision where the script is still open.
