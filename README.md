---
title: EEW Quality Control
emoji: 🌍
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
---

# EEW Quality Control

Earthquake Early Warning (EEW) Quality Control tools for analyzing and visualizing seismic data.

## About

This repository contains Python scripts for analyzing Earthquake Early Warning (EEW) system data, including:

- Report processing and conversion
- Data visualization and mapping
- Quality analysis and reporting time studies
- County-based analysis

## Features

- 📊 **Report Processing**: Convert EEW reports to text format
- 🗺️ **Data Visualization**: Plot EEW report summaries and maps
- ⏱️ **Quality Analysis**: Analyze reporting times and trigger maps
- 🏛️ **County Analysis**: Analyze EEW data by county

## Scripts

1. `01_rep2txt_pfile.py`: Convert report files to text format
2. `02_plot_report_pfile.py`: Plot EEW report summaries
3. `03_plot_ez_maps.py`: Plot epicenter zone maps
4. `04_plot_tsmip_trigger_map.py`: Plot TSMIP trigger maps
5. `05_plot_conunty.py`: Analyze data by county
6. `06_plot_reporting_time_pfile.py`: Plot reporting time analysis

## Usage

Visit the [Hugging Face Space](https://huggingface.co/spaces/cwbdayi/EEW_quality_control) for the web interface.

For command-line usage, clone this repository and run the scripts with appropriate arguments:

```bash
python 02_plot_report_pfile.py <pfile> --kind all
```

## Dependencies

- Python 3.7+
- pandas
- numpy
- matplotlib
- obspy
- pygmt
- gradio (for web interface)

## License

MIT