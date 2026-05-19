# 財經日報系統 設計規格
**日期：** 2026-05-19  
**狀態：** 已確認

---

## 產品定位

幫助忙碌的台灣人每天早上 7:00 收到一份經過 AI 過濾假訊息的美股 + 台股財經日報。  
初期免費，未來走訂閱制變現。

---

## 交付方式

| 管道 | 工具 | 說明 |
|------|------|------|
| Email Newsletter | Beehiiv | 免費支援 2,500 訂閱者，有 API |
| 網站存檔 | Beehiiv 內建 | 訂閱者可在網頁瀏覽歷史報告 |

發送時間：每天台灣時間 AM 7:00（UTC 23:00 前一天）

---

## 整體架構

```
[Scheduler] GitHub Actions cron (每天 UTC 23:00)
     │
[data_fetcher.py]
     ├── 美股：yfinance + NewsAPI（白名單來源）+ SEC EDGAR + Fed RSS
     └── 台股：TWSE API + MOPS 公開資訊觀測站 + 央行/金管會 RSS
     │
[fake_news_filter.py]
     ├── 白名單來源過濾
     ├── 多源交叉驗證（≥2 個來源才標為「已確認」）
     └── 模糊語言偵測（「聽說」「消息人士」→ 過濾）
     │
[analyzer.py]  ← Claude API (claude-sonnet-4-6)
     ├── 生成每日報告（繁體中文）
     └── 市場情緒判斷（偏多/偏空/觀望）
     │
[publisher.py]
     ├── 組裝 HTML Email 模板
     └── Beehiiv API 推送發布
```

---

## 報告內容結構

### ① 大盤總覽
- 美股：S&P500、NASDAQ、道瓊 — 收盤漲跌幅
- 台股：加權指數、成交量、外資買賣超
- 匯率：美元/台幣、美元指數 DXY

### ② 今日重點新聞（已過濾）
- 每則新聞標注：`✅ 多源確認` / `⚠️ 單一來源`
- 只顯示白名單來源新聞

### ③ 個股動態
**美股追蹤清單：**
- Mag 7：AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA
- AI/半導體：AMD, TSM, ARM
- 金融：JPM, GS, BRK.B

每檔：昨日漲跌% + 關鍵新聞標題 + AI 一句話解讀

**台股：**
- 台積電（2330）、聯發科（2454）、鴻海（2317）
- 可後續擴充清單

### ④ 總體經濟信號
- Fed 最新動向 / 利率預期
- CPI、就業數據（有發布時）
- 台灣：央行政策、通膨數據

### ⑤ 今日操作參考
- AI 市場情緒：偏多 / 偏空 / 觀望
- 本週需注意事件（財報、Fed 會議等）
- 風險提示

---

## 假訊息過濾機制

### 美股新聞白名單
Reuters, Bloomberg, WSJ, CNBC, AP, Financial Times, MarketWatch, SEC.gov, federalreserve.gov

### 台股新聞白名單
中央社 CNA, 經濟日報, 工商時報, 鉅亨網 Anue, 金管會 FSC, 中央銀行 CBC, MOPS 公開資訊觀測站

### 驗證邏輯
```
1. 來源是否在白名單？         → 否 = 直接丟棄
2. 幾個白名單來源報導？       → 1個 = 標 ⚠️；≥2個 = 標 ✅
3. 有無模糊語言？             → 有 = 降權或過濾
4. 個股重大消息有無 MOPS 登記？→ 無 = 不呈現為事實
```

---

## 模組檔案結構

```
Delvin agent/
├── main.py                  # 入口，排程觸發點
├── config.py                # API keys、股票清單、白名單
├── data_fetcher.py          # 數據抓取（美股、台股、新聞）
├── fake_news_filter.py      # 假訊息過濾層
├── analyzer.py              # Claude API 分析與報告生成
├── publisher.py             # Beehiiv API 推送
├── templates/
│   └── email.html           # Email HTML 模板
├── .github/
│   └── workflows/
│       └── daily_digest.yml # GitHub Actions 排程
└── requirements.txt
```

---

## 擴充性設計

`config.py` 中的 `NEWS_CATEGORIES` 為清單結構，未來新增領域（科技、能源、加密貨幣等）只需：
1. 在 `NEWS_CATEGORIES` 新增類別與關鍵字
2. 在 `data_fetcher.py` 新增對應來源
3. 在報告模板新增對應區塊

核心 pipeline 不需要修改。

---

## 所需 API 與帳號

| 服務 | 用途 | 費用 |
|------|------|------|
| NewsAPI | 新聞抓取 | 免費（100 req/day） |
| yfinance | 美股數據 | 免費 |
| TWSE 開放 API | 台股數據 | 免費 |
| Claude API | AI 分析 | 按用量（每日約 $0.1-0.3） |
| Beehiiv | Email + 網站 | 免費（≤2,500 訂閱者） |
| GitHub Actions | 排程執行 | 免費 |
