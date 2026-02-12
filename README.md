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
