---
name: short-drama-reference-linker
description: 讀取短劇 `output_prompt.json` 與 `角色包.md`，先輸出 `anchor_material_pack.json`，再將整份 shot array 轉成 reference-aware 起始幀 prompt 並輸出 `output_linked_prompt.json`；不改動故事線。
---

# 短劇 Reference Linker

這個 skill 是檔案型流程。必要輸入是同一個短劇專案裡的 `output/output_prompt.json` 與 `角色包.md`。`output_prompt.json` 內容是一整份 shot array；`角色包.md` 是角色 anchor 的權威來源。它只處理整份 shot array，不處理單格 shot。

流程會先分析全片需要固定的角色和場景，輸出獨立檔案 `anchor_material_pack.json`，再逐格改寫成 reference-aware 的 `start_image_prompt`，輸出 `output_linked_prompt.json`。它不負責規劃分鏡，不負責重寫劇情，也不取代 start-image review。

## 核心目標

把「整份已成立的短劇 shot array」改成下游圖片生成與圖生片流程可用的 reference-aware prompt。

它必須回答：

- 哪些角色、場景需要先做 anchor reference。
- 每個 anchor object 的生成 prompt 是甚麼。
- 每格應該使用哪些 reference image。
- 每張 reference image 在該格裡負責保留甚麼。
- 每格 `start_image_prompt` 作為影片首幀 reference image 時，`video_prompt` 應如何承接。

## 邊界

不可改動：

- 改 shot 數量、順序或 scene 歸屬
- 重新設計分鏡或改寫劇情事件
- 移動 reveal、proof、情緒 beat 或 cliffhanger
- 新增輸入裡不存在的角色、場景或故事事實

只可以做：

- 分析需要被固定的角色和場景
- 生成 anchor prompt
- 為每格分配 reference slots
- 把每格 `start_image_prompt` 改成 reference-aware 版本

`caption` 必須原樣保留。`start_image_prompt` 是後續圖生片流程的首幀 reference image prompt；`video_prompt` 必須從這個首幀狀態開始，不可另起一個畫面。`video_prompt` 只在起始狀態與新版 `start_image_prompt` 不一致、或原句不利於圖生片理解時小修。

## 輸入格式

必要輸入：

- 一個 `<project>/output/output_prompt.json` 檔案路徑。檔案內容必須是一整份 shot array，不包外層 metadata 物件。
- 同一個短劇專案的 `角色包.md` 檔案路徑。角色 anchor 必須優先從這份檔案抽取，不可只靠 shot prompt 猜角色外觀。

`output_prompt.json` 必須位於短劇專案的 `output` 資料夾；`角色包.md` 必須位於同一個短劇專案根資料夾。

每格必要欄位：

- `scene_id`
- `scene_number`
- `shot_id`
- `shot_number`
- `start_image_prompt`
- `video_prompt`
- `caption`

## 輸出路徑

固定產生兩個檔案，但位置不同：

- `anchor_material_pack.json`：產生在 `角色包.md` 所在的短劇專案根資料夾。
- `output_linked_prompt.json`：產生在 `output_prompt.json` 所在的 output 資料夾。

路徑關係：

```text
<project>/anchor_material_pack.json
<project>/output/output_linked_prompt.json
```

## 輸出格式

必須輸出兩個 JSON 檔案。

### `anchor_material_pack.json`

`anchor_material_pack.json` 必須是一個 JSON 物件，包含：

```json
{
  "character_anchors": [],
  "scene_anchors": []
}
```

### `output_linked_prompt.json`

`output_linked_prompt.json` 必須是一個 JSON 物件，包含：

```json
{
  "anchor_material_pack_path": "../anchor_material_pack.json",
  "shots": []
}
```

不要在 `output_linked_prompt.json` 重複塞完整 `anchor_material_pack`；只保留 `anchor_material_pack_path`，讓下游知道 anchor 檔案位置。

不要覆蓋原本的 `output_prompt.json` 或 `角色包.md`。不要修改 `output.json`、`output_vdo.json` 或其他 story output。

### `character_anchors`

每個角色 anchor：

```json
{
  "anchor_id": "character_ref_main_character",
  "name": "主角",
  "priority": "primary",
  "anchor_prompt": "依照角色包生成主角 reference image，鎖定年齡感、臉型氣質、髮型、服裝方向、姿態和表情基調，避免角色包列明的錯誤方向。",
  "negative_prompt_note": "避免角色包禁止的年齡漂移、氣質漂移和誇張表演；不要自行加入角色包沒有提供的固定服裝款式、顏色或飾物。"
}
```

角色 anchor 必須優先使用 `角色包.md` 的 `core appearance`、`visual anchors`、`clothing system`、`continuity locks` 和 `quick prompt version`。`anchor_prompt` 是用來生成角色 reference image，可以承接角色包裡的服裝系統，但不可硬造角色包沒有提供的固定款式、顏色或飾物。如果 `角色包.md` 沒有寫死具體五官，不要硬造不可逆 canon，只用年齡感、輪廓、髮型、氣質和禁忌方向鎖定。

角色 anchor prompt 是「生成 reference image」用；逐格 `start_image_prompt` 是「使用已生成 reference image」用。兩者服裝規則必須分開：角色 anchor 可以使用 `角色包.md` 的服裝系統；逐格 `start_image_prompt` 只能寫 `圖中服裝` 或 reference image 中可見服裝，不要在逐格 prompt 新增款式、顏色或飾物。

### `scene_anchors`

每個場景 anchor：

```json
{
  "anchor_id": "scene_anchor_living_room",
  "scene_name": "主要客廳場景",
  "used_by_scene_ids": ["SC1"],
  "anchor_prompt": "依照 shot array 鎖定同一個主要客廳空間、核心家具位置和室內光線，生活感真實，不讓空間在後續 shots 中漂移。",
  "continuity_notes": "主要家具、空間格局和光線是後續同場景 shots 的主要空間錨點。"
}
```

場景 anchor 從 `output_prompt.json` 的 repeated location、主要家具、燈光和主要空間壓力推斷。`anchor_prompt` 要固定空間類型、空間格局、光線和不可漂移的場景特徵。只有當房門、走廊、入口或方向關係是該 scene 的壓力中心，或多格 shot 明確依賴該方向關係時，才把它寫成場景 anchor；普通場景不要額外加入 shot 沒有必要強調的方向描述，例如通往某處的方向。

### `shots`

每格 shot 包含：

```json
{
  "scene_id": "SC1",
  "scene_number": 1,
  "shot_id": "SC1_SH1",
  "shot_number": 1,
  "start_image_prompt": "...",
  "negative_prompt_note": "...",
  "video_prompt": "...",
  "caption": "...",
  "reference_assignment": [],
  "consistency_note": ""
}
```

保留原有識別欄位和順序。`caption` 原樣複製。

## Anchor 分析規則

先讀 `角色包.md`，建立角色 anchor 候選；再讀完整份 shot array，判斷哪些角色和場景需要 anchor。

優先 anchor：

- 多格反覆出現的主要角色
- 會被不同角度拍到的關鍵場景
- 會造成 continuity 誤讀的主要家具、場景光線，以及作為壓力中心的房門或方向關係

不要 anchor：

- 一次性背景物件
- 道具或 proof object
- 不影響故事讀感的裝飾
- 只在 caption 裡提及、畫面不可見的抽象資訊
- 可用 prompt 弱承接的普通小物件

每個 anchor 的 `anchor_id` 要穩定、語義清楚、可機器讀取。建議格式：

- `character_ref_<romanized_name>`
- `scene_anchor_<location>`

`anchor_id` 只放在 JSON 欄位裡，不要直接寫進自然語言 prompt。

## Reference 選擇規則

每格 reference 結構只允許以下兩種：

- `1 scene + 1 character`
- `1 scene + 2 characters`

不可使用 `1 scene + 1 character + 1 prop`、`prop + character + scene` 或只有道具沒有場景的 reference 結構。道具可以在 `start_image_prompt` 裡描述，但不建立 anchor，也不進入逐格 `reference_assignment`。

沒有 prop anchor 時，道具描述只寫可畫的當格狀態，例如 `黑色手機`、`亮起的手機螢幕`、`黑屏手機`。不要反覆使用 `同一部` 這類 continuity 暗示來補道具 reference；如果道具 continuity 之後需要更強控制，應另行新增 prop anchor 規則。

輔助小道具如果不是該格第一眼中心，優先刪除，不要硬寫進 `start_image_prompt` 或 `video_prompt`。尤其是會增加手部難度的小物件，例如充電線、鑰匙、紙巾、筷子、遙控器。只有當小道具直接影響這格的 reveal、動作或證據時才保留。保留時要寫成簡單靜態狀態，不要寫成複雜手部動作。

例如，若重點是女孩看見手機螢幕，不要寫 `一隻手拿著充電線停在半空`。可直接刪除充電線，改成 `女孩雙手低低握著亮起的黑色手機，低頭看著螢幕`。若必須保留，寫成 `充電線垂在手機旁邊，沒有插上`，不要讓輔助道具搶走畫面中心。

### 預設策略

- 單人 proof shot：場景 + 主角
- 單人反應 shot：場景 + 主角
- 雙人關係 shot：場景 + 角色A + 角色B

## `reference_assignment` 規則

每張圖只能有一個清楚任務，不要讓多張 reference 做同一個模糊任務。

`reference_assignment` 使用 array：

```json
[
  {
    "slot": "image1",
    "anchor_id": "scene_anchor_living_room",
    "job": "保留客廳餐桌、空間格局和暖色室內光"
  },
  {
    "slot": "image2",
    "anchor_id": "character_ref_main_character",
    "job": "保留主角的臉、髮型和圖中服裝"
  },
  {
    "slot": "image3",
    "anchor_id": "character_ref_support_character",
    "job": "保留配角的臉、髮型和圖中服裝"
  }
]
```

`reference_assignment` 每格最多一個 scene anchor，最多兩個 character anchors。不可把道具放進逐格 `reference_assignment`。

## Prompt 清晰度規則

`start_image_prompt` 和 `video_prompt` 都要寫得簡單，像中學生也能一眼看懂。句子要短，每句只講一件可見事情。不要用抽象劇情判斷代替畫面，例如 `兩人被困住`、`確認危險`、`求助落空`、`被證據壓住`。

每格只能集中表達一個核心畫面概念。圖片模型和影片模型都不擅長同時處理太多動作、太多道具或太多細節。先判斷這格最重要的是甚麼，例如 `手機交接`、`女孩看見手機照片`、`母女看向房門`、`黑屏手機特寫`。`start_image_prompt` 和 `video_prompt` 都要圍繞這個核心，刪掉不直接服務核心的小動作、小道具和背景細節。

如果一格 prompt 同時包含多個動作，例如 `拿線`、`看手機`、`插線`、`抬頭`，應只保留最重要的一個。其他內容如果不是首幀或影片 motion 的核心，就刪除或放到 `caption`。

抽象意思可以保留在 `caption` 或 `consistency_note`，但實際生成 prompt 要改成可見畫面，例如：

- `兩人被困住` -> `兩人站在關上的房門前`
- `確認危險` -> `女孩低頭看著手機，身體停住`
- `求助落空` -> `中年女性避開女孩視線`
- `證據被藏起` -> `手機螢幕保持黑屏`

如果一句 prompt 需要讀兩次才明白，應改短。優先使用：

- 簡單主詞：`女孩`、`中年女性`、`中年男人`、`手指`、`手機`、`房門`
- 簡單動詞：`看向`、`握住`、`拉開`、`推近`、`停住`、`不動`
- 可見結果：`手機螢幕保持黑屏`、`房門沒有打開`、`黑屏手機前景和關上房門背景同框`

## 固定輸出規則

同一份 `output_prompt.json` 和 `角色包.md` 每次都必須使用同一個 JSON shape、同一個欄位順序和同一個資料類型。這裡固定的是 output format，不是每句 prompt 的實際內容。`start_image_prompt`、`negative_prompt_note`、`job`、`consistency_note` 可以按故事內容自然生成，但不可改欄位名、容器結構或欄位順序。

### 固定頂層格式

`output_linked_prompt.json` 的頂層只允許以下欄位，順序固定：

```json
{
  "anchor_material_pack_path": "../anchor_material_pack.json",
  "shots": []
}
```

`anchor_material_pack.json` 的頂層只允許以下欄位，順序固定：

```json
{
  "character_anchors": [],
  "scene_anchors": []
}
```

不可有時輸出 array、有時輸出 object；不可加入 `metadata`、`summary`、`shot_reference_plan`、`notes` 或其他外層欄位。

Array 順序也必須固定：`shots` 必須跟 input shot array 的原始順序；`character_anchors` 依 `角色包.md` 的角色出現順序；`scene_anchors` 依 scene 第一次在 `output_prompt.json` 出現的順序。

### 固定 anchor object 格式

`character_anchors` 每個物件欄位順序固定：

```json
{
  "anchor_id": "",
  "name": "",
  "priority": "",
  "anchor_prompt": "",
  "negative_prompt_note": ""
}
```

`scene_anchors` 每個物件欄位順序固定：

```json
{
  "anchor_id": "",
  "scene_name": "",
  "used_by_scene_ids": [],
  "anchor_prompt": "",
  "continuity_notes": ""
}
```

不可把 scene anchor 和 character anchor 混在同一個 array。

### 固定 shot object 格式

`shots` 每個物件欄位順序固定：

```json
{
  "scene_id": "",
  "scene_number": 0,
  "shot_id": "",
  "shot_number": 0,
  "start_image_prompt": "",
  "negative_prompt_note": "",
  "video_prompt": "",
  "caption": "",
  "reference_assignment": [],
  "consistency_note": ""
}
```

每格都必須有以上全部欄位。即使沒有負向限制，`negative_prompt_note` 也要保留並填空字串；即使沒有 consistency risk，`consistency_note` 也要保留並填空字串。不可新增 `original_start_image_prompt`、`linked_prompt`、`image_prompt`、`notes` 或其他 shot 欄位。

### 固定 slot 順序

- `image1` 永遠是 scene anchor。
- `image2` 永遠是本 shot 的主要畫面角色。
- `image3` 只在雙人 shot 使用，永遠是次要畫面角色。
- 不可把道具放進任何 image slot。
- 不可因語感、敘事重點或重新判斷而調換已確定的 slot。

`reference_assignment` 每個物件欄位順序固定：

```json
{
  "slot": "",
  "anchor_id": "",
  "job": ""
}
```

### 固定角色排序

如果一格有兩個角色，主要角色用以下順序判斷：

1. 原始 `start_image_prompt` 第一個被描述動作、視線或手部狀態的角色。
2. 如果第一個角色不是畫面中心，改用第一眼中心角色。
3. 如果仍不清楚，使用 `角色包.md` 的 `Casting Priority` 順序。
4. 如果沒有 `Casting Priority`，使用角色在 `角色包.md` 第一次出現的順序。

不可把任何範例故事的角色名寫成固定優先順序。這個 skill 必須能套用到不同短劇；角色排序只可來自當次輸入的 `start_image_prompt`、`角色包.md` 和 `Casting Priority`。

### `negative_prompt_note` 與 `consistency_note` 格式

`negative_prompt_note` 永遠是 string，放置每格起始幀生成時的負向約束。它是實際 image generator 可用的負向提示；內容要短、具體、可避免畫面錯誤，不要寫劇情解釋。

`negative_prompt_note` 不重複 character anchor 已經處理的年齡、臉、髮型、服裝、氣質禁忌，也不重複 scene anchor 已經處理的空間、家具、光線禁忌。每格只寫該 shot 容易畫錯的第一幀狀態，例如動作提前完成、視線方向錯、手部接觸錯、道具狀態錯、場景壓力點消失、畫面中心跑偏。只有當某格特別容易把角色或場景畫錯時，才簡短補一條相關限制。

每格 `negative_prompt_note` 可以在最後附加一組通用圖像品質負向詞，尤其是有人手、多人近距離、手機交接或道具特寫時。建議使用短句：`避免多餘手指、多餘手臂、畸形手、手指融合、錯誤握持、臉部變形、文字水印。` 不要把這些通用品質負向詞寫進 `start_image_prompt`。

`consistency_note` 永遠是 string。只在有真實 continuity 風險時填寫，沒有風險時使用空字串。可以按 shot 內容自然寫短句，但不可改成 array 或 object。

`consistency_note` 是給人類或下游檢查流程看的註記，不是 image generator prompt。不可把 `consistency_note` 拼進 `start_image_prompt`、anchor prompt 或任何實際生成 prompt。

## 固定格式範例

以下範例只示範 JSON shape、欄位順序和資料類型。處理實際故事時，內容必須按輸入生成。

雙人 shot：

```json
{
  "scene_id": "SC1",
  "scene_number": 1,
  "shot_id": "SC1_SH1",
  "shot_number": 1,
  "start_image_prompt": "reference-aware 起始幀 prompt",
  "negative_prompt_note": "起始幀生成時要避免的畫面錯誤",
  "video_prompt": "原本或小修後的 video prompt",
  "caption": "原樣保留 caption",
  "reference_assignment": [
    {
      "slot": "image1",
      "anchor_id": "scene_anchor_example",
      "job": "場景 reference 的單一任務"
    },
    {
      "slot": "image2",
      "anchor_id": "character_ref_primary",
      "job": "主要角色 reference 的單一任務"
    },
    {
      "slot": "image3",
      "anchor_id": "character_ref_secondary",
      "job": "次要角色 reference 的單一任務"
    }
  ],
  "consistency_note": ""
}
```

單人 shot：

```json
{
  "scene_id": "SC1",
  "scene_number": 1,
  "shot_id": "SC1_SH2",
  "shot_number": 2,
  "start_image_prompt": "reference-aware 起始幀 prompt",
  "negative_prompt_note": "起始幀生成時要避免的畫面錯誤",
  "video_prompt": "原本或小修後的 video prompt",
  "caption": "原樣保留 caption",
  "reference_assignment": [
    {
      "slot": "image1",
      "anchor_id": "scene_anchor_example",
      "job": "場景 reference 的單一任務"
    },
    {
      "slot": "image2",
      "anchor_id": "character_ref_primary",
      "job": "主要角色 reference 的單一任務"
    }
  ],
  "consistency_note": ""
}
```

## Reference-Aware Prompt 規則

reference-aware `start_image_prompt` 必須用自然繁體中文，並遵守 `1 scene + 1 character` 或 `1 scene + 2 characters` 的構圖。寫法要接近 image edit instruction：先用短句說每張圖要保留甚麼，再說要改成當前 shot 的第一幀。

`start_image_prompt` 同樣必須遵守 Prompt 清晰度規則。不要因為需要接 reference 就寫得很長。每張 reference 的保留句只寫必要元素；`改成...` 後只寫首幀可見畫面，不寫心理推理、劇情解釋或複雜長句。

`start_image_prompt` 必須先選定本格第一眼中心。第一眼中心只能有一個，例如手機、房門、兩人手部交接、女孩低頭看螢幕。不要讓多個重點同時搶畫面。

已有 reference image 時，不要在 `start_image_prompt` 重複完整角色包細節。每張角色 reference 只保留最重要的可見身份錨點：臉、髮型、圖中服裝；必要時才加一個姿態或表情。每張場景 reference 只保留 2-4 個核心元素，例如空間格局、主要家具、房門位置、光線；不要反覆塞長串場景描述。

場景 reference 要用 `圖X作為場景參考` 開頭，然後列出要保留的核心空間元素，例如空間格局、主要家具和光線。不要只寫「保留圖1的場景」或「背景不變」，也不要額外加入對當前 shot 沒有幫助的方向描述。例如：

- `以圖1作為場景參考，保留客廳餐桌、空間格局和暖色室內光`
- `以圖1作為場景參考，保留臥室房門、狹窄空間感和暖色低光`

角色 reference 要用自然圖像指代，不要只寫「以圖2保留主角」，也不要自行改換服裝。服裝描述應跟隨 reference image 中可見服裝。例如：

- `保留圖2中的女孩主角的臉、髮型和圖中服裝`
- `保留圖3中的中年女性母親的臉、髮型和圖中服裝`

如果 reference image 裡有多個人，必須用可見位置或身份消歧，例如 `圖2左側的女孩`、`圖3中正在低頭的中年男人`。不要輸出 raw anchor id。

`改成...` 後面要回到當前 shot 的第一幀畫面。第一次提到角色時，必須把角色名和圖像指代綁定，例如 `圖2中的女孩主角`、`圖3中的中年男人叔父`；之後同一句內才可以只用角色名。不要直接裸用角色名，避免模型不知道名字對應哪張 reference。

`start_image_prompt` 必須先建立 `video_prompt` 會使用的位置指代。當一格有兩個以上人物，或有前景/背景、左側/右側、房門/手機等重要空間關係時，`start_image_prompt` 要先寫清楚同一套位置，例如：

- `圖2中的女孩站在畫面左側`
- `圖3中的中年女性站在畫面右側`
- `前景是中年女性攥住黑屏手機的手`
- `背景是關上的房門`

`video_prompt` 不可突然使用 `start_image_prompt` 沒有建立過的位置關係。若 `video_prompt` 需要寫 `畫面左側的女孩`、`畫面右側的中年女性`、`前景的黑屏手機`、`背景的房門`，`start_image_prompt` 必須先用同樣的詞建立清楚位置。

- 寫清楚鏡頭距離
- 寫清楚人物位置和視線
- 寫清楚手部和道具物理支撐
- 寫清楚第一眼中心
- 保持停格感，不提前完成 `video_prompt` 裡才發生的 motion

不要在自然語言 prompt 裡使用「保持一致」「不要變樣」「不是 generic」「像之前一樣」、raw reference marker、作者解說、不可畫的抽象判斷，或把多個時間動作串成 sequence。

## `video_prompt` 規則

`video_prompt` 是給圖生片使用，必須把新版 `start_image_prompt` 生成出的首幀圖當成起點。不要把 `video_prompt` 寫成另一個分鏡、另一張圖，或和首幀不連續的動作描述。

`video_prompt` 不需要用冗長句式重述完整首幀構圖。因為首幀已由 `start_image_prompt` 生成，`video_prompt` 應直接描述首幀之後的鏡頭與 motion。避免固定寫成 `從……首幀開始`，尤其不要把人物位置、場景、道具和情緒全部重述一遍。只有當承接關係可能混淆時，才用一句很短的起點，例如 `從手機交接點開始`、`從黑屏手機特寫開始`。

`video_prompt` 不應依賴角色名讓模型辨識人物。圖生片模型主要讀取首幀圖，prompt 應使用首幀可見的人物位置、身份外觀、動作和道具來指代人物。除非角色名對字幕、旁白或人工追蹤有必要，否則不要裸用角色名。優先寫成：

- `畫面左側的中年男人`
- `坐在餐桌旁的女孩`
- `拿著手機的中年女性`
- `站在房門前的母女`
- `畫面中的女孩`

如果同一格有兩個以上人物，人物指代必須能從首幀直接看出差異，例如位置、年齡段、性別、手上道具、正在看的方向或身體姿態。不要只寫 `他`、`她`、`母親`、`舅父` 或角色名，避免圖生片模型無法對應到首幀中的具體人物。

多人 shot 的 `video_prompt` 優先使用 `start_image_prompt` 已建立的位置指代，例如 `畫面左側的女孩`、`畫面右側的中年女性`、`前景的黑屏手機`、`背景的房門`。如果 `start_image_prompt` 沒有建立左右或前後位置，不要在 `video_prompt` 臨時加入這些位置；應先小修 `start_image_prompt` 建立位置，再小修 `video_prompt` 承接。

建議 `video_prompt` 使用這個簡潔順序：

```text
鏡頭動作 + 人物或物件 motion + 必要限制 + 終點狀態
```

`video_prompt` 必須遵守 Prompt 清晰度規則。它比 `start_image_prompt` 更短，只寫鏡頭、motion、限制和終點，不補角色背景或劇情解釋。

`video_prompt` 只描述一個主要 motion。不要同時要求人物走位、表情轉變、手部動作、鏡頭推近和新證據出現。若需要取捨，保留最能延續 `start_image_prompt` 第一眼中心的 motion。

例如：

- `鏡頭緩慢推近亮起的手機螢幕，女孩低頭不動，不抬頭。最後停在她側臉和手機螢幕同框。`
- `鏡頭守住關上的房門，房內兩人僵住不動，只微微呼吸，聽著門外平靜的男人聲音。不要切到門外，房門不要打開。`
- `鏡頭從被攥緊的黑屏手機慢慢拉開，手指仍然用力發白。背景中的兩人繼續看向關上的房門，手機螢幕不要亮起。最後停在黑屏手機前景和關上房門背景同框。`

原則上保留原本 `video_prompt`，只在以下情況小修：

- 原本開頭沒有承接新版 `start_image_prompt` 的第一幀狀態。
- 原本用冗長 `從……首幀開始` 重述完整構圖，而不是直接描述 motion。
- 原本包含太多連續事件，會讓圖生片一次生成多個劇情 beat。
- 原本沒有清楚說明鏡頭是平穩、推近、跟拍、短切、拉開或守住不動。
- 原本沒有清楚說明最後停在哪個可見畫面狀態。
- 原本使用抽象劇情結果，而不是可見畫面結果。
- 原本引入了新版 `start_image_prompt` 沒有的人物入鏡、場景切換或新證據。

小修後的 `video_prompt` 必須符合：

- 第一個動作直接接住首幀，例如交接、抬頭、低頭、握住、僵住、看向某處。
- 不重述完整首幀構圖；直接寫鏡頭動作、人物或物件 motion、限制和終點。
- 人物用首幀可見指代，不靠角色名辨識；必要時用位置、年齡段、性別、手上道具或視線方向消歧。
- `video_prompt` 的位置指代必須承接 `start_image_prompt` 已建立的位置，不能臨時發明新的左右、前後或背景關係。
- 每格只保留一個主要 motion beat，不新增第二個劇情 beat。
- 鏡頭運動要可拍，不使用抽象心理描述代替畫面。
- 終點要是可見停格狀態，方便下游判斷影片是否完成。
- 句子要短、直白、可見；不要寫需要推理才明白的抽象劇情句。
- 不改變原 shot 的劇情功能、情緒節點和 reveal 順序。

## 自我檢查

返回前逐項檢查：

- 已讀取 `output_prompt.json` 和 `角色包.md`
- 已輸出 `anchor_material_pack.json`
- 已輸出 `output_linked_prompt.json`
- 沒有改 shot 數量和順序
- `caption` 原樣保留
- `anchor_material_pack.json` 只包含真正需要固定的角色和場景
- 每個 anchor object 都有可直接生成 reference image 的 `anchor_prompt`
- 角色 anchor 已使用 `角色包.md`，沒有只靠 shot prompt 猜角色
- 每格都有 `reference_assignment`
- 每張 reference image 的 job 不重疊
- `start_image_prompt` 使用自然繁體中文
- 每格都有 `negative_prompt_note`，沒有需要避免的錯誤時填空字串
- `negative_prompt_note` 可附加通用圖像品質負向詞，例如多餘手指、多餘手臂、畸形手、文字水印，但不寫進 `start_image_prompt`
- `start_image_prompt` 句子短、直白、可見，沒有把抽象劇情結果當成畫面指令
- `start_image_prompt` 只有一個第一眼中心，沒有多個動作、道具或細節同時搶畫面
- `start_image_prompt` 有清楚的圖像指代，例如 `圖1作為場景參考`、`圖2中的女孩`，並用 `改成...` 回到當前 shot 第一幀
- `start_image_prompt` 已建立 `video_prompt` 會用到的位置指代，例如左側、右側、前景、背景、房門或手機位置
- 輔助小道具沒有搶走畫面中心；不必要的小物件已刪除，必要小物件只用簡單靜態狀態描述
- `start_image_prompt` 不重複完整角色包細節；角色 preserve 只保留臉、髮型、圖中服裝等少數可見錨點
- prompt 裡沒有 raw reference marker
- prompt 裡沒有「保持一致」、「不要變樣」、「不是 generic」、「像之前一樣」
- rewritten prompt 仍是第一幀，不把 `video_prompt` 的動作提前完成
- `video_prompt` 已承接新版 `start_image_prompt` 生成的首幀圖，沒有另起畫面
- `video_prompt` 使用首幀可見人物指代，例如位置、身份外觀、手上道具或視線方向，不依賴裸角色名
- `video_prompt` 的位置指代有承接 `start_image_prompt`，沒有臨時發明新的左右、前後或背景關係
- `video_prompt` 沒有用冗長 `從……首幀開始` 重述完整首幀構圖，而是直接描述鏡頭動作、motion、限制和終點
- `video_prompt` 句子短、直白、可見，沒有把抽象劇情結果當成畫面指令
- `video_prompt` 只有一個主要 motion beat，鏡頭運動和終點停格清楚
- `video_prompt` 的 motion 有延續 `start_image_prompt` 的第一眼中心，沒有同時要求多個不必要動作
- `consistency_note` 只在有真實風險時填寫
