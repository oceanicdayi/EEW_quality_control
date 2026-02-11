# GitHub Actions 自動部署至 Hugging Face Spaces 設定指南

本專案已設定 GitHub Actions 工作流程，可自動將程式碼同步至 Hugging Face Spaces。

## 📋 前置作業

### 1. 取得 Hugging Face Token

1. 前往 [Hugging Face Settings > Tokens](https://huggingface.co/settings/tokens)
2. 點擊 **"New token"**
3. **Role 請務必選擇 "Write"**（寫入權限）
4. 複製產生的 Token（格式類似：`hf_...`）

### 2. 設定 GitHub Secrets

為了安全性，我們不能把 Token 直接寫在程式碼裡。請依照以下步驟設定：

1. 前往你的 GitHub Repository：`https://github.com/oceanicdayi/EEW_quality_control`
2. 點擊 **Settings** > **Secrets and variables** > **Actions**
3. 點擊 **New repository secret**
4. **Name** 欄位輸入：`HF_TOKEN`
5. **Secret** 欄位貼上剛才從 Hugging Face 複製的 Token
6. 點擊 **Add secret** 儲存

## 🚀 工作流程說明

GitHub Actions 工作流程檔案位於：`.github/workflows/sync_to_hf.yml`

### 觸發條件

工作流程會在以下情況自動執行：

1. **自動觸發**：當有程式碼推送至 `main` 分支時
2. **手動觸發**：可在 GitHub Actions 頁面手動執行

### 工作流程步驟

1. **Checkout code**：檢出完整的 Git 歷史記錄和 LFS 檔案
2. **Push to hub**：將程式碼強制推送至 Hugging Face Spaces

目標 Hugging Face Space：`https://huggingface.co/spaces/cwbdayi/EEW_quality_control`

## 📝 使用方式

### 自動同步

設定完成後，每次你將程式碼推送至 `main` 分支時：

```bash
git add .
git commit -m "更新程式碼"
git push origin main
```

GitHub Actions 會自動將程式碼同步至 Hugging Face Spaces。

### 手動觸發

如果需要手動觸發同步：

1. 前往 GitHub Repository 的 **Actions** 頁籤
2. 選擇左側的 **Sync to Hugging Face Hub** 工作流程
3. 點擊右上角的 **Run workflow** 按鈕
4. 選擇分支（通常是 `main`）
5. 點擊 **Run workflow** 確認執行

## ✅ 驗證部署

同步完成後，你的應用程式將會在以下網址更新：

**https://huggingface.co/spaces/cwbdayi/EEW_quality_control**

Hugging Face Spaces 會自動：
- 從 `requirements.txt` 安裝相依套件
- 從 `app.py` 啟動 Gradio 應用程式
- 透過網頁瀏覽器提供存取服務

## 🔍 查看執行狀態

1. 前往 GitHub Repository 的 **Actions** 頁籤
2. 查看最近的工作流程執行記錄
3. 點擊特定執行項目查看詳細日誌

## 🛠️ 疑難排解

### Token 權限問題

如果出現權限錯誤，請確認：
- Token 的角色為 **"Write"**（寫入）權限
- Secret 名稱為 `HF_TOKEN`（大小寫需一致）
- Token 未過期

### 同步失敗

如果同步失敗，請檢查：
1. GitHub Actions 日誌中的錯誤訊息
2. 確認 Hugging Face Space 存在且可存取
3. 確認 Token 仍然有效

### Space 未更新

如果 Space 沒有更新，請：
1. 檢查 Hugging Face Space 的建置日誌
2. 確認 `requirements.txt` 中的相依套件正確
3. 確認 `app.py` 沒有語法錯誤

## 📚 相關資源

- [GitHub Actions 文件](https://docs.github.com/en/actions)
- [Hugging Face Spaces 文件](https://huggingface.co/docs/hub/spaces)
- [Gradio 文件](https://gradio.app/docs)

## 💡 提示

- 這個設定完全免費（在 GitHub Actions 和 Hugging Face 的免費額度內）
- 每次推送都會自動同步，無需手動操作
- 建議在推送前先在本地測試程式碼
- 可以透過 `.gitignore` 排除不需要同步的檔案
