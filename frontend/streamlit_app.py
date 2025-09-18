import streamlit as st
import requests
import os
import pandas as pd

# ✅ Backend URL (use secrets in Streamlit Cloud for flexibility)
API_BASE = os.getenv("BACKEND_URL", "https://distinguished-imagination-production.up.railway.app")

st.set_page_config(page_title="Data Quality Dashboard", layout="wide")
st.title("📊 Data Quality Dashboard - Frontend")
st.write("This is the Streamlit frontend connected to your Flask backend.")

# 🔍 Backend Health
st.subheader("🔍 Backend Health Check")
try:
    res = requests.get(f"{API_BASE}/health", timeout=5)
    if res.status_code == 200:
        st.success(f"✅ Backend is online! Response: {res.json()}")
    else:
        st.error(f"❌ Backend returned an error: {res.status_code}")
except Exception as e:
    st.error(f"Failed to connect to backend: {e}")

st.divider()

# 📡 Example API Call
st.subheader("📡 Example API Call")
try:
    res = requests.get(f"{API_BASE}/api/")  # Your example route
    if res.status_code == 200:
        st.success("✅ Data received successfully!")
        st.json(res.json())
    else:
        st.warning(f"Endpoint returned {res.status_code}")
except Exception as e:
    st.error(f"API call failed: {e}")

st.divider()

# 📈 Analytics Section
st.subheader("📊 Analytics (last 7 days)")
try:
    res = requests.get(f"{API_BASE}/api/analytics", timeout=5)
    if res.status_code == 200:
        data = res.json()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Sessions", data.get("total_sessions", 0))
        col2.metric("Completed Sessions", data.get("completed_sessions", 0))
        col3.metric("Avg. Duration (min)", data.get("avg_duration_minutes", 0))

        st.metric(label="Total Actions", value=data.get("total_actions", 0))
        st.metric(label="Avg Actions per Session", value=data.get("avg_actions_per_session", 0))
    else:
        st.warning(f"Analytics endpoint returned {res.status_code}")
except Exception as e:
    st.error(f"Failed to fetch analytics: {e}")

st.divider()

# 📝 Feedback Table
st.subheader("📝 User Feedback")
try:
    res = requests.get(f"{API_BASE}/api/feedback?limit=20", timeout=5)
    if res.status_code == 200:
        feedback_data = res.json()
        feedback_list = feedback_data.get("feedback", [])

        if feedback_list:
            df = pd.DataFrame(feedback_list)
            # Clean columns for display
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No feedback found yet.")
    else:
        st.warning(f"Feedback endpoint returned {res.status_code}")
except Exception as e:
    st.error(f"Failed to fetch feedback: {e}")
