import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

# -------------------------------
# In-memory storage for last seen
# -------------------------------
if "last_seen" not in st.session_state:
    st.session_state.last_seen = {
        "C-GABC": {"hangar": "Palmer Hanger 2", "time": datetime.utcnow() - timedelta(minutes=1)},
        "C-GXYZ": {"hangar": "McCall Hanger (663847)", "time": datetime.utcnow() - timedelta(minutes=10)},
        "C-GNOV": {"hangar": "Palmer Hanger 2", "time": datetime.utcnow() - timedelta(minutes=3)}
    }

st.title("Aircraft Hangar Dashboard")
st.markdown("""
Displays the last ping location for each aircraft.
Rows highlighted in green show pings received in the last 5 minutes (“NOW”).
""")

# -------------------------------
# Optional: Simulate webhook ping
# -------------------------------
st.subheader("Simulate Webhook Ping")
sim_tail = st.text_input("Tail Number", "C-GABC")
sim_hangar = st.selectbox("Hangar", ["Palmer Hanger 2", "McCall Hanger (663847)"])
if st.button("Send Simulated Ping"):
    now = datetime.utcnow()
    st.session_state.last_seen[sim_tail] = {"hangar": sim_hangar, "time": now}
    st.success(f"Updated {sim_tail} to {sim_hangar} at {now.strftime('%H:%M:%S UTC')}")

# -------------------------------
# Prepare DataFrame
# -------------------------------
rows = []
now_cutoff = datetime.utcnow() - timedelta(minutes=5)

for tail, info in st.session_state.last_seen.items():
    if info["time"] >= now_cutoff:
        last_seen_str = "NOW"
        highlight = True
    else:
        last_seen_str = info["time"].strftime('%H:%M:%S UTC')
        highlight = False
    rows.append({
        "Tail Number": tail,
        "Hangar": info["hangar"],
        "Last Seen": last_seen_str,
        "Highlight": highlight
    })

df = pd.DataFrame(rows)

# Sort so 'NOW' rows are at the top
df.sort_values("Highlight", ascending=False, inplace=True)

# -------------------------------
# Highlighting function
# -------------------------------
def highlight_now(row):
    return ['background-color: #90ee90' if row["Highlight"] else '' for _ in row]

# -------------------------------
# Display table
# -------------------------------
st.subheader("Fleet Status")
st.dataframe(
    df.style.apply(highlight_now, axis=1).hide_columns(["Highlight"]),
    use_container_width=True
)

# -------------------------------
# Auto-refresh checkbox
# -------------------------------
auto_refresh = st.checkbox("Auto-refresh every 30 seconds", value=True, key="auto_refresh_checkbox")
if auto_refresh:
    st.experimental_rerun()
