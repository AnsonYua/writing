---
name: short-drama-shot-prompt
description: 將一格一般 shot 描述轉成一條 Qwen-Image 可用的單格圖片 prompt，並帶上可選 caption，且不改動故事線。用於把 shot 描述轉譯成單張圖片需求，以 camera / image space 而不是 story-summary space 來表達。
---

# 短劇 Shot Prompt

當你需要把一格 shot 描述轉成一條單格圖片 prompt 時，就使用這個 skill。

## 輸入與輸出

必要輸入：

- `shot_description`

可選輸入：

- `shot_id`
- `caption`
- `audience_read`
- `anchor_mapping`

輸出：

- `shot_id` optional
- `image_prompt`
- `caption`

`anchor_mapping` 只是可選支援資料，不是核心必要欄位。它的作用是幫你縮短 prompt，而不是成為 prompt 的主體。

## 核心邊界

這個 skill 只負責把當前 shot 壓成一張圖片 prompt。

不要：

- question shot count
- merge 或 split shots
- move a beat to another scene
- redesign shot structure
- invent new plot information
- 寫 `image1` / `image2` / `image3` assignment
- 寫 reference-linking plans
- 把 shot 改成另一個更方便出圖的意思

如果 shot 本身偏弱，都要先忠實寫出當前這格的最佳 prompt，而不是偷偷重規劃。

## 寫法重點

這個 skill 主要從以下欄位讀意思：

- `shot_description`：這格 shot 畫面上要見到什麼
- `audience_read` optional：觀眾第一眼應讀到什麼

寫 prompt 時，優先順序是：

1. 第一眼要見到什麼
2. 主要人物或主體
3. 可見動作、姿勢、proof 或 prop 關係
4. 最少但必要的空間提示
5. 只有在有助讀感時才加光線或氣氛

## 核心規則

### 1. One shot, one image

一格 shot 就是一張圖片。

不要把一格 shot 寫成小型 sequence。

畫面要寫成已經成立的可見狀態，不是正在發生中的 transition。

### 2. 從 image space 出發

prompt 要從鏡頭實際看見的內容出發，而不是從故事摘要、作者意圖、觀眾感受出發。

優先寫：

- framing / shot distance
- 主體放在畫面哪裡
- 可見動作或姿勢
- 關鍵 proof 或 prop 的位置
- 最少房間提示

### 3. 保住這格的戲劇重心

如果這格賣的是 proof，就讓 proof 先讀到。

如果這格賣的是羞辱、危險、曖昧或 confrontation，就把張力透過距離、姿勢、視線、阻隔、負空間或物件接觸寫出來。

不要把真正的 hook 埋在中性背景描述後面。

### 4. 只寫畫面需要的東西

保留：

- 讓這格成立的主體
- 讓這格可讀的動作
- 讓這格夠具體的少量空間或物件信息

刪掉：

- 故事摘要
- 作者解說
- workflow memo
- 與當前畫面無關的 setup 補完
- 只為了好看而加入、但會削弱主讀感的裝飾

### 5. 信任可選 anchors

如果 `anchor_mapping` 已經提供穩定的人物、場景或物件資訊，除非當前畫面真的需要，否則不要重覆交代那些穩定外觀或穩定設定。

anchor 的價值是令 prompt 更短、更乾淨，不是令 prompt 更長。

### 6. `shot_description` 是主基礎

`shot_description` 是 prompt 的主要基礎。

可以把它翻成更自然的 image language，但不要把它改成另一個 shot idea。

`audience_read` 主要用來決定哪個部分要佔主導，不要機械式重述。

## 常見失誤

以下寫法通常要重寫：

- `starts to`
- `suddenly`
- `is about to`
- `turns and then`
- `this shot should express`
- `create a feeling of`
- 用長篇背景說明蓋過當前畫面

如果一條 prompt 讀起來像 recap、說明書、導演備註，而唔似一張可直接想像的圖片，就應該重寫。

## 參考文件

遇到以下情況時，可先參考：

- shot 依賴 proof、chemistry、humiliation、danger、reversal 或強第一眼讀感：`references/shot-value-rules.md`
- prompt 技術上正確，但畫面平、太 generic、太安全：`references/shot-fail-patterns.md`
- 需要明確 before/after 例子：`examples/prompt-example.md`
