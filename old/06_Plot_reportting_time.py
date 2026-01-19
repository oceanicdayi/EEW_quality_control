import re
import pandas as pd
import eewrep_function
import matplotlib.pyplot as plt
from datetime import datetime
import argparse

# === ERR event info ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot EEW reporting time"
    )
    parser.add_argument(
        "eq_id",
        help="地震年份(西元)+編號，例如 2025001"
    )
    args = parser.parse_args()

    eq_info = None
    lines = []

    eq_input = args.eq_id.strip()
    year = eq_input[:4]
    eq_id = eq_input[4:].zfill(3)

    eq_info = eewrep_function.read_eq_xml(year, eq_id)
    if not eq_info:
        raise FileNotFoundError("找不到對應的 XML 檔案")

    if eq_info:
        print(">> 成功讀取時間、地點、規模")
        report = eq_info["reportContent"]

        m = re.match(r"(\d{2})/(\d{2})-\d{2}:\d{2}(.*)發生規模([\d.]+)有感地震", report)
        if m:
            month, day, location, magnitude = m.groups()
            roc_year = int(year) - 1911
            lines = [
                f"{roc_year}年{int(month)}月{int(day)}日",
                f"{location}  規模{magnitude}地震"
            ]
        else:
            # 若格式不符合，直接放整行文字
            print("格式不符合，直接放整行文字")
            lines = [report]

ref_lat, ref_lon = eq_info["epicenterLat"], eq_info["epicenterLon"]
ref_mag, ref_dep = eq_info["magnitude"], eq_info["depth"]
ref_time = eq_info["ot"]

# === EEW rep ===
INPUT_PATH = "./outputs/summary_20_192.txt"
df = pd.read_csv(INPUT_PATH, sep=r'\s+')
for col in ['Mag', 'Lat', 'Lon', 'Depth', 'Ma.', ]:
    if col == "Report_time":
        df[col] = df['Date'].str.replace('-', '') + ' ' + df['Time']
    else:
        df[col] = df[col].astype(float)

df['Tdiff'] = pd.to_datetime(df['Report_time'],utc=True) - ref_time
df['Tdiff_second'] = df['Tdiff'].dt.total_seconds()
df['Repfile_short'] = df['Repfile'].apply(lambda x: "_".join(x.split('_')[-2:]))

# === Proessing time hito ===
# --- 1. Plotting ---
fig, ax = plt.subplots(figsize=(14, 7))
    
colors = []
for note in df['note']:
    if "(eew)" in str(note).lower():
        colors.append('green')
    elif "(pws)" in str(note).lower():
        colors.append('orange')
    elif str(note) != "nan":
        colors.append('red')
    else:
        colors.append('skyblue')
bars = ax.bar(df['Repfile_short'], df['Tdiff_second'], color=colors, edgecolor='black', linewidth=0.5)

y_vals = df['Tdiff_second'].dropna()
if y_vals.empty:
    y_min, y_max = 0, 1
else:
    y_min, y_max = y_vals.min(), y_vals.max()
annot_count = 0  # 用來計算需要標註的數量，控制 offset 錯開

# --- 1. 處理 Annotations (Bar 上的標籤) ---
for i, (bar, note, mag) in enumerate(zip(bars, df['note'], df['Mag'])):
    # 判斷 note 是否為有效標籤 (非 NaN 且非空字串)
    is_valid_note = not pd.isna(note) and str(note).strip() != ""
    
    if is_valid_note:
        yval = bar.get_height()
        label = f"M{mag:.2f}\n{note}"
        
        # 決定顏色主題
        note_lower = str(note).lower()
        if "(eew)" in note_lower:
            theme_color = 'green'
        elif "(pws)" in note_lower:
            theme_color = 'darkorange'
        else:
            theme_color = 'red'

        # 控制標籤高度錯開 (避免重疊)
        offsets = [100, 150, 40, 200]
        offset_y = offsets[annot_count % 4]
        annot_count += 1

        ax.annotate(label,
            xy=(bar.get_x() + bar.get_width()/2, yval),
            xytext=(0, offset_y),
            textcoords="offset points",
            ha='center', va='bottom',
            color=theme_color, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=theme_color, alpha=1.0, lw=1),
            arrowprops=dict(arrowstyle='->', color=theme_color, lw=1))
    else:
        # 如果沒有標籤，這裡不需要做 annotate，或可以選擇做簡單處理
        pass

# --- 2. X-axis Tick Label Coloring (刻度顏色) ---
plt.xticks(rotation=45, ha='right')
labels = ax.get_xticklabels()

for i, label in enumerate(labels):
    # 這裡要注意 i 必須對應到 df 的 row index
    note_val = df.loc[i, 'note']
    
    if not pd.isna(note_val) and str(note_val).strip() != "":
        note_lower = str(note_val).lower()
        if "(eew)" in note_lower:
            tick_color = 'green'
        elif "(pws)" in note_lower:
            tick_color = 'darkorange'
        else:
            tick_color = 'red'
        label.set_fontweight('bold')
    else:
        # note 為空或 NaN 時，設定為 skyblue
        tick_color = 'skyblue'
        label.set_fontweight('normal')
    
    label.set_color(tick_color)

# --- 3. X-axis Tick Label Coloring ---
plt.xticks(rotation=45, ha='right')
labels = ax.get_xticklabels()

for i, label in enumerate(labels):
    # 確保索引與 DataFrame 對應 (若 df 經過 filter 或 reindex，請用 .iloc[i])
    note_val = df.iloc[i]['note']
    
    # 判斷 note 是否為有效標籤 (排除 NaN, None, 與空字串)
    if pd.notna(note_val) and str(note_val).strip() != "":
        # 轉小寫進行關鍵字判斷
        note_s = str(note_val).lower()
        
        if "(eew)" in note_s:
            tick_color = 'green'
        elif "(pws)" in note_s:
            tick_color = 'darkorange'
        else:
            tick_color = 'red'
        
        label.set_fontweight('bold')
    else:
        # 若 note 為空 (記錄標籤不存在)，則設定為 skyblue
        tick_color = 'black'
        label.set_fontweight('normal') # 沒標籤的通常不加粗，視覺更平衡

    label.set_color(tick_color)

# --- 4. Final styling ---
ax.axhline(y=0, color='gray', linestyle='-', alpha=0.5) 
ax.set_ylabel('Processing Time [seconds]', fontsize=12)
ax.set_xlabel('Report ID', fontsize=12)
ax.set_title(f'Alert Latency relative to Origin Time\n(Origin: {ref_time})', fontsize=14)
margin = max(5, y_max * 0.1)
if y_min == y_max:
    y_min -= 1
    y_max += 1
pad = max(5, (y_max - y_min) * 0.1)
ax.set_ylim(y_min - pad, y_max + pad)
ax.grid(axis='y', linestyle='--', alpha=0.5)
    
plt.tight_layout()
plt.savefig('outputs/06_EEW_PT.png', dpi=300)
print("EEW_processing_time Done")
