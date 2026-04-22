---
name: short-drama-shot-review
description: 審查一格一般 shot 描述，或一條已生成的單格圖片 prompt，且不改動故事線。用於檢查 planned shot 是否清楚、可理解、可交接，以及 generated prompt 是否以 image space 而不是 story-summary space 來表達。
---

# 短劇 Shot Review

當一格 shot、一組相鄰 shots、或一條 image prompt 需要審查時，就使用這個 skill。

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

### Sequence-review mode

用途：審查同一 scene 內一組相鄰 planned shots 是否重複、是否應合併、或是否需要改視覺角度。

輸入形狀：

- `scene_id` optional
- `scene_number` optional
- `shots` array，每格至少包含：
  - `shot_id`
  - `shot_number`
  - `shot_description`
  - `caption`
  - `audience_read` optional

可改欄位：

- `shot_description`
- `caption`
- `audience_read`

可建議結構操作：

- `keep`
- `merge`
- `rewrite visual angle`

## 核心邊界

只審當前輸入，不改故事線。

planned-shot mode 和 prompt-review mode 不重做結構。
sequence-review mode 可以建議相鄰 shots 合併或改視覺角度，但不可新增 plot beat、提前 reveal，或把整場戲改成另一條故事線。

不要：

- 新增 plot beats
- 提前 reveal
- 重寫整個 scene
- 在單格 review mode 偷偷 merge 或 redesign 鄰近 shots
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

### Sequence-review checks

逐格先判斷每格的實際 `shot_function`。`shot_function` 不一定要出現在輸入裡，要由 `shot_description`、`caption`、`audience_read` 推斷。

檢查相鄰 shots 是否重複：

- function 是否相同，例如兩格都只是「求助落空」或兩格都只是「危險逼近」
- blocking 是否相同，例如連續都是雙人中近景、同一距離、同一站位、同一個手機
- first-look center 是否相同，例如每格第一眼都是母女站住看手機或看門
- prop 狀態是否沒有變，例如手機一直只是握在手裡，沒有亮屏、黑屏、遞出、藏起等變化
- caption meaning 是否相同，例如兩句都只是在說「我好驚 / 我望住佢 / 我唔敢出聲」
- audience_read 是否只是換字重覆上一格
- 前一格是否只是 reaction-only，下一格才出現真正 decision / turn，例如「手震臉白」之後才「望門、壓低聲、叫她不要講」
- 前一格是否只是 first-proof，下一格只是同一層級 confirmation，例如「見到一張怪相」之後才「再滑先知不止一張」

判斷方式：

- `keep`：相鄰 shot 有新 function、新可見動作，或令證據、權力關係、危險距離、結尾 hook 更清楚
- `merge`：兩格只差在更多恐懼、更多沉默、更多凝望、同一 prop / 同一 blocking 的延長、前一格只是下一格 decision 的反應前奏，或 first-proof 只是 confirmation 的前置
- `rewrite visual angle`：兩格 function 都值得保留，但畫面太似；應改其中一格的主體、鏡頭距離、first-look center、prop 狀態、空間壓力或 action source

sequence-review mode 的輸出應直接按 shot 或 shot pair 給 verdict：

```md
- `S2_SH3` + `S2_SH4`: merge
  - reason: 兩格都在講女兒等母親保護但母親避開，blocking 和 audience_read 太接近。
  - safer direction: 保留較強一格，或把其中一格改成女兒手勢收住 / 單人近景。

- `S2_SH5` + `S2_SH6`: rewrite visual angle
  - reason: 兩格都以母女望房門收束，但 `S2_SH6` 的黑屏手機有 key image 價值。
  - safer direction: `S2_SH5` 改成門縫或門把壓力，`S2_SH6` 改成黑屏手機特寫。

- `S2_SH2` + `S2_SH3`: merge
  - reason: `S2_SH2` 只證明母親看懂後手震臉白，`S2_SH3` 才是她看懂後選擇先望門和壓事的真正 turn。
  - safer direction: 合併成「母親睇到手震，但第一眼望嘅唔係女兒，係房門」。

- `S1_SH2` + `S1_SH3`: merge
  - reason: `S1_SH2` 是第一眼撞見怪相，`S1_SH3` 只是同一部手機上的連續確認；若第二格沒有把「proof 指向曉晴本人」或「她冒險查證」做成第一眼中心，兩格讀感會太近。
  - safer direction: 合併成「充電線停住、單張怪相擊中她；等舅父背影離開，她把手機收近打開相簿，縮圖顯示不止一張且有幾張指向她」。
```

## 專項規則

### Reaction / proof

- reaction 不可無 trigger
- proof 不可只存在於說明，必須存在於畫面
- 如果 reaction 要接 checking，當前 shot 必須保留角色與 trigger/object 的活關係
- 如果 reaction 後面緊接 decision / turn，先問 reaction 是否只是替 decision 鋪路；若是，優先 merge，不要獨立保留
- 如果 first-proof 後面緊接 checking / confirmation，先問 checking 是否揭示新層級或新風險；若只是同一 proof 的延長，優先 merge

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
