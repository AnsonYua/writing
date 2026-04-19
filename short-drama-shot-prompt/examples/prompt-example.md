# Prompt Example

This example shows how to turn one approved shot into a prompt that keeps proof readable and emotional continuity intact.

## Input Shot

```json
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
    {
      "anchor_id": "girl_anchor",
      "object_name": "女孩",
      "anchor_type": "character_anchor",
      "role_hint": "main_character"
    },
    {
      "anchor_id": "phone_anchor",
      "object_name": "手機",
      "anchor_type": "prop_anchor",
      "role_hint": "proof_prop"
    },
    {
      "anchor_id": "living_room_anchor",
      "object_name": "客廳",
      "anchor_type": "scene_anchor",
      "role_hint": "scene_space"
    }
  ]
}
```

## Good Output

```json
{
  "shot_id": "S1_SH2",
  "image_prompt": "近距離的臉與手機同框，女孩低頭盯著手上的手機，手指停在螢幕邊緣沒有滑開，手機畫面清楚可見同一個家中餐桌角度排著好幾張陌生女人的生活照，客廳只保留最少的沙發與暖色室內光線作為背景提示。",
  "caption": "[女孩心聲]: 這些照片怎麼會在他手機裡？"
}
```

## Why This Works

- The first-look center is the face-and-phone relation.
- The proof is described as one visible grouped arrangement.
- The body state keeps the reaction attached to the trigger.
- The room cue stays minimal, so the payload does not get buried.
