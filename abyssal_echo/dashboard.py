"""Streamlit dashboard for Abyssal Echo."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


DEFAULT_OUTPUT_DIR = Path("outputs")


@st.cache_data
def load_dashboard_data(output_dir: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    root = Path(output_dir)
    cleaned = pd.read_csv(root / "cleaned_acoustic_pings.csv")
    trajectory = pd.read_csv(root / "reconstructed_trajectory.csv")
    speed = pd.read_csv(root / "doppler_speed_summary.csv")
    return cleaned, trajectory, speed


def render_dashboard(output_dir: str = "outputs") -> None:
    """Render the analytical dashboard."""
    st.set_page_config(page_title="Abyssal Echo", layout="wide")
    st.title("Abyssal Echo – Acoustic Reconnaissance")
    st.caption("Stealth submarine trajectory reconstruction from distorted hydrophone pings.")

    cleaned, trajectory, speed = load_dashboard_data(output_dir)
    latest_track = trajectory.iloc[-1]
    latest_speed = speed.iloc[-1]

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Depth (m)", f"{latest_track['Estimated_Depth_m']:.1f}")
    col2.metric("Sound Speed (m/s)", f"{latest_track['Mean_Sound_Speed_mps']:.1f}")
    col3.metric("Speed (knots)", f"{latest_speed['Submarine_Speed_knots']:.2f}")

    left, right = st.columns([1.7, 1.0])

    with left:
        st.subheader("Trajectory Reconstruction")
        fig3d = go.Figure()
        fig3d.add_trace(
            go.Scatter3d(
                x=trajectory["Raw_X"],
                y=trajectory["Raw_Y"],
                z=trajectory["Raw_Z"],
                mode="lines+markers",
                name="Raw Path",
                line={"color": "#7f8c8d", "width": 5},
                marker={"size": 3},
            )
        )
        fig3d.add_trace(
            go.Scatter3d(
                x=trajectory["Corrected_X"],
                y=trajectory["Corrected_Y"],
                z=trajectory["Corrected_Z"],
                mode="lines+markers",
                name="Corrected Path",
                line={"color": "#00b894", "width": 7},
                marker={"size": 4},
            )
        )
        fig3d.update_layout(
            height=560,
            scene={"xaxis_title": "X (m)", "yaxis_title": "Y (m)", "zaxis_title": "Z (m)"},
            legend={"orientation": "h"},
        )
        st.plotly_chart(fig3d, use_container_width=True)

        fig2d = px.line(
            trajectory,
            x="Corrected_X",
            y="Corrected_Y",
            markers=True,
            title="Top-Down Track",
        )
        fig2d.add_scatter(
            x=trajectory["Raw_X"],
            y=trajectory["Raw_Y"],
            mode="lines",
            name="Raw Path",
            line={"dash": "dash", "color": "#636e72"},
        )
        st.plotly_chart(fig2d, use_container_width=True)

    with right:
        st.subheader("Doppler Speedometer")
        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=float(latest_speed["Submarine_Speed_knots"]),
                number={"suffix": " kn"},
                title={"text": "Estimated Speed"},
                gauge={
                    "axis": {"range": [0, max(20.0, speed["Submarine_Speed_knots"].max() * 1.2)]},
                    "bar": {"color": "#0984e3"},
                    "steps": [
                        {"range": [0, 5], "color": "#dfe6e9"},
                        {"range": [5, 12], "color": "#81ecec"},
                        {"range": [12, 20], "color": "#74b9ff"},
                    ],
                },
            )
        )
        gauge.update_layout(height=320, margin={"t": 60, "b": 10})
        st.plotly_chart(gauge, use_container_width=True)

        st.subheader("Environmental HUD")
        hud = trajectory[["Corrected_Timestamp_ms", "Estimated_Depth_m", "Mean_Sound_Speed_mps"]].copy()
        hud["Time_s"] = hud["Corrected_Timestamp_ms"] / 1000.0
        hud_fig = go.Figure()
        hud_fig.add_trace(
            go.Scatter(
                x=hud["Time_s"],
                y=hud["Estimated_Depth_m"],
                mode="lines",
                name="Depth (m)",
                line={"color": "#2d3436"},
                yaxis="y1",
            )
        )
        hud_fig.add_trace(
            go.Scatter(
                x=hud["Time_s"],
                y=hud["Mean_Sound_Speed_mps"],
                mode="lines",
                name="Sound Speed (m/s)",
                line={"color": "#e17055"},
                yaxis="y2",
            )
        )
        hud_fig.update_layout(
            height=260,
            xaxis={"title": "Time (s)"},
            yaxis={"title": "Depth (m)"},
            yaxis2={"title": "Sound Speed (m/s)", "overlaying": "y", "side": "right"},
            legend={"orientation": "h"},
        )
        st.plotly_chart(hud_fig, use_container_width=True)

    st.subheader("Signal Waterfall")
    waterfall = cleaned.copy()
    waterfall["Time_s"] = waterfall["Corrected_Timestamp_ms"] / 1000.0
    waterfall["Signal_Type"] = waterfall["Is_Primary"].map({True: "Primary", False: "Echo"})
    waterfall_fig = px.scatter(
        waterfall.sort_values("Corrected_Timestamp_ms"),
        x="Time_s",
        y="Received_Frequency_Hz",
        color="Signal_Type",
        color_discrete_map={"Primary": "#2ecc71", "Echo": "#e74c3c"},
        size="Intensity_dB",
        hover_data=["Packet_ID", "Sensor_ID", "Intensity_dB"],
        title="Incoming Acoustic Events",
    )
    waterfall_fig.update_layout(height=420, xaxis_title="Corrected Time (s)", yaxis_title="Frequency (Hz)")
    st.plotly_chart(waterfall_fig, use_container_width=True)


if __name__ == "__main__":
    selected_output_dir = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_OUTPUT_DIR)
    render_dashboard(selected_output_dir)
