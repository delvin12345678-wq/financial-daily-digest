# MarketDaily SaaS Explainer — 設計規格

- 日期:2026-05-21
- 狀態:待用戶審核
- 作者:Claude Code(brainstorming skill)

## 1. 背景與目標

MarketDaily 是每日財經 AI Email 日報平台。本案產出兩個**用途不同**的解說素材:

| 交付物 | 通路 | 目的 | 受眾心理階段 |
|--------|------|------|-------------|
| 社群解說影片 | TikTok / Reels / Threads / FB | 認知 — 我們是什麼、為何選我們 | 還不認識,要被吸引 |
| 網站 How It Works 區塊 | `docs/index.html` | 教學 — 怎麼操作專區(偏好設定 / 後台) | 已感興趣,要懂怎麼用 |

兩者皆做**中文 + 英文**兩版。

## 2. 範圍

**包含**
- 社群解說影片:9:16 直式 MP4(中/英),另出 1:1 版給 IG feed
- 網站新增「How It Works / 怎麼用」互動區塊(雙語、scrollytelling)
- 雙語腳本、AI 旁白、配樂、真實 UI 截圖
- 部署到 `marketdaily.pages.dev`

**不包含**
- 真人實拍、真人配音
- 既有頁面(dashboard / preferences)的功能改動
- 付費音樂版權採購(僅用免費可商用授權)

## 3. 交付物 1 — 社群解說影片

### 3.1 規格
| 項目 | 值 |
|------|-----|
| 長寬比 | 9:16 主版(1080×1920);另切 1:1(1080×1080)給 IG feed |
| 長度 | 約 42 秒 |
| 幀率 | 30 fps |
| 語言 | 中文版、英文版各一 |
| 視覺風格 | MarketDaily 深色玻璃:`#060611` 底、indigo `#6366f1` 漸層、Inter 字體、scene-reveal 動畫 |
| 音軌 | Gemini TTS 旁白 + 畫面字幕 + 免費可商用配樂 |
| 製作法 | HTML 動畫場景 → Playwright 逐幀截圖 → ffmpeg 合成 MP4 → mux 旁白與配樂 |

### 3.2 分鏡(中文版)
| 幕 | 時間 | 畫面 | 旁白 / 字幕 |
|----|------|------|-------------|
| 1 鉤子 | 0–4s | 手機塞滿雜亂紅綠財經新聞、快速閃動 | 「每天滑 30 分鐘財經新聞,你記得住幾條?」|
| 2 痛點 | 4–13s | 「假新聞」標籤、術語亂飛、時鐘倒數 | 「資訊太多、假消息混雜、術語難懂、還是沒時間。」|
| 3 解法 | 13–22s | logo 浮現 + 一封 email 卡片滑入 | 「MarketDaily — 每天早上 7 點,一封信。」|
| 4 為何選我們 | 22–33s | 3 張賣點卡依序彈出:選股票 / AI 過濾假新聞 / 個人化 | 「你選股票 → AI 過濾假新聞 → 個人化日報,寫得像朋友傳訊息。」|
| 5 證明 | 33–38s | 真實日報 digest 卡片展開 | 「30 秒,看完今天該知道的。」|
| 6 CTA | 38–42s | logo + 網址 + 訂閱按鈕脈動 | 「marketdaily.pages.dev — 明天早上見。」|

### 3.3 分鏡(英文版)
| Scene | Time | Visual | VO / Caption |
|-------|------|--------|--------------|
| 1 Hook | 0–4s | Phone flooded with chaotic red/green news | "30 minutes of market news a day — how much do you actually remember?" |
| 2 Problem | 4–13s | Fake-news tags, jargon, ticking clock | "Too much noise, fake news, jargon — and no time." |
| 3 Solution | 13–22s | Logo + email card slides in | "MarketDaily — one email, every morning at 7AM." |
| 4 Why us | 22–33s | 3 benefit cards pop in | "Pick your stocks → AI filters fake news → personalized, written like a friend texting you." |
| 5 Proof | 33–38s | Real digest card expands | "Everything that matters today — in 30 seconds." |
| 6 CTA | 38–42s | Logo + URL + pulsing subscribe button | "marketdaily.pages.dev — see you tomorrow morning." |

### 3.4 製作管線
1. 建參數化動畫場景 `marketing/explainer/scene.html`,以 `?lang=zh|en` 切換文案;內含 JS `seek(t)` 可跳到任意時間點的畫面狀態(確保截幀可決定性重現)。
2. Playwright 開啟場景,從 0 到 42s 每 1/30 秒呼叫 `seek(t)` 並 `browser_take_screenshot`,輸出幀序列。
3. `ffmpeg` 將幀序列(image2)合成無聲 MP4。
4. Gemini TTS 依腳本生成中/英旁白音檔。
5. `ffmpeg` 將旁白 + 配樂混音並 mux 進影片;配樂音量壓低(ducking)。
6. 切 1:1 版本(`ffmpeg crop`)。

### 3.5 輸出檔案
```
marketing/explainer/
  scene.html                         # 參數化動畫場景
  script.md                          # 中英雙語腳本(VO + 字幕)
  render.py                          # 截幀 + ffmpeg 合成腳本
  vo/vo_zh.mp3  vo/vo_en.mp3          # Gemini TTS 旁白
  music/bed.mp3                       # 免費可商用配樂
  out/marketdaily_explainer_zh_9x16.mp4
  out/marketdaily_explainer_en_9x16.mp4
  out/marketdaily_explainer_zh_1x1.mp4
  out/marketdaily_explainer_en_1x1.mp4
```

## 4. 交付物 2 — 網站 How It Works 區塊

### 4.1 位置
新增區塊到 `docs/index.html`,置於 **Features 區塊之後、Pricing 區塊之前**(行 1186 Features 與 1309 Pricing 之間)。
漏斗順序:是什麼 → 為何選我們 → **怎麼用** → 價格 → 訂閱。

### 4.2 內容(scrollytelling,4 步驟)
| 步驟 | 真實截圖來源 | 中文說明 | 英文說明 |
|------|-------------|---------|---------|
| 1 註冊 | `index.html` email 輸入框 | 輸入 email、選擇方案 | Enter your email, pick a plan |
| 2 選股票 | `preferences.html` | 到偏好設定挑你的美股 / 台股 | Pick your US & TW stocks in Preferences |
| 3 看後台 | `dashboard.html` | 後台確認你的偏好摘要 | Review your preferences in the dashboard |
| 4 收日報 | `output/` 日報截圖 | 每天早上 7 點,個人化日報進信箱 | A personalized digest lands at 7AM daily |

### 4.3 技術
- 截圖:Playwright 對本地 `docs/*.html` 與日報 HTML 截圖,輸出至 `docs/assets/howto/step1~4.png`(放 `docs/` 內因網站需引用)。
- 動畫:沿用既有 `ui-pro.js` 的 `scene-reveal` IntersectionObserver,逐步進場。
- 雙語:用既有 `data-i18n` 機制,新增 i18n key:`howto_eyebrow`、`howto_title`、`howto_sub`、`howto_step{1-4}_title`、`howto_step{1-4}_desc`。
- 樣式:沿用既有 `.section-head`、`.section-eyebrow`、深色玻璃卡片,不新增設計語言。
- 不使用自訂游標(專案慣例)。

## 5. 製作流程(執行順序)

```
0. brew install ffmpeg
1. Playwright 抓 UI 截圖 → docs/assets/howto/
2. 寫雙語腳本 script.md(VO + 字幕 + 教學文案)
3. 建影片動畫場景 scene.html
4. Gemini TTS 生中/英旁白
5. 挑免費配樂 → render.py 截幀 + ffmpeg 合成 4 支 MP4
6. 寫 How It Works 區塊進 docs/index.html(含 i18n key)
7. npx wrangler pages deploy docs --project-name marketdaily --commit-dirty=true
```

## 6. 依賴與決策(已確認)

| 項目 | 決定 |
|------|------|
| ffmpeg | 用 `brew install ffmpeg` 安裝 |
| 旁白引擎 | Gemini TTS(用既有 `GEMINI_API_KEY`),中英雙語 |
| 配樂 | Claude 挑選免費可商用授權音樂(YouTube Audio Library / Pixabay) |
| Muapi(可選) | 預設不用;如需動態背景 b-roll 再以 `MUAPI_API_KEY` 生成 |

## 7. 檔案異動清單

**新增**
- `marketing/explainer/`(scene.html、script.md、render.py、vo/、music/、out/)
- `docs/assets/howto/step1~4.png`

**修改**
- `docs/index.html`:新增 How It Works 區塊 + 對應 i18n key(中/英)

## 8. 風險與緩解
| 風險 | 緩解 |
|------|------|
| Gemini TTS 中文發音不自然 | 生成後試聽,必要時調整斷句標點或改 macOS `say` 備援 |
| 逐幀截圖 42s × 30fps = 1260 幀,耗時 | 場景做成可 `seek(t)` 的決定性時間軸,平行截圖;必要時降到 24fps |
| 免費配樂授權條款 | 只選明確標示「可商用、免署名或可署名」者,於 script.md 記錄來源與授權 |
| docs/ 內截圖增加部署體積 | 截圖壓縮(WebP 或壓過的 PNG),單張控制在合理大小 |

## 9. 驗收標準
- [ ] 產出 4 支 MP4(中/英 × 9:16/1:1),約 42 秒,含旁白 + 字幕 + 配樂
- [ ] 影片品牌色、字體與網站一致;字幕無錯字
- [ ] `docs/index.html` 新增 How It Works 區塊,4 步驟用真實截圖
- [ ] 中 / 英語言切換正常,scene-reveal 進場動畫正常
- [ ] 部署到 `marketdaily.pages.dev` 後區塊在桌機與手機皆正常顯示
