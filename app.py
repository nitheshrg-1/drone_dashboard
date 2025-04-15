import streamlit as st
import numpy as np
import plotly.graph_objs as go
import time
import random
import pandas as pd

st.set_page_config(page_title="Drone Telemetry Dashboard", layout="wide")

# Sidebar: Flight Mode
st.sidebar.title("Drone Control")
flight_mode = st.sidebar.selectbox("Flight Mode", ["Manual", "Stabilize", "Altitude Hold"])

# Geo-fence boundary
fence_bounds = (-50, 50)  # x and y boundaries

# Initialize session state
if "pos" not in st.session_state:
    st.session_state.pos = [0.0, 0.0]
if "prev_pos" not in st.session_state:
    st.session_state.prev_pos = [0.0, 0.0]
if "path" not in st.session_state:
    st.session_state.path = [[], []]  # x, y
if "battery" not in st.session_state:
    st.session_state.battery = 100.0
if "altitudes" not in st.session_state:
    st.session_state.altitudes = []
if "timestamps" not in st.session_state:
    st.session_state.timestamps = []
if "log" not in st.session_state:
    st.session_state.log = []

# Simulate movement
dx, dy = np.random.uniform(-5, 5), np.random.uniform(-5, 5)
st.session_state.prev_pos = st.session_state.pos[:]
st.session_state.pos[0] += dx
st.session_state.pos[1] += dy

# Speed calculation
distance = np.sqrt((st.session_state.pos[0] - st.session_state.prev_pos[0])**2 +
                   (st.session_state.pos[1] - st.session_state.prev_pos[1])**2)
speed = distance  # Units per second

# Append to path
st.session_state.path[0].append(st.session_state.pos[0])
st.session_state.path[1].append(st.session_state.pos[1])

# Drain battery
st.session_state.battery -= random.uniform(0.1, 0.5)
if st.session_state.battery < 0:
    st.session_state.battery = 0

# Geo-fence check
out_of_bounds = not (fence_bounds[0] <= st.session_state.pos[0] <= fence_bounds[1] and
                     fence_bounds[0] <= st.session_state.pos[1] <= fence_bounds[1])

# Simulated PID values
pid_output = {
    "P": random.uniform(0, 1),
    "I": random.uniform(0, 1),
    "D": random.uniform(0, 1)
}

# Simulated altitude
altitude = random.uniform(10, 100)
st.session_state.altitudes.append(altitude)
timestamp = time.strftime("%H:%M:%S")
st.session_state.timestamps.append(timestamp)

# Log current frame
st.session_state.log.append({
    "Time": timestamp,
    "X": st.session_state.pos[0],
    "Y": st.session_state.pos[1],
    "Altitude": altitude,
    "Battery": st.session_state.battery,
    "Speed": speed,
    "Flight Mode": flight_mode,
    "Out of Bounds": out_of_bounds
})

# Layout
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Altitude (m)", f"{altitude:.2f}")
    st.metric("Battery (%)", f"{st.session_state.battery:.2f}")
with col2:
    st.metric("Speed (u/s)", f"{speed:.2f}")
    st.metric("Flight Mode", flight_mode)
with col3:
    st.metric("PID P", f"{pid_output['P']:.2f}")
    st.metric("PID I", f"{pid_output['I']:.2f}")
    st.metric("PID D", f"{pid_output['D']:.2f}")

# GPS and Geo-Fence Display
st.subheader("Drone GPS Position and Geo-Fence")
fig = go.Figure()

# Geo-fence boundary
fig.add_shape(type="rect",
              x0=fence_bounds[0], y0=fence_bounds[0],
              x1=fence_bounds[1], y1=fence_bounds[1],
              line=dict(color="Green", width=2, dash="dash"))

# Drone trail
fig.add_trace(go.Scatter(
    x=st.session_state.path[0],
    y=st.session_state.path[1],
    mode="lines+markers",
    line=dict(color="blue"),
    marker=dict(size=6),
    name="Trail"
))

# Current drone position
fig.add_trace(go.Scatter(
    x=[st.session_state.pos[0]],
    y=[st.session_state.pos[1]],
    mode="markers",
    marker=dict(size=15, color="red" if out_of_bounds else "blue"),
    name="Current Position"
))

fig.update_layout(
    xaxis=dict(range=[-100, 100]),
    yaxis=dict(range=[-100, 100]),
    width=700,
    height=500
)

st.plotly_chart(fig)

# Altitude Over Time
st.subheader("Altitude Trend")
alt_fig = go.Figure()
alt_fig.add_trace(go.Scatter(
    x=st.session_state.timestamps,
    y=st.session_state.altitudes,
    mode="lines+markers",
    line=dict(color="orange"),
    name="Altitude"
))
alt_fig.update_layout(
    xaxis_title="Time",
    yaxis_title="Altitude (m)",
    height=300
)
st.plotly_chart(alt_fig, use_container_width=True)

# Alerts
if out_of_bounds:
    st.error("Warning: Drone is out of geo-fence bounds!")
if st.session_state.battery <= 10:
    st.warning("Low Battery!")

# Flight Log Export
st.subheader("Flight Log")
df_log = pd.DataFrame(st.session_state.log)
st.dataframe(df_log.tail(10), use_container_width=True)
csv = df_log.to_csv(index=False).encode("utf-8")
st.download_button("Download Full Flight Log (CSV)", csv, "flight_log.csv", "text/csv")

# Auto-refresh
time.sleep(1)
st.experimental_rerun()
