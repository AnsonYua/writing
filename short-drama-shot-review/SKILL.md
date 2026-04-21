---
name: short-drama-shot-review
description: 審查一格一般 shot 描述，或一條已生成的單格圖片 prompt，且不改動故事線。用於檢查 planned shot 是否清楚、可理解、可交接，以及 generated prompt 是否以 image space 而不是 story-summary space 來表達。
---

# 短劇 Shot Review

當一格 shot 或一條 image prompt 需要審查時，就使用這個 skill。

## Review Modes

### Planned-shot mode

用途：審查一格一般 shot 描述是否已經可用。

輸入形狀：

- `shot_description`
- `caption`
- `audience_read` optional

可改欄位：

- `shot_description`
- `caption`
- `audience_read`

### Prompt-review mode

用途：審查一條單格圖片 prompt 是否已經可生成。

輸入形狀：

- `shot_id`
- `image_prompt`
- `caption`

可改欄位：

- `image_prompt`
- `caption`

## 核心邊界

只審當前輸入，不改故事線，不重做結構。

不要：

- 新增 plot beats
- 提前 reveal
- 重寫整個 scene
- 偷偷 merge 或 redesign 鄰近 shots
- 在 prompt-review mode 倒回去重規劃 shot 結構

## 核心檢查

### Planned-shot checks

- 這格 shot 是否單看就清楚
- `shot_description` 是否像可拍攝、可視覺化的 shot 描述，而不是抽象概括
- 畫面中心是否明確
- `audience_read` 是否準確反映觀眾第一眼會讀到的事
- 如果是 reaction shot，trigger 是否可讀
- 如果是 proof shot，proof 是否第一眼可見
- 如果下一格會繼續查看同一個 object 或 proof，這格是否已經交代角色為何無法抽離
- `caption` 是否真的有需要，而且夠短
- 如果 `caption` 用代詞，指向是否清楚
- 如果 `caption` 是內心聲音，是否像即時想法，而不是摘要

### Prompt-review checks

- prompt 是否在 image space，而不是 story-summary space
- prompt 是否從鏡頭實際看見的內容出發
- prompt 是否仍然像一張單格圖片，而不是一段正在發生的過程
- prompt 是否描述穩定可見狀態，而不是 unfolding transition
- prompt 是否有明確 first-look center
- prompt 是否避免 workflow memo、operator note、preserve memo 味道
- 如果 prompt 依賴 anchors，是否有信任 anchors，而不是重覆交代穩定外觀或穩定場景

## 專項規則

### Reaction / proof

- reaction 不可無 trigger
- proof 不可只存在於說明，必須存在於畫面
- 如果 reaction 要接 checking，當前 shot 必須保留角色與 trigger/object 的活關係

### Still image

以下類型要判定為有問題：

- `starts to`
- `suddenly`
- `is about to`
- `turns and then`
- 逐步 reveal、逐步 browsing、逐步出現的寫法

應改成一個在同一格裡已成立、可同時讀到的畫面。

### Collection / pattern readability

如果 prompt 依賴 collection、grid、重覆物件、shared source 或 pattern 才成立，就必須把可見 cues 寫清楚。

不要把意義放在推論，而不是放在畫面證據。
