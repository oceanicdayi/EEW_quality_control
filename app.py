import gradio as gr
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
import matplotlib.pyplot as plt
import matplotlib
import io

# 設定 Matplotlib 後端為 Agg，避免在無螢幕環境(Server)報錯
matplotlib.use('Agg')

def fetch_earthquake_data(start_time_str, end_time_str, min_mag, request_waveforms):
    """
    主要處理函數：搜尋地震並抓取波形
    """
    client = Client("IRIS")
    
    # 1. 解析時間
    try:
        t1 = UTCDateTime(start_time_str)
        t2 = UTCDateTime(end_time_str)
    except:
        return None, None, "❌ 時間格式錯誤，請使用 YYYY-MM-DD 格式 (例如: 2024-04-03)"

    # 2. 定義台灣的大致經緯度範圍
    min_lat, max_lat = 21.0, 26.0
    min_lon, max_lon = 119.0, 123.0

    status_log = []
    status_log.append(f"🔍 正在搜尋 {t1.date} 到 {t2.date} 規模 > {min_mag} 的地震...")

    # 3. 搜尋地震目錄 (Catalog)
    try:
        catalog = client.get_events(
            starttime=t1,
            endtime=t2,
            minmagnitude=min_mag,
            minlatitude=min_lat,
            maxlatitude=max_lat,
            minlongitude=min_lon,
            maxlongitude=max_lon
        )
        status_log.append(f"✅ 找到 {len(catalog)} 起地震。")
    except Exception as e:
        return None, None, f"❌ 搜尋地震目錄失敗: {str(e)}"

    if len(catalog) == 0:
        return None, None, "⚠️ 此條件下未找到任何地震紀錄。"

    # 4. 繪製地震分佈圖 (Map)
    # 為了避免 ObsPy 內建 plot 依賴 Basemap/Cartopy 在雲端環境出錯，我們用純 Matplotlib 畫簡單散佈圖
    fig_map = plt.figure(figsize=(10, 6))
    lats = []
    lons = []
    mags = []
    
    for event in catalog:
        origin = event.preferred_origin() or event.origins[0]
        mag = event.preferred_magnitude() or event.magnitudes[0]
        lats.append(origin.latitude)
        lons.append(origin.longitude)
        mags.append(mag.mag)

    plt.scatter(lons, lats, s=[m**3 for m in mags], c=mags, cmap='Reds', alpha=0.7, edgecolors='k')
    plt.colorbar(label='Magnitude')
    plt.title(f"Earthquakes in Taiwan Region ({t1.date} - {t2.date})")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # 標示台灣範圍框
    plt.xlim(min_lon-0.5, max_lon+0.5)
    plt.ylim(min_lat-0.5, max_lat+0.5)

    # 5. 抓取波形 (Waveforms)
    fig_wave = None
    
    if request_waveforms and len(catalog) > 0:
        # 為了演示，我們只抓取「規模最大」的那一個地震
        target_event = max(catalog, key=lambda e: (e.preferred_magnitude() or e.magnitudes[0]).mag)
        origin = target_event.preferred_origin() or target_event.origins[0]
        event_time = origin.time
        
        mag_val = (target_event.preferred_magnitude() or target_event.magnitudes[0]).mag
        status_log.append(f"🌊 正在抓取最大地震 (M{mag_val}, {event_time}) 的波形數據...")
        status_log.append("   目標測站網: IU, TW (IRIS 資料庫)")

        try:
            # 設定抓取波形的參數
            # 注意：IRIS 上不一定有完整的 TW 網路即時資料，通常 IU (Global Seismograph Network) 較穩定
            st = client.get_waveforms(
                network="TW,IU",      # 台灣寬頻網 與 全球網
                station="*",          # 所有測站
                location="*",
                channel="BHZ,HHZ",    # 只抓垂直分量以節省流量
                starttime=event_time,
                endtime=event_time + 120, # 抓取起始後 120 秒
                attach_response=False 
            )
            
            if len(st) > 0:
                status_log.append(f"✅ 成功下載 {len(st)} 條波形紀錄。")
                
                # 簡單的波形繪圖
                fig_wave = plt.figure(figsize=(10, 8))
                st.plot(fig=fig_wave, type='relative') # 使用 ObsPy 的繪圖功能並注入 figure
            else:
                status_log.append("⚠️ 伺服器回應無波形資料 (可能是 IRIS 沒有該時段 TW 網資料)。")

        except Exception as e:
            status_log.append(f"⚠️ 波形下載失敗或部分遺失: {str(e)}")

    # 整理輸出文字
    result_text = "\n".join(status_log)
    
    return fig_map, fig_wave, result_text

# --- Gradio 介面設定 ---

with gr.Blocks(title="台灣地震資料檢索 (IRIS FDSN)") as demo:
    gr.Markdown("# 🇹🇼 台灣地震資料檢索系統 (Based on ObsPy & IRIS)")
    gr.Markdown("此工具透過 IRIS FDSN Client 搜尋台灣區域地震，並嘗試從 `IU` (全球網) 與 `TW` (台灣網) 抓取波形。")
    
    with gr.Row():
        with gr.Column():
            start_date = gr.Textbox(value="2024-04-03", label="開始日期 (YYYY-MM-DD)")
            end_date = gr.Textbox(value="2024-04-04", label="結束日期 (YYYY-MM-DD)")
            min_mag = gr.Slider(minimum=3.0, maximum=9.0, value=5.0, step=0.1, label="最小規模 (Magnitude)")
            get_wave = gr.Checkbox(value=True, label="同時下載最大地震之波形 (會較慢)")
            submit_btn = gr.Button("開始搜尋", variant="primary")
        
        with gr.Column():
            output_log = gr.Textbox(label="執行狀態與結果", lines=6)
    
    with gr.Row():
        map_plot = gr.Plot(label="地震分佈圖")
        wave_plot = gr.Plot(label="地震波形圖 (最大事件)")

    submit_btn.click(
        fn=fetch_earthquake_data,
        inputs=[start_date, end_date, min_mag, get_wave],
        outputs=[map_plot, wave_plot, output_log]
    )

# 啟動應用
if __name__ == "__main__":
    demo.launch()
