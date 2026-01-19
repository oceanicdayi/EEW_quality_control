import argparse
import os
import pygmt
import pandas as pd
import numpy as np

# --- 1. 資料處理 ---
parser = argparse.ArgumentParser(description="Plot EZ maps from summary")
parser.add_argument("pfile", help="Pfile 檔名，例如 17010623.P20")
parser.add_argument("--base-folder", default="./192", help="rep 檔案所在目錄（預設 ./192）")
parser.add_argument("--epi-lon", type=float, required=True, help="震央經度")
parser.add_argument("--epi-lat", type=float, required=True, help="震央緯度")
parser.add_argument(
    "--kind",
    choices=["f42", "f43", "gei", "all"],
    default="all",
    help="選擇分析類型：f42 / f43 / gei（預設 all）"
)
args = parser.parse_args()

basefolder_name = os.path.basename(os.path.normpath(args.base_folder))
pfilename = os.path.splitext(os.path.basename(args.pfile))[0]
summary_path = f"./outputs/summary_{basefolder_name}_{pfilename}.txt"

pfile = [args.epi_lon, args.epi_lat, 0.0] # 震央經度, 緯度
df = pd.read_csv(summary_path, sep=r'\s+')
if args.kind != "all":
    df = df[df["Repfile"].astype(str).str.contains(f"_{args.kind}")].copy()
    if df.empty:
        raise ValueError(f"summary 檔內沒有 {args.kind} 類型資料")
gmt_file = "city_2016.gmt"
df.columns = ['Mag', 'Lat', 'Lon', 'Depth', 'Or.', 'Ma.', 'Repfile', 'Report_time', 'Note']

# 確保數值型別
for col in ['Lon', 'Lat', 'Depth', 'Mag']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# --- 新增：計算距離並過濾範圍外資料 ---
def haversine_dist(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    return 6371 * 2 * np.arcsin(np.sqrt(a))

# 計算每個點到震央的距離 (km)
df['dist_to_epi'] = haversine_dist(df['Lon'], df['Lat'], pfile[0], pfile[1])

# 篩選出在 5km 範圍外的資料
outside_5km = df[df['dist_to_epi'] > 5.0]

# --- 2. PyGMT 主圖 ---
fig = pygmt.Figure()

# 設定範圍與底色
buffer = 0.03
min_lon, max_lon = df['Lon'].min() - buffer, df['Lon'].max() + buffer
min_lat, max_lat = df['Lat'].min() - 0.5 * buffer, df['Lat'].max() + 2 * buffer
region = [min_lon, max_lon, min_lat, max_lat] 

fig.coast(
    region=region, projection="M15c", 
    land="palegreen3", water="skyblue", 
    shorelines="1p,black", borders=["1/0.5p,black", "2/0.5p,gray30"],
    resolution="h", frame=["a0.05f0.01", "WSne"]
)
fig.plot(data=gmt_file, pen="0.5p,black")

# 繪製所有地震點
pygmt.makecpt(cmap="jet", series=[5, 20], reverse=True)
fig.plot(x=df['Lon'], y=df['Lat'], size=df['Mag']*0.1, fill=df['Depth'], 
         cmap=True, style="c", pen="0.8p,black", transparency=30)

# 繪製震央 5km 虛線圈 (直徑 10k)
fig.plot(x=pfile[0], y=pfile[1], style="E-10k", pen="1p,red")

# 標註 5km 圈
fig.text(
    x=pfile[0],
    y=pfile[1],
    text="5 km",
    font="10p,Helvetica-Bold,red",
    offset="0c/1.2c",
    fill="white@40"
)

# 繪製震央紅色星號
fig.plot(x=pfile[0], y=pfile[1], style="a0.5c", fill="red", pen="1p,black")

# --- 新增：標註 5km 以外的解名稱 ---
if not outside_5km.empty:
    fig.text(
        x=outside_5km['Lon'],
        y=outside_5km['Lat'],
        text=outside_5km['Repfile'], # 標註解的名稱 (Type 欄位)
        font="9p,Helvetica-Bold,black",
        justify="BC",            # 文字底部中心對齊點位
        offset="0c/0.5c",        # 往上偏移 0.3cm 避免壓到圓圈
        fill="white@30"          # 半透明底色增加辨識度
    )

# --- 新增：篩選 Note 有值的資料 ---
# 過濾掉 NaN 以及空字串
df_note = df[df['Note'].notnull() & (df['Note'].astype(str).str.strip() != "")].copy()

# --- 新增：標註 Note 標籤 ---
if not df_note.empty:
    fig.plot(x=df_note['Lon'], y=df_note['Lat'], size=df_note['Mag']*0.1, fill=df_note['Depth'] ,cmap=True, style="c", pen="1.2,red", transparency=30)
    
    fig.text(
        x=df_note['Lon'],
        y=df_note['Lat'],
        text=df_note['Note'],
        font="10p,Helvetica-Bold,blue", # 使用藍色字體與 Repfile 區隔
        justify="LM",                   # 靠左對齊 (文字在點的右方)
        offset="0.5c/0c",               # 向右偏移 0.5 公分，避免壓到圓圈
        fill="white@25"                 # 淺色背景遮罩增加辨識度
    )

## 不繪製 Pfile 震央星號

# --- 3. Inset 與 Colorbar ---
# place inset inside bottom-right to avoid covering data
with fig.inset(position="jBR+w3.6c+o-0.2c/0.2c"):
    fig.coast(region=[119, 123, 21, 26], projection="M?", land="palegreen3", water="skyblue", 
              shorelines="0.5p,black", resolution="i")
    fig.plot(data=gmt_file, pen="0.5p,black")
    fig.plot(x=[region[0], region[1], region[1], region[0], region[0]],
             y=[region[2], region[2], region[3], region[3], region[2]], pen="1p,red")
    fig.basemap(frame="0")
fig.colorbar(frame=['a5f2.5', 'x+l"Depth (km)"'], position="JBC+w10c/0.5c+h+o0c/1.2c")
fig.savefig("outputs/03_EEW_epicenter.png")
