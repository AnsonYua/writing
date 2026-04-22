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
    "caption": "舅父叫我幫佢拎部手機去充電。我嗰陣仲以為只係一件小事。",
    "audience_read": "她自然接過手機，後面的偷看有了合理入口"
  },
  {
    "scene_id": "S1",
    "scene_number": 1,
    "shot_id": "S1_SH2",
    "shot_number": 2,
    "shot_description": "女孩低頭看著手機畫面，螢幕上同一個家中餐桌角度出現好幾張陌生女人的生活照，她的手指停在畫面邊緣沒有滑走。",
    "caption": "我一低頭，就見到螢幕停咗喺幾張怪相度。",
    "audience_read": "她看到不能存在的照片",
    "motion_note": "鏡頭先停在她低頭看手機的狀態，再輕微向手機畫面逼近，讓證據逐步變得更清楚。"
  },
  {
    "scene_id": "S1",
    "scene_number": 1,
    "shot_id": "S1_SH3",
    "shot_number": 3,
    "shot_description": "女孩僵在原地，眼睛仍盯著手機，拇指停在放大後的照片上，照片裡女人的半張臉已經露出她熟悉的五官，氣氛一下子變得更危險。",
    "caption": "我越睇越唔敢郁，因為相入面嗰個人，我好似認得。",
    "audience_read": "她被畫面擊中，卻又停不下來繼續確認"
  },
  {
    "scene_id": "S1",
    "scene_number": 1,
    "shot_id": "S1_SH4",
    "shot_number": 4,
    "shot_description": "手機螢幕佔滿畫面，放大的家庭照片裡，叔叔摟著她媽媽站在同一個客廳裡，角落還露出她小時候常見的舊相框。",
    "caption": "放大之後我先睇清楚，嗰個係我媽。",
    "audience_read": "這一刻她知道自己被設局了",
    "motion_note": "畫面直接收窄到放大後的照片內容，停住半秒，讓真相作為場尾勾子落地。"
  }
]
```

## Duplicate Pair Example

以下是一組應該被 planner 刪改的重複 shot。兩格 wording 不同，但觀眾讀到的其實都是「母女在臥室僵住，壓力來自門外」。

```json
[
  {
    "scene_id": "S2",
    "scene_number": 2,
    "shot_id": "S2_SH5",
    "shot_number": 5,
    "shot_description": "臥室中近景，母女兩人同時僵住，兩人都看向關上的房門，手機在母親手裡。",
    "caption": "門外一傳嚟舅父把聲，我同我媽都即刻僵住。",
    "audience_read": "門外壓力逼近，兩人不敢動"
  },
  {
    "scene_id": "S2",
    "scene_number": 2,
    "shot_id": "S2_SH6",
    "shot_number": 6,
    "shot_description": "臥室中近景，母親攥著手機，曉晴站在旁邊，兩人一齊望住房門不敢出聲。",
    "caption": "我哋只可以一齊望住房門，連聲都唔敢出。",
    "audience_read": "母女被房門外的人壓住"
  }
]
```

更好的版本應該合併，並把第一眼中心改成場尾 key image：

```json
{
  "scene_id": "S2",
  "scene_number": 2,
  "shot_id": "S2_SH5",
  "shot_number": 5,
  "shot_description": "黑屏手機特寫，母親發白的手指死死攥住手機；背景裡母女模糊站住，同時望向關上的房門。",
  "caption": "我媽一聽到舅父把聲，就即刻將部手機按黑。到嗰下我先知，連證據都被佢壓住。",
  "audience_read": "證據被藏起，危險仍在門外，這是本場收束 hook",
  "motion_note": "先守住黑屏手機和發白指節，再慢慢退到母女一起望住房門的沉默狀態。"
}
```

## Reaction-Decision Merge Example

以下這組不是完全重複，但第一格只是 reaction-only，第二格才是戲劇 turn。這種情況通常也應該合併。

```json
[
  {
    "scene_id": "S2",
    "scene_number": 2,
    "shot_id": "S2_SH2",
    "shot_number": 2,
    "shot_description": "手機亮屏近景帶到李美珍發白的臉，她低頭滑看相簿，手指越滑越慢，指節開始發抖；曉晴在背景盯住她。",
    "caption": "我一路望住我媽個樣。佢越睇越白，連隻手都開始震。",
    "audience_read": "母親看懂了證據，身體反應先出賣她。"
  },
  {
    "scene_id": "S2",
    "scene_number": 2,
    "shot_id": "S2_SH3",
    "shot_number": 3,
    "shot_description": "臥室近景，李美珍握著手機先看向房門，再壓低身體和聲音避開女兒的正面視線；曉晴站在她面前等答案。",
    "caption": "我等佢講句會幫我。點知佢第一個反應，係望門口，叫我細聲啲。",
    "audience_read": "母親第一選擇不是保護女兒，而是先壓住事情。"
  }
]
```

更好的版本是把「手震臉白」變成「壓事選擇」的可見證據：

```json
{
  "scene_id": "S2",
  "scene_number": 2,
  "shot_id": "S2_SH2",
  "shot_number": 2,
  "shot_description": "臥室近景，李美珍低頭滑看亮屏手機，臉色慢慢發白，握手機的手指開始發抖；曉晴站在她面前盯住她等答案。李美珍看完後沒有立刻看女兒，而是先抬眼望向關上的房門，把手機壓低貼近身體。",
  "caption": "我一路望住我媽，等佢開口幫我。點知佢睇到手都震，第一眼望嘅唔係我，係房門。",
  "audience_read": "母親看懂了證據，但她的第一反應是怕門外的人，而不是保護女兒。",
  "motion_note": "從李美珍低頭滑看手機開始，守住她發白的臉和發抖的手；她看完後先望向房門，再把手機壓低，最後停在曉晴等不到答案的臉。"
}
```

## First-Proof Confirmation Merge Example

以下這組也容易被誤拆。第一格是撞見 proof，第二格是同一部手機上的連續確認；如果第二格沒有新的第一眼中心，就會變成兩格「低頭看手機發現不對」。

```json
[
  {
    "scene_id": "S1",
    "scene_number": 1,
    "shot_id": "S1_SH2",
    "shot_number": 2,
    "shot_description": "手機亮屏和充電線近景，曉晴的充電線停在插口前，螢幕上是一張自家走廊和洗手間門口角度異常的照片，她的手僵住不動。",
    "caption": "我一低頭想插線，就見到一張唔應該存在嘅相。嗰個角度，係我屋企。",
    "audience_read": "第一張 proof 清楚可見，曉晴被怪相釘住。"
  },
  {
    "scene_id": "S1",
    "scene_number": 1,
    "shot_id": "S1_SH3",
    "shot_number": 3,
    "shot_description": "客廳一角，陳國強背影已往房間方向離開；曉晴把手機收近身前，低頭快速打開相簿往下滑，肩膀繃緊。",
    "caption": "等舅父一行開，我即刻打開相簿。越滑落去，我越知唔係一張咁簡單。",
    "audience_read": "她趁短暫空檔確認，危險不是偶然一張照片。"
  }
]
```

更好的版本要把「撞見」和「確認」合成一條連續 proof discovery，並讓第二層資訊在同一格落地：

```json
{
  "scene_id": "S1",
  "scene_number": 1,
  "shot_id": "S1_SH2",
  "shot_number": 2,
  "shot_description": "手機亮屏和充電線近景，曉晴的充電線停在插口前，螢幕先停在一張自家走廊和洗手間門口角度異常的照片；她僵住半秒，抬眼確認陳國強背影離開後，把手機收近身前打開相簿，畫面裡出現多張家中不同角落的可疑縮圖，其中幾張明顯指向她。",
  "caption": "我一低頭就見到一張唔應該存在嘅相。等舅父一行開，我再打開相簿，先知入面唔止一張偷拍我嘅相。",
  "audience_read": "曉晴從撞見怪相一路確認到手機裡有多張偷拍證據，而且目標包括她本人。",
  "motion_note": "從充電線停住和單張怪相開始，短暫抬眼確認舅父背影離開，再收近手機打開相簿，最後停在多張可疑縮圖和她發白的臉。"
}
```

如果要拆成兩格，第二格必須更換第一眼中心，例如：

- 第一格中心：充電線停在插口前 + 單張怪相
- 第二格中心：相簿縮圖群 + 幾張明顯指向曉晴 + 她抬頭找母親

## Why This Works

- shot 由接手機、看到異樣、被擊中、確認真相一路推進，讀感清楚
- 每格 caption 都有內容，不再用空 caption 違反契約
- duplicate pair 示範了要看真正讀感，不只看 wording 是否不同
- reaction-decision example 示範了反應如果只是替真正 turn 鋪路，就應合併到 decision shot 裡
- first-proof confirmation example 示範了 proof checking 如果沒有新層級或新第一眼中心，就應合併成一格更強的 proof discovery
- `shot_description` 以可見內容為主，但可以帶少量戲劇總結，仍然足夠給下游 prompt 繼續落地
- `audience_read` 只負責鎖第一眼重點，不代替 `shot_description`
- `motion_note` 只在有助 video prompt 時才出現，不代替 `shot_description`
- 最後一格直接把最強證據留到場尾，hook 清楚
