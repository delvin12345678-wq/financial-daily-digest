# MarketDaily Agent Team — 夜間值班系統

睡前把任務交給 Claude,雲端排程的 Worker 整夜自動執行,早上給你成果。

## 運作

```
inbox/  →  working/  →  done/   ┐
                   └→  failed/  ┘ → 即時信 + 晨間匯總信
```

- **inbox/** — 待辦任務。delvin 睡前交代,Claude 寫成 `.md` 檔放這。
- **working/** — 執行中。卡在這的任務下次排程會自動接力(容忍中斷 / 額度上限)。
- **done/ · failed/** — 完成 / 失敗,各寄一封即時信。
- 每天早上一封匯總信,總整理昨夜所有成果。

## 任務檔格式
見 `task_template.md`。frontmatter 的 `type` 決定派哪個專家:
`營運` / `開發` / `投資` / `行銷` / `短影片`。

## 容忍中斷與額度上限
Worker 每做一步就 commit。若撞到用量上限,進度寫進任務檔留在 `working/`,
下次排程(額度 reset 後)自動從中斷點接續 —— 不會重做、不會掉任務。

## 戰情室儀表板
雙擊開啟 `dashboard.html` —— 看 5 個 Agent 現在各自在做什麼、任務看板(待辦/進行中/
完成/失敗)、git 活動軌跡。分頁每 60 秒自動重載;Worker 每輪會用 `build_board.py`
重建這個檔,所以畫面永遠跟著最新進度走。檔案自帶資料,離線、不需要伺服器。

## 元件
| 檔案 | 用途 |
|------|------|
| `worker.md` | 夜間 Worker 執行指令(排程 routine 跑這個) |
| `morning_digest.md` | 晨間匯總執行指令 |
| `notify.py` | Brevo 寄信(即時通知 + 晨間匯總) |
| `build_board.py` | 掃描佇列,重建戰情室 `dashboard.html` |
| `dashboard.html` | 戰情室儀表板(自帶資料,雙擊開) |
| `state.json` | 值班狀態(上次匯總時間等) |
| `task_template.md` | 任務檔範本 |

## 怎麼下任務
睡前直接跟 Claude 說要做什麼 —— Claude 會建任務檔、commit、push。
雲端 Worker 每 30 分鐘醒一次撿任務做。進度看 `dashboard.html`。
