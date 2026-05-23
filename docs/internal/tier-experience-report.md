# MarketDaily 三層訂戶完整體驗報告

> 第三人稱模擬:從註冊到日常使用,Free / Pro / Premium 三層的真實落差。
> 日期:2026-05-23

---

## 👤 角色 A:免費用戶(親友方案)

**Persona**:小陳 / 朋友送邀請碼 / NT$0/月

### 註冊路徑
1. 朋友丟邀請碼 + 連結
2. 點 `marketdaily.ai` → 看到紫色 banner「🎁 你的朋友送你一份禮物」
3. 點「免費加入」→ 輸 email + 邀請碼 → ✅
4. 收到歡迎信(寫他是 free 親友方案)
5. localStorage 存 `ref` code → 之後若他邀別人也能拿獎勵

### 每日體驗(典型一天)

| 時間 | 收到什麼 |
|-----|---------|
| 06:55 | 📧 **每日 AI 財經日報**(Brevo broadcast) |
| 內容 | 30 秒 TL;DR / 美股 + 台股全市場 / 多源新聞過濾 / 大盤情緒儀表板 |
| **沒有** | ❌ 個股 buy/hold/sell verdict(Pro+ 才有) |
| **沒有** | ❌ 進場價 / 停損價建議(Pro+) |
| **沒有** | ❌ 個人化持股分析(他根本沒進偏好頁設) |
| **沒有** | ❌ LINE 即時新聞推播 |
| **沒有** | ❌ AI 對話助手 |

### Dashboard 看得到的
- 偏好設定頁(可以填股票)— **但日報內容不會個人化**
- 帳號狀態:`親友方案`
- 推薦計畫區塊:✅ 可以邀朋友(雙邊各 30 天 Premium 信用累積)
- ❌ LINE 綁定區塊隱藏(Premium 專屬)
- ❌ AI 投資助手卡隱藏(Premium 專屬)

### 在 LINE OA 對話打字

```
[他]→ NVDA 怎麼樣?
[Bot]→ 嗨!AI 投資助手是 Premium 專屬功能。
        升級 Premium 解鎖:
        • 即時個股 AI 對話
        • LINE 重大新聞推播
        ...
        升級 → marketdaily.ai/pricing
```

### 他升級的觸發點(我們設的)
- **D7 lifecycle email**:「你已讀 7 封日報 — 升級 Premium 首月 7 折」
- **D14 lifecycle email**:「邀請朋友雙邊得 30 天 Premium」
- 推薦計畫每邀 1 人賺 30 天 Premium 信用

### 一句話形容他的體驗
> **「我在看 Morning Brew 風格的早報,只是中文 + 美股台股都有。」**

---

## 👤 角色 B:Pro 用戶 NT$299/月

**Persona**:Jason / 上班族 / 美股科技股投資者

### 註冊路徑
1. 看到首頁 Pro 方案「⭐ 最受歡迎」
2. 點立即訂閱 → Stripe checkout 信用卡付款
3. webhook 收到 `checkout.session.completed` → KV 寫 `plan:${email}=pro`
4. 歡迎信寫他是 Pro,告知功能差異
5. 連結 dashboard → 設定股票偏好(NVDA / TSM / META)

### 每日體驗

| 時間 | 收到什麼 |
|-----|---------|
| 06:55 | 📧 **個人化日報**(只分析他的 NVDA / TSM / META) |
| 內容增量 vs Free | ✅ 個股 **action board**(NVDA 🟢 可以買 / TSM 🟡 抱著 / META 🔴 觀望) |
| | ✅ **signal-card**(每支股 1-10 信心分數 + bias bullish/bearish) |
| | ✅ **進出場戰術 board**(建議買價 / 賺錢目標 / 止損賣價) |
| | ✅ 中英文公司名(輝達 NVDA / 台積電 ADR TSM) |
| **沒有** | ❌ LINE 即時新聞推播 |
| **沒有** | ❌ AI 對話助手 |
| **沒有** | ❌ 月度投資組合健檢 |

### Dashboard 看得到的
- 偏好設定頁 — 日報**真的**會個人化(他選什麼就分析什麼)
- 帳號狀態:`⭐ Pro 付費方案`
- 推薦計畫:✅ 可邀朋友
- ❌ LINE 綁定區塊隱藏(Premium 專屬)
- ❌ AI 投資助手卡隱藏(Premium 專屬)
- 客服:標記為「優先回覆」(主編 24h 內必回 vs Free 48h)

### 在 LINE OA 對話
跟 Free 一樣:「升級 Premium 解鎖 AI 對話」

### 他升級到 Premium 的觸發點
- 看到日報底部「想知道盤中該不該動?升級 Premium 解鎖 AI 對話 + LINE 即時推播」
- 突發新聞時想要更即時(Pro 只有早上 7 點一次)
- 一次性大跌想找人即時問

### 一句話形容他的體驗
> **「我有個人投顧老師,但他每天只跟我說一次話(早上 7 點),其他時間自生自滅。」**

---

## 👤 角色 C:Premium 用戶 NT$499/月

**Persona**:Claire / 金融業 / 美股長期 + 部分台股配息

### 註冊路徑
1. 點 Premium 訂閱 → Stripe
2. webhook → KV `plan:${email}=premium`
3. 歡迎信告知 LINE 即時推播功能 + AI 對話功能
4. 設股票偏好(NVDA / TSM / 中信金 2891)
5. **重點:dashboard 引導她綁 LINE**(必要,否則 LINE 推播跟對話沒用)

### 每日體驗(全套打開)

#### 早晨 06:55
跟 Pro 一樣的個人化日報,**外加**:
- ✅ **個股深度分析報告**(每支 3-5 段分析,Pro 只有 1 段)
- ✅ **月初**會收到「投資組合健檢」專題報告
- ✅ 重大新聞影響評估(這則新聞如何影響你的 3 支持股)

#### 盤中(任何時間)
- ⚡ **LINE 即時推播**:當某支持股觸發 alert-worker 重大新聞檢測,5 分鐘內 LINE 收到:

```
⚡ 重大新聞 · NVDA
Nvidia 法說會優於預期,Q4 營收暴增 95%
(Reuters · 5 分鐘前)
→ 全文連結
```

自動,不用她做任何事

#### 想問就問(任何時間)
🤖 **LINE 對話框直接問 AI**:

```
[她]→ 我手上 NVDA / TSM / 中信金,現在大盤怎樣?
[Bot]→ 從你的組合來看:

       NVDA(輝達) — 動能仍強,Fed 鴿派利好,可繼續持有
       TSM(台積電 ADR) — AI 訂單能見度高,觀察 180 支撐
       中信金 2891 — 高股息穩定,可加碼

       整體大盤偏多但波動,建議分批操作

       ⚠️ 僅供參考,非投資建議
```

- Premium 30 次/天 quota
- 24 小時 session 記憶

💬 **Dashboard 也有 AI 投資助手卡**(同 LINE bot 後端邏輯,只是介面不同)

### Dashboard 看得到的
- ✅ 全部 Pro 功能
- ✅ **LINE 即時提醒卡**(綁定 / 解除)
- ✅ **AI 投資助手卡**(在 dashboard 直接問,跟 LINE 同邏輯)
- 帳號狀態:`👑 Premium`
- 推薦計畫:✅ 可邀朋友(自己已是 Premium 但雙邊 30 天 = 等於延長 30 天)
- 客服:最高優先級 + 主編親自回覆

### 她升級到年繳 / 不流失的觸發點
- 看到 D28 lifecycle email「續訂提醒 + 年繳 20% off」
- 一次成功避開 NVDA 跌 5% 的「啊還好我問了 AI」moment 後直接信任你

### 一句話形容她的體驗
> **「我有個 24/7 在 LINE 跟我講話的智慧投顧,而且不會叫我頻繁交易亂收手續費。」**

---

# 📊 三層差異一張表

| 功能 | Free | Pro | Premium |
|------|:----:|:---:|:-------:|
| **價格** | NT$0 (邀請碼) | NT$299/月 | NT$499/月 |
| **進入方式** | 邀請碼 | Stripe checkout | Stripe checkout |
| 每日早報 | ✅ 通用版 | ✅ **個人化** | ✅ **個人化深度** |
| 30 秒 TL;DR | ✅ | ✅ | ✅ |
| 多源新聞過濾 | ✅ | ✅ | ✅ |
| 美股 + 台股 | ✅ | ✅ | ✅ |
| 個股 buy/hold/sell verdict | ❌ | ✅ | ✅ |
| 進場價 / 停損價建議 | ❌ | ✅ | ✅ |
| 個股深度分析(3-5 段) | ❌ | 1 段 | ✅ 完整 |
| 月度投資組合健檢 | ❌ | ❌ | ✅ |
| **LINE 即時新聞推播** | ❌ | ❌ | ✅ **盤中關鍵差異** |
| **LINE Bot 雙向 AI Q&A** | ❌ | ❌ | ✅ **盤中關鍵差異** |
| Dashboard AI 投資助手 | ❌ | ❌ | ✅ |
| 公開戰績 track record | ✅ 可看 | ✅ 可看 | ✅ 可看 |
| vs 對手對比頁 | ✅ 可看 | ✅ 可看 | ✅ 可看 |
| 主編承諾頁 | ✅ 可看 | ✅ 可看 | ✅ 可看 |
| 推薦計畫(邀請雙邊 30 天) | ✅ | ✅ | ✅ |
| Lifecycle Email (D1/D7/D14) | ✅(D7 推升級) | ✅ | ✅ |
| 客服優先級 | 48h | 24h 優先 | 最高 + 主編親回 |
| 退費保證 | N/A | 30 天 | 30 天 |

---

# 🔑 三層的「升級驅動力」設計

| 層 → 層 | 驅動力 |
|--------|-------|
| Free → Pro | 「日報跟我無關」→ Pro 給個人化 |
| Pro → Premium | 「早上看完,白天市場波動沒人問」→ Premium 給 LINE Bot 即時對話 + 推播 |

---

# 💡 戰略觀察:Pro 的價值區間最尷尬

看完上表會發現 **Pro 跟 Free 的差距 < Premium 跟 Pro 的差距**:
- Free → Pro:多了「個人化」(內容差不多,但寫法針對你)
- Pro → Premium:多了「即時性」(全新維度:LINE 推播 + 對話)

實際上 Premium 是 Pro 的 **2x 服務**,但只貴 NT$200。

**這代表 Pro 是個「過渡層」**,用戶試了一個月後不是退到 Free 就是升到 Premium。長期穩態你的訂戶分布會是 Free / Premium 兩端為主,Pro 中間慢慢空。

## 可考慮的策略

1. **Pro 改成 Premium 的試讀**(NT$299 試 1 個月,然後自動 NT$499/月)
2. **拿掉 Pro,只賣 Free / Premium**(像 Spotify / Netflix 的單一付費層)
3. **Pro 加一個跟 Premium 真正不同的價值**(例如 Pro = 美股 only / Premium = 美股 + 台股 + LINE)

---

# 📝 報告生成資訊

- 生成日期:2026-05-23
- 涵蓋功能:截至 2026-05-23 全部已上線功能
- 主要參考檔:
  - `docs/pricing.html`(定價結構)
  - `stripe-webhook/src/index.js`(plan tier 邏輯 / chat 端點 / LINE webhook)
  - `alert-worker/src/index.js`(LINE 即時推播)
  - `docs/dashboard.html`(各層 UI 差異)
- 維護方法:每次新增功能後重新生成,或手動更新對應表格欄位
