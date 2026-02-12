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
        return "0 – Micro"
    elif pga_gal < 2.5:
        return "1 – Very Minor"
    elif pga_gal < 8.0:
        return "2 – Minor"
    elif pga_gal < 25:
        return "3 – Light"
    elif pga_gal < 80:
        return "4 – Moderate"
    elif pga_gal < 140:
        return "5 Weak"
    elif pga_gal < 250:
        return "5 Strong"
    elif pga_gal < 440:
        return "6 Weak"
    elif pga_gal < 800:
        return "6 Strong"
    else:
        return "7 – Severe"


# --- Plotting Functions ---

def plot_wave_propagation(distance_km, detection_time_s):
    """Generate a time-distance plot showing P-wave, S-wave, and warning time."""
    t_p, t_s, warning = calculate_warning_time(distance_km, detection_time_s)

    max_dist = max(distance_km * 1.3, 50)
    distances = np.linspace(0, max_dist, 300)
    t_p_line = distances / VP
    t_s_line = distances / VS

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(t_p_line, distances, label=f"P-wave ({VP} km/s)", color="#2196F3", linewidth=2)
    ax.plot(t_s_line, distances, label=f"S-wave ({VS} km/s)", color="#F44336", linewidth=2)

    if distance_km > 0:
        ax.axhline(y=distance_km, color="gray", linestyle="--", alpha=0.5, label=f"Station at {distance_km} km")
        ax.plot(t_p, distance_km, "bo", markersize=10, zorder=5)
        ax.plot(t_s, distance_km, "ro", markersize=10, zorder=5)

        alert_time = t_p + detection_time_s
        if warning > 0:
            ax.fill_betweenx(
                [distance_km - 2, distance_km + 2],
                alert_time, t_s,
                color="#4CAF50", alpha=0.3, label=f"Warning time: {warning}s"
            )
            ax.annotate(
                f"⚠ {warning}s warning",
                xy=((alert_time + t_s) / 2, distance_km),
                fontsize=12, ha="center", va="bottom", fontweight="bold", color="#2E7D32"
            )

        blind_radius = VP * detection_time_s * VS / (VP - VS) if VP != VS else 0
        if blind_radius > 0:
            ax.axhline(y=blind_radius, color="#FF9800", linestyle=":", alpha=0.7, label=f"Blind zone radius: {blind_radius:.1f} km")

    ax.set_xlabel("Time (seconds)", fontsize=12)
    ax.set_ylabel("Distance from Epicenter (km)", fontsize=12)
    ax.set_title("EEW Wave Propagation & Warning Time", fontsize=14, fontweight="bold")
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
        blind = plt.Circle((0, 0), blind_radius, color="#FFCDD2", alpha=0.6, zorder=1, label=f"Blind zone ({blind_radius:.1f} km)")
        ax.add_patch(blind)

    ax.plot(0, 0, "r*", markersize=20, zorder=3, label="Epicenter")

    limit = blind_radius * 3 if blind_radius > 0 else 60
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_xlabel("Distance (km)", fontsize=11)
    ax.set_ylabel("Distance (km)", fontsize=11)
    ax.set_title("EEW Blind Zone (Top View)", fontsize=14, fontweight="bold")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.3)

    red_patch = mpatches.Patch(color="#FFCDD2", alpha=0.6, label="No warning possible")
    blue_patch = mpatches.Patch(color="#E3F2FD", label="Warning possible")
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
    ax.set_xlabel("Maximum Amplitude (mm)", fontsize=12)
    ax.set_ylabel("Estimated Magnitude (ML)", fontsize=12)
    ax.set_title(f"Richter Magnitude Estimation (Distance = {distance_km} km)", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3, which="both")
    ax.axhline(y=3, color="green", linestyle="--", alpha=0.5, label="ML 3 – Light")
    ax.axhline(y=5, color="orange", linestyle="--", alpha=0.5, label="ML 5 – Moderate")
    ax.axhline(y=7, color="red", linestyle="--", alpha=0.5, label="ML 7 – Major")
    ax.legend(fontsize=9)
    plt.tight_layout()
    return fig


# --- Gradio callback wrappers ---

def warning_time_callback(distance_km, detection_time_s):
    t_p, t_s, warning = calculate_warning_time(distance_km, detection_time_s)
    fig = plot_wave_propagation(distance_km, detection_time_s)
    summary = (
        f"**P-wave arrival:** {t_p} s  \n"
        f"**S-wave arrival:** {t_s} s  \n"
        f"**Detection delay:** {detection_time_s} s  \n"
        f"**Available warning time:** {warning} s"
    )
    return fig, summary


def blind_zone_callback(detection_time_s):
    blind_radius = VP * detection_time_s * VS / (VP - VS) if VP != VS else 0
    fig = plot_blind_zone(detection_time_s)
    summary = (
        f"**Detection delay:** {detection_time_s} s  \n"
        f"**Blind zone radius:** {blind_radius:.1f} km  \n\n"
        "Stations inside the blind zone cannot receive a warning before S-wave shaking arrives."
    )
    return fig, summary


def magnitude_callback(amplitude_mm, distance_km):
    ml = estimate_magnitude(amplitude_mm, distance_km)
    fig = plot_magnitude_estimation(distance_km)
    summary = (
        f"**Amplitude:** {amplitude_mm} mm  \n"
        f"**Distance:** {distance_km} km  \n"
        f"**Estimated magnitude (ML):** {ml}"
    )
    return fig, summary


def intensity_callback(pga_gal):
    intensity = intensity_from_pga(pga_gal)
    return f"**PGA:** {pga_gal} gal  \n**Estimated Intensity:** {intensity}"


# --- Build Gradio App ---

with gr.Blocks(title="Earthquake Early Warning Concepts") as demo:
    gr.Markdown(
        """
        # 🌍 Earthquake Early Warning (EEW) — Interactive Concepts

        This interactive site demonstrates the core principles behind **Earthquake Early Warning** systems.
        Use the tabs below to explore each concept.
        """
    )

    with gr.Tabs():
        # --- Tab 1: Overview ---
        with gr.TabItem("📖 What is EEW?"):
            gr.Markdown(
                """
                ## What is Earthquake Early Warning?

                An **Earthquake Early Warning (EEW)** system detects earthquakes quickly and sends alerts
                **before strong shaking arrives** at a location. It exploits the fact that electronic
                signals travel much faster than seismic waves.

                ### How it works
                1. **Seismic sensors** near the epicenter detect the fast but less destructive **P-wave**.
                2. The system **estimates** the earthquake location, magnitude, and expected intensity.
                3. **Alerts** are issued to areas that have not yet experienced strong shaking (S-wave).
                4. People and automated systems can take protective actions during the **warning window**.

                ### Key seismic waves
                | Wave Type | Speed (approx.) | Damage Potential |
                |-----------|-----------------|------------------|
                | **P-wave** (Primary) | ~6 km/s | Low — compressional |
                | **S-wave** (Secondary) | ~3.5 km/s | High — shearing motion |

                ### Limitations
                - **Blind zone**: Areas very close to the epicenter receive little or no warning.
                - **Detection delay**: It takes a few seconds to detect and process the first P-wave.
                - **Accuracy**: Initial estimates may be revised as more data arrives.

                > ⏱ Even **a few seconds** of warning can save lives — enough time to
                > drop/cover/hold on, stop elevators, slow trains, and shut down critical systems.
                """
            )

        # --- Tab 2: Warning Time Calculator ---
        with gr.TabItem("⏱ Warning Time"):
            gr.Markdown("## Warning Time Calculator\nExplore how distance and detection delay affect the available warning time.")
            with gr.Row():
                with gr.Column(scale=1):
                    dist_slider = gr.Slider(1, 500, value=100, step=1, label="Distance from Epicenter (km)")
                    det_slider = gr.Slider(0, 20, value=5, step=0.5, label="Detection Delay (s)")
                    calc_btn = gr.Button("Calculate", variant="primary")
                    warning_md = gr.Markdown()
                with gr.Column(scale=2):
                    wave_plot = gr.Plot(label="Wave Propagation Diagram")
            calc_btn.click(warning_time_callback, [dist_slider, det_slider], [wave_plot, warning_md])
            demo.load(warning_time_callback, [dist_slider, det_slider], [wave_plot, warning_md])

        # --- Tab 3: Blind Zone ---
        with gr.TabItem("🔴 Blind Zone"):
            gr.Markdown(
                """
                ## The Blind Zone

                The **blind zone** is the area around the epicenter where the S-wave arrives
                before an alert can be issued. Its radius depends on the system's detection delay.
                """
            )
            with gr.Row():
                with gr.Column(scale=1):
                    bz_det_slider = gr.Slider(0, 20, value=5, step=0.5, label="Detection Delay (s)")
                    bz_btn = gr.Button("Visualize", variant="primary")
                    bz_md = gr.Markdown()
                with gr.Column(scale=2):
                    bz_plot = gr.Plot(label="Blind Zone Visualization")
            bz_btn.click(blind_zone_callback, [bz_det_slider], [bz_plot, bz_md])
            demo.load(blind_zone_callback, [bz_det_slider], [bz_plot, bz_md])

        # --- Tab 4: Magnitude Estimation ---
        with gr.TabItem("📏 Magnitude"):
            gr.Markdown("## Magnitude Estimation\nSee how the recorded wave amplitude relates to earthquake magnitude using the classic Richter approach.")
            with gr.Row():
                with gr.Column(scale=1):
                    amp_slider = gr.Slider(0.01, 100, value=10, step=0.1, label="Max Amplitude (mm)")
                    mag_dist_slider = gr.Slider(1, 600, value=100, step=1, label="Epicentral Distance (km)")
                    mag_btn = gr.Button("Estimate", variant="primary")
                    mag_md = gr.Markdown()
                with gr.Column(scale=2):
                    mag_plot = gr.Plot(label="Magnitude vs Amplitude")
            mag_btn.click(magnitude_callback, [amp_slider, mag_dist_slider], [mag_plot, mag_md])
            demo.load(magnitude_callback, [amp_slider, mag_dist_slider], [mag_plot, mag_md])

        # --- Tab 5: Intensity Scale ---
        with gr.TabItem("💥 Intensity"):
            gr.Markdown(
                """
                ## Seismic Intensity from PGA

                **Peak Ground Acceleration (PGA)** measured in gal (cm/s²) can be converted
                to a seismic intensity scale. Enter a PGA value to see the estimated intensity.
                """
            )
            with gr.Row():
                with gr.Column():
                    pga_slider = gr.Slider(0.1, 1000, value=80, step=0.1, label="PGA (gal)")
                    int_btn = gr.Button("Convert", variant="primary")
                    int_md = gr.Markdown()
            int_btn.click(intensity_callback, [pga_slider], [int_md])
            demo.load(intensity_callback, [pga_slider], [int_md])

    gr.Markdown(
        """
        ---
        *Built for educational purposes. Wave velocities and formulas are simplified models.*
        """
    )

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
