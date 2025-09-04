import streamlit as st
from datetime import datetime
import pandas as pd

# --- In-memory storage of last seen info ---
# Structure: { tail_number: {"hangar": str, "time": datetime} }
if "last_seen" not in st.session_state:
    st.session_state.last_seen = {}

st.title("Aircraft Hangar Dashboard")
st.markdown("""
Displays the last ping location for each aircraft.
Clean interface showing only tail number, hangar, and last seen time.
""")

# --- Simulate receiving a webhook ---
st.subheader("Simulate Webhook Ping")
sim_tail = st.text_input("Tail Number", "C-GABC")
sim_hangar = st.selectbox("Hangar", ["Palmer Hanger 2", "McCall Hanger (663847)"])
if st.button("Send Simulated Ping"):
    now = datetime.utcnow()
    st.session_state.last_seen[sim_tail] = {"hangar": sim_hangar, "time": now}
    st.success(f"Updated {sim_tail} to {sim_hangar} at {now.strftime('%Y-%m-%d %H:%M:%S UTC')}")

# --- Convert last_seen to DataFrame for display ---
if st.session_state.last_seen:
    df = pd.DataFrame([
        {"Tail Number": tail,
         "Hangar": info["hangar"],
         "Last Seen": info["time"].strftime('%Y-%m-%d %H:%M:%S UTC')}
        for tail, info in st.session_state.last_seen.items()
    ])
    df = df.sort_values("Tail Number")  # optional sorting

    st.subheader("Fleet Status")
    st.dataframe(df, use_container_width=True)
else:
    st.info("No aircraft pings received yet.")

# --- Optional: Auto-refresh every 30 seconds ---
st_autorefresh = st.checkbox("Auto-refresh every 30 seconds", value=True)
if st_autorefresh:
    st.experimental_rerun()
