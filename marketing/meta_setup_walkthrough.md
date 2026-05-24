# Meta Ads 啟動完整 Walkthrough

> **目的**:拿到 4 個東西交給我,我把它們塞進 worker / docs / wrangler secret,然後你就能開始投廣告。
> **總時間**:25–40 分鐘(看你 Meta Business 帳號是否已建)

---

## 你要交給我的清單(checklist)

| # | 項目 | 範例格式 | 從哪拿 |
|---|------|------|------|
| 1 | **Meta Business Account ID** | `123456789012345`(15 位數)| Step A |
| 2 | **Meta Ad Account ID** | `act_1234567890123456`(act_ 開頭)| Step A |
| 3 | **Meta Pixel ID** | `987654321098765`(15 位數)| Step B |
| 4 | **Conversions API Access Token** | `EAA...` 長字串(150+ 字)| Step C |

> 拿到後直接貼給我 4 個值,我幫你接所有點位。

---

## Step A · 建 Meta Business Account + Ad Account(若你還沒)

### A1 · 開直達 URL
👉 https://business.facebook.com/

### A2 · 沒帳號 → 右上「Create Account」
- Name:`MarketDaily`
- Your name:你的真名(必須跟 FB 個人帳號一致,Meta 會 verify)
- Business email:用 `marketdailyhq@gmail.com`(已是 MarketDaily 寄件信箱,品牌一致)
- 進去後 Meta 會問一堆「Business 類型 / 國家 / 行業」→ 行業選「**Media / News**」最合
- ⚠️ 不要選「Financial Services」,會被丟到金融類嚴審

### A3 · 拿 Business ID
進到 Business Settings 後:
👉 https://business.facebook.com/settings/info
- 頁面上方就是 **Business Account ID**(複製給我)

### A4 · 建 Ad Account
👉 https://business.facebook.com/settings/ad-accounts
- 點右上「Add → Create a new ad account」
- Name:`MarketDaily Ads`
- Time zone:**Asia/Taipei**(GMT+8)
- Currency:**TWD**(別選 USD,後續對帳麻煩)
- Payment method:選**信用卡** > 銀行帳號
- 建好後左上會看到 **act_XXXXXXXXXXXXXXX**(複製給我)

---

## Step B · 建 Meta Pixel + 拿 Pixel ID

### B1 · 開 Events Manager 直達
👉 https://business.facebook.com/events_manager2/list/

### B2 · 建 Pixel
- 點 **「Connect Data Sources」** → 選 **「Web」** → **「Get Started」**
- 選 **「Meta Pixel」**(不要選 Conversions API only,等下我們兩個都要)
- Pixel name:`MarketDaily Pixel`
- Website URL:`https://marketdaily.ai`
- 連線方式:選 **「Set up the Meta Pixel and Conversions API」**(一次設兩個)

### B3 · 跳過自動裝程式碼步驟
- Meta 會問「要不要用 Shopify / WordPress 等整合」→ 選 **「Install code manually」**
- 然後它會給你一段 base code → 不用複製,**我已經幫你寫好在 `docs/meta-pixel.js`**
- 直接點 **「Continue」**

### B4 · 拿 Pixel ID
左上 Pixel 名字下面就是 ID,例如:
```
MarketDaily Pixel
ID: 987654321098765 ← 複製這個給我
```

---

## Step C · 拿 Conversions API Access Token

### C1 · 同樣在 Events Manager,進 Pixel 設定頁
👉 https://business.facebook.com/events_manager2/list/dataset/{你的 PIXEL_ID}/settings

(把 {你的 PIXEL_ID} 換成 B4 拿到的數字)

### C2 · 找「Conversions API」區段
- 往下滾,有一段 **「Set up manually」** → 點 **「Get started」**
- 選 **「Generate access token」**
- ⚠️ Token 只顯示一次,複製後馬上貼給我,不然要重生

### C3 · Token 範例
```
EAAB5XK2hY... (約 150-200 字)
```

---

## Step D · 加 Domain Verification(防被丟低 priority)

### D1 · 開 Brand Safety
👉 https://business.facebook.com/settings/owned-domains

### D2 · 加 marketdaily.ai
- 點 **「Add」** → 輸 `marketdaily.ai`
- 選驗證方式 **「DNS Verification」**(最快)
- Meta 給你一個 TXT record,**告訴我**那串 record,我幫你加到 Cloudflare DNS(你帳號)

---

## 5 個 Meta 政策踩雷預警(先知道,避免被封)

| 雷 | 你會怎麼踩 | 防範 |
|------|------|------|
| **金融類嚴審** | Industry 選「Financial Services」 | A2 步驟選「Media / News」 |
| **承諾收益** | 廣告寫「月賺 X%」「穩賺」 | `/ads-score` 已自動 flag,V01-V20 已過 |
| **未驗證 domain** | 直接投 | 做 Step D |
| **廣告帳號剛開立刻 burn 高額** | Day 1 就 $50/day | 從 $4/day 起跑(Meta 信任分數要養) |
| **同 IP 多個 Ad Account** | 同電腦開多個 Business | 一個 Business 一個 Ad Account 就好 |

---

## 我已幫你準備好的(交完 4 個 ID 立刻生效)

| 點位 | 已 ready,等你 ID |
|------|------|
| `docs/index.html` `window.META_PIXEL_ID = ""` | 注入 Pixel ID → 自動 PageView + Lead |
| `docs/pricing.html` 同上 | 同上 |
| `docs/dashboard.html` 同上 | 同上 |
| `docs/meta-pixel.js` | lazy load fbevents.js + Lead/Purchase helpers |
| `stripe-webhook` `sendMetaPurchase()` | 你給 Token 後 `wrangler secret put` 兩個 env 就 fire |
| `marketing/creative_batch_20260524.json` | 20 套廣告 variants 已生成 |
| `marketing/ads_score_20260524.md` | top 5 已篩好 |
| `marketing/meta_campaign_spec_20260524.md` | Campaign / Ad Set spec 已寫好 |

## 我還能幫你做(等你拿到 token)

| 做什麼 | 需要什麼 |
|------|------|
| Pixel ID 注入 3 個 HTML 檔 + 部署 | 你貼 Pixel ID |
| Worker `META_PIXEL_ID` + `META_CONVERSIONS_API_TOKEN` 設 secret + 部署 | 你貼 token |
| Cloudflare DNS 加 Meta domain verification TXT record | 你貼 TXT 值 |
| Brevo 訂閱者 export → Meta Custom Audience CSV 自動產生 | 已寫 script,執行就好(下一個 deliverable)|

## 我無論如何幫不了你做的

| 事 | 為什麼 |
|------|------|
| 替你在 FB / Meta 建帳號 | 需要你個人 FB 帳號 verify |
| 替你綁信用卡 | 法律 / 個資 |
| 替你拍 V09 founder selfie video | 你的臉 |
| 替你按 Meta Ads Manager 的「Launch」鍵 | 帳號是你的,法律責任是你的 |

---

## 你下一個動作

開以下兩個分頁:
1. https://business.facebook.com/(Step A → B → C)
2. 這個檔(對著做)

每完成一個 ID / token,複製貼給我即可。全部拿到大概 25 分鐘。
