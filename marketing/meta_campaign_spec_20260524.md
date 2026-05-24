# Meta Campaign Spec — MarketDaily Launch 20260524

> **Mode**:Manual(MarketDaily 還沒設 META_ACCESS_TOKEN,所以 spec 給你照貼 Ads Manager)
> **Auto-API mode**:等你給我 Meta Business System User token + ad account ID,我可以改用 `POST /v20.0/{ad_account_id}/campaigns` 自動建

---

## Campaign Level

| 欄位 | 值 |
|------|------|
| Name | `MD_2605_FreeSub_Launch_A` |
| Objective | **Conversions**(若 < 50 conv/week 先用 Traffic 養 pixel)|
| Conversion event | `subscribe_free`(已在 `/track/convert` worker 端點 wired up)|
| Pixel ID | (尚未設,需先在 Meta Events Manager 建)|
| Spend cap | $300 / month(NT$10,000 試水)|
| Special Ad Categories | None(不算金融商品 — 你不賣證券,賣 newsletter)|

---

## Ad Set 1 — Cold TW Investors(主力 60% budget)

| 欄位 | 值 |
|------|------|
| Audience | Location: Taiwan; Age: 28-55; |
| | Interests: 股票投資 / 美股 / 台股 / 經濟日報 / 商業周刊 / Bloomberg / CNBC / Robinhood / Moomoo / 富途 |
| | Behaviors: Engaged Shoppers(願意 click out)|
| | Exclude: Custom Audience「已訂閱」(從 Brevo export CSV upload 到 Meta)|
| Placement | **Automatic**(讓 Meta 學)|
| Budget | $4/day(NT$130)|
| Optimization | Conversions(目標 subscribe_free)|
| Schedule | 平日 06:30–22:00 TWT(避開週日 + 配合日報 7AM 時段)|
| Ads | **V09 + V14 + V01**(top 3,各 1/3 spend)|

---

## Ad Set 2 — Cold US Mandarin-speaking TW Diaspora(20% budget)

| 欄位 | 值 |
|------|------|
| Audience | Location: LA / SF / NYC / Seattle / Boston(高 TW 社群密度)|
| | Language: Mandarin (Traditional) |
| | Interests: Taiwan / TSMC / Asia ETF / 台積電 |
| | Age: 30-50 |
| Placement | Automatic |
| Budget | $2/day |
| Ads | V09(founder)+ V17(中文 + 美台雙市場 angle)|

---

## Ad Set 3 — Retargeting Warm(20% budget)

| 欄位 | 值 |
|------|------|
| Audience | Custom Audience: Pixel `PageView` past 30d AND NOT `subscribe_free` |
| Placement | Feed + Stories + Reels |
| Budget | $2/day |
| Ads | **V15(anti-fraud)+ V11(fix 過的折扣版本)**:Warm TA 已認識品牌,可推折扣 + trust |

---

## Tracking & Attribution

### UTM template
```
?utm_source=meta
&utm_medium=cpc
&utm_campaign={{campaign.name}}
&utm_content={{ad.name}}
```
你 worker 端 `/track/visit` + `/track/convert` 已能接,Analytics 後台會自動歸因。

### Pixel events to fire
- `PageView`(全站,已內建)
- `Lead`(自訂):當 `/subscribe-free-direct` 200 → fire from 前端
- `Purchase`(自訂):當 Stripe checkout.session.completed webhook → fire from Worker(伺服器端,Meta Conversions API)

### Conversion API(必做)
iOS 14+ pixel 被遮蔽嚴重,Meta Conversions API 是現在標準。
**你 Worker 已能 hook**:Stripe webhook 收到 `checkout.session.completed` 時加一個 fetch 到 `https://graph.facebook.com/v20.0/{pixel_id}/events?access_token={CAPI_TOKEN}` 報 `Purchase` event,匹配 fbp / fbc cookie。

我可以幫你實作 — 等你給:
- META_PIXEL_ID
- META_CONVERSIONS_API_TOKEN

---

## Day-by-Day Plan(7 天 launch playbook)

| Day | 動作 | KPI 看點 |
|------|------|------|
| 1-3 | **Learning phase**:不要動,讓 Meta 跑滿 50 conv 才有訊號 | 蒐集 baseline CPM / CTR |
| 4 | **Kill bad**:停 CTR < 0.5% 或 CPM > 平均 1.5× 的 creative | 通常會殺 V07(若還在)+ V08 |
| 5-6 | 看 winner 是哪個 angle:founder / demo / track-record / anti-fraud | |
| 7 | **Scale winners**:贏家 budget +20%/天,直到 CPA 開始劣化 | 目標 CPA: 訂閱 free < $1, premium < $30 |

---

## 健康預期(NT$10K / 30 天)

| KPI | 保守 | 樂觀 |
|------|------|------|
| Impressions | 80k | 200k |
| Clicks | 800 (1% CTR) | 3000 (1.5% CTR) |
| Subscribe Free | 80 (10% LP CR) | 450 (15% LP CR) |
| Premium trial | 4 (5% free→prem) | 22 |
| CPA Premium trial | $80 | $15 |
| LTV(假設 3 個月平均訂閱) | $45 | $45 |

**訊號讀法**:
- 30 天 < 80 訂閱 → creative 弱 / TA 錯,先回 `/spy` + `/bulk-creative` 重做
- 30 天 80-200 訂閱 → 健康,擴 budget
- > 200 訂閱 → product-market fit 訊號,加碼 NT$30K-100K/月

---

## 你要準備的 asset(沒做不能投)

| 必要 | 狀態 |
|------|------|
| Meta Business Account | 你已有(`@marketdaily` 之類)|
| Meta Pixel(已埋網站)| ❌ 還沒,要先建 |
| Custom Audience「已訂閱」CSV | ❌ 需從 Brevo export |
| Founder selfie video(V09 + V14 用)| ❌ 你自己拍 30 秒 |
| Digest screenshot(V14 用)| ✅ 截今早收的就行 |
| 戰績頁截圖(V01 用)| ✅ 已上線 |

---

## 下一步建議

1. **本週你拍 V09 + V14 的影片素材**(手機 selfie 即可,不要修)
2. **我幫你寫 Meta Conversions API 接線到 Stripe webhook**(等你給 token)
3. **跑 7 天看 KPI**,我幫你解讀數字
4. **Phase 2**:接 Meta Ad Library API 才能真正跑 live `/spy`(目前是 baseline intel)
