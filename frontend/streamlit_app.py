import streamlit as st
import requests
import os

# ✅ Get backend URL from environment variable or default to Railway URL
API_BASE = os.getenv("BACKEND_URL", "https://distinguished-imagination-production.up.railway.app")

st.title("📊 Data Quality Dashboard - Frontend")
st.write("This is the Streamlit frontend connected to your Flask backend.")

# 🔗 Health Check
st.subheader("🔍 Backend Health Check")
try:
    res = requests.get(f"{API_BASE}/health", timeout=5)
    if res.status_code == 200:
        st.success(f"✅ Backend is online! Response: {res.json()}")
    else:
        st.error(f"❌ Backend returned an error: {res.status_code}")
except Exception as e:
    st.error(f"Failed to connect to backend: {e}")

# Example API call (adjust based on your backend routes)
st.subheader("📡 Example API Call")
try:
    res = requests.get(f"{API_BASE}/api/your-endpoint")
    if res.status_code == 200:
        st.json(res.json())
    else:
        st.warning(f"No data or endpoint returned {res.status_code}")
except Exception as e:
    st.warning(f"API call failed: {e}")
