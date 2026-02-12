import gradio as gr
import folium
from folium.plugins import MarkerCluster
from obspy.clients.fdsn import Client
from obspy import UTCDateTime
import warnings

# 忽略 Obspy 的特定警告
warnings.filterwarnings("ignore", message="The coordinates conversion method is not specified.*")

def get_earthquake_map(start_time_str, end_time_str, min_mag, max_mag):
    """
    從 IRIS FDSN 獲取地震目錄並在 Folium 地圖上繪製。
    """
    try:
        # 1. 轉換時間字串為 UTCDateTime 物件
        start_time = UTCDateTime(start_time_str)
        end_time = UTCDateTime(end_time_str)

        # 2. 初始化 FDSN 客戶端
        client = Client("IRIS")

        # 3. 獲取地震目錄
        catalog = client.get_events(
            starttime=start_time,
            endtime=end_time,
            minmagnitude=min_mag,
            maxmagnitude=max_mag
        )

        # 4. 建立 Folium 地圖
        # 以台灣為中心點，但可以調整
        m = folium.Map(location=[23.5, 121], zoom_start=6, tiles="CartoDB positron")

        if not catalog:
            # 如果沒有找到事件，回傳一個空地圖和訊息
            folium.Marker(
                [23.5, 121], 
                popup="在指定範圍內沒有找到地震事件。"
            ).add_to(m)
            return m._repr_html_()

        # 5. 建立一個 MarkerCluster
        marker_cluster = MarkerCluster().add_to(m)

        # 6. 遍歷地震事件並添加到地圖
        for event in catalog:
            try:
                # 獲取首選的震源和規模
                origin = event.preferred_origin()
                magnitude = event.preferred_magnitude()

                if not origin or not magnitude:
                    continue

                lat = origin.latitude
                lon = origin.longitude
                # 深度（公尺），轉換為公里
                depth_km = origin.depth / 1000.0 if origin.depth else 0
                mag_value = magnitude.mag
                mag_type = magnitude.magnitude_type
                event_time = origin.time.strftime('%Y-%m-%d %H:%M:%S UTC')

                # 建立彈出視窗的 HTML
                popup_html = f"""
                <b>時間:</b> {event_time}<br>
                <b>規模:</b> {mag_value:.1f} ({mag_type})<br>
                <b>深度:</b> {depth_km:.1f} km<br>
                <b>位置:</b> ({lat:.2f}, {lon:.2f})
                """

                # 根據規模設定圓圈大小
                radius = mag_value * 2

                # 添加 CircleMarker 到 MarkerCluster
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=radius,
                    popup=folium.Popup(popup_html, max_width=300),
                    color="red",
                    fill=True,
                    fill_color="red",
                    fill_opacity=0.4
                ).add_to(marker_cluster)
                
            except Exception as e:
                # 忽略單一事件的錯誤
                print(f"處理事件時發生錯誤: {e}")

        # 添加圖層控制器
        folium.LayerControl().add_to(m)

        # 7. 回傳地圖的 HTML 內容
        return m._repr_html_()

    except Exception as e:
        # 處理主要錯誤 (例如 FDSN 服務無法連線或時間格式錯誤)
        return f"<p style='color:red;'>查詢時發生錯誤：{e}</p>"

# 建立 Gradio 介面
with gr.Blocks(title="地震目錄視覺化") as demo:
    gr.Markdown("# IRIS FDSN 地震目錄地圖")
    gr.Markdown("使用 Obspy 從 IRIS FDSN 抓取地震目錄，並使用 Folium 繪製互動式地圖。")
    
    with gr.Row():
        start_time_input = gr.Textbox(
            label="開始時間 (UTC)", 
            value="2024-04-02T16:00:00",
            info="格式: YYYY-MM-DDTHH:MM:SS"
        )
        end_time_input = gr.Textbox(
            label="結束時間 (UTC)", 
            value="2024-04-03T16:00:00",
            info="格式: YYYY-MM-DDTHH:MM:SS"
        )
    
    with gr.Row():
        min_mag_input = gr.Slider(
            label="最小規模", 
            minimum=0.0, 
            maximum=10.0, 
            value=4.0, 
            step=0.1
        )
        max_mag_input = gr.Slider(
            label="最大規模", 
            minimum=0.0, 
            maximum=10.0, 
            value=10.0, 
            step=0.1
        )
        
    submit_btn = gr.Button("查詢並繪製地圖", variant="primary")
    
    # 輸出元件：使用 gr.HTML 來顯示 Folium 地圖
    map_output = gr.HTML(label="地震分佈圖")

    # 綁定按鈕點擊事件
    submit_btn.click(
        fn=get_earthquake_map,
        inputs=[start_time_input, end_time_input, min_mag_input, max_mag_input],
        outputs=[map_output]
    )
    
    gr.Examples(
        [
            ["2011-03-10T00:00:00", "2011-03-12T00:00:00", 7.0, 10.0], # 2011 日本東北大地震
            ["2024-04-02T16:00:00", "2024-04-04T00:00:00", 5.0, 10.0], # 2024 台灣花蓮地震
            ["2023-02-06T00:00:00", "2023-02-07T00:00:00", 6.0, 10.0]  # 2023 土耳其大地震
        ],
        inputs=[start_time_input, end_time_input, min_mag_input, max_mag_input]
    )

if __name__ == "__main__":
    demo.launch()
