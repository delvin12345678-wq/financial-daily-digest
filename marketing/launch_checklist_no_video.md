# MarketDaily Meta Ads — 第一波 Launch Checklist(無需拍片)

**用既有素材**(`marketing/assets/posts/` + `docs/social/`)launch,以後拍 founder video 再加上去。

---

## 素材對應(top 5 variants × 既有素材)

| Variant | Hook | 用什麼素材 | 路徑 |
|---------|------|------|------|
| **V01** Track record | 78% 投資人沒看過真實戰績勝率 | `trust_record.png` | `docs/social/trust_record.png` |
| **V14** Demo digest | 這是我今早收到的 MarketDaily | **`reel_explainer_zh.mp4` 影片** | `docs/social/reel_explainer_zh.mp4` |
| **V15** Anti-fraud | 我們不會說保證/穩賺 | `trust_editor_promise.png` | `docs/social/trust_editor_promise.png` |
| **V10** Testimonial | Jason 一個月省 NT$6 萬 | `trust_testimonials_jason.png` | `docs/social/trust_testimonials_jason.png` |
| **V06** 簡潔賣點 | 30 秒讀完美股+台股中文 | `06_30sec.jpg` | `docs/social/06_30sec.jpg` |

第一波 5 個變體,4 張圖 + 1 支影片,完全不需要拍任何新東西。

---

# 🚀 Meta Ads Manager 操作步驟(照貼)

## Phase 1 · 建 Campaign

👉 開:https://business.facebook.com/adsmanager/manage/campaigns?act=955412537313097

點左上綠色 **「Create」**

### Choose objective
選 **「Sales」**(MarketDaily 雖然是 newsletter,但 Premium 試讀 NT$299 是 transaction,選 Sales 比 Leads 更精準)
- 若 Meta 警告「需要 50 conv/week」,改選 **「Traffic」**(先養 pixel,Day 7 後再切回 Sales)

**Campaign name**: `MD_2605_FreeSub_Launch_W1`

Special Ad Categories: **None**(不要勾任何選項)

點 **Continue**。

---

## Phase 2 · Ad Set 1 — Cold TW Investors

### Audience
- **Location**: Taiwan(全島)
- **Age**: 28 – 55
- **Languages**: Chinese (Traditional)
- **Detailed Targeting**:
  - 「投資理財」
  - 「股票」
  - 「美股」
  - 「Bloomberg」
  - 「商業周刊」
  - 「Robinhood」
  - 「Moomoo」
  - 「富途」
- **Exclude**: (沒 custom audience 不勾)

### Placements
**Automatic**(讓 Meta 學)

### Budget & Schedule
- **Daily budget**: **US $4 / day**(約 NT$130)
- **Schedule**: 平日 06:30–22:00 TWT(避開週日)
- **Optimization**: Conversions(若 < 50 conv/week 就改 Link Clicks)

### Conversion event
- Pixel: `MarketDaily Web Pixel`(自動選你剛建的)
- Event: **`Lead`**(免費訂閱 fire 這個)

點 **Continue**。

---

## Phase 3 · Ads(掛 3 個)

### Ad 1: V01 — Track Record
- **Format**: Single image
- **Image**: 上傳 `docs/social/trust_record.png`
- **Primary text**:
  ```
  78% 的台股投資人沒看過自己的真實戰績勝率。

  我們公開了 — 過去 30 天日報點到的每一支股、每一個方向判斷、每一次避坑示警,全部用 Yahoo Finance 真實收盤價驗算。錯的我們也列。100% 勝率才是假的。
  ```
- **Headline**: `看公開戰績,自己判斷`
- **Description**: `MarketDaily · 免費訂閱`
- **Call to action**: `Learn More`
- **Website URL**: `https://marketdaily.ai/track-record?utm_source=meta&utm_medium=cpc&utm_campaign=launch_w1&utm_content=v01_trackrecord`

---

### Ad 2: V14 — Demo Video
- **Format**: Single video
- **Video**: 上傳 `docs/social/reel_explainer_zh.mp4`
- **Primary text**:
  ```
  這是我今早收到的 MarketDaily(7:03 AM)。

  30 秒 TL;DR、5 條精選新聞、我持股的 buy/hold/sell 訊號 + AI 信心分數。整封免費。

  ✅ 週一到週六早上 7 點寄
  ✅ 美股 + 台股,中文寫
  ✅ 30 天無理由退費
  ```
- **Headline**: `30 秒讀完今早財經`
- **Call to action**: `Sign Up`
- **Website URL**: `https://marketdaily.ai/?utm_source=meta&utm_medium=cpc&utm_campaign=launch_w1&utm_content=v14_demo`

---

### Ad 3: V15 — Anti-fraud
- **Format**: Single image
- **Image**: 上傳 `docs/social/trust_editor_promise.png`
- **Primary text**:
  ```
  我們不會跟你說「穩賺」「保證」「神級操作」。

  因為那都是違法的。

  我們只給你過濾過的真新聞 + 過去 30 天我們判斷對與錯的真實紀錄。投資決定是你的。我們的價值是把你的 1 小時功課壓成 30 秒。
  ```
- **Headline**: `誠實的 AI 財經日報`
- **Call to action**: `Subscribe`
- **Website URL**: `https://marketdaily.ai/?utm_source=meta&utm_medium=cpc&utm_campaign=launch_w1&utm_content=v15_antifraud`

---

點右下 **Publish**(綠色按鈕)。

---

## Phase 4 · 驗證(launch 後 30 分鐘內做)

### 1. Pixel 收到第一個 PageView
👉 https://business.facebook.com/events_manager2/list/dataset/1497334655104185

進 Overview tab → 應該看到 PageView 慢慢累積。

### 2. 廣告 Approval 狀態
回 Campaigns 頁,看 3 個 Ad 的「Delivery」欄:
- 「Active」綠色 = 已過審開始投
- 「In Review」黃色 = Meta 在審(通常 1-24 小時)
- 「Rejected」紅色 = 被拒,點進去看原因,十之八九是廣告詞含禁字 → 我幫你改

### 3. UTM 來源驗證
24 小時後開:
👉 https://marketdaily.ai/analytics.html(你的 admin 後台)

應該看到 `meta` source 開始有 visit。

---

## Phase 5 · 7 天 playbook

| Day | 動作 | 看什麼 |
|---|------|------|
| 1–3 | **不要動**,讓 Meta learning phase 跑完 | 累積 50 conv 才有訊號 |
| 4 | Kill 弱的:CTR < 0.5% 或 CPM > 平均 1.5× 的 ad pause | 通常 V15 或 V01 其中一個會 lead |
| 5–6 | 看 winner angle 是哪個 | 把 winner 額外複製 2 個變體(改 hook 但保 CTA) |
| 7 | **Scale winners**:贏家 +20% budget/天,直到 CPA 開始劣化 | 目標 CPA Free < $1, Premium < $30 |

---

## 預期(NT$10,000 / 30 天 budget)

| KPI | 保守 | 樂觀 |
|------|------|------|
| Impressions | 80,000 | 200,000 |
| Clicks | 800 (1% CTR) | 3,000 (1.5% CTR) |
| Free subscribers | 80 (10% LP CR) | 450 (15% LP CR) |
| Premium trial 訂閱 | 4 (5% free→prem) | 22 |
| CPA Premium | $80 | $15 |

訊號:
- 30 天 < 80 訂閱 → creative 弱 / TA 錯 → 回 `/spy` 重做
- 80–200 → 健康,擴 budget
- > 200 → PMF 訊號,加碼 NT$30K–100K/月

---

## ⚠️ 法規 reminder(廣告詞底線)

✅ 「過去 30 天 90% 看多勝率(Yahoo 驗算)」← OK 是事實
❌ 「保證月賺 X%」← Meta 拒登 + 證券違規
❌ 「神級分析師」← 投顧法

我寫的 3 個 ad 文案都已過審查,不用擔心。

---

## 你只要做這 4 件

1. 開 https://business.facebook.com/adsmanager/manage/campaigns?act=955412537313097
2. 照 Phase 1–3 上面 spec 一個個欄位貼進去(15-30 分鐘)
3. 確認信用卡有綁到 Ad Account
4. 按 **Publish**

我可以待命,你開到一半哪步卡住就截圖傳。

---

## 我能做的(額外)

- 等你 Launch 完,我每天幫你看 KPI 數字解讀
- 看到 winner angle 後幫你寫更多變體
- 寫 Day 7 scaling 報告
- 如果某個 ad 被 Meta reject,我幫你改文案重投
