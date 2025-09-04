import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# -------------------------------
# Get credentials from Streamlit Secrets
# -------------------------------
USERNAME = st.secrets["WESTCOAST_USER"]
PASSWORD = st.secrets["WESTCOAST_PASS"]

# -------------------------------
# Selenium Scraper Function
# -------------------------------
def scrape_westcoast_dashboard(username, password):
    """
    Logs into WestCoast GPS and scrapes the aircraft table.
    Returns a DataFrame with Tail, Hangar, Last Ping.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # run in background
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # 1️⃣ Go to login page (replace with actual URL)
        driver.get("https://your-westcoast-login-page.com")

        # 2️⃣ Enter credentials (update selectors)
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "login-button").click()

        # 3️⃣ Wait for table to load
        driver.implicitly_wait(5)

        # 4️⃣ Scrape aircraft table (update CSS selector)
        table_rows = driver.find_elements(By.CSS_SELECTOR, "table#aircraft-table tbody tr")

        data = []
        for row in table_rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            tail = cells[0].text.strip()
            hangar = cells[1].text.strip()
            last_ping = cells[2].text.strip()  # adjust index if needed

            try:
                last_ping_dt = datetime.strptime(last_ping, "%Y-%m-%d %H:%M:%S")
            except:
                last_ping_dt = datetime.utcnow() - timedelta(days=1)

            data.append({
                "Tail Number": tail,
                "Hangar": hangar,
                "Last Seen": last_ping_dt
            })

        df = pd.DataFrame(data)
        return df

    finally:
        driver.quit()

# -------------------------------
# Streamlit Dashboard
# -------------------------------
st.title("Aircraft Hangar Dashboard")
st.markdown("""
Displays the last ping location for each aircraft.  
Rows highlighted in green show pings received in the last 5 minutes (“NOW”).
""")

# -------------------------------
# Scrape Data
# -------------------------------
with st.spinner("Fetching latest aircraft positions..."):
    df = scrape_westcoast_dashboard(USERNAME, PASSWORD)

# -------------------------------
# Compute 'NOW' and Highlight
# -------------------------------
now_cutoff = datetime.utcnow() - timedelta(minutes=5)
df["Highlight"] = df["Last Seen"] >= now_cutoff
df["Last Seen Display"] = df["Last Seen"].apply(lambda x: "NOW" if x >= now_cutoff else x.strftime('%H:%M:%S'))

# Sort 'NOW' rows to top
df.sort_values("Highlight", ascending=False, inplace=True)

# -------------------------------
# Highlighting function
# -------------------------------
def highlight_now(row):
    return ['background-color: #90ee90' if row["Highlight"] else '' for _ in row]

df_display = df.drop(columns=["Highlight", "Last Seen"])
st.subheader("Fleet Status")
st.dataframe(df_display.style.apply(highlight_now, axis=1), use_container_width=True)

# -------------------------------
# Auto-refresh checkbox
# -------------------------------
if "last_action" not in st.session_state:
    st.session_state.last_action = None

auto_refresh = st.checkbox("Auto-refresh every 30 seconds", value=True, key="auto_refresh_checkbox")

if auto_refresh and st.session_state.last_action != "button_click":
    st.experimental_rerun()
else:
    st.session_state.last_action = None
