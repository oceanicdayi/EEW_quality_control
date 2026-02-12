---
license: apache-2.0
title: Eew
sdk: gradio
emoji: 📚
colorFrom: green
colorTo: blue
sdk_version: 6.5.1
---

# EEW 地震早期警報互動展示

本專案以 Gradio 打造互動式介面，展示地震早期警報（EEW）的核心概念，
包含警報時間、盲區、規模估算與震度換算等內容，適合作為教育與示範用途。

## 主要功能

- 警報時間計算與波傳播示意圖
- 盲區半徑視覺化
- 芮氏規模估算
- PGA 轉換震度

## 本機啟動

1. 安裝相依套件：
   ```bash
   pip install -r requirements.txt
   ```
2. 啟動服務：
   ```bash
   python app.py
   ```

## GitHub Actions 自動化工作流程

本專案設定了自動化工作流程，會執行以下任務：

### 📧 自動化 Email 通知

當 GitHub Actions 工作流程執行時，系統會自動：

1. **同步程式碼到 Hugging Face Space**
   - 雙向同步 GitHub 與 Hugging Face 的程式碼
   - 監控 Hugging Face Space 的部署狀態
   - 抓取並存檔部署日誌

2. **產生詳細工作流程報告**
   - 使用 `workflow_report.py` 腳本自動產生執行報告
   - 包含工作流程基本資訊、執行步驟、部署日誌統計等
   - 提供快速連結到 GitHub Actions、Hugging Face Space 和儲存庫

3. **寄送 Email 通知**
   - 自動寄送完整的工作流程報告到 **oceanicdayi@gmail.com**
   - 報告內容包含執行結果、觸發資訊、部署日誌摘要
   - 提供詳細執行記錄的連結

### 工作流程報告腳本

`workflow_report.py` 會收集以下資訊：
- 工作流程名稱、執行編號、觸發方式
- 執行分支、提交雜湊、觸發人員
- 執行步驟清單與狀態
- 部署日誌統計（最近的建置與執行日誌）
- 相關連結（GitHub Actions、Hugging Face、儲存庫）

### 設定需求

工作流程需要以下 GitHub Secrets：
- `HF_TOKEN`: Hugging Face 存取權杖
- `MAIL_SERVER`: SMTP 伺服器位址（例：smtp.gmail.com）
- `MAIL_USERNAME`: 寄件者電子郵件帳號
- `MAIL_PASSWORD`: 寄件者電子郵件密碼（建議使用應用程式專用密碼）
