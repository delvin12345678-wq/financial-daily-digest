# MarketDaily — Premium 即時 LINE 重大新聞提醒｜設計規格

- 日期:2026-05-22
- 狀態:設計待用戶覆核
- 規格位置說明:放在 repo 根目錄 `specs/`,**不放 `docs/`** —— `docs/` 會被 wrangler 部署成公開網站,內部規格不應外洩。

## 1. 目標

當美國或其他地區出現重大新聞、且會影響到某 Premium 用戶的持股時,系統即時用 LINE 1-1 推播提醒該用戶,不必等到隔天早上 7 點的日報。

## 2. 成功標準

- Premium 用戶能在後台一鍵綁定 LINE,綁定後自動接收提醒。
- 重大新聞發生後,持有相關個股的 Premium 用戶在「數分鐘內」(受新聞來源延遲限制,初期約 5–20 分)收到 LINE 提醒。
- 非重大新聞、與用戶持股無關的新聞,不會推播。
- 同一則新聞不重複轟炸;每人每日有安全上限。

## 3. 非目標(本期不做)

- TikTok / 其他平台的即時提醒。
- Flex Message 精緻卡片(MVP 用文字訊息,列為日後優化)。
- 付費低延遲新聞 API(新聞抓取模組做成可抽換,日後再接)。
- 盤中價格急跳的獨立觸發(本期以「新聞」為觸發主體;價格急跳僅作為規則粗篩的加分訊號)。

## 4. 系統架構

全雲端 Cloudflare Worker,不依賴本機 Mac,與現有日報架構(`digest-cron`)方向一致。

```
                    ┌─────────────────────────────┐
  Cron 每 2 分鐘 ──▶ │  alert-worker (新)            │
                    │  抓新聞→粗篩→比對持股→AI→推播 │
                    └──────────┬──────────────────┘
                               │ 讀寫
                    ┌──────────▼──────────────────┐
                    │  Workers KV (USER_PREFS)      │
                    │  持股 / LINE 綁定 / 去重 / 名單│
                    └──────────▲──────────────────┘
                               │ 寫入綁定 & Premium 標記
       LINE Login ──▶ ┌────────┴──────────────────┐
       OAuth callback │  marketdaily-webhook (現有) │◀── dashboard.html
                      │  + 綁定端點 + Premium 標記  │    「綁定 LINE」按鈕
                      └───────────────────────────┘
                               │ push
                               ▼
                       LINE Messaging API
                       /v2/bot/message/push
```

兩個 Worker 同一個 Cloudflare 帳號,共用 `USER_PREFS` KV namespace 綁定。

## 5. 元件詳述

### 5.1 `alert-worker`(新 Worker)

- **觸發**:Cron Trigger `*/2 * * * *`(每 2 分鐘)。
- **`scheduled()`**:跑完整偵測→推播管線(見第 6 節)。
- **`fetch()`**:除錯/維運端點 —
  - `GET /check` —— 回報 KV、secret、上次執行狀態。
  - `GET /dry-run` —— 跑一次完整管線但**不推播**,回傳「會推什麼」的 JSON。
- **Secrets**:`ANTHROPIC_API_KEY`(AI 嚴重度判定)、`LINE_CHANNEL_ACCESS_TOKEN`(推播;或由 channel id+secret 動態換,與 `auto_post.py` 同模式)。
- **新聞抓取模組**:獨立檔案 `news_source.js`,輸入無、輸出標準化新聞陣列 `{id, title, summary, url, source, publishedAt, tickers[]}`。初期實作為 RSS 抓取+解析;介面固定,日後可換成付費 API 而不動其他程式。

### 5.2 `marketdaily-webhook`(現有 Worker)增補

- `GET /line/login` —— 導向 LINE Login 授權頁(帶 state = 用戶 email 的簽章 token)。
- `GET /line/callback` —— LINE Login 回呼:用 code 換 token、取 userId、寫入 KV `line:{email}` 與 `linemap:{userId}`。
- `POST /line/unbind` —— 解除綁定。
- `GET /line/status?email=` —— 回傳該用戶是否已綁定(dashboard 用)。
- **Premium 標記**:現有優惠碼註冊流程(`subscribeInvite`)補一步 —— 寫 KV `plan:{email} = "premium"`;Premium 方案付費流程同樣寫入。

### 5.3 `dashboard.html` 綁定區塊

- 新增「即時提醒」區塊,**僅 Premium 用戶可見**(`check-subscriber` 回傳 `plan` 已可判斷)。
- 未綁定:顯示「綁定 LINE 接收即時重大新聞提醒」按鈕 → 連到 `/line/login`。
- 已綁定:顯示綁定狀態 + 「解除綁定」。
- 非 Premium 用戶:顯示這是 Premium 功能 + 升級連結。

### 5.4 Workers KV schema(`USER_PREFS` namespace)

| Key | Value | TTL | 說明 |
|-----|-------|-----|------|
| `line:{email}` | LINE userId | 永久 | 正向對應 |
| `linemap:{userId}` | email | 永久 | 反向對應 |
| `plan:{email}` | `premium` / `free` | 永久 | 方案標記(alert 系統的真實來源) |
| `seen:{newsHash}` | timestamp | 48h | 已完整評估過的新聞,避免重複處理 |
| `pushed:{email}:{storyCluster}` | timestamp | 48h | 該用戶已收過此「事件」,跨來源去重 |
| `alertcount:{email}:{YYYY-MM-DD}` | 整數 | 26h | 每日推播計數,做安全上限 |
| (現有)用戶持股偏好 | 既有格式 | — | 沿用現有 `preferences` 儲存,不更動 |

## 6. 資料流(每 2 分鐘一輪 `scheduled()`)

1. **抓新聞** —— `news_source.js` 取得最新新聞陣列。
2. **去重** —— 每則算穩定 id(URL 雜湊)。`seen:{hash}` 存在 → 跳過。
3. **規則粗篩** —— 留下符合重大事件訊號者:關鍵字命中(財報/earnings、併購/M&A、FDA、財測下修/guidance cut、訴訟/lawsuit、停牌/halt、破產/bankruptcy、降評/downgrade、CEO 異動…)。其餘直接標 `seen` 並丟棄。
4. **抓相關股票代碼** —— 由新聞的 ticker 標註 + 標題/內文比對股名清單(`stock_names.py` 對應表移植成 JS 資料)。
5. **比對 Premium 持股** —— `KV.list({prefix:"line:"})` 列出所有已綁定用戶,過濾 `plan=premium`,讀其持股。若無任何 Premium 用戶持有此新聞相關個股 → 標 `seen`、丟棄(**不呼叫 AI,省成本**)。
6. **AI 嚴重度判定** —— 只有「通過粗篩 + 至少一位 Premium 持有者」的新聞才呼叫 Claude:輸入新聞 + 相關 ticker,輸出 `{severity: 0-10, reason: "一句話"}`。`severity < 7` → 標 `seen`、丟棄。
7. **同則新聞去重(story cluster)** —— 以「主要 ticker + 事件類型 + 時間窗(數小時)」產生 cluster key。若用戶的 `pushed:{email}:{cluster}` 已存在 → 該用戶不重發。
8. **每日上限** —— 檢查 `alertcount:{email}:{today}`,達 5 則則該用戶當日不再推(僅記 log)。
9. **推播** —— 對每個通過的(用戶 × 新聞)呼叫 LINE `POST /v2/bot/message/push`,送文字訊息(格式見第 9 節)。成功後寫 `pushed:` 與遞增 `alertcount:`。
10. **標記 `seen`** —— 新聞完整處理完才標 `seen:{hash}`;若步驟 1/6 因網路或 API 失敗,**不標 `seen`**,下一輪(2 分鐘後)自動重試。

## 7. LINE 綁定流程(LINE Login)

1. 在 LINE Developers Console 於同一個 Provider「MarketDaily」下,新增一個 **LINE Login channel**(與 Messaging API channel 同 Provider → userId 一致,推播才找得到人)。
2. 用戶在 dashboard 點「綁定 LINE」→ `marketdaily-webhook` 的 `/line/login` 產生帶簽章 state 的授權 URL,導向 LINE。
3. 用戶在 LINE 授權 → 回呼 `/line/callback?code=&state=` → Worker 用 code 換 access token → 呼叫 LINE Profile API 取 `userId` → 驗證 state 還原 email → 寫入 KV `line:{email}`、`linemap:{userId}`。
4. dashboard 重新整理顯示「已綁定」。

> 前提:用戶必須先把 MarketDaily LINE 官方帳號加為好友,推播才送得到。綁定頁與使用說明都會明確提示這點。

## 8. Premium 判定

- **新用戶**:優惠碼註冊 / Premium 付費 → webhook 寫 `plan:{email}=premium`。
- **現有用戶**:目前系統無法回溯辨識(優惠碼註冊未留記錄)。用戶基數小 —— 由 Delvin 提供現有 Premium email 清單,以一次性腳本或 admin 後台寫入 `plan:` KV。
- alert 系統只服務 **`plan=premium` 且已綁定 LINE** 的用戶。

## 9. 推播訊息格式(MVP:文字訊息)

```
🚨 重大消息｜你的持股 NVDA

[標題]
Nvidia 預警下季財測,資料中心需求轉弱

💡 為什麼跟你有關
你持有 NVDA。財測下修通常直接壓低股價,
留意盤前反應。

🔗 原文:https://...
—— MarketDaily 即時提醒｜僅供參考,非投資建議
```

- 嚴重度高(≥9)時標題加「⚠️ 高度重大」。
- 一律附「僅供參考,非投資建議」。
- Flex Message 卡片列為日後優化。

## 10. 邊界處理

- **半夜照推** —— 依用戶決定,無靜音時段。
- **每日上限** —— 每人每日 5 則,超過僅記 log。
- **跨來源去重** —— story cluster 機制,3 來源報同一事件用戶只收 1 則。
- **推播失敗** —— LINE 回 userId 失效/未加好友 → 記 log、標記該綁定為 stale,通知用戶重新綁定(下次登入 dashboard 顯示),不中斷其他用戶推播。
- **抓取/AI 失敗** —— 該則不標 `seen`,下一輪重試;連續失敗寫入 `/check` 可見的錯誤狀態。
- **新聞來源延遲** —— 初期免費 RSS 約 5–20 分;`news_source.js` 介面固定,日後可換付費 API。

## 11. 成本估算

- Cron 每 2 分鐘 = 720 次/日,Workers 免費額度(10 萬次/日)內。
- Claude 呼叫:僅「通過粗篩 + 有 Premium 持有者」的新聞 → 預估一天個位數至數十次,成本極低。
- LINE push:免費額度內(訊息量遠低於月上限)。
- 新增固定成本:無(除非日後選擇接付費新聞 API)。

## 12. 測試策略

- `alert-worker` 的 `/dry-run` 端點:跑完整管線、輸出「會推什麼」,不真推。
- 規則粗篩、ticker 比對、story cluster:純函式,寫單元測試。
- 端對端:綁一個測試 LINE 帳號設為 Premium + 假持股,將一則已知重大新聞灌進管線,確認收到推播。
- 上線後先以 dry-run 觀察數日,確認嚴重度門檻 7 與推播量合理,再開真推。

## 13. 交付物

1. `alert-worker` Worker(含 `news_source.js`、cron、`/check`、`/dry-run`)。
2. `marketdaily-webhook` 增補:LINE Login 綁定端點 + Premium 標記。
3. `dashboard.html`:Premium 專屬「綁定 LINE」區塊。
4. **Premium 用戶使用說明文件** —— 教 Premium 用戶如何綁定 LINE、需先加官方帳號好友、會收到什麼、如何解除綁定 / 注意每日上限。
5. LINE Login channel 設定(需 Delvin 在 LINE 後台操作,流程文件由本專案提供逐步指引)。

## 14. 已鎖定決策參數

| 參數 | 值 |
|------|-----|
| Cron 頻率 | 每 2 分鐘 |
| 嚴重度推播門檻 | 7 / 10 |
| 每人每日上限 | 5 則 |
| 新聞來源 | 免費 RSS 起步,模組可抽換 |
| 訊息格式 | 文字訊息(MVP) |
| 靜音時段 | 無(半夜照推) |

## 15. 待用戶提供

- 現有 Premium 用戶的 email 清單(用於回填 `plan:` 標記)。
- LINE 後台新增 LINE Login channel 時的逐步操作(屆時依文件引導,類似 Threads 設定流程)。

## 16. 建議實作順序

1. LINE Login channel 設定 + webhook 綁定端點 + dashboard 綁定 UI(先讓綁定能動)。
2. Premium 標記(優惠碼流程 + 回填腳本)。
3. `alert-worker` 骨架 + `news_source.js` + 規則粗篩 + `/dry-run`。
4. 持股比對 + AI 嚴重度判定 + 去重 / 上限。
5. LINE push 推播 + 錯誤處理。
6. dry-run 觀察數日 → 開真推。
7. Premium 用戶使用說明文件。
