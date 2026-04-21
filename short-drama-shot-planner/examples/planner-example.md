# Planner Example

這個例子示範一場「發現證據」的 scene，planner 應如何輸出符合目前契約的 shot 規劃結果。

## Input Scene Card

```md
scene_id: S1
scene_number: 1
scene_goal: 女主角替叔叔拿手機充電，意外看到不該存在的家庭照片，先是愣住，接著忍不住再點開確認，最後發現照片裡的人就是自己媽媽。
must_preserve:
- 叔叔先把手機交到她手上
- 第一張照片先讓她覺得不對勁
- 第二次確認才發現真正可怕的資訊
- 本場結尾要有強勾子
```

## Good Output Shape

以下例子直接示範 planner 輸出的一個 `shots` array。

```json
[
  {
    "scene_id": "S1",
    "scene_number": 1,
    "shot_id": "S1_SH1",
    "shot_number": 1,
    "shot_description": "客廳沙發邊，叔叔把亮著的手機遞給她，她下意識伸手接住，充電線和插座就在一旁。",
    "caption": "",
    "audience_read": "她自然接過手機，後面的偷看有了合理入口"
  },
  {
    "scene_id": "S1",
    "scene_number": 1,
    "shot_id": "S1_SH2",
    "shot_number": 2,
    "shot_description": "女孩低頭看著手機畫面，螢幕上同一個家中餐桌角度出現好幾張陌生女人的生活照，她的手指停在畫面邊緣沒有滑走。",
    "caption": "[女孩心聲]: 這些照片怎麼會在他手機裡？",
    "audience_read": "她看到不能存在的照片",
    "motion_note": "鏡頭先停在她低頭看手機的狀態，再輕微向手機畫面逼近，讓證據逐步變得更清楚。"
  },
  {
    "scene_id": "S1",
    "scene_number": 1,
    "shot_id": "S1_SH3",
    "shot_number": 3,
    "shot_description": "女孩僵在原地，眼睛仍盯著手機，拇指停在放大後的照片上，照片裡女人的半張臉已經露出她熟悉的五官，氣氛一下子變得更危險。",
    "caption": "",
    "audience_read": "她被畫面擊中，卻又停不下來繼續確認"
  },
  {
    "scene_id": "S1",
    "scene_number": 1,
    "shot_id": "S1_SH4",
    "shot_number": 4,
    "shot_description": "手機螢幕佔滿畫面，放大的家庭照片裡，叔叔摟著她媽媽站在同一個客廳裡，角落還露出她小時候常見的舊相框。",
    "caption": "[女孩心聲]: 那是我媽。",
    "audience_read": "這一刻她知道自己被設局了",
    "motion_note": "畫面直接收窄到放大後的照片內容，停住半秒，讓真相作為場尾勾子落地。"
  }
]
```

## Why This Works

- shot 由接手機、看到異樣、被擊中、確認真相一路推進，讀感清楚
- `shot_description` 以可見內容為主，但可以帶少量戲劇總結，仍然足夠給下游 prompt 繼續落地
- `audience_read` 只負責鎖第一眼重點，不代替 `shot_description`
- `motion_note` 只在有助 video prompt 時才出現，不代替 `shot_description`
- 最後一格直接把最強證據留到場尾，hook 清楚
