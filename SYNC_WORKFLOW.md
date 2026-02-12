# 雙向同步工作流程說明 (Bidirectional Sync Workflow)

## 概述 Overview

本專案實現了 GitHub 與 Hugging Face Space 之間的雙向同步機制：

1. **GitHub → Hugging Face**: 當 GitHub 有新的推送時，自動同步到 Hugging Face
2. **Hugging Face → GitHub**: 定期檢查 Hugging Face 是否有較新的變更，若有則同步回 GitHub

This project implements a bidirectional sync mechanism between GitHub and Hugging Face Space:

1. **GitHub → Hugging Face**: Automatically sync to Hugging Face when GitHub has new pushes
2. **Hugging Face → GitHub**: Periodically check if Hugging Face has newer changes and sync back to GitHub if so

## 工作流程觸發條件 Workflow Triggers

工作流程 `sync_to_hf.yml` 會在以下情況下觸發：

- **push**: 當 main 分支有新的推送時
- **workflow_dispatch**: 支援手動觸發
- **schedule**: 每 6 小時自動執行一次，檢查 HF 是否有更新

The `sync_to_hf.yml` workflow is triggered by:

- **push**: When there's a new push to the main branch
- **workflow_dispatch**: Supports manual triggering
- **schedule**: Automatically runs every 6 hours to check for HF updates

## 工作流程說明 Workflow Description

### Job 1: check-hf-updates

此工作負責檢查 Hugging Face 是否有比 GitHub 更新的變更：

1. **檢出 GitHub 倉庫** - 使用完整的 git 歷史記錄
2. **比較版本** - 比較 GitHub 和 HF 的最新提交時間戳
3. **同步變更** - 如果 HF 較新，則合併並推送變更到 GitHub

This job checks if Hugging Face has newer changes than GitHub:

1. **Checkout GitHub repo** - With full git history
2. **Compare versions** - Compare latest commit timestamps between GitHub and HF
3. **Sync changes** - If HF is newer, merge and push changes to GitHub

#### 版本比較邏輯 Version Comparison Logic

```bash
# 取得兩邊的最新提交時間
GITHUB_COMMIT_TIME=$(git log -1 --format=%ct)
HF_COMMIT_TIME=$(git log -1 --format=%ct hf/main)

# 如果 HF 的時間戳較大（較新），則進行同步
if [ $HF_COMMIT_TIME -gt $GITHUB_COMMIT_TIME ]; then
  # 執行同步...
fi
```

### Job 2: sync-to-hub

此工作負責將 GitHub 的變更同步到 Hugging Face：

1. **推送到 HF** - 使用 force push 確保同步成功
2. **等待部署** - 監控 HF Space 的部署狀態
3. **抓取日誌** - 下載部署日誌
4. **提交日誌** - 將日誌推送回 GitHub

This job syncs GitHub changes to Hugging Face:

1. **Push to HF** - Using force push to ensure successful sync
2. **Wait for deployment** - Monitor HF Space deployment status
3. **Fetch logs** - Download deployment logs
4. **Commit logs** - Push logs back to GitHub

#### 執行條件 Execution Conditions

- 依賴 `check-hf-updates` 工作完成
- 僅在 `push` 事件時執行（避免在定期檢查時重複推送）

- Depends on `check-hf-updates` job completion
- Only runs on `push` events (avoids redundant pushes during scheduled checks)

## 使用場景 Use Cases

### 場景 1: GitHub 更新 (GitHub Update)

1. 開發者推送程式碼到 GitHub main 分支
2. `check-hf-updates` 檢查 HF 版本（通常 HF 不會更新）
3. `sync-to-hub` 將 GitHub 變更推送到 HF
4. HF Space 自動重新部署

### 場景 2: Hugging Face 更新 (Hugging Face Update)

1. 使用者在 HF Space 介面直接編輯檔案並提交
2. 定期排程觸發工作流程（每 6 小時）
3. `check-hf-updates` 檢測到 HF 有較新的提交
4. 自動合併 HF 變更並推送回 GitHub
5. GitHub 倉庫更新為最新版本

### 場景 3: 手動觸發 (Manual Trigger)

可以在 GitHub Actions 介面手動觸發工作流程，立即執行版本檢查和同步。

You can manually trigger the workflow from the GitHub Actions interface to immediately perform version checking and syncing.

## 權限要求 Required Permissions

工作流程需要以下 secrets：

- `HF_TOKEN`: Hugging Face 的存取權杖
- `GITHUB_TOKEN`: GitHub Actions 自動提供（用於推送變更）

The workflow requires the following secrets:

- `HF_TOKEN`: Hugging Face access token
- `GITHUB_TOKEN`: Automatically provided by GitHub Actions (for pushing changes)

## 衝突處理 Conflict Handling

如果在合併 HF 變更時發生衝突：

1. 工作流程會顯示錯誤訊息
2. 合併會被中止（`git merge --abort`）
3. 需要手動解決衝突

If conflicts occur when merging HF changes:

1. The workflow will display an error message
2. The merge will be aborted (`git merge --abort`)
3. Manual conflict resolution is required

## 注意事項 Notes

- 使用提交時間戳進行版本比較，因此確保兩邊的時鐘同步很重要
- 定期排程設定為每 6 小時執行一次，可根據需求調整
- 使用 `--no-edit` 合併以避免需要互動式編輯器
- HF → GitHub 同步使用標準合併策略，保留兩邊的歷史記錄

- Commit timestamps are used for version comparison, so clock synchronization is important
- Scheduled execution is set to every 6 hours, adjustable as needed
- Uses `--no-edit` merge to avoid requiring an interactive editor
- HF → GitHub sync uses standard merge strategy, preserving both sides' history

## 故障排除 Troubleshooting

### 問題：無法抓取 HF 資料

檢查 `HF_TOKEN` 是否正確設定且有適當的權限。

**Problem: Cannot fetch HF data**

Check if `HF_TOKEN` is correctly configured with appropriate permissions.

### 問題：合併衝突

手動解決衝突後重新推送到相應的平台。

**Problem: Merge conflicts**

Manually resolve conflicts and re-push to the respective platform.

### 問題：排程未執行

確認 GitHub Actions 已啟用且工作流程檔案語法正確。

**Problem: Schedule not executing**

Ensure GitHub Actions is enabled and the workflow file syntax is correct.
