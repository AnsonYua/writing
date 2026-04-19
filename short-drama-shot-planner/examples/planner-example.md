# Planner Example

This example shows a proof-discovery scene where the planner chooses panels for readability and hook value, not just for coverage.

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

```json
{
  "scene_id": "S1",
  "scene_number": 1,
  "shots": [
    {
      "scene_id": "S1",
      "scene_number": 1,
      "shot_id": "S1_SH1",
      "shot_number": 1,
      "shot_task": "先把手機自然交到她手上，讓後面的偷看有合理入口。",
      "shot_description": "客廳沙發邊，叔叔把亮著的手機遞給她，她下意識伸手接住，充電線和插座就在一旁。",
      "caption": "",
      "anchor_mapping": [
        {"anchor_id": "uncle_anchor", "object_name": "叔叔", "anchor_type": "character_anchor", "role_hint": "support_character"},
        {"anchor_id": "girl_anchor", "object_name": "女孩", "anchor_type": "character_anchor", "role_hint": "main_character"},
        {"anchor_id": "living_room_anchor", "object_name": "客廳", "anchor_type": "scene_anchor", "role_hint": "scene_space"},
        {"anchor_id": "phone_anchor", "object_name": "手機", "anchor_type": "prop_anchor", "role_hint": "proof_prop"}
      ]
    },
    {
      "scene_id": "S1",
      "scene_number": 1,
      "shot_id": "S1_SH2",
      "shot_number": 2,
      "shot_task": "讓她第一次看到不對勁的證據，但先不要把最可怕的答案全說完。",
      "shot_description": "女孩低頭看著手機畫面，螢幕上同一個家中餐桌角度出現好幾張陌生女人的生活照，女孩的手指停在畫面邊緣沒有滑走。",
      "caption": "[女孩心聲]: 這些照片怎麼會在他手機裡？",
      "audience_read": "她看到不能存在的照片",
      "anchor_mapping": [
        {"anchor_id": "girl_anchor", "object_name": "女孩", "anchor_type": "character_anchor", "role_hint": "main_character"},
        {"anchor_id": "phone_anchor", "object_name": "手機", "anchor_type": "prop_anchor", "role_hint": "proof_prop"},
        {"anchor_id": "living_room_anchor", "object_name": "客廳", "anchor_type": "scene_anchor", "role_hint": "scene_space"}
      ]
    },
    {
      "scene_id": "S1",
      "scene_number": 1,
      "shot_id": "S1_SH3",
      "shot_number": 3,
      "shot_task": "把她的震住和停不下來的確認放在同一個連續視覺裡，讓下一步有內在動機。",
      "shot_description": "女孩僵在原地，眼睛仍盯著手機，拇指停在放大後的照片上，照片裡女人的半張臉已經露出她熟悉的五官。",
      "caption": "",
      "anchor_mapping": [
        {"anchor_id": "girl_anchor", "object_name": "女孩", "anchor_type": "character_anchor", "role_hint": "main_character"},
        {"anchor_id": "phone_anchor", "object_name": "手機", "anchor_type": "prop_anchor", "role_hint": "proof_prop"}
      ]
    },
    {
      "scene_id": "S1",
      "scene_number": 1,
      "shot_id": "S1_SH4",
      "shot_number": 4,
      "shot_task": "用最強的證據畫面把場尾勾子直接釘住。",
      "shot_description": "手機螢幕佔滿畫面，放大的家庭照片裡，叔叔摟著她媽媽站在同一個客廳裡，角落還露出她小時候常見的舊相框。",
      "caption": "[女孩心聲]: 那是我媽。",
      "audience_read": "這一刻她知道自己被設局了",
      "anchor_mapping": [
        {"anchor_id": "phone_anchor", "object_name": "手機", "anchor_type": "prop_anchor", "role_hint": "proof_prop"},
        {"anchor_id": "living_room_anchor", "object_name": "客廳", "anchor_type": "scene_anchor", "role_hint": "scene_space"}
      ]
    }
  ]
}
```

## Why This Works

- The final shot is the strongest hook image, not just a bridge into the next scene.
- The proof gets clearer and more personal across the scene.
- The reaction shot stays attached to the phone, so the next checking beat feels motivated.
- `audience_read` appears only where it helps lock the strongest first-glance takeaway.
