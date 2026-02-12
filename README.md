---
title: 臺灣地震資料查詢系統 Taiwan Earthquake Data Fetcher
emoji: 🌏
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.50.0
app_file: app.py
pinned: false
license: mit
---

# 🌏 臺灣地震資料查詢系統

使用 ObsPy 從 IRIS FDSN 抓取臺灣地震記錄和地震波形資料

Taiwan Earthquake Data Fetcher - Fetch Taiwan earthquake records and seismic waveforms from IRIS FDSN using ObsPy

## 功能特色 Features

- 🔍 **地震目錄查詢**：從 IRIS FDSN 搜尋臺灣地區的地震記錄
- 📊 **波形資料抓取**：下載地震波形資料（支援 TW 和 IU 網路）
- 🗺️ **資料視覺化**：繪製地震分布圖和波形圖
- ⚙️ **彈性搜尋條件**：可自訂時間範圍、震級、深度和地理區域
- 🌐 **網頁介面**：使用 Gradio 提供友善的互動式介面
- 🔄 **雙向同步**：GitHub 與 Hugging Face Space 之間自動雙向同步（詳見 [SYNC_WORKFLOW.md](SYNC_WORKFLOW.md)）

### Earthquake Catalog Search
Query earthquake records from the Taiwan region via IRIS FDSN services

### Waveform Data Fetching
Download seismic waveforms using TW (Taiwan) and IU (Global Seismographic Network) networks

### Data Visualization
Plot earthquake distribution maps and seismogram visualizations

### Flexible Search Criteria
Customize time range, magnitude, depth, and geographic region

### Web Interface
User-friendly interactive interface powered by Gradio

## 使用方式 Usage

### 線上使用 Online Access

訪問 [Hugging Face Space](https://huggingface.co/spaces/cwbdayi/EEW_quality_control) 使用網頁介面。

Visit the [Hugging Face Space](https://huggingface.co/spaces/cwbdayi/EEW_quality_control) for the web interface.

### 本地執行 Local Installation

```bash
# 安裝相依套件
pip install -r requirements.txt

# 執行應用程式
python app.py
```

## 功能說明 Features Description

### 1. 地震目錄查詢 Earthquake Catalog Query

- 設定時間範圍、震級、深度和地理區域
- 搜尋符合條件的地震記錄
- 顯示地震詳細資訊（時間、震級、位置、深度）
- 自動繪製地震分布圖和震級-深度關係圖

Set search criteria including time range, magnitude, depth, and geographic region to query earthquake records with detailed information and automatic visualization.

### 2. 地震波形抓取 Seismic Waveform Fetching

- 支援 TW（臺灣地震科學中心）和 IU（全球地震網）網路
- 可選擇特定測站或抓取所有測站資料
- 可自訂時間窗（事件前後的時間長度）
- 支援多種通道類型（BH*, HH*, LH* 等）
- 自動繪製波形圖

Supports TW (Taiwan Earthquake Center) and IU (Global Seismographic Network) networks with customizable station selection and time windows.

### 3. 資料視覺化 Data Visualization

- 地震分布地圖（經緯度、震級、深度）
- 震級-深度關係圖
- 波形時間序列圖
- 自動標記地震發生時間

Automatic generation of earthquake distribution maps, magnitude-depth plots, and waveform time series.

## 技術架構 Technical Stack

- **ObsPy**：Python 地震學資料處理工具
- **IRIS FDSN**：國際地震資料服務
- **Gradio**：互動式網頁介面框架
- **Matplotlib**：資料視覺化

## 資料來源 Data Source

本系統使用 IRIS（Incorporated Research Institutions for Seismology）的 FDSN（International Federation of Digital Seismograph Networks）服務，提供全球地震目錄和波形資料。

This system uses IRIS FDSN services to provide global earthquake catalogs and waveform data.

## 相依套件 Dependencies

- Python 3.7+
- obspy >= 1.4.0
- gradio >= 5.0.0
- matplotlib >= 3.7.0
- numpy >= 1.24.0

## 授權 License

MIT License

## 作者 Author

oceanicdayi

## 相關連結 Links

- [IRIS DMC](https://ds.iris.edu/ds/nodes/dmc/)
- [ObsPy Documentation](https://docs.obspy.org/)
- [FDSN Web Services](https://www.fdsn.org/webservices/)
- [Taiwan Earthquake Center](https://tec.earth.sinica.edu.tw/)