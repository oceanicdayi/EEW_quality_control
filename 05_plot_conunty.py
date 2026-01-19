import argparse
import pygmt
import os
import math

# --- 1. 檔案設定 ---
gmt_file = "city_2016.gmt"
status_file = "county_list.txt"
bg_temp = "temp_background.gmt"
hl_temp = "temp_highlight.gmt"

parser = argparse.ArgumentParser(description="Plot county map")
parser.add_argument("--epi-lon", type=float, required=True, help="震央經度")
parser.add_argument("--epi-lat", type=float, required=True, help="震央緯度")
parser.add_argument("--start-seconds", type=float, default=10, help="起始秒數（預設 10）")
args = parser.parse_args()

epicenter = [args.epi_lon, args.epi_lat]
start_dist = args.start_seconds * 3.5          # 起始距離 (km)
dist_step = 32               # 距離增量 (km) -> 對應每 5s 一格
start_time = 0               # 起始標記時間
time_step = 10               # 時間增量 (秒)
num_circles = 10              # 預計繪製的圓圈數量

# --- 2. 更加強健的讀取方式 ---
highlight_targets = []
print(f"--- 正在檢查 {status_file} 內容 ---")

if os.path.exists(status_file):
    # 使用 utf-8-sig 處理可能存在的 BOM，errors='ignore' 處理特殊字元
    with open(status_file, "r", encoding="utf-8-sig", errors="ignore") as f:
        for line in f:
            words = line.split()
            if len(words) >= 2:
                # 【修改點】：最後一個單字永遠是標記，前面所有單字組合為縣市名
                mark = words[-1].strip()
                name = " ".join(words[:-1]).strip()
                
                # 只要標記包含 '1' 就列入清單 (處理 1.0 或 1 帶空格的情況)
                if "0" in mark:
                    highlight_targets.append(name)
                    print(f"   找到目標: [{name}] (標記為 {mark})")
                else:
                    print(f"   跳過縣市: [{name}] (標記為 {mark})")

print(f"✅ 讀取完成，最終上色名單: {highlight_targets}\n")

if not highlight_targets:
    print("⚠️ 警告：上色名單為空！請確認 county_status.txt 標記是否為 1。")

# --- 3. 解析 GMT 檔案 (加入狀態繼承) ---
# 因為 GMT 檔案中，縣市名稱通常只出現在該區域的第一個段落，後續段落(如島嶼)標題常為空
with open(gmt_file, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

segments = content.split(">")
is_current_seg_target = False # 用來紀錄當前區塊是否屬於要上色的縣市

with open(bg_temp, "w", encoding="utf-8") as f_bg, \
     open(hl_temp, "w", encoding="utf-8") as f_hl:
    
    for seg in segments:
        seg_text = seg.strip()
        if not seg_text or seg_text.startswith("#"):
            continue
            
        lines = seg_text.split("\n")
        header = lines[0].strip()
        
        # 【修改點】：如果標頭有名字，更新「目前是否要上色」的狀態
        if header:
            clean_header = header.replace("-L", "").replace('"', '').strip()
            # 檢查標題是否包含名單中的任何一個縣市名
            if any(target in clean_header for target in highlight_targets):
                is_current_seg_target = True
            else:
                is_current_seg_target = False
        
        # 根據狀態寫入對應檔案 (如果標頭為空，會沿用上一個有名字標頭的決定)
        full_seg = f"> {seg_text}\n"
        if is_current_seg_target:
            f_hl.write(full_seg)
        else:
            f_base.write(full_seg) if 'f_base' in locals() else f_bg.write(full_seg)


# --- 5. PyGMT 繪圖 ---
fig = pygmt.Figure()
buffer = 1
# region = [epicenter[0]-buffer, epicenter[0]+buffer, epicenter[1]-buffer, epicenter[1]+buffer]
region = [119, 123, 21, 26]
projection = "M15c"

# A. 海洋背景
fig.coast(region=region, projection=projection, water="skyblue")

# B. 畫白色背景縣市
if os.path.exists(bg_temp) and os.path.getsize(bg_temp) > 0:
    fig.plot(data=bg_temp, fill="white", pen="0.5p,black")
    # fig.plot(data=bg_temp, fill="darkseagreen1", pen="0.5p,black")

# C. 畫標記為 1 的上色縣市
if os.path.exists(hl_temp) and os.path.getsize(hl_temp) > 0:
    fig.plot(data=hl_temp, fill="gold", pen="0.5p,black")

# C.2 繪製震央
# fig.plot(x=120.51, y=23.22, style="x0.6c", fill="red", pen="1p,black")
# fig.plot(x=120.62, y=23.20, style="x0.6c", fill="red", pen="1p,black")
fig.plot(x=epicenter[0], y=epicenter[1], style="a0.8c", fill="red", pen="1p,black")

# --- 迴圈繪製同心圓（延後）與標籤 ---
fig.coast(land="c")
circle_radii = []
for i in range(num_circles):
    # 計算當前半徑與時間標籤
    current_radius = start_dist + (i * dist_step)
    current_time = start_time + (i * time_step)
    circle_radii.append((current_radius, current_time))
    
    # 繪製圓圈 (style="E" 在地理座標下參數為直徑，所以半徑要 * 2)
    # +k 代表單位為公里
    pass

fig.coast(Q=True)

# 最後繪製虛線圓圈與時間標籤（置頂）
for current_radius, current_time in circle_radii:
    fig.plot(
        x=epicenter[0],
        y=epicenter[1],
        style=f"E-{current_radius * 2}k",
        pen="0.8p,blue,dashed",
        transparency=30
    )

    # 標籤放在圓圈正下方（往南）
    angle = math.radians(270)
    dist_km = current_radius
    lon_offset = (dist_km / (111 * math.cos(math.radians(epicenter[1])))) * math.cos(angle)
    lat_offset = (dist_km / 111) * math.sin(angle)
    fig.text(
        x=epicenter[0] + lon_offset,
        y=epicenter[1] + lat_offset,
        text=f"{current_time}s",
        font="12p,Helvetica-Bold,blue",
        fill="white",
        pen="0.5p,black",
        justify="CM"
    )

# D. 比例尺
fig.basemap(frame=["a1f0.5","WSne"])

# 5. 存檔與清理
fig.savefig("outputs/05_PWS_map.png")

for tmp in [bg_temp, hl_temp]:
    if os.path.exists(tmp):
        os.remove(tmp)

print("🎯 繪圖任務完成：final_map_fixed.png")
