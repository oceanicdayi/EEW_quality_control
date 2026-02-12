import gradio as gr
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# --- Constants ---
VP = 6.0   # P-wave velocity (km/s)
VS = 3.5   # S-wave velocity (km/s)

# --- Calculation Functions ---

def calculate_warning_time(distance_km, detection_time_s):
    """Calculate EEW warning time given distance from epicenter and detection delay."""
    if distance_km <= 0:
        return 0.0, 0.0, 0.0
    t_p = distance_km / VP
    t_s = distance_km / VS
    warning_time = t_s - t_p - detection_time_s
    return round(t_p, 2), round(t_s, 2), round(max(warning_time, 0), 2)


def estimate_magnitude(amplitude_mm, distance_km):
    """Estimate local magnitude using the Richter formula: ML = log10(A) + distance correction."""
    if amplitude_mm <= 0 or distance_km <= 0:
        return 0.0
    ml = np.log10(amplitude_mm) + 1.11 * np.log10(distance_km) + 0.00189 * distance_km - 2.09
    return round(float(ml), 2)


def intensity_from_pga(pga_gal):
    """Convert PGA (gal) to approximate seismic intensity scale (CWA scale)."""
    if pga_gal < 0.8:
        return "0－微震"
    elif pga_gal < 2.5:
        return "1－極輕微"
    elif pga_gal < 8.0:
        return "2－輕微"
    elif pga_gal < 25:
        return "3－弱"
    elif pga_gal < 80:
        return "4－中等"
    elif pga_gal < 140:
        return "5－弱"
    elif pga_gal < 250:
        return "5－強"
    elif pga_gal < 440:
        return "6－弱"
    elif pga_gal < 800:
        return "6－強"
    else:
        return "7－劇烈"


# --- Plotting Functions ---

def plot_wave_propagation(distance_km, detection_time_s):
    """Generate a time-distance plot showing P-wave, S-wave, and warning time."""
    t_p, t_s, warning = calculate_warning_time(distance_km, detection_time_s)

    max_dist = max(distance_km * 1.3, 50)
    distances = np.linspace(0, max_dist, 300)
    t_p_line = distances / VP
    t_s_line = distances / VS

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(t_p_line, distances, label=f"P 波 ({VP} 公里/秒)", color="#2196F3", linewidth=2)
    ax.plot(t_s_line, distances, label=f"S 波 ({VS} 公里/秒)", color="#F44336", linewidth=2)

    if distance_km > 0:
        ax.axhline(y=distance_km, color="gray", linestyle="--", alpha=0.5, label=f"測站距離 {distance_km} 公里")
        ax.plot(t_p, distance_km, "bo", markersize=10, zorder=5)
        ax.plot(t_s, distance_km, "ro", markersize=10, zorder=5)

        alert_time = t_p + detection_time_s
        if warning > 0:
            ax.fill_betweenx(
                [distance_km - 2, distance_km + 2],
                alert_time, t_s,
                color="#4CAF50", alpha=0.3, label=f"警報時間：{warning} 秒"
            )
            ax.annotate(
                f"⚠ 提前 {warning} 秒",
                xy=((alert_time + t_s) / 2, distance_km),
                fontsize=12, ha="center", va="bottom", fontweight="bold", color="#2E7D32"
            )

        blind_radius = VP * detection_time_s * VS / (VP - VS) if VP != VS else 0
        if blind_radius > 0:
            ax.axhline(y=blind_radius, color="#FF9800", linestyle=":", alpha=0.7, label=f"盲區半徑：{blind_radius:.1f} 公里")

    ax.set_xlabel("時間（秒）", fontsize=12)
    ax.set_ylabel("距震央距離（公里）", fontsize=12)
    ax.set_title("EEW 波傳播與警報時間", fontsize=14, fontweight="bold")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig


def plot_blind_zone(detection_time_s):
    """Visualize the EEW blind zone as a top-down view."""
    blind_radius = VP * detection_time_s * VS / (VP - VS) if VP != VS else 0

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect("equal")

    outer = plt.Circle((0, 0), blind_radius * 2.5 if blind_radius > 0 else 50, color="#E3F2FD", zorder=0)
    ax.add_patch(outer)

    if blind_radius > 0:
        blind = plt.Circle((0, 0), blind_radius, color="#FFCDD2", alpha=0.6, zorder=1, label=f"盲區（{blind_radius:.1f} 公里）")
        ax.add_patch(blind)

    ax.plot(0, 0, "r*", markersize=20, zorder=3, label="震央")

    limit = blind_radius * 3 if blind_radius > 0 else 60
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_xlabel("距離（公里）", fontsize=11)
    ax.set_ylabel("距離（公里）", fontsize=11)
    ax.set_title("EEW 盲區（俯視圖）", fontsize=14, fontweight="bold")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.3)

    red_patch = mpatches.Patch(color="#FFCDD2", alpha=0.6, label="無法警報")
    blue_patch = mpatches.Patch(color="#E3F2FD", label="可警報")
    ax.legend(handles=[red_patch, blue_patch], loc="upper right", fontsize=9)

    plt.tight_layout()
    return fig


def plot_magnitude_estimation(distance_km):
    """Show how amplitude relates to magnitude at a given distance."""
    amplitudes = np.logspace(-2, 2, 200)
    magnitudes = [estimate_magnitude(a, distance_km) for a in amplitudes]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(amplitudes, magnitudes, color="#9C27B0", linewidth=2)
    ax.set_xscale("log")
    ax.set_xlabel("最大振幅（毫米）", fontsize=12)
    ax.set_ylabel("估計規模（ML）", fontsize=12)
    ax.set_title(f"芮氏規模估算（距離 = {distance_km} 公里）", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3, which="both")
    ax.axhline(y=3, color="green", linestyle="--", alpha=0.5, label="ML 3－輕微")
    ax.axhline(y=5, color="orange", linestyle="--", alpha=0.5, label="ML 5－中等")
    ax.axhline(y=7, color="red", linestyle="--", alpha=0.5, label="ML 7－強烈")
    ax.legend(fontsize=9)
    plt.tight_layout()
    return fig


# --- Gradio callback wrappers ---

def warning_time_callback(distance_km, detection_time_s):
    t_p, t_s, warning = calculate_warning_time(distance_km, detection_time_s)
    fig = plot_wave_propagation(distance_km, detection_time_s)
    summary = (
        f"**P 波抵達：** {t_p} 秒  \n"
        f"**S 波抵達：** {t_s} 秒  \n"
        f"**偵測延遲：** {detection_time_s} 秒  \n"
        f"**可用警報時間：** {warning} 秒"
    )
    return fig, summary


def blind_zone_callback(detection_time_s):
    blind_radius = VP * detection_time_s * VS / (VP - VS) if VP != VS else 0
    fig = plot_blind_zone(detection_time_s)
    summary = (
        f"**偵測延遲：** {detection_time_s} 秒  \n"
        f"**盲區半徑：** {blind_radius:.1f} 公里  \n\n"
        "盲區內的測站在 S 波抵達前無法收到警報。"
    )
    return fig, summary


def magnitude_callback(amplitude_mm, distance_km):
    ml = estimate_magnitude(amplitude_mm, distance_km)
    fig = plot_magnitude_estimation(distance_km)
    summary = (
        f"**振幅：** {amplitude_mm} 毫米  \n"
        f"**距離：** {distance_km} 公里  \n"
        f"**估計規模（ML）：** {ml}"
    )
    return fig, summary


def intensity_callback(pga_gal):
    intensity = intensity_from_pga(pga_gal)
    return f"**PGA：** {pga_gal} gal  \n**估計震度：** {intensity}"


# --- Build Gradio App ---

with gr.Blocks(title="地震早期警報概念") as demo:
    gr.Markdown(
        """
        # 🌍 地震早期警報（EEW）— 互動概念

        此互動網站展示 **地震早期警報** 系統的核心原理。
        請使用下方分頁探索各項概念。
        """
    )

    with gr.Tabs():
        # --- Tab 1: Overview ---
        with gr.TabItem("📖 什麼是 EEW？"):
            gr.Markdown(
                """
                ## 什麼是地震早期警報？

                **地震早期警報（EEW）** 系統能快速偵測地震，並在強烈搖晃抵達前
                發送警報。其原理是利用電子訊號傳播速度遠快於地震波。

                ### 運作方式
                1. 震央附近的 **地震感測器** 偵測速度快但破壞力較小的 **P 波**。
                2. 系統 **估算** 震央位置、規模與可能的震度。
                3. 對尚未感受到強烈搖晃（S 波）的區域 **發布警報**。
                4. 人員與自動化系統可在 **警報時間窗** 內採取防護措施。

                ### 主要地震波
                | 波型 | 速度（約） | 破壞性 |
                |------|-----------|--------|
                | **P 波**（Primary） | ~6 公里/秒 | 低 — 壓縮波 |
                | **S 波**（Secondary） | ~3.5 公里/秒 | 高 — 剪力波 |

                ### 限制
                - **盲區**：距震央太近的區域幾乎無法提前警報。
                - **偵測延遲**：需要數秒偵測與處理首波 P 波。
                - **準確度**：初步估算可能會隨後續資料修正。

                > ⏱ 即使只有 **幾秒** 的警報，也足以爭取時間
                > 進行就地避難、停止電梯、減速列車、關閉關鍵系統等。
                """
            )

        # --- Tab 2: Warning Time Calculator ---
        with gr.TabItem("⏱ 警報時間"):
            gr.Markdown("## 警報時間計算器\n探索距離與偵測延遲如何影響可用的警報時間。")
            with gr.Row():
                with gr.Column(scale=1):
                    dist_slider = gr.Slider(1, 500, value=100, step=1, label="距震央距離（公里）")
                    det_slider = gr.Slider(0, 20, value=5, step=0.5, label="偵測延遲（秒）")
                    calc_btn = gr.Button("計算", variant="primary")
                    warning_md = gr.Markdown()
                with gr.Column(scale=2):
                    wave_plot = gr.Plot(label="波傳播示意圖")
            calc_btn.click(warning_time_callback, [dist_slider, det_slider], [wave_plot, warning_md])
            demo.load(warning_time_callback, [dist_slider, det_slider], [wave_plot, warning_md])

        # --- Tab 3: Blind Zone ---
        with gr.TabItem("🔴 盲區"):
            gr.Markdown(
                """
                ## 盲區

                **盲區** 是指震央周圍在 S 波抵達前無法發送警報的區域，
                其半徑取決於系統的偵測延遲。
                """
            )
            with gr.Row():
                with gr.Column(scale=1):
                    bz_det_slider = gr.Slider(0, 20, value=5, step=0.5, label="偵測延遲（秒）")
                    bz_btn = gr.Button("視覺化", variant="primary")
                    bz_md = gr.Markdown()
                with gr.Column(scale=2):
                    bz_plot = gr.Plot(label="盲區視覺化")
            bz_btn.click(blind_zone_callback, [bz_det_slider], [bz_plot, bz_md])
            demo.load(blind_zone_callback, [bz_det_slider], [bz_plot, bz_md])

        # --- Tab 4: Magnitude Estimation ---
        with gr.TabItem("📏 規模"):
            gr.Markdown("## 規模估算\n使用經典芮氏方法，查看地震波振幅與地震規模的關係。")
            with gr.Row():
                with gr.Column(scale=1):
                    amp_slider = gr.Slider(0.01, 100, value=10, step=0.1, label="最大振幅（毫米）")
                    mag_dist_slider = gr.Slider(1, 600, value=100, step=1, label="震央距離（公里）")
                    mag_btn = gr.Button("估算", variant="primary")
                    mag_md = gr.Markdown()
                with gr.Column(scale=2):
                    mag_plot = gr.Plot(label="規模與振幅關係")
            mag_btn.click(magnitude_callback, [amp_slider, mag_dist_slider], [mag_plot, mag_md])
            demo.load(magnitude_callback, [amp_slider, mag_dist_slider], [mag_plot, mag_md])

        # --- Tab 5: Intensity Scale ---
        with gr.TabItem("💥 震度"):
            gr.Markdown(
                """
                ## 由 PGA 估算震度

                **最大地動加速度（PGA）** 以 gal（cm/s²）為單位，可換算為震度等級。
                輸入 PGA 數值即可查看估計震度。
                """
            )
            with gr.Row():
                with gr.Column():
                    pga_slider = gr.Slider(0.1, 1000, value=80, step=0.1, label="PGA（gal）")
                    int_btn = gr.Button("換算", variant="primary")
                    int_md = gr.Markdown()
            int_btn.click(intensity_callback, [pga_slider], [int_md])
            demo.load(intensity_callback, [pga_slider], [int_md])

    gr.Markdown(
        """
        ---
        *本工具為教育用途，波速與公式為簡化模型。*
        """
    )

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
