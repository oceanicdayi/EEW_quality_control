---
title: 地震預警品質控制系統 EEW Quality Control
emoji: 🌍
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.50.0
app_file: app.py
pinned: false
license: mit
---

# 地震預警品質控制系統 (EEW Quality Control)

地震預警（EEW）品質控制工具，用於分析與視覺化地震資料。

Earthquake Early Warning (EEW) Quality Control tools for analyzing and visualizing seismic data.

## 關於 About

本儲存庫包含用於分析地震預警（EEW）系統資料的 Python 腳本，包括：

This repository contains Python scripts for analyzing Earthquake Early Warning (EEW) system data, including:

- 報告處理與轉換 (Report processing and conversion)
- 資料視覺化與地圖繪製 (Data visualization and mapping)
- 品質分析與報告時間研究 (Quality analysis and reporting time studies)
- 縣市分析 (County-based analysis)

## 功能特色 Features

- 📊 **報告處理 Report Processing**：將地震預警報告轉換為文字格式 (Convert EEW reports to text format)
- 🗺️ **資料視覺化 Data Visualization**：繪製地震預警報告摘要與地圖 (Plot EEW report summaries and maps)
- ⏱️ **品質分析 Quality Analysis**：分析報告時間與觸發地圖 (Analyze reporting times and trigger maps)
- 🏛️ **縣市分析 County Analysis**：依縣市分析地震預警資料 (Analyze EEW data by county)

## 腳本 Scripts

1. `01_rep2txt_pfile.py`: 將報告檔案轉換為文字格式 (Convert report files to text format)
2. `02_plot_report_pfile.py`: 繪製地震預警報告摘要 (Plot EEW report summaries)
3. `03_plot_ez_maps.py`: 繪製震央區域地圖 (Plot epicenter zone maps)
4. `04_plot_tsmip_trigger_map.py`: 繪製 TSMIP 觸發地圖 (Plot TSMIP trigger maps)
5. `05_plot_conunty.py`: 依縣市分析資料 (Analyze data by county)
6. `06_plot_reporting_time_pfile.py`: 繪製報告時間分析 (Plot reporting time analysis)

## 使用方式 Usage

訪問 [Hugging Face Space](https://huggingface.co/spaces/cwbdayi/EEW_quality_control) 使用網頁介面。

Visit the [Hugging Face Space](https://huggingface.co/spaces/cwbdayi/EEW_quality_control) for the web interface.

命令列使用範例 (For command-line usage):

```bash
python 02_plot_report_pfile.py <pfile> --kind all
```

## 相依套件 Dependencies

- Python 3.7+
- pandas
- numpy
- matplotlib
- obspy
- pygmt
- gradio (for web interface)

## 授權 License

MIT