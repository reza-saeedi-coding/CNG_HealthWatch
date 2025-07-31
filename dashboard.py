# ==========================================================
# DASHBOARD (Streamlit App)
#
# This dashboard serves as the real-time interface to monitor:
# 1. Live sensor metrics (updated every 10 seconds)
# 2. Summary charts for trends over past days/weeks
# 3. Logged anomalies with Z-score insights
#
# Tabs are auto-refreshing and interactive. Uses SQLite as backend.
# Requires: streamlit, matplotlib, pandas, altair, streamlit-autorefresh
# Run via: streamlit run dashboard.py
# ==========================================================

# NOTE: This script requires the 'streamlit' library to be installed.
# If you encounter a ModuleNotFoundError, run: pip install streamlit

import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
from streamlit_autorefresh import st_autorefresh
import matplotlib.pyplot as plt

# === Define database path ===
DB_PATH = Path(__file__).resolve().parent / "data" / "sensor_data.db"

# === Load anomalies once per run ===
try:
    with sqlite3.connect(DB_PATH) as conn:
        anomalies_df = pd.read_sql_query("SELECT * FROM anomalies", conn)
except Exception as e:
    anomalies_df = pd.DataFrame(columns=["timestamp", "sensor", "value", "z_score"])
    st.warning(f"Could not load anomalies: {e}")

# === Persistent tab selection across refreshes ===
tab_options = ["Live Metrics", "Summary Charts", "Anomalies"]
if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = "Live Metrics"

selected_tab = st.radio("Select a tab", tab_options, index=tab_options.index(st.session_state.selected_tab))
st.session_state.selected_tab = selected_tab

# ==================== TAB 1: LIVE METRICS ====================
if selected_tab == "Live Metrics":
    st_autorefresh(interval=10_000, key="auto_refresh")

    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM processed_logs ORDER BY id DESC LIMIT 50000", conn)

    st.title("SAFE SENSOR DASHBOARD")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["timestamp"] = df["timestamp"].dt.tz_convert("Europe/Rome")
    local_time = df["timestamp"].iloc[0]
    st.write("Last Update (Local):", local_time.strftime("%Y-%m-%d %H:%M:%S"))

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Pressure", df["pressure"].iloc[0])
    with col2:
        if df["pressure"].iloc[0] > 200:
            st.error("Status: ALERT")
        elif df["pressure"].iloc[0] > 120:
            st.warning("Status: WARNING")
        else:
            st.success("Status: OK")

    col3, col4 = st.columns([1, 1])
    with col3:
        st.metric("Temperature", df["temperature"].iloc[0])
    with col4:
        if df["temperature"].iloc[0] > 55:
            st.error("Status: ALERT")
        elif df["temperature"].iloc[0] > 45:
            st.warning("Status: WARNING")
        else:
            st.success("Status: OK")

    col5, col6 = st.columns([2, 1])
    with col5:
        st.metric("Flow Rate", df["flow_rate"].iloc[0])
    with col6:
        if df["flow_rate"].iloc[0] < 30:
            st.error("Status: ALERT")
        else:
            st.success("Status: OK")

    col7, col8 = st.columns([1, 1])
    with col7:
        st.metric("Vibration", df["vibration"].iloc[0])
    with col8:
        if df["vibration"].iloc[0] > 10:
            st.error("Status: ALERT")
        elif df["vibration"].iloc[0] > 7:
            st.warning("Status: WARNING")
        else:
            st.success("Status: OK")

    col9, col10 = st.columns([1, 2])
    with col9:
        st.metric("Humidity", df["humidity"].iloc[0])
    with col10:
        if df["humidity"].iloc[0] > 70:
            st.error("Status: ALERT")
        elif df["humidity"].iloc[0] > 60:
            st.warning("Status: WARNING")
        else:
            st.success("Status: OK")

    st.metric("Compressor Status", "ON" if df["compressor_status"].iloc[0] == 1 else "OFF")

    def plot_line_chart(df, column_name, title):
        fig, ax = plt.subplots()
        df = df.sort_values("timestamp")
        ax.plot(df["timestamp"], df[column_name], color="skyblue")
        ax.set_title(title)
        ax.set_xlabel("Time")
        ax.set_ylabel(column_name.capitalize())
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()
        st.pyplot(fig)

    colA, colB, colC = st.columns(3)
    with colA:
        st.write("Pressure")
        plot_line_chart(df, "pressure", "Pressure Over Time")
    with colB:
        st.write("Temperature")
        plot_line_chart(df, "temperature", "Temperature Over Time")
    with colC:
        st.write("Vibration")
        plot_line_chart(df, "vibration", "Vibration Over Time")

# ==================== TAB 2: SUMMARY CHARTS ====================
elif selected_tab == "Summary Charts":
    st_autorefresh(interval=30_000, key="auto_refresh_summary")

    st.subheader("Live Summary Charts")

    with sqlite3.connect(DB_PATH) as conn:
        query = """
        SELECT *
        FROM processed_logs
        WHERE timestamp >= datetime('now', '-14 days')
        ORDER BY timestamp ASC
        """
        df = pd.read_sql_query(query, conn)

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["timestamp"] = df["timestamp"].dt.tz_convert("Europe/Rome")
    df["time_label"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    df["hour"] = df["timestamp"].dt.hour
    df["minute"] = df["timestamp"].dt.floor("min")
    df["day"] = df["timestamp"].dt.date
    df["weekday"] = df["timestamp"].dt.day_name()

    def plot_bar(data, title, xlabel, ylabel):
        fig, ax = plt.subplots()
        data.plot(kind="bar", ax=ax)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        st.pyplot(fig)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("Average Pressure by Hour")
        df["hour_label"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:00")
        avg_pressure_hour = df.groupby("hour_label")["pressure"].mean().sort_index().tail(48)
        plot_bar(avg_pressure_hour, "Avg Pressure by Hour", "Date-Hour", "Pressure")

    with col2:
        st.caption("Compressor Transition Count")
        df = df.sort_values("timestamp")
        df["prev_status"] = df["compressor_status"].shift(1)
        df["status_change"] = df["compressor_status"] != df["prev_status"]
        df_trans = df[df["status_change"] == True].copy()
        df_trans["Status Change"] = df_trans["compressor_status"].map({1: "Turned ON", 0: "Turned OFF"})
        df_trans["day"] = df_trans["timestamp"].dt.date
        transition_counts = df_trans.groupby(["day", "Status Change"]).size().unstack(fill_value=0)
        fig, ax = plt.subplots()
        transition_counts.plot(kind="bar", stacked=True, ax=ax, color=["orange", "blue"])
        ax.set_title("Compressor ON/OFF Transitions per Day")
        ax.set_xlabel("Date")
        ax.set_ylabel("Number of Transitions")
        ax.legend(title="Compressor")
        st.pyplot(fig)

    with col3:
        st.caption("Max Temperature by Day")
        max_temp_day = df.groupby("day")["temperature"].max()
        plot_bar(max_temp_day, "Max Temp by Day", "Day", "Temperature")

    col4, col5, col6 = st.columns(3)
    with col4:
        st.caption("Avg Vibration by Weekday")
        avg_vib_weekday = df.groupby("weekday")["vibration"].mean()
        plot_bar(avg_vib_weekday, "Avg Vibration by Weekday", "Weekday", "Vibration")

    with col5:
        st.caption("Avg Flow Rate by Hour")
        df["hour_label"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:00")
        avg_flow_hour = df.groupby("hour_label")["flow_rate"].mean().sort_index().tail(48)
        plot_bar(avg_flow_hour, "Avg Flow by Hour", "Date-Hour", "Flow Rate")

    with col6:
        st.caption("Avg Humidity by Day")
        df["day_label"] = df["timestamp"].dt.strftime("%Y-%m-%d")
        avg_hum_day = df.groupby("day_label")["humidity"].mean().sort_index().tail(14)
        plot_bar(avg_hum_day, "Avg Humidity by Day", "Date", "Humidity")

    col7, _ = st.columns([1, 2])
    with col7:
        st.caption("Avg Vibration by Minute")
        df["minute_label"] = df["timestamp"].dt.strftime("%H:%M")
        avg_vib_minute = df.groupby("minute_label")["vibration"].mean().tail(120)

        fig, ax = plt.subplots()
        avg_vib_minute.plot(ax=ax, kind="line", marker="o")
        ax.set_title("Avg Vibration (Last 2 Hours)")
        ax.set_xlabel("Time (HH:MM)")
        ax.set_ylabel("Vibration")
        ax.tick_params(axis="x", rotation=90, labelsize=8)
        st.pyplot(fig)

# ==================== TAB 3: ANOMALIES ====================
elif selected_tab == "Anomalies":
    st_autorefresh(interval=30_000, key="auto_refresh_anomalies")

    if not anomalies_df.empty:
        anomalies_df["timestamp"] = pd.to_datetime(anomalies_df["timestamp"], utc=True)
        anomalies_df["timestamp"] = anomalies_df["timestamp"].dt.tz_convert("Europe/Rome")

    st.subheader("Recent Anomalies")
    st.dataframe(anomalies_df.sort_values("timestamp", ascending=False).head(300))

    st.subheader("Anomaly Z-Score Trend (Line Chart)")
    if not anomalies_df.empty:
        sensor_list = anomalies_df["sensor"].unique()
        if "selected_sensor" not in st.session_state or st.session_state.selected_sensor not in sensor_list:
            st.session_state.selected_sensor = sensor_list[0]

        sensor_to_plot = st.selectbox(
            "Select sensor to view anomaly trend:",
            options=sensor_list,
            index=list(sensor_list).index(st.session_state.selected_sensor),
            key="anomaly_sensor_select"
        )
        st.session_state.selected_sensor = sensor_to_plot

        filtered = anomalies_df[anomalies_df["sensor"] == sensor_to_plot]
        if not filtered.empty:
            st.line_chart(filtered.set_index("timestamp")["z_score"])
        else:
            st.info("No anomaly data for selected sensor.")
    else:
        st.info("No anomalies logged yet.")

    st.subheader("Detected Anomalies")
    if not anomalies_df.empty:
        import altair as alt
        chart = alt.Chart(anomalies_df).mark_circle(size=60).encode(
            x="timestamp:T",
            y="value:Q",
            color="sensor:N",
            tooltip=["timestamp", "sensor", "value", "z_score"]
        ).properties(width=800, height=400, title="Anomalies Detected Over Time")
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No anomalies detected yet.")
