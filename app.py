#!/usr/bin/env python3
"""
Taiwan Earthquake Data Fetcher
使用 ObsPy 從 IRIS FDSN 抓取臺灣地震記錄和波形資料
"""

import gradio as gr
import io
import base64
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

_obspy_import_error = None

try:
    import setuptools  # noqa: F401 - ensure pkg_resources is available (Python 3.12+)
    from obspy import UTCDateTime
    from obspy.clients.fdsn import Client
    OBSPY_AVAILABLE = True
except ImportError as e:
    OBSPY_AVAILABLE = False
    _obspy_import_error = str(e)

# IRIS FDSN 客戶端（延遲初始化）
_client = None

def get_client():
    """獲取或初始化 IRIS FDSN 客戶端"""
    if not OBSPY_AVAILABLE:
        hint = ""
        if "pkg_resources" in (_obspy_import_error or ""):
            hint = "\n提示：此錯誤通常發生在 Python 3.12+ 環境中，請先安裝 setuptools：pip install setuptools"
        raise Exception(
            f"ObsPy 未安裝或無法匯入: {_obspy_import_error}\n\n"
            f"請確認已安裝所有系統相依套件。{hint}"
        )
    global _client
    if _client is None:
        try:
            _client = Client("IRIS")
        except Exception as e:
            raise Exception(f"無法連接到 IRIS FDSN 服務: {str(e)}\n\n請檢查網路連線或稍後再試。")
    return _client

def search_earthquakes(start_date, end_date, min_magnitude, max_magnitude, 
                      min_depth, max_depth, min_latitude, max_latitude, 
                      min_longitude, max_longitude):
    """
    搜尋臺灣地震記錄
    
    Parameters:
    -----------
    start_date, end_date : str
        搜尋時間範圍
    min_magnitude, max_magnitude : float
        震級範圍
    min_depth, max_depth : float
        深度範圍（公里）
    min_latitude, max_latitude : float
        緯度範圍
    min_longitude, max_longitude : float
        經度範圍
    
    Returns:
    --------
    str : 搜尋結果文字
    """
    try:
        # 獲取客戶端
        client = get_client()
        
        # 轉換日期格式
        starttime = UTCDateTime(start_date)
        endtime = UTCDateTime(end_date)
        
        # 搜尋地震目錄
        catalog = client.get_events(
            starttime=starttime,
            endtime=endtime,
            minmagnitude=min_magnitude,
            maxmagnitude=max_magnitude,
            mindepth=min_depth,
            maxdepth=max_depth,
            minlatitude=min_latitude,
            maxlatitude=max_latitude,
            minlongitude=min_longitude,
            maxlongitude=max_longitude
        )
        
        if len(catalog) == 0:
            return "未找到符合條件的地震記錄"
        
        # 格式化輸出
        result = f"找到 {len(catalog)} 筆地震記錄:\n\n"
        result += "=" * 80 + "\n"
        
        for i, event in enumerate(catalog, 1):
            origin = event.preferred_origin() or event.origins[0]
            magnitude = event.preferred_magnitude() or event.magnitudes[0]
            
            result += f"\n地震 #{i}:\n"
            result += f"  時間: {origin.time}\n"
            result += f"  震級: {magnitude.mag:.1f} ({magnitude.magnitude_type})\n"
            result += f"  位置: {origin.latitude:.3f}°N, {origin.longitude:.3f}°E\n"
            result += f"  深度: {origin.depth/1000:.1f} km\n"
            
            if origin.region:
                result += f"  區域: {origin.region}\n"
            
            result += "-" * 80 + "\n"
        
        return result
        
    except Exception as e:
        return f"錯誤: {str(e)}\n\n請檢查搜尋條件是否正確，或確認網路連線正常。"


def fetch_waveforms(event_time, latitude, longitude, networks, stations, 
                   channels, duration_before, duration_after):
    """
    抓取地震波形資料
    
    Parameters:
    -----------
    event_time : str
        地震發生時間
    latitude, longitude : float
        地震位置
    networks : str
        網路代碼（逗號分隔，如 "TW,IU"）
    stations : str
        測站代碼（逗號分隔，留空表示全部）
    channels : str
        通道代碼（如 "BH*" 表示所有寬頻通道）
    duration_before, duration_after : float
        事件前後的時間長度（秒）
    
    Returns:
    --------
    str : 波形資料資訊
    fig : matplotlib figure
    """
    try:
        # 獲取客戶端
        client = get_client()
        
        # 轉換時間
        event_time_utc = UTCDateTime(event_time)
        starttime = event_time_utc - duration_before
        endtime = event_time_utc + duration_after
        
        # 處理網路和測站列表
        network_list = [n.strip() for n in networks.split(',') if n.strip()]
        station_list = [s.strip() for s in stations.split(',') if s.strip()] if stations.strip() else ["*"]
        
        # 抓取波形資料
        all_streams = []
        info_text = f"正在抓取波形資料...\n"
        info_text += f"時間範圍: {starttime} 至 {endtime}\n"
        info_text += f"網路: {', '.join(network_list)}\n\n"
        
        for network in network_list:
            for station in station_list:
                try:
                    st = client.get_waveforms(
                        network=network,
                        station=station,
                        location="*",
                        channel=channels,
                        starttime=starttime,
                        endtime=endtime
                    )
                    
                    if len(st) > 0:
                        all_streams.append(st)
                        info_text += f"✓ {network}.{station}: 找到 {len(st)} 個通道\n"
                        
                except Exception as e:
                    info_text += f"✗ {network}.{station}: {str(e)}\n"
        
        if len(all_streams) == 0:
            return "未找到符合條件的波形資料", None
        
        # 合併所有波形
        from obspy import Stream
        combined_stream = Stream()
        for st in all_streams:
            combined_stream += st
        
        info_text += f"\n總共抓取到 {len(combined_stream)} 個波形通道\n"
        info_text += "=" * 80 + "\n\n"
        
        # 列出所有波形
        info_text += "波形清單:\n"
        for i, tr in enumerate(combined_stream, 1):
            info_text += f"{i}. {tr.id} | {tr.stats.starttime} | "
            info_text += f"取樣率: {tr.stats.sampling_rate} Hz | "
            info_text += f"資料點: {tr.stats.npts}\n"
        
        # 繪製波形圖
        fig = plot_waveforms(combined_stream, event_time_utc, latitude, longitude)
        
        return info_text, fig
        
    except Exception as e:
        import traceback
        return f"錯誤: {str(e)}\n\n{traceback.format_exc()}", None


def plot_waveforms(stream, event_time, event_lat, event_lon):
    """
    繪製波形圖
    
    Parameters:
    -----------
    stream : obspy.Stream
        波形資料流
    event_time : UTCDateTime
        地震發生時間
    event_lat, event_lon : float
        地震位置
    
    Returns:
    --------
    matplotlib.figure.Figure
    """
    # 設定中文字體
    try:
        matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Microsoft YaHei', 'SimHei']
        matplotlib.rcParams['axes.unicode_minus'] = False
    except:
        pass
    
    # 限制繪製的波形數量
    max_traces = min(10, len(stream))
    
    fig, axes = plt.subplots(max_traces, 1, figsize=(14, max_traces * 1.5))
    if max_traces == 1:
        axes = [axes]
    
    for i, tr in enumerate(stream[:max_traces]):
        ax = axes[i]
        
        # 準備資料
        times = tr.times()
        data = tr.data
        
        # 繪製波形
        ax.plot(times, data, 'k-', linewidth=0.5)
        
        # 標記地震發生時間
        if event_time:
            event_offset = event_time - tr.stats.starttime
            if 0 <= event_offset <= times[-1]:
                ax.axvline(event_offset, color='r', linestyle='--', linewidth=2, 
                          label='地震發生', alpha=0.7)
        
        # 設定標籤
        ax.set_ylabel(f'{tr.id}\n振幅', fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', fontsize=7)
        
        # 只在最後一個子圖顯示 x 軸標籤
        if i == max_traces - 1:
            ax.set_xlabel('時間 (秒)', fontsize=10)
        else:
            ax.set_xticklabels([])
    
    # 設定標題
    title = f'地震波形資料\n'
    title += f'地震時間: {event_time} | 位置: {event_lat:.3f}°N, {event_lon:.3f}°E\n'
    title += f'顯示前 {max_traces} 個通道（共 {len(stream)} 個）'
    fig.suptitle(title, fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    
    return fig


def create_earthquake_map(catalog_text):
    """
    繪製地震分布地圖
    
    Parameters:
    -----------
    catalog_text : str
        地震目錄文字
    
    Returns:
    --------
    matplotlib.figure.Figure
    """
    try:
        # 從文字中解析地震資料
        lines = catalog_text.split('\n')
        lats, lons, mags, depths = [], [], [], []
        
        for i, line in enumerate(lines):
            if '位置:' in line:
                # 解析位置
                parts = line.split(':')[1].split(',')
                lat = float(parts[0].replace('°N', '').strip())
                lon = float(parts[1].replace('°E', '').strip())
                lats.append(lat)
                lons.append(lon)
                
                # 解析震級
                mag_line = lines[i-1]
                mag = float(mag_line.split(':')[1].split()[0])
                mags.append(mag)
                
                # 解析深度
                depth_line = lines[i+1]
                depth = float(depth_line.split(':')[1].split()[0])
                depths.append(depth)
        
        if len(lats) == 0:
            return None
        
        # 設定中文字體
        try:
            matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Microsoft YaHei', 'SimHei']
            matplotlib.rcParams['axes.unicode_minus'] = False
        except:
            pass
        
        # 繪製地圖
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 左圖：地震分布
        scatter = ax1.scatter(lons, lats, c=depths, s=[m**2*10 for m in mags], 
                            alpha=0.6, cmap='viridis_r', edgecolors='black', linewidth=0.5)
        ax1.set_xlabel('經度 (°E)', fontsize=11)
        ax1.set_ylabel('緯度 (°N)', fontsize=11)
        ax1.set_title('地震分布圖\n（大小表示震級，顏色表示深度）', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # 添加台灣輪廓參考
        ax1.plot([120, 122], [22, 22], 'k--', alpha=0.3, linewidth=0.5)
        ax1.plot([120, 122], [25, 25], 'k--', alpha=0.3, linewidth=0.5)
        ax1.plot([120, 120], [22, 25], 'k--', alpha=0.3, linewidth=0.5)
        ax1.plot([122, 122], [22, 25], 'k--', alpha=0.3, linewidth=0.5)
        
        cbar = plt.colorbar(scatter, ax=ax1)
        cbar.set_label('深度 (km)', fontsize=10)
        
        # 右圖：震級-深度關係
        scatter2 = ax2.scatter(mags, depths, c=depths, s=100, 
                              alpha=0.6, cmap='viridis_r', edgecolors='black', linewidth=0.5)
        ax2.set_xlabel('震級', fontsize=11)
        ax2.set_ylabel('深度 (km)', fontsize=11)
        ax2.set_title('震級-深度關係圖', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.invert_yaxis()
        
        plt.tight_layout()
        
        return fig
        
    except Exception as e:
        print(f"繪製地圖時發生錯誤: {e}")
        return None


def create_interface():
    """建立 Gradio 介面"""
    
    with gr.Blocks(title="臺灣地震資料查詢系統", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # 🌏 臺灣地震資料查詢系統
            
            使用 ObsPy 從 IRIS FDSN 抓取臺灣地震記錄和地震波形資料
            
            ## 功能說明
            
            1. **地震目錄查詢**：搜尋特定時間和區域的地震記錄
            2. **地震波形抓取**：下載地震事件的波形資料（支援 TW 和 IU 網路）
            3. **資料視覺化**：繪製地震分布圖和波形圖
            
            ---
            """
        )
        
        with gr.Tab("📋 地震目錄查詢"):
            gr.Markdown(
                """
                ### 搜尋地震記錄
                
                設定搜尋條件以查詢臺灣地區的地震記錄。預設範圍涵蓋臺灣本島及周邊海域。
                """
            )
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### 時間範圍")
                    start_date = gr.Textbox(
                        label="開始日期",
                        value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                        placeholder="YYYY-MM-DD"
                    )
                    end_date = gr.Textbox(
                        label="結束日期",
                        value=datetime.now().strftime("%Y-%m-%d"),
                        placeholder="YYYY-MM-DD"
                    )
                    
                    gr.Markdown("#### 震級範圍")
                    with gr.Row():
                        min_mag = gr.Number(label="最小震級", value=4.0)
                        max_mag = gr.Number(label="最大震級", value=10.0)
                    
                    gr.Markdown("#### 深度範圍（公里）")
                    with gr.Row():
                        min_depth = gr.Number(label="最小深度", value=0)
                        max_depth = gr.Number(label="最大深度", value=700)
                
                with gr.Column():
                    gr.Markdown("#### 地理範圍（臺灣及周邊）")
                    with gr.Row():
                        min_lat = gr.Number(label="最小緯度", value=21.0)
                        max_lat = gr.Number(label="最大緯度", value=26.0)
                    with gr.Row():
                        min_lon = gr.Number(label="最小經度", value=119.0)
                        max_lon = gr.Number(label="最大經度", value=123.0)
                    
                    gr.Markdown(
                        """
                        **參考範圍**：
                        - 臺灣本島：約 21.9°N-25.3°N, 120.0°E-122.0°E
                        - 預設範圍包含周邊海域
                        """
                    )
            
            search_btn = gr.Button("🔍 搜尋地震記錄", variant="primary", size="lg")
            
            with gr.Row():
                catalog_output = gr.Textbox(
                    label="搜尋結果",
                    lines=15,
                    max_lines=25,
                    interactive=False
                )
            
            with gr.Row():
                map_output = gr.Plot(label="地震分布圖")
            
            # 連接搜尋功能
            search_btn.click(
                fn=search_earthquakes,
                inputs=[start_date, end_date, min_mag, max_mag, min_depth, max_depth,
                       min_lat, max_lat, min_lon, max_lon],
                outputs=catalog_output
            )
            
            # 連接地圖繪製功能
            catalog_output.change(
                fn=create_earthquake_map,
                inputs=catalog_output,
                outputs=map_output
            )
        
        with gr.Tab("📊 地震波形抓取"):
            gr.Markdown(
                """
                ### 抓取地震波形資料
                
                使用 TW（臺灣）和 IU（全球地震網）網路的測站資料。請先在「地震目錄查詢」中找到感興趣的地震事件。
                """
            )
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### 地震事件資訊")
                    event_time = gr.Textbox(
                        label="地震時間",
                        placeholder="YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DDTHH:MM:SS",
                        info="從地震目錄中複製時間"
                    )
                    with gr.Row():
                        event_lat = gr.Number(label="緯度", value=23.5)
                        event_lon = gr.Number(label="經度", value=121.0)
                    
                    gr.Markdown("#### 資料抓取設定")
                    networks = gr.Textbox(
                        label="網路代碼",
                        value="TW,IU",
                        info="逗號分隔，例如：TW,IU"
                    )
                    stations = gr.Textbox(
                        label="測站代碼（選填）",
                        placeholder="留空表示全部測站",
                        info="逗號分隔，例如：TPUB,YULB 或留空"
                    )
                    channels = gr.Textbox(
                        label="通道代碼",
                        value="BH*",
                        info="例如：BH* 表示所有寬頻通道"
                    )
                
                with gr.Column():
                    gr.Markdown("#### 時間窗設定")
                    duration_before = gr.Number(
                        label="事件前時間（秒）",
                        value=60,
                        info="地震發生前抓取的時間長度"
                    )
                    duration_after = gr.Number(
                        label="事件後時間（秒）",
                        value=300,
                        info="地震發生後抓取的時間長度"
                    )
                    
                    gr.Markdown(
                        """
                        **說明**：
                        - **TW 網路**：臺灣地震科學中心（TEC）測站
                        - **IU 網路**：IRIS/USGS 全球地震網測站
                        - **通道代碼**：
                          - BH*: 寬頻高增益（20-50 Hz）
                          - HH*: 高頻高增益（80-250 Hz）
                          - LH*: 長週期（1 Hz）
                        """
                    )
            
            fetch_btn = gr.Button("📡 抓取波形資料", variant="primary", size="lg")
            
            with gr.Row():
                waveform_info = gr.Textbox(
                    label="波形資料資訊",
                    lines=12,
                    max_lines=20,
                    interactive=False
                )
            
            with gr.Row():
                waveform_plot = gr.Plot(label="波形圖")
            
            # 連接波形抓取功能
            fetch_btn.click(
                fn=fetch_waveforms,
                inputs=[event_time, event_lat, event_lon, networks, stations, 
                       channels, duration_before, duration_after],
                outputs=[waveform_info, waveform_plot]
            )
        
        with gr.Tab("ℹ️ 使用說明"):
            gr.Markdown(
                """
                ## 系統說明
                
                ### 資料來源
                
                本系統使用 IRIS（Incorporated Research Institutions for Seismology）
                的 FDSN（International Federation of Digital Seismograph Networks）服務，
                提供全球地震目錄和波形資料。
                
                ### 使用步驟
                
                #### 1. 查詢地震目錄
                
                - 在「地震目錄查詢」頁面設定搜尋條件
                - 預設範圍涵蓋臺灣及周邊區域
                - 點擊「搜尋地震記錄」按鈕
                - 系統會顯示符合條件的地震列表和分布圖
                
                #### 2. 抓取波形資料
                
                - 從地震目錄中選擇感興趣的地震事件
                - 複製地震的時間和位置資訊
                - 在「地震波形抓取」頁面輸入事件資訊
                - 選擇網路（TW、IU 或兩者）
                - 可選擇特定測站或抓取所有測站資料
                - 設定時間窗（預設為事件前 60 秒、事件後 300 秒）
                - 點擊「抓取波形資料」按鈕
                - 系統會顯示波形資訊和波形圖
                
                ### 網路說明
                
                #### TW 網路
                
                臺灣地震科學中心（Taiwan Earthquake Center）運營的測站網路，
                提供臺灣地區的高品質地震觀測資料。
                
                #### IU 網路
                
                IRIS/USGS 全球地震網（Global Seismographic Network），
                在臺灣也有部分測站，提供全球標準的地震觀測資料。
                
                ### 技術細節
                
                - **ObsPy**：Python 地震學資料處理工具
                - **FDSN 服務**：標準化的地震資料查詢協定
                - **時間格式**：UTC 時間
                - **資料格式**：miniSEED（波形資料）
                
                ### 常見問題
                
                **Q: 為什麼有些時段找不到資料？**
                
                A: 可能的原因包括：
                - 該時段沒有符合條件的地震
                - 測站在該時段未運作
                - 網路連線問題
                - FDSN 服務暫時不可用
                
                **Q: 如何選擇合適的時間窗？**
                
                A: 建議：
                - 近震（< 100 km）：前 30 秒、後 120 秒
                - 區域地震（100-1000 km）：前 60 秒、後 300 秒
                - 遠震（> 1000 km）：前 120 秒、後 600 秒
                
                **Q: 資料可以下載嗎？**
                
                A: 目前版本主要用於線上查詢和視覺化。如需下載原始資料，
                建議使用 ObsPy 或直接從 IRIS 的 FDSN 服務下載。
                
                ### 相關連結
                
                - [IRIS DMC](https://ds.iris.edu/ds/nodes/dmc/)
                - [ObsPy 文件](https://docs.obspy.org/)
                - [FDSN 網路服務](https://www.fdsn.org/webservices/)
                - [台灣地震科學中心](https://tec.earth.sinica.edu.tw/)
                
                ### 授權資訊
                
                本系統使用的地震資料來自 IRIS FDSN 服務，資料使用請遵循
                IRIS 資料使用政策。
                
                ---
                
                **開發者**：oceanicdayi  
                **專案**：[EEW_quality_control](https://github.com/oceanicdayi/EEW_quality_control)  
                **版本**：2.0.0
                """
            )
        
        gr.Markdown(
            """
            ---
            
            ### 注意事項
            
            - 本系統需要網路連線以存取 IRIS FDSN 服務
            - 資料查詢可能需要幾秒到幾十秒，請耐心等候
            - 大量資料查詢可能較慢，建議適當限制搜尋範圍
            - 所有時間均為 UTC 時間（臺灣時間 = UTC + 8）
            
            **系統狀態**：🟢 正常運作
            """
        )
    
    return demo


if __name__ == "__main__":
    demo = create_interface()
    demo.launch()
