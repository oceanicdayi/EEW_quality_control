#!/usr/bin/env python3
"""
Earthquake Early Warning (EEW) Quality Control Web Interface
A Gradio-based web application for analyzing and visualizing EEW data
"""

import gradio as gr
import os
import sys
import subprocess
from pathlib import Path
import tempfile
import shutil
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server
import matplotlib.pyplot as plt

# Ensure the current directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def create_interface():
    """Create the Gradio interface for EEW Quality Control"""
    
    with gr.Blocks(title="地震預警品質控制系統") as demo:
        gr.Markdown(
            """
            # 地震預警（EEW）品質控制系統
            
            本應用程式提供地震預警（EEW）資料分析與視覺化工具。
            
            ## 功能特色：
            - **報告處理**：將地震預警報告轉換為文字格式
            - **資料視覺化**：繪製地震預警報告摘要與地圖
            - **品質分析**：分析報告時間與觸發地圖
            - **縣市分析**：依縣市分析地震預警資料
            
            ## 可用功能：
            - **🗺️ TSMIP 觸發地圖**：上傳報告檔案和測站資料，生成互動式觸發地圖
            - **🧪 環境測試**：檢查系統環境與相依套件
            - **📖 使用說明**：詳細的腳本使用文件
            - **🎯 互動式展示**：地震預警系統效能展示範例
            """
        )
        
        with gr.Tab("📊 關於"):
            gr.Markdown(
                """
                ### 地震預警品質控制工具
                
                本儲存庫包含用於分析地震預警（EEW）系統資料的 Python 腳本：
                
                1. **01_rep2txt_pfile.py**：使用 P 檔輸入將報告檔案轉換為文字格式
                2. **02_plot_report_pfile.py**：從 P 檔資料繪製地震預警報告摘要
                3. **03_plot_ez_maps.py**：繪製震央區域地圖
                4. **04_plot_tsmip_trigger_map.py**：繪製 TSMIP 觸發地圖
                5. **05_plot_conunty.py**：依縣市分析資料
                6. **06_plot_reporting_time_pfile.py**：繪製報告時間分析
                
                ### 資料需求
                
                腳本需要以下資料檔案：
                - `192/` 目錄中的 P 檔（副檔名為 .P20）
                - 測站資料（`station.txt`）
                - 縣市清單（`county_list.txt`）
                - 縣市邊界資料（`city_2016.gmt`）
                - 地震預警報告檔案（`.rep` 檔案）
                - 包含地震資料的 XML 檔案
                
                ### 使用方式
                
                使用這些工具時，您需要：
                1. 準備所需格式的資料檔案
                2. 將 P 檔放置在 `192/` 目錄中
                3. 使用必要的參數執行適當的腳本
                
                ### 命令列使用範例
                
                ```bash
                # 將報告檔案轉換為文字
                python 01_rep2txt_pfile.py
                
                # 繪製報告摘要
                python 02_plot_report_pfile.py <pfile> --kind all
                
                # 繪製震央區域地圖
                python 03_plot_ez_maps.py <pfile> --epi-lon 120.5 --epi-lat 23.5
                
                # 繪製觸發地圖
                python 04_plot_tsmip_trigger_map.py <pfile>
                
                # 繪製縣市分析
                python 05_plot_conunty.py <pfile>
                
                # 繪製報告時間
                python 06_plot_reporting_time_pfile.py <pfile>
                ```
                
                ### 相依套件
                
                - Python 3.7+
                - pandas
                - numpy
                - matplotlib
                - obspy
                - pygmt
                
                ### 儲存庫
                
                原始碼：[github.com/oceanicdayi/EEW_quality_control](https://github.com/oceanicdayi/EEW_quality_control)
                """
            )
        
        with gr.Tab("🧪 環境測試"):
            gr.Markdown(
                """
                ### 環境檢查
                
                點擊下方按鈕以驗證所有必要的相依套件是否已安裝且可存取。
                """
            )
            
            test_output = gr.Textbox(
                label="測試結果",
                lines=10,
                max_lines=20,
                interactive=False
            )
            
            def run_environment_test():
                """Run basic environment checks"""
                output = []
                output.append("=== 地震預警品質控制環境測試 ===\n")
                
                # Check Python version
                import sys
                output.append(f"Python 版本：{sys.version}\n")
                
                # Check dependencies
                deps = {
                    "pandas": "pandas",
                    "numpy": "numpy", 
                    "matplotlib": "matplotlib",
                    "obspy": "obspy",
                    "pygmt": "pygmt",
                    "gradio": "gradio"
                }
                
                output.append("\n=== 檢查相依套件 ===")
                for name, module in deps.items():
                    try:
                        mod = __import__(module)
                        version = getattr(mod, '__version__', 'unknown')
                        output.append(f"✓ {name}：{version}")
                    except ImportError as e:
                        output.append(f"✗ {name}：未找到 - {e}")
                
                # Check for data files
                output.append("\n=== 檢查資料檔案 ===")
                required_files = [
                    "eewrep_function.py",
                    "01_rep2txt_pfile.py",
                    "02_plot_report_pfile.py",
                    "03_plot_ez_maps.py",
                    "04_plot_tsmip_trigger_map.py",
                    "05_plot_conunty.py",
                    "06_plot_reporting_time_pfile.py"
                ]
                
                for filepath in required_files:
                    if os.path.exists(filepath):
                        output.append(f"✓ {filepath}")
                    else:
                        output.append(f"✗ {filepath} - 未找到")
                
                # Check directories
                output.append("\n=== 檢查目錄 ===")
                dirs = ["192", "outputs", "old"]
                for dirname in dirs:
                    if os.path.exists(dirname):
                        output.append(f"✓ {dirname}/ - 存在")
                    else:
                        output.append(f"✗ {dirname}/ - 未找到")
                
                output.append("\n=== 測試完成 ===")
                output.append("\n注意：這是地震預警品質控制工具的部署版本。")
                output.append("若要使用應用程式的完整功能，您需要提供所需的資料檔案。")
                
                return "\n".join(output)
            
            test_button = gr.Button("執行環境測試", variant="primary")
            test_button.click(fn=run_environment_test, outputs=test_output)
        
        with gr.Tab("📖 使用說明"):
            gr.Markdown(
                """
                ### 腳本說明文件
                
                #### 01_rep2txt_pfile.py
                使用 P 檔輸入將地震預警報告檔案轉換為文字格式。
                
                **使用方式：**
                ```bash
                python 01_rep2txt_pfile.py
                ```
                
                ---
                
                #### 02_plot_report_pfile.py
                從 P 檔資料繪製地震預警報告摘要。
                
                **參數：**
                - `pfile`：P 檔名稱（例如：17010623.P20）
                - `--kind`：分析類型（f42/f43/gei/all，預設：all）
                - `--base-folder`：包含 .rep 檔案的目錄（預設：./192）
                - `--xmin`、`--xmax`：X 軸範圍（秒）
                - `--ymin`、`--ymax`：Y 軸範圍
                
                **使用方式：**
                ```bash
                python 02_plot_report_pfile.py 17010623.P20 --kind all
                ```
                
                ---
                
                #### 03_plot_ez_maps.py
                繪製震央區域地圖。
                
                **參數：**
                - `pfile`：P 檔名稱
                - `--epi-lon`：震央經度（必要）
                - `--epi-lat`：震央緯度（必要）
                - `--kind`：分析類型（f42/f43/gei/all，預設：all）
                - `--base-folder`：包含 .rep 檔案的目錄（預設：./192）
                
                **使用方式：**
                ```bash
                python 03_plot_ez_maps.py 17010623.P20 --epi-lon 120.5 --epi-lat 23.5
                ```
                
                ---
                
                #### 04_plot_tsmip_trigger_map.py
                繪製 TSMIP 觸發地圖。
                
                **參數：**
                - `pfile`：P 檔名稱
                - `--kind`：分析類型（f42/f43/gei/all，預設：all）
                - `--base-folder`：包含 .rep 檔案的目錄（預設：./192）
                
                **使用方式：**
                ```bash
                python 04_plot_tsmip_trigger_map.py 17010623.P20
                ```
                
                ---
                
                #### 05_plot_conunty.py
                依縣市分析地震預警資料。
                
                **參數：**
                - `pfile`：P 檔名稱
                - `--kind`：分析類型（f42/f43/gei/all，預設：all）
                - `--base-folder`：包含 .rep 檔案的目錄（預設：./192）
                
                **使用方式：**
                ```bash
                python 05_plot_conunty.py 17010623.P20
                ```
                
                ---
                
                #### 06_plot_reporting_time_pfile.py
                從 P 檔資料繪製報告時間分析。
                
                **參數：**
                - `pfile`：P 檔名稱
                - `--kind`：分析類型（f42/f43/gei/all，預設：all）
                - `--base-folder`：包含 .rep 檔案的目錄（預設：./192）
                - `--xmin`、`--xmax`：X 軸範圍（秒）
                
                **使用方式：**
                ```bash
                python 06_plot_reporting_time_pfile.py 17010623.P20
                ```
                
                ---
                
                ### 資料檔案格式
                
                #### P 檔格式
                P 檔包含地震參數與測站資料：
                - 第 1 行：事件資訊（時間、規模、深度）
                - 第 2 行以後：測站資訊（名稱、到時、震度、PGA）
                
                #### 報告檔案（.rep）
                報告檔案包含地震預警系統報告，包括時間與位置資訊。
                
                #### XML 檔案
                XML 檔案包含中央氣象署（CWA）的官方地震資訊。
                
                ### 聯絡方式
                
                如有問題或疑問，請訪問 GitHub 儲存庫：
                [github.com/oceanicdayi/EEW_quality_control](https://github.com/oceanicdayi/EEW_quality_control)
                """
            )
        
        with gr.Tab("🗺️ TSMIP 觸發地圖"):
            gr.Markdown(
                """
                ### TSMIP 觸發地圖生成器
                
                此功能可以繪製 TSMIP 測站觸發地圖，顯示：
                - 所有 TSMIP 測站位置（灰色三角形）
                - 已觸發的測站（紅色三角形）
                - 震央位置（黃色星號）
                - 最遠觸發距離範圍圓圈
                - 觸發比率統計
                """
            )
            
            with gr.Row():
                with gr.Column():
                    rep_file = gr.File(
                        label="上傳報告檔案 (.rep)",
                        file_types=[".rep"],
                        type="filepath"
                    )
                    station_file = gr.File(
                        label="上傳測站檔案 (station.txt)",
                        file_types=[".txt"],
                        type="filepath"
                    )
                    
                    with gr.Row():
                        epi_lon = gr.Number(
                            label="震央經度",
                            value=121.0,
                            precision=4
                        )
                        epi_lat = gr.Number(
                            label="震央緯度",
                            value=24.0,
                            precision=4
                        )
                    
                    generate_map_btn = gr.Button("生成觸發地圖", variant="primary")
                    
                with gr.Column():
                    map_output = gr.Image(
                        label="TSMIP 觸發地圖",
                        type="filepath"
                    )
                    map_stats = gr.Textbox(
                        label="統計資訊",
                        lines=6,
                        interactive=False
                    )
            
            def generate_trigger_map(rep_file_path, station_file_path, epicenter_lon, epicenter_lat):
                """Generate TSMIP trigger map using matplotlib"""
                if not rep_file_path or not station_file_path:
                    return None, "錯誤：請上傳報告檔案和測站檔案"
                
                try:
                    import matplotlib
                    matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'Microsoft YaHei', 'SimHei']
                    matplotlib.rcParams['axes.unicode_minus'] = False
                    
                    # Constants
                    KM_PER_DEGREE = 111.0  # Approximate kilometers per degree of latitude/longitude
                    
                    # Read station file
                    tsmip_all = pd.read_csv(
                        station_file_path,
                        sep=r'\s+',
                        header=None,
                        names=['Station', 'Lon', 'Lat', 'Depth']
                    )
                    
                    # Read rep file
                    rep_used = pd.read_csv(
                        rep_file_path,
                        sep=r'\s+',
                        skiprows=5,
                        header=None,
                        usecols=[0, 4, 5, 6, 7, 8],
                        names=['Station', 'Lat', 'Lon', 'PGA', 'PGV', 'PGD']
                    )
                    
                    # Calculate distances
                    def get_dist(lon, lat):
                        return 6371 * 2 * np.arcsin(np.sqrt(
                            np.sin(np.radians(lat - epicenter_lat)/2)**2 +
                            np.cos(np.radians(epicenter_lat)) * np.cos(np.radians(lat)) *
                            np.sin(np.radians(lon - epicenter_lon)/2)**2
                        ))
                    
                    rep_used['Dist'] = get_dist(rep_used['Lon'], rep_used['Lat'])
                    max_dist_km = rep_used['Dist'].max()
                    
                    # Calculate all station distances
                    tsmip_all['Dist'] = get_dist(tsmip_all['Lon'], tsmip_all['Lat'])
                    
                    # Calculate trigger ratio
                    stations_within_range = tsmip_all[tsmip_all['Dist'] <= max_dist_km]
                    total_in_range = len(stations_within_range)
                    triggered_in_range = len(rep_used[rep_used['Dist'] <= max_dist_km])
                    
                    if total_in_range > 0:
                        trigger_ratio = (triggered_in_range / total_in_range) * 100
                    else:
                        trigger_ratio = 0
                    
                    # Create plot
                    fig, ax = plt.subplots(figsize=(12, 10))
                    
                    # Set map bounds
                    buffer = (max_dist_km / KM_PER_DEGREE) + 0.3
                    ax.set_xlim(epicenter_lon - buffer, epicenter_lon + buffer)
                    ax.set_ylim(epicenter_lat - buffer, epicenter_lat + buffer)
                    
                    # Plot all stations (gray triangles)
                    ax.scatter(
                        tsmip_all['Lon'],
                        tsmip_all['Lat'],
                        marker='^',
                        s=50,
                        c='gray',
                        alpha=0.5,
                        edgecolors='darkgray',
                        linewidths=0.5,
                        label='所有測站',
                        zorder=2
                    )
                    
                    # Plot triggered stations (red triangles)
                    ax.scatter(
                        rep_used['Lon'],
                        rep_used['Lat'],
                        marker='^',
                        s=100,
                        c='red',
                        alpha=0.8,
                        edgecolors='black',
                        linewidths=1,
                        label='觸發測站',
                        zorder=3
                    )
                    
                    # Plot epicenter (yellow star)
                    ax.scatter(
                        epicenter_lon,
                        epicenter_lat,
                        marker='*',
                        s=500,
                        c='yellow',
                        edgecolors='red',
                        linewidths=2,
                        label='震央',
                        zorder=4
                    )
                    
                    # Plot trigger range circle
                    circle = plt.Circle(
                        (epicenter_lon, epicenter_lat),
                        max_dist_km / KM_PER_DEGREE,  # Convert km to degrees
                        fill=False,
                        color='orange',
                        linestyle='--',
                        linewidth=2,
                        alpha=0.7,
                        label=f'觸發範圍 ({max_dist_km:.1f} km)',
                        zorder=1
                    )
                    ax.add_patch(circle)
                    
                    # Add labels and title
                    farthest_sta = rep_used.loc[rep_used['Dist'].idxmax(), 'Station']
                    ax.set_xlabel('經度', fontsize=12)
                    ax.set_ylabel('緯度', fontsize=12)
                    ax.set_title(
                        f'TSMIP 觸發地圖\n觸發比率: {trigger_ratio:.1f}% ({triggered_in_range}/{total_in_range})\n最遠測站: {farthest_sta} ({max_dist_km:.1f} km)',
                        fontsize=14,
                        fontweight='bold'
                    )
                    
                    ax.legend(loc='upper right', fontsize=10)
                    ax.grid(True, alpha=0.3)
                    ax.set_aspect('equal')
                    
                    plt.tight_layout()
                    
                    # Save to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                        temp_path = temp_file.name
                        plt.savefig(temp_path, dpi=150, bbox_inches='tight')
                    plt.close()
                    
                    # Generate statistics text
                    stats_text = f"""半徑 {max_dist_km:.2f} km 內總站數: {total_in_range}
半徑內觸發站數: {triggered_in_range}
觸發比率: {trigger_ratio:.2f}%
最遠觸發測站: {farthest_sta}
最遠觸發距離: {max_dist_km:.2f} km
震央位置: ({epicenter_lon:.4f}, {epicenter_lat:.4f})"""
                    
                    return temp_path, stats_text
                    
                except Exception as e:
                    import traceback
                    error_msg = f"錯誤：{str(e)}\n\n{traceback.format_exc()}"
                    return None, error_msg
            
            generate_map_btn.click(
                fn=generate_trigger_map,
                inputs=[rep_file, station_file, epi_lon, epi_lat],
                outputs=[map_output, map_stats]
            )
        
        with gr.Tab("🎯 互動式展示"):
            gr.Markdown(
                """
                ### 地震預警效能互動展示
                
                此功能展示地震預警系統的效能分析與視覺化功能。
                """
            )
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("""
                    #### 模擬資料範例
                    以下展示地震預警系統可能的分析結果：
                    """)
                    
                    demo_stats = gr.DataFrame(
                        value=pd.DataFrame({
                            "項目": [
                                "平均報告時間",
                                "最快報告時間",
                                "最慢報告時間",
                                "觸發測站數",
                                "涵蓋縣市數"
                            ],
                            "數值": ["8.5 秒", "3.2 秒", "15.8 秒", "45 站", "12 縣市"]
                        }),
                        label="效能統計摘要",
                        interactive=False
                    )
                    
                with gr.Column():
                    gr.Markdown("""
                    #### 系統特色
                    """)
                    gr.Markdown("""
                    - ⚡ **快速反應**：平均 8.5 秒內發出預警
                    - 🗺️ **廣泛覆蓋**：涵蓋全台主要縣市
                    - 📊 **精準分析**：整合多站資料提高準確度
                    - 🔍 **品質控制**：持續監控系統效能
                    """)
            
            gr.Markdown("""
            ---
            #### 資料視覺化範例
            
            地震預警系統可產生以下類型的視覺化圖表：
            
            1. **報告時間分析圖**：顯示各測站的報告時間分布
            2. **觸發地圖**：顯示觸發的測站位置與震度
            3. **震央區域圖**：顯示震央位置與周圍測站
            4. **縣市統計圖**：依縣市統計觸發情況
            5. **時序分析圖**：顯示預警系統的時間演進
            
            若要產生實際的分析圖表，請使用對應的 Python 腳本並提供資料檔案。
            """)
            
            def generate_sample_plot():
                """Generate a sample performance plot"""
                import matplotlib
                # Try to set a font that supports Chinese characters
                try:
                    matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'Microsoft YaHei', 'SimHei']
                    matplotlib.rcParams['axes.unicode_minus'] = False
                except:
                    pass  # Fall back to default if font setting fails
                
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
                
                # Sample reporting time plot
                stations = [f'STA{i:02d}' for i in range(1, 11)]
                times = np.random.uniform(3, 15, 10)
                colors = ['green' if t < 8 else 'orange' if t < 12 else 'red' for t in times]
                
                ax1.barh(stations, times, color=colors, alpha=0.7)
                ax1.set_xlabel('報告時間（秒）', fontsize=12)
                ax1.set_ylabel('測站', fontsize=12)
                ax1.set_title('測站報告時間分布（範例）', fontsize=14, fontweight='bold')
                ax1.axvline(x=8.5, color='blue', linestyle='--', linewidth=2, label='平均時間')
                ax1.legend()
                ax1.grid(axis='x', alpha=0.3)
                
                # Sample intensity distribution
                intensities = ['0', '1', '2', '3', '4', '5-', '5+', '6-', '6+']
                counts = [120, 85, 65, 45, 30, 18, 10, 5, 2]
                colors_int = ['lightgreen', 'yellow', 'gold', 'orange', 'darkorange', 
                             'red', 'darkred', 'purple', 'darkviolet']
                
                ax2.bar(intensities, counts, color=colors_int, alpha=0.7, edgecolor='black')
                ax2.set_xlabel('震度級距', fontsize=12)
                ax2.set_ylabel('測站數量', fontsize=12)
                ax2.set_title('震度分布統計（範例）', fontsize=14, fontweight='bold')
                ax2.grid(axis='y', alpha=0.3)
                
                plt.tight_layout()
                
                # Save to temporary file with automatic cleanup
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png', dir='/tmp') as temp_file:
                    temp_path = temp_file.name
                    plt.savefig(temp_path, dpi=100, bbox_inches='tight')
                plt.close()
                
                return temp_path
            
            demo_button = gr.Button("產生範例圖表", variant="primary")
            demo_plot = gr.Image(label="地震預警效能分析圖表", type="filepath")
            demo_button.click(fn=generate_sample_plot, outputs=demo_plot)
        
        gr.Markdown(
            """
            ---
            
            ### 注意事項
            
            這是地震預警品質控制工具的網頁介面。原始腳本是設計為使用特定資料檔案從命令列執行。
            本介面提供說明文件、環境測試功能以及互動式展示範例。
            
            若要使用這些工具的完整功能，請複製儲存庫並使用您的地震預警資料檔案在本地執行腳本。
            
            **儲存庫：**[github.com/oceanicdayi/EEW_quality_control](https://github.com/oceanicdayi/EEW_quality_control)
            """
        )
    
    return demo


if __name__ == "__main__":
    demo = create_interface()
    demo.launch()
