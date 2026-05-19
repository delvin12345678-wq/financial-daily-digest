# Delvin Agent 專案

## 語言偏好
- 回覆語言：繁體中文
- 主要開發語言：Python

## 開發環境
- 平台：macOS
- 終端機：Terminal

## 專案說明
<!-- 請在此描述這個專案的用途和目標 -->

## 可用工具權限

### 直接可用工具
| 工具 | 功能 |
|------|------|
| `Bash` | 執行 shell 命令 |
| `Read` | 讀取本地檔案 |
| `Edit` | 編輯檔案（精確替換） |
| `Write` | 寫入/覆蓋檔案 |
| `Agent` | 啟動子代理執行複雜任務 |
| `AskUserQuestion` | 向用戶提問（互動選擇） |
| `ToolSearch` | 搜尋並載入延遲工具 |
| `ScheduleWakeup` | 排程自動喚醒（loop 模式） |
| `ShareOnboardingGuide` | 分享 ONBOARDING.md |
| `Skill` | 呼叫內建技能 |

### 延遲工具（需透過 ToolSearch 載入）
- **任務管理**：`TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate`, `TaskStop`, `TaskOutput`
- **排程/自動化**：`CronCreate`, `CronDelete`, `CronList`, `RemoteTrigger`, `Monitor`
- **網路**：`WebFetch`, `WebSearch`
- **其他**：`NotebookEdit`, `PushNotification`, `EnterPlanMode`, `ExitPlanMode`, `EnterWorktree`, `ExitWorktree`

### MCP 整合工具（延遲，需透過 ToolSearch 載入）
- **Gmail**：搜尋郵件、建立草稿、標籤管理（`create_draft`, `search_threads`, `label_message` 等）
- **Google Calendar**：建立/修改/刪除活動、查詢行程（`create_event`, `list_events`, `update_event` 等）
- **Firecrawl**：網頁爬取、搜尋、瀏覽器互動（`scrape`, `crawl`, `search`, `firecrawl_agent` 等）
- **Playwright**：瀏覽器自動化（`browser_navigate`, `browser_click`, `browser_take_screenshot` 等）

### 內建技能（Skills）
| 技能 | 用途 |
|------|------|
| `update-config` | 修改 settings.json、hooks、權限設定 |
| `keybindings-help` | 自訂鍵盤快捷鍵 |
| `simplify` | 審查並精簡修改過的程式碼 |
| `fewer-permission-prompts` | 減少重複的權限提示 |
| `loop` | 設定週期性重複任務 |
| `schedule` | 建立/管理排程自動化任務 |
| `claude-api` | 建構/除錯 Claude API 應用 |
| `init` | 初始化 CLAUDE.md |
| `review` | 審查 Pull Request |
| `security-review` | 執行安全性審查 |

## 編碼規範
- 使用 Python 開發
- 不加不必要的註解
- 保持程式碼簡潔
