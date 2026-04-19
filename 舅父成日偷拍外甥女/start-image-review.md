# 《舅父成日偷拍外甥女》Storyboard 二審

## Review Summary

- material reviewed:
  - [storyboard.json](C:/Users/anson/Desktop/writing/out/舅父成日偷拍外甥女/storyboard.json)
  - [storyboard.md](C:/Users/anson/Desktop/writing/out/舅父成日偷拍外甥女/storyboard.md)
- overall clarity: strong
- overall continuity safety: medium
- overall image-text fit: medium-strong
- biggest risk:
  - 少數兩角色關係動作格，第二人物雖然已被寫進 prompt，但 reference 規劃仍未完全跟上；另外有一格 prompt 仍帶少量 meta 語言，不夠純 drawable

## Top Problems

- serious: `S2_SH1` 是明確的 relationship-action shot，但周曉晴仍未升級成 reference support
- medium: `S1_SH1` 是 handoff shot，陳國強作為 acting subject 的 identity 還不夠硬
- medium: `S1_SH5` 的 prompt 已補李美珍 reference，但句子裡仍有 `generic 婦人` 這種 meta 語言

## Prompt-by-Prompt Review

### `S1_SH1`

- verdict: medium
- what a stranger can understand immediately:
  - 晚飯後舅父把手機交給曉晴去充電
- framing consistency: pass
- continuity risk:
  - handoff beat 清楚，但陳國強是這格的 acting subject 之一，現在 workflow 只有 `scene_anchor_s1 + 周曉晴 ref`，叔輩 identity 仍偏弱
- reference workflow fit:
  - warning
- comfy prompt fit:
  - medium
- dialogue fit:
  - pass
- issue:
  - 這格不只是「後景有一個男人」，而是「陳國強把手機交出去」這個動作本身成立場景因果。若模型把右側人畫成 generic 中年男人，故事仍勉強通，但威脅來源的太正常外皮會變弱。
- safe fix:
  - 若流程支援三參考，升級成 `scene_anchor_s1 + character_ref_zhou_xiaoqing + character_ref_chen_guoqiang`
  - 若只支援兩張圖，至少在 workflow note 裡明寫這是一個 `main subject + acting subject` 的 handoff fallback，而不是普通 pressure presence

### `S1_SH2`

- verdict: strong
- what a stranger can understand immediately:
  - 曉晴在幫人充電時，看到手機裡一張來自自家空間的怪相
- framing consistency: pass
- continuity risk:
  - low
- reference workflow fit:
  - pass
- comfy prompt fit:
  - strong
- dialogue fit:
  - strong
- issue:
  - 無明顯大問題
- safe fix:
  - 保持

### `S1_SH3`

- verdict: strong
- what a stranger can understand immediately:
  - 曉晴被畫面嚇停，而危險來源仍在同一空間
- framing consistency: pass
- continuity risk:
  - medium-low
- reference workflow fit:
  - pass
- comfy prompt fit:
  - strong
- dialogue fit:
  - strong
- issue:
  - 陳國強作為 pressure presence 的描述已比之前清楚，但如果後續生成常把他畫成不同年齡層，可考慮補 `character_ref_chen_guoqiang`
- safe fix:
  - 先保持；如果實際生成漂，就升級到三參考

### `S1_SH4`

- verdict: strong
- what a stranger can understand immediately:
  - 曉晴偷滑相簿，發現不是一張怪相，而是一串偷拍內容
- framing consistency: pass
- continuity risk:
  - low
- reference workflow fit:
  - pass
- comfy prompt fit:
  - strong
- dialogue fit:
  - strong
- issue:
  - 無明顯大問題
- safe fix:
  - 保持

### `S1_SH5`

- verdict: medium
- what a stranger can understand immediately:
  - 曉晴確認出事後，立刻把母親從客廳帶走
- framing consistency: pass
- continuity risk:
  - medium
- reference workflow fit:
  - warning
- comfy prompt fit:
  - medium
- dialogue fit:
  - pass
- issue:
  - 這格已正確判斷成 relationship-action shot，也已補 `character_ref_li_meizhen`。但 `comfy_image_prompt` 仍寫了 `李美珍不是 generic 婦人`，這是 meta 語言，不是 drawable instruction。另一路徑上，這格其實理想是三參考，否則客廳空間只靠文字承接仍有風險。
- safe fix:
  - 把 `不是 generic 婦人` 改成正面 drawable traits，例如：
    - `李美珍保持中年勞累母親的臉型、簡單髮型、樸素家居服和被突然拉動時跟上的身體感`
  - 保留三參考理想方案說明，不要再把 scene anchor 降級成默認可省略

### `S2_SH1`

- verdict: serious
- what a stranger can understand immediately:
  - 曉晴把手機塞給母親，叫她自己看
- framing consistency: pass
- continuity risk:
  - high
- reference workflow fit:
  - fail
- comfy prompt fit:
  - medium
- dialogue fit:
  - strong
- issue:
  - 這格和 `S1_SH5` 同類，都是 relationship-action shot。現在 workflow 只有 `scene_anchor_s2 + character_ref_li_meizhen`，周曉晴雖然只出半張側臉和手，但她是「把證據塞給母親」的 action source，換成 generic 少女會削弱母女求助關係。
- safe fix:
  - 理想升級成三參考：`scene_anchor_s2 + character_ref_li_meizhen + character_ref_zhou_xiaoqing`
  - 若流程只支援兩張圖，要至少明寫 fallback：優先保留兩個角色 identity，房間方向用 prompt 承接

### `S2_SH2`

- verdict: strong
- what a stranger can understand immediately:
  - 母親看懂了手機內容，而且被嚇住
- framing consistency: pass
- continuity risk:
  - low
- reference workflow fit:
  - pass
- comfy prompt fit:
  - strong
- dialogue fit:
  - strong
- issue:
  - 無明顯大問題
- safe fix:
  - 保持

### `S2_SH3`

- verdict: medium-strong
- what a stranger can understand immediately:
  - 母親不是替她出頭，而是先壓低聲音叫她不要講出去
- framing consistency: pass
- continuity risk:
  - medium
- reference workflow fit:
  - warning
- comfy prompt fit:
  - strong
- dialogue fit:
  - strong
- issue:
  - 周曉晴只作為接收這句話的前景半臉存在，現在仍可接受；但如果實際生成時這個前景半臉總變成 generic girl，就會削弱「這句話是對女兒說」的關係力度。
- safe fix:
  - 先保持
  - 若實際生成不穩，升級成三參考

### `S2_SH4`

- verdict: strong
- what a stranger can understand immediately:
  - 手機被按黑藏起來，門外那個人就在要回它
- framing consistency: pass
- continuity risk:
  - low
- reference workflow fit:
  - pass
- comfy prompt fit:
  - strong
- dialogue fit:
  - strong
- issue:
  - 無明顯大問題
- safe fix:
  - 保持

## Safe Rewrite

### `S1_SH5` revised `comfyImagePrompt`

- original intent:
  - 曉晴把母親直接帶離客廳，切進下一場
- revised `comfyImagePrompt`:
  - 圖1保持周曉晴未成年高中女生的臉型、短馬尾、學生感和偏收但突然變直接的姿態，並保持同一部黑色手機還握在她手裡。圖2保持李美珍中年勞累母親的臉型、簡單髮型、樸素家居服和被突然拉動時跟上的身體感。改成客廳往房門方向的中景靜態畫面，晚飯後餐桌和房門方向仍然清楚，周曉晴一手攥著手機，一手直接扯住李美珍手腕往房裡走。李美珍以被拉動的半身、跟上的腳步和轉過來的肩身出現在畫面左側。畫面重點是她直接把母親帶離客廳。
- why this is safer:
  - 去掉 meta 語言，改成純 drawable 描述

### `S2_SH1` revised reference plan

- original intent:
  - 曉晴把證據直接塞給母親
- safer reference plan:
  - `scene_anchor_s2.png`
  - `character_ref_li_meizhen.png`
  - `character_ref_zhou_xiaoqing.png`
- why this is safer:
  - 這格不是 generic 少女把手機遞給 generic 母親，而是女兒向母親求助的關係啟動點
