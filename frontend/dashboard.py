import os
import csv
import time
import math
import io
import json
import numpy as np
import requests
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime, timedelta
import streamlit.components.v1 as components

try:
	import plotly.express as px  # optional
except Exception:
	px = None

# -------------------------
# Page config
# -------------------------
st.set_page_config(
	page_title="Data Quality Dashboard",
	page_icon="✅",
	layout="wide",
	initial_sidebar_state="expanded",
)

# -------------------------
# CSS loader (optional external CSS)
# -------------------------
def load_custom_css() -> None:
	# Looks for multiple likely CSS locations
	candidate_paths = [
		os.path.join("frontend", "assets", "styles.css"),
		os.path.join("frontend", "style.css"),
		os.path.join("assets", "styles.css"),
		"styles.css",
	]
	for path in candidate_paths:
		if os.path.exists(path):
			with open(path, "r", encoding="utf-8") as f:
				st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
			return

# Baseline minimal CSS (overridden if external found)
st.markdown(
	"""
	<style>
		.kpi-card { border-radius: 14px; padding: 18px 18px; background: linear-gradient(180deg, #0f172a 0%, #0b1222 100%); border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 6px 22px rgba(0,0,0,0.25); color: #e5e7eb; }
		.kpi-title { font-size: 12px; color: #9ca3af; text-transform: uppercase; letter-spacing: .08em; margin-bottom: 6px; }
		.kpi-value { font-size: 30px; font-weight: 800; line-height: 1.1; color: #fafafa; }
		.kpi-delta.pos { color: #10b981; } .kpi-delta.neg { color: #ef4444; } .kpi-delta.neu { color: #9ca3af; }
		.card { border-radius: 14px; padding: 18px 18px; background: #0b1222; border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 6px 22px rgba(0,0,0,0.25); color: #e5e7eb; }
		.section-title { font-size: 16px; font-weight: 700; margin: 0 0 12px 0; color: #e5e7eb; }
		.small-muted { color: #9ca3af; font-size: 12px; }
		.hero-title { font-size: 28px; font-weight: 800; color: #fafafa; margin-bottom: 8px; }
		.dq-progress { background: rgba(255,255,255,0.1); border-radius: 8px; height: 8px; overflow: hidden; }
		.dq-progress .fill { background: linear-gradient(90deg, #10b981, #34d399); height: 100%; transition: width 0.3s ease; }
		
		/* Footer Styling */
		.app-footer { 
			position: fixed !important; 
			bottom: 0 !important; 
			left: 0 !important; 
			right: 0 !important; 
			z-index: 9999 !important; 
			background: #0f172a !important; 
			border-top: 1px solid rgba(255,255,255,0.1) !important; 
			padding: 10px 20px !important; 
			box-shadow: 0 -4px 20px rgba(0,0,0,0.5) !important;
		}
		.footer-links { 
			display: flex !important; 
			justify-content: space-between !important; 
			align-items: flex-start !important; 
			width: 100% !important; 
			max-width: 1200px !important;
			margin: 0 auto !important;
		}
		.footer-item { 
			text-align: center !important; 
			position: relative !important; 
			flex: 1 !important;
			margin: 0 10px !important;
		}
		.footer-title { 
			display: block !important; 
			padding: 8px 12px !important; 
			background: #1e293b !important; 
			color: #e2e8f0 !important; 
			border-radius: 6px !important; 
			cursor: pointer !important; 
			transition: all 0.2s ease !important; 
			margin-bottom: 8px !important; 
			font-weight: 500 !important; 
		}
		.footer-title:hover { background: #334155 !important; color: #f1f5f9 !important; }
		.footer-desc { 
			display: none; 
			position: absolute; 
			bottom: 100%; 
			left: 50%; 
			transform: translateX(-50%); 
			background: #0f172a; 
			border: 1px solid #334155; 
			border-radius: 8px; 
			padding: 12px; 
			min-width: 250px; 
			max-width: 320px; 
			color: #cbd5e1; 
			font-size: 12px; 
			line-height: 1.4; 
			z-index: 10000; 
			box-shadow: 0 4px 20px rgba(0,0,0,0.6); 
			margin-bottom: 10px; 
		}
		.footer-item input[type="radio"]:checked + .footer-title { background: #3b82f6 !important; color: white !important; }
		.footer-item input[type="radio"]:checked ~ .footer-desc { display: block; }
		.footer-item input[type="radio"] { display: none; }
		.footer-desc a { color: #60a5fa; text-decoration: none; }
		.footer-desc a:hover { color: #93c5fd; text-decoration: underline; }
		.footer-close { 
			position: absolute; 
			top: 8px; 
			right: 8px; 
			background: #ef4444; 
			color: white; 
			border-radius: 50%; 
			width: 20px; 
			height: 20px; 
			display: flex; 
			align-items: center; 
			justify-content: center; 
			font-size: 14px; 
			font-weight: bold; 
			cursor: pointer; 
			transition: all 0.2s ease;
		}
		.footer-close:hover { 
			background: #dc2626; 
			transform: scale(1.1); 
		}
		
		/* Ensure main content doesn't overlap footer and center content */
		.main .block-container { 
			padding-bottom: 120px !important; 
			max-width: 95% !important;
			margin: 0 auto !important;
		}
		
		/* Sidebar styling - make it more compact */
		section[data-testid="stSidebar"] {
			width: 280px !important;
			min-width: 280px !important;
		}
		section[data-testid="stSidebar"] > div {
			width: 280px !important;
			padding-left: 1rem !important;
			padding-right: 1rem !important;
		}
		
		/* Sidebar inputs - more compact */
		section[data-testid="stSidebar"] .stSelectbox,
		section[data-testid="stSidebar"] .stTextInput,
		section[data-testid="stSidebar"] .stMultiSelect,
		section[data-testid="stSidebar"] .stNumberInput {
			max-width: 100% !important;
		}
		
		section[data-testid="stSidebar"] .stSelectbox > div,
		section[data-testid="stSidebar"] .stTextInput > div,
		section[data-testid="stSidebar"] .stMultiSelect > div,
		section[data-testid="stSidebar"] .stNumberInput > div {
			font-size: 14px !important;
		}
		
		/* Fix number input overflow - constrain within sidebar */
		section[data-testid="stSidebar"] .stNumberInput {
			overflow: hidden !important;
		}
		section[data-testid="stSidebar"] .stNumberInput > div > div {
			max-width: 100% !important;
			overflow: hidden !important;
		}
		section[data-testid="stSidebar"] .stNumberInput input {
			max-width: 100% !important;
		}
		section[data-testid="stSidebar"] .stNumberInput button {
			padding: 0.25rem 0.5rem !important;
			font-size: 14px !important;
		}
		
		/* Sidebar buttons - normal width */
		section[data-testid="stSidebar"] .stButton > button {
			width: auto !important;
			padding: 0.5rem 1rem !important;
			font-size: 14px !important;
		}
		
		/* Mobile Responsive Styles */
		@media screen and (max-width: 768px) {
			/* Main container adjustments */
			.main .block-container { 
				padding-bottom: 180px !important; 
				padding-left: 1rem !important;
				padding-right: 1rem !important;
				max-width: 95% !important;
				margin: 0 auto !important;
			}
			
			/* KPI Cards - Stack vertically on mobile */
			.kpi-card { 
				margin-bottom: 1rem !important;
				padding: 16px !important;
			}
			.kpi-value { 
				font-size: 24px !important; 
			}
			.kpi-title { 
				font-size: 11px !important; 
			}
			
			/* Footer adjustments for mobile */
			.app-footer { 
				padding: 8px 10px !important; 
				height: auto !important;
			}
			.footer-links { 
				flex-direction: column !important; 
				gap: 8px !important;
			}
			.footer-item { 
				margin: 0 5px 8px 5px !important; 
				flex: none !important;
			}
			.footer-title { 
				padding: 6px 10px !important; 
				font-size: 13px !important;
				margin-bottom: 4px !important;
			}
			.footer-desc { 
				min-width: 280px !important; 
				max-width: 90vw !important;
				font-size: 11px !important;
				padding: 10px !important;
				left: 10px !important;
				transform: none !important;
			}
			
			/* Section titles */
			.section-title { 
				font-size: 14px !important; 
				margin-bottom: 8px !important;
			}
			
			/* Hero title */
			.hero-title { 
				font-size: 20px !important; 
			}
			
			/* Cards and containers */
			.card { 
				padding: 12px !important; 
				margin-bottom: 1rem !important;
			}
			
			/* Streamlit columns - force single column on mobile */
			.stColumns > div { 
				min-width: 100% !important; 
				margin-bottom: 1rem !important;
			}
			
			/* Tables - horizontal scroll */
			.stDataFrame { 
				overflow-x: auto !important; 
			}
			
			/* Charts - make responsive */
			.stPlotlyChart, .stPyplot { 
				width: 100% !important; 
				height: auto !important;
			}
			
			/* Form elements */
			.stSelectbox, .stTextInput, .stTextArea, .stNumberInput { 
				margin-bottom: 0.5rem !important; 
			}
			
			/* Number input - ensure it fits on mobile */
			.stNumberInput {
				max-width: 100% !important;
			}
			.stNumberInput > div > div {
				max-width: 100% !important;
			}
			
			/* Buttons */
			.stButton > button { 
				width: 100% !important; 
				margin-bottom: 0.5rem !important;
			}
			
			/* Download buttons */
			.stDownloadButton > button { 
				width: 100% !important; 
				margin-bottom: 0.5rem !important;
				font-size: 12px !important;
				padding: 0.5rem !important;
			}
			
			/* Metrics */
			.stMetric { 
				margin-bottom: 1rem !important; 
			}
			
			/* Sidebar adjustments */
			.css-1d391kg { 
				padding-top: 1rem !important; 
			}
		}
		
		@media screen and (max-width: 480px) {
			/* Extra small screens */
			.main .block-container { 
				padding-left: 0.5rem !important;
				padding-right: 0.5rem !important;
				padding-bottom: 200px !important;
				max-width: 95% !important;
				margin: 0 auto !important;
			}
			
			.kpi-card { 
				padding: 12px !important; 
			}
			.kpi-value { 
				font-size: 20px !important; 
			}
			.kpi-title { 
				font-size: 10px !important; 
			}
			
			.footer-desc { 
				min-width: 260px !important; 
				max-width: 95vw !important;
				font-size: 10px !important;
			}
			
			.footer-title { 
				font-size: 12px !important; 
				padding: 5px 8px !important;
			}
			
			.hero-title { 
				font-size: 18px !important; 
			}
			
			.section-title { 
				font-size: 13px !important; 
			}
		}
		
		/* Tablet landscape adjustments */
		@media screen and (min-width: 769px) and (max-width: 1024px) {
			.main .block-container { 
				padding-left: 1.5rem !important;
				padding-right: 1.5rem !important;
				max-width: 95% !important;
				margin: 0 auto !important;
			}
			
			.footer-links { 
				flex-wrap: wrap !important; 
			}
			.footer-item { 
				flex: 1 1 45% !important; 
				margin: 0 5px 10px 5px !important;
			}
		}
		
		/* Chart spacing - add gap between charts */
		div[data-testid="column"] {
			margin: 0 8px !important;
		}
		
		/* Ensure responsive behavior for Streamlit elements */
		@media screen and (max-width: 768px) {
			/* Force single column layout for all column containers */
			div[data-testid="column"] {
				width: 100% !important;
				min-width: 100% !important;
				margin-bottom: 1rem !important;
			}
			
			/* Tab container adjustments */
			.stTabs [data-baseweb="tab-list"] {
				gap: 0.5rem !important;
				flex-wrap: wrap !important;
			}
			
			.stTabs [data-baseweb="tab"] {
				font-size: 12px !important;
				padding: 0.5rem !important;
			}
			
			/* File uploader */
			.stFileUploader {
				margin-bottom: 1rem !important;
			}
			
			/* Expander */
			.streamlit-expanderHeader {
				font-size: 13px !important;
			}
			
			/* Progress bars */
			.dq-progress {
				height: 6px !important;
				margin-top: 4px !important;
			}
		}
	</style>
	""",
	unsafe_allow_html=True,
)
load_custom_css()

# -------------------------
# Sidebar controls
# -------------------------
st.sidebar.title("Controls")

default_api = os.getenv("BACKEND_URL", "http://127.0.0.1:5001")
api_base_url = st.sidebar.text_input("API Base URL", value=default_api).rstrip("/")

try:
    health_url = f"{api_base_url}/health"
    ok = False
    try:
        r = requests.get(health_url, timeout=2)
        ok = r.ok
    except Exception:
        ok = False
    if not ok:
        fallback = "http://127.0.0.1:5001"
        try:
            r2 = requests.get(f"{fallback}/health", timeout=2)
            if r2.ok:
                api_base_url = fallback
                st.session_state["api_base_url"] = fallback
        except Exception:
            pass
except Exception:
    pass

# Date presets with awareness of uploaded dataset date range
preset = st.sidebar.selectbox("Date Preset", ["Last 7 days", "Last 30 days", "Custom"], index=1)
today = datetime.utcnow().date()

# Detect uploaded dataset date bounds (if available)
uploaded_df = st.session_state.get("upload_df") if "upload_df" in st.session_state else None
uploaded_date_col = st.session_state.get("upload_date_col") if "upload_date_col" in st.session_state else None
upload_active = uploaded_df is not None

# If upload has been removed, clear any lingering upload-specific state so app resets to defaults
if not upload_active:
    if "upload_date_col" in st.session_state:
        del st.session_state["upload_date_col"]
    if "per_col_filters" in st.session_state:
        del st.session_state["per_col_filters"]
data_min_date = None
data_max_date = None

if uploaded_df is not None:
    try:
        # If no date column has been chosen yet, attempt strict auto-detection now
        if not uploaded_date_col or uploaded_date_col not in uploaded_df.columns:
            best_col = None
            best_score = (-1, -1, -1)  # (valid_ratio, unique_days, span_days)
            for c in uploaded_df.columns:
                # Skip obvious non-date columns (ids, indices, keys, numeric small ints)
                name = str(c).lower()
                if any(token in name for token in ["id", "index", "idx", "key", "pk", "number", "num", "#"]):
                    continue
                ser = uploaded_df[c]
                # Skip numeric columns that are not plausible unix timestamps
                if pd.api.types.is_numeric_dtype(ser):
                    non_null = ser.dropna()
                    if non_null.empty:
                        continue
                    sample = non_null.iloc[0]
                    if sample < 1_000_000_000 or sample > 9_999_999_999:
                        continue
                # Try several strict formats first
                parsed = None
                for fmt in ('%Y-%m-%d','%m/%d/%Y','%d/%m/%Y','%Y/%m/%d','%m-%d-%Y','%d-%m-%Y','%Y%m%d','%m/%d/%y','%d/%m/%y'):
                    try:
                        tmp = pd.to_datetime(ser, format=fmt, errors='coerce')
                        if tmp.notna().mean() >= 0.8:
                            parsed = tmp
                            break
                    except Exception:
                        continue
                # Fallback to pandas parser with strict validation
                if parsed is None:
                    tmp = pd.to_datetime(ser, errors='coerce')
                    if tmp.notna().mean() >= 0.8:
                        parsed = tmp
                if parsed is None or parsed.isna().all():
                    continue
                valid = parsed.dropna()
                if valid.empty:
                    continue
                min_year = valid.min().year
                max_year = valid.max().year
                curr_year = datetime.utcnow().year
                if not (1900 <= min_year <= curr_year + 1 and 1900 <= max_year <= curr_year + 1):
                    continue
                valid_ratio = float(valid.size) / float(len(parsed))
                unique_days = valid.dt.normalize().nunique()
                span_days = int((valid.max() - valid.min()).days) if valid.size > 1 else 0
                score = (valid_ratio, unique_days, span_days)
                if score > best_score:
                    best_score = score
                    best_col = c
            if best_col:
                uploaded_date_col = best_col
                st.session_state.upload_date_col = best_col

        # If we now have a valid date column, compute bounds from it
        if uploaded_date_col and uploaded_date_col in uploaded_df.columns:
            series = pd.to_datetime(uploaded_df[uploaded_date_col], errors='coerce').dropna()
            if not series.empty:
                data_min_date = series.min().date()
                data_max_date = series.max().date()
    except Exception:
        pass

# Strictly use data bounds if CSV is uploaded, otherwise use reasonable defaults
if data_min_date is not None and data_max_date is not None:
	# Use exact data bounds - no extensions or modifications
	overall_min = data_min_date
	overall_max = data_max_date
	# Silently use data bounds without cluttering sidebar
	pass
else:
	# Default range when no CSV uploaded
	overall_min = today - timedelta(days=365)
	overall_max = today

# Universal preset logic that works with or without CSV
if preset == "Last 7 days":
	default_end = overall_max
	if data_min_date is not None and data_max_date is not None:
		# Calculate actual data span
		data_span_days = (data_max_date - data_min_date).days + 1
		# If data span is less than 7 days, show all data
		if data_span_days <= 7:
			default_start = overall_min
		else:
			# Show last 7 days from the end of data
			calculated_start = default_end - timedelta(days=6)
			default_start = max(overall_min, calculated_start)
	else:
		# Default case: show last 7 days from overall_max
		default_start = max(overall_min, default_end - timedelta(days=6))

elif preset == "Last 30 days":
	default_end = overall_max
	if data_min_date is not None and data_max_date is not None:
		# Calculate actual data span
		data_span_days = (data_max_date - data_min_date).days + 1
		# If data span is less than 30 days, show all data
		if data_span_days <= 30:
			default_start = overall_min
		else:
			# Show last 30 days from the end of data
			calculated_start = default_end - timedelta(days=29)
			default_start = max(overall_min, calculated_start)
	else:
		# Default case: show last 30 days from overall_max
		default_start = max(overall_min, default_end - timedelta(days=29))

else:  # Custom
    default_start = overall_min
    default_end = overall_max

if preset == "Custom":
    # Only show date range input when a CSV is uploaded
    if upload_active:
        # Use a different widget key depending on whether an upload is active to force reset when CSV is removed
        date_widget_key = "date_range_uploaded" if upload_active else "date_range_default"
        date_range = st.sidebar.date_input(
            "Date Range (optional - leave empty to show all data)",
            value=(),  # Empty tuple to show date range picker without default selection
            min_value=overall_min,
            max_value=overall_max,
            key=date_widget_key,
        )
    else:
        # No CSV uploaded, don't show date range input
        date_range = None

# Authoritative start/end based on preset (Custom uses widget)
apply_date_filter = True  # Flag to control date filtering
if preset == "Custom":
	# For Custom preset: if no date range selected, show all data
	if date_range is not None and isinstance(date_range, (tuple, list)) and len(date_range) == 2:
		# User selected specific dates - filter to that range
		start_dt, end_dt = date_range[0], date_range[1]
		apply_date_filter = True
	else:
		# No date range selected - show all data (skip date filtering)
		start_dt, end_dt = overall_min, overall_max
		apply_date_filter = False  # Don't apply date filter - show all data
else:
	start_dt = default_start
	end_dt = default_end
	apply_date_filter = True

# normalize to full-day bounds
start_dt = datetime.combine(start_dt, datetime.min.time())
end_dt = datetime.combine(end_dt, datetime.max.time())

# Filters
_default_cols = ["Name", "Age", "Salary", "Department", "JoinDate"]
_uploaded_cols = []
try:
	if st.session_state.get("upload_df") is not None:
		_uploaded_cols = [str(c) for c in st.session_state["upload_df"].columns]
except Exception:
	_uploaded_cols = []
column_filter = st.sidebar.multiselect(
	"Filter by column",
	options=_uploaded_cols or _default_cols,
	default=[],
)
# Simple duplicate detection - just 2 options
duplicate_mode = st.sidebar.radio(
	"Duplicate Detection Mode",
	options=["By ID Column", "By All Columns"],
	index=0,
	help="Choose how to detect duplicates: by a specific ID column or by comparing all columns"
)

id_column_name = None
if duplicate_mode == "By ID Column":
	if _uploaded_cols:
		# Auto-detect ID column
		id_candidates = [c for c in _uploaded_cols if 'id' in str(c).lower()]
		id_column_name = id_candidates[0] if id_candidates else _uploaded_cols[0]
	else:
		id_column_name = None

# Chart controls removed

# Refresh controls (manual only)
refresh_now = st.sidebar.button("Refresh Now")
# Reset views
reset_clicked = st.sidebar.button("Reset Views", key="reset_views_btn")
if reset_clicked:
	st.session_state.show_valid = False
	st.session_state.show_warnings = False
	st.session_state.show_errors = False

# Thresholds
error_threshold = st.sidebar.number_input("Critical Quality Threshold (1-20 scale)", min_value=1, max_value=20, value=10, step=1, help="Set threshold on 1-20 scale where 20 = 100% errors, 19 = 95% errors, etc.")

# Drill-down state
if "show_errors" not in st.session_state: st.session_state.show_errors = False
if "show_warnings" not in st.session_state: st.session_state.show_warnings = False
if "show_valid" not in st.session_state: st.session_state.show_valid = False

# -------------------------
# Data fetching and caching
# -------------------------
def _mock_data(start_date: datetime, end_date: datetime) -> pd.DataFrame:
	dates = pd.date_range(start=start_date, end=end_date, freq="D")
	rng = pd.Series(range(len(dates)))
	base_valid = 10000 + (rng * 35).clip(upper=900)
	warnings = (25 + 12 * (1 + (rng % 7))).astype(int)
	errors = (12 + 7 * (1 + ((rng + 3) % 5))).astype(int)
	df = pd.DataFrame({
		"date": dates,
		"valid": base_valid.astype(int),
		"warning": warnings,
		"error": errors,
	})
	return df

@st.cache_data(show_spinner=False, ttl=300, max_entries=10)
def fetch_quality_data(api_url: str, start_dt: datetime, end_dt: datetime) -> pd.DataFrame:
	params = {"start": start_dt.strftime("%Y-%m-%d"), "end": end_dt.strftime("%Y-%m-%d")}
	url = f"{api_url}/api/quality"
	try:
		resp = requests.get(url, params=params, timeout=8)
		resp.raise_for_status()
		payload = resp.json()
		items = payload.get("data", [])
		df = pd.DataFrame(items)
		if df.empty:
			return _mock_data(start_dt, end_dt)
		df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
		return df.sort_values("date")
	except Exception:
		return _mock_data(start_dt, end_dt)

# -------------------------
# Utility functions
# -------------------------
def format_int(n: int) -> str:
	if n is None or (isinstance(n, float) and math.isnan(n)):
		return "–"
	if n >= 1_000_000:
		return f"{n/1_000_000:.1f}M"
	if n >= 1_000:
		return f"{n/1_000:.1f}k"
	return f"{n:,}"

def compute_delta(curr: int, prev: int) -> tuple[str, str]:
	if prev is None or prev == 0:
		return ("–", "neu")
	diff = curr - prev
	sign = "pos" if diff >= 0 else "neg"
	return (f"{diff:+,}", sign if diff != 0 else "neu")

def get_prev_period_index(df: pd.DataFrame, window: int = 7) -> int:
	if len(df) <= window:
		return max(0, len(df) - 2)
	return max(0, len(df) - window - 1)

# -------------------------
# Header
# -------------------------
st.markdown(
    f"""
    <div style='text-align: center; margin: 0 auto; max-width: 800px;'>
        <h1 class='hero-title' style='margin: 0.5em 0;'>Data Quality Dashboard</h1>
        <div class='small-muted'>API: {api_base_url}</div>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------
# Data load
# -------------------------
# Check if we have uploaded data
use_uploaded = bool(st.session_state.get("upload_df") is not None)

if use_uploaded:
	# Use uploaded data
	with st.spinner("Processing uploaded data..."):
		df = pd.DataFrame()  # Will be populated below from uploaded data
else:
	# Use default/mock data when no file is uploaded
	with st.spinner("Loading default data..."):
		df = fetch_quality_data(api_base_url, start_dt, end_dt)
if use_uploaded:
	df_up = st.session_state.get("upload_df").copy()
	date_col = st.session_state.get("upload_date_col")
	# If no date column selected, try to auto-detect a likely date column
	if not date_col:
		try:
			candidates = []
			for c in df_up.columns:
				# Skip columns that are likely IDs or numeric indices
				col_name_lower = str(c).lower()
				if any(skip_word in col_name_lower for skip_word in ['id', 'index', 'idx', 'key', 'pk', 'number', 'num', '#']):
					continue
				
				ser = df_up[c]
				
				# Skip if column is purely numeric (likely not dates)
				if pd.api.types.is_numeric_dtype(ser):
					# Check if it could be timestamps (large numbers)
					if ser.notna().any():
						sample_val = ser.dropna().iloc[0] if len(ser.dropna()) > 0 else 0
						# Skip if values are too small (likely IDs) or too large (likely not dates)
						if sample_val < 1000000000 or sample_val > 9999999999:  # Not Unix timestamp range
							continue
				
				# Try robust date parsing with multiple strategies
				parsed = None
				successful_format = None
				
				# Strategy 1: Try specific date formats first
				date_formats = [
					'%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d', 
					'%m-%d-%Y', '%d-%m-%Y', '%Y%m%d', '%m/%d/%y', '%d/%m/%y',
					'%Y-%m-%d %H:%M:%S', '%m/%d/%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S'
				]
				
				for fmt in date_formats:
					try:
						test_parsed = pd.to_datetime(ser, format=fmt, errors="coerce")
						valid_count = test_parsed.notna().sum()
						
						if valid_count > len(ser) * 0.6:  # At least 60% valid (more lenient)
							# Validate year range
							valid_dates = test_parsed.dropna()
							if len(valid_dates) > 0:
								min_year = valid_dates.min().year
								max_year = valid_dates.max().year
								current_year = datetime.now().year
								
								# More lenient year validation
								if 1900 <= min_year <= current_year + 2 and 1900 <= max_year <= current_year + 2:
									parsed = test_parsed
									successful_format = fmt
									break
					except:
						continue
				
				# Strategy 2: If specific formats failed, try auto-detection
				if parsed is None or parsed.isna().all():
					try:
						test_parsed = pd.to_datetime(ser, errors="coerce")
						valid_dates = test_parsed.dropna()
						if len(valid_dates) > len(ser) * 0.6:  # More lenient threshold
							min_year = valid_dates.min().year
							max_year = valid_dates.max().year
							current_year = datetime.now().year
							
							# More lenient validation for auto-detection
							if 1900 <= min_year <= current_year + 2 and 1900 <= max_year <= current_year + 2:
								parsed = test_parsed
								successful_format = "auto"
					except:
						pass
				
				# Strategy 3: Try infer_datetime_format for edge cases
				if parsed is None or parsed.isna().all():
					try:
						test_parsed = pd.to_datetime(ser, infer_datetime_format=True, errors="coerce")
						valid_dates = test_parsed.dropna()
						if len(valid_dates) > len(ser) * 0.6:
							min_year = valid_dates.min().year
							max_year = valid_dates.max().year
							current_year = datetime.now().year
							
							if 1900 <= min_year <= current_year + 2 and 1900 <= max_year <= current_year + 2:
								parsed = test_parsed
								successful_format = "infer"
					except:
						pass
				
				if parsed is not None and not parsed.isna().all():
					valid_ratio = float(parsed.notna().mean()) if len(parsed) else 0.0
					unique_days = parsed.dt.normalize().nunique() if parsed.notna().any() else 0
					
					# More lenient criteria for date column detection
					if valid_ratio >= 0.6 and unique_days >= 1:  # 60% valid, at least 1 unique day
						# Calculate date range span for scoring
						if parsed.notna().any():
							date_span_days = (parsed.max() - parsed.min()).days if parsed.notna().sum() > 1 else 0
							candidates.append((c, valid_ratio, unique_days, date_span_days))
			
			if candidates:
				# Sort by valid_ratio first, then unique_days, then date_span
				candidates.sort(key=lambda x: (x[1], x[2], x[3]), reverse=True)
				date_col = candidates[0][0]
				# persist detection
				st.session_state.upload_date_col = date_col
				
				# Silently detect date range without showing confusing message
		except Exception:
			pass

	# Per-column row filters removed per request; keep a passthrough structure to avoid breakage
	per_col_filters = {}
	st.session_state.per_col_filters = per_col_filters
	filtered_df = df_up.copy()

	# Column filter defines which columns participate in missing (warnings)
	quality_cols = [c for c in (column_filter or []) if c in filtered_df.columns]
	if not quality_cols:
		quality_cols = list(filtered_df.columns)


	# Simple duplicate detection based on mode
	if duplicate_mode == "By ID Column" and id_column_name and id_column_name in filtered_df.columns:
		dup_mask = filtered_df.duplicated(subset=[id_column_name], keep=False)
	else:
		# By all columns
		dup_mask = filtered_df.duplicated(keep=False)
	# Warnings: missing in quality_cols only
	if quality_cols:
		missing_mask = filtered_df[quality_cols].isna().any(axis=1)
	else:
		missing_mask = filtered_df.isna().any(axis=1)
	warning_mask = missing_mask & (~dup_mask)
	error_mask = dup_mask
	valid_mask = ~(warning_mask | error_mask)

	if date_col and date_col in filtered_df.columns:
		# Ensure datetime with robust parsing
		if not pd.api.types.is_datetime64_any_dtype(filtered_df[date_col]):
			# Try multiple parsing strategies
			try:
				# First try pandas auto-parsing
				filtered_df[date_col] = pd.to_datetime(filtered_df[date_col], errors="coerce")
			except:
				# If that fails, try manual parsing with common formats
				try:
					filtered_df[date_col] = pd.to_datetime(filtered_df[date_col], format='%Y-%m-%d', errors="coerce")
				except:
					try:
						filtered_df[date_col] = pd.to_datetime(filtered_df[date_col], format='%m/%d/%Y', errors="coerce")
					except:
						# Last resort: infer datetime
						filtered_df[date_col] = pd.to_datetime(filtered_df[date_col], infer_datetime_format=True, errors="coerce")
		
		# Drop rows without a valid date
		original_count = len(filtered_df)
		filtered_df = filtered_df.dropna(subset=[date_col])
		if filtered_df.empty:
			st.warning("No rows with valid dates found in the uploaded file.")
			st.stop()
		
		# Apply date range filter only if apply_date_filter is True
		if apply_date_filter:
			# Apply date range filter with proper normalization
			start_norm = pd.to_datetime(start_dt).normalize()
			end_norm = pd.to_datetime(end_dt).normalize()
			
			# Convert date column to normalized dates for comparison
			data_dates = pd.to_datetime(filtered_df[date_col]).dt.normalize()
			
			# More robust date filtering - include all dates within the range
			date_filtered_df = filtered_df[
				(data_dates >= start_norm) & (data_dates <= end_norm)
			]
			
			if date_filtered_df.empty:
				st.error(f"""
				**No data points in the selected date range:**
				- **Requested range**: {start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}
				- **Available data range**: {data_min_date.strftime('%Y-%m-%d')} to {data_max_date.strftime('%Y-%m-%d')}
				- **Total rows in CSV**: {len(filtered_df):,}
				- **Date column used**: {date_col}
				
				**Suggestion**: Try selecting "Custom" and choose dates within your data range.
				""")
				st.stop()
		else:
			# No date filtering - use all data
			date_filtered_df = filtered_df
		
		
		# Recalculate masks for date-filtered data
		# Apply same simple duplicate detection logic to date-filtered data
		if duplicate_mode == "By ID Column" and id_column_name and id_column_name in date_filtered_df.columns:
			dup_mask_filtered = date_filtered_df.duplicated(subset=[id_column_name], keep=False)
		else:
			dup_mask_filtered = date_filtered_df.duplicated(keep=False)
		if quality_cols:
			missing_mask_filtered = date_filtered_df[quality_cols].isna().any(axis=1)
		else:
			missing_mask_filtered = date_filtered_df.isna().any(axis=1)
		warning_mask_filtered = missing_mask_filtered & (~dup_mask_filtered)
		error_mask_filtered = dup_mask_filtered
		valid_mask_filtered = ~(warning_mask_filtered | error_mask_filtered)
		
		# Aggregate by day
		agg = pd.DataFrame({
			"date": pd.to_datetime(date_filtered_df[date_col]).dt.normalize(),
			"valid": valid_mask_filtered.astype(int),
			"warning": warning_mask_filtered.astype(int),
			"error": error_mask_filtered.astype(int),
		})
		df = agg.groupby("date", as_index=False).sum().sort_values("date")
	else:
		# Single snapshot (no date column)
		valid_count = int(valid_mask.sum())
		warning_count = int(warning_mask.sum())
		error_count = int(error_mask.sum())
		_snapshot_date = pd.to_datetime(datetime.utcnow().date())
		df = pd.DataFrame([{ "date": _snapshot_date, "valid": valid_count, "warning": warning_count, "error": error_count }])

	# Rebuild rows_df for Details based on date-filtered data if available
	if date_col and date_col in filtered_df.columns and 'date_filtered_df' in locals():
		# Use the date-filtered data for consistency with overview
		rows_df = date_filtered_df.copy()
		rows_df["status"] = np.where(error_mask_filtered, "error", np.where(warning_mask_filtered, "warning", "valid"))
		rows_df["record_id"] = np.arange(1, len(rows_df) + 1)
		# Identify first missing column per row within quality_cols (vectorized)
		if quality_cols:
			miss_mask = date_filtered_df[quality_cols].isna()
			first_missing_series = pd.Series(index=date_filtered_df.index, dtype=object)
			any_missing = miss_mask.any(axis=1)
			if any_missing.any():
				first_missing_series.loc[any_missing] = miss_mask.loc[any_missing].idxmax(axis=1)
		else:
			first_missing_series = pd.Series(index=date_filtered_df.index, dtype=object)
		rows_df["column"] = first_missing_series
		rows_df["issue"] = np.where(error_mask_filtered, "duplicate", np.where(warning_mask_filtered, "missing", "ok"))
		rows_df["date"] = pd.to_datetime(date_filtered_df[date_col]).dt.normalize()
	else:
		# Fallback to original logic for non-date or single snapshot data
		rows_df = filtered_df.copy()
		rows_df["status"] = np.where(error_mask, "error", np.where(warning_mask, "warning", "valid"))
		rows_df["record_id"] = np.arange(1, len(rows_df) + 1)
		# Identify first missing column per row within quality_cols (vectorized)
		if quality_cols:
			miss_mask = filtered_df[quality_cols].isna()
			first_missing_series = pd.Series(index=filtered_df.index, dtype=object)
			any_missing = miss_mask.any(axis=1)
			if any_missing.any():
				first_missing_series.loc[any_missing] = miss_mask.loc[any_missing].idxmax(axis=1)
		else:
			first_missing_series = pd.Series(index=filtered_df.index, dtype=object)
		rows_df["column"] = first_missing_series
		rows_df["issue"] = np.where(error_mask, "duplicate", np.where(warning_mask, "missing", "ok"))
		rows_df["date"] = df["date"].iloc[-1] if len(df)>0 else pd.to_datetime(datetime.utcnow().date())
	if "value" not in rows_df.columns:
		rows_df["value"] = ""
	# Build filtered_by context column
	ctx_parts = []
	
	# Add duplicate filtering info
	if duplicate_mode == "By ID Column" and id_column_name:
		ctx_parts.append(f"duplicates_by: '{id_column_name}' (same {id_column_name} values)")
	else:
		ctx_parts.append("duplicates_by: all_columns (identical rows)")
	
	# Add other filters
	pcf = st.session_state.get('per_col_filters', {})
	for c, cfg in pcf.items():
		kind = cfg[0]
		if kind == 'range':
			ctx_parts.append(f"{c}: {cfg[1]:g}-{cfg[2]:g}")
		elif kind == 'daterange':
			ctx_parts.append(f"{c}: {cfg[1].date()}→{cfg[2].date()}")
		elif kind == 'contains':
			ctx_parts.append(f"{c}: contains '{cfg[1]}'")
	
	rows_df["filtered_by"] = ",  ".join(ctx_parts) if ctx_parts else "filtered_by: none"

if df.empty:
	st.warning("No data available for the selected range.")
	st.stop()

# Derived columns
df = df.copy()
df["total"] = df[["valid", "warning", "error"]].sum(axis=1)
df["dq_score"] = (df["valid"] / df["total"]).fillna(0) * 100
if len(df) > 0:
	err_mean, err_std = df["error"].mean(), df["error"].std(ddof=0)
	threshold = err_mean + 2 * (err_std if (err_std and err_std > 0) else 1)
	df["error_anomaly"] = df["error"] > threshold
else:
	df["error_anomaly"] = False
# Smoothing and month comparison removed per request

# Alert banner based on error rate threshold (latest)
total_valid = int(pd.to_numeric(df["valid"], errors="coerce").sum())
total_warn = int(pd.to_numeric(df["warning"], errors="coerce").sum())
total_err = int(pd.to_numeric(df["error"], errors="coerce").sum())
overall_total = max(1, total_valid + total_warn + total_err)
overall_error_rate = min(100.0, 100.0 * (total_err / overall_total))
# Convert error_threshold from 1-20 scale to percentage (0-100) by multiplying by 5
error_threshold_pct = error_threshold * 5
# Convert overall error rate to 1-20 scale by dividing by 5
overall_error_on_scale = overall_error_rate / 5

# Debug display to show current values (period-wide)
if use_uploaded and 'upload_df' in st.session_state and st.session_state.upload_df is not None:
    # Calculate actual duplicate count based on selected mode
    if duplicate_mode == "By ID Column" and id_column_name and id_column_name in st.session_state.upload_df.columns:
        actual_dup_count = int(st.session_state.upload_df.duplicated(subset=[id_column_name], keep=False).sum())
        dup_info = f"Duplicates in '{id_column_name}': {actual_dup_count}"
    else:
        actual_dup_count = int(st.session_state.upload_df.duplicated(keep=False).sum())
        dup_info = f"Duplicates (all columns): {actual_dup_count}"
    
    st.sidebar.markdown(f"""  
**Quality Monitor Debug:**  
- Errors (period): {int(total_err)}/{overall_total} records  
- Error rate: **{overall_error_on_scale:.2f}/20** ({overall_error_rate:.1f}%)  
- Threshold: **{error_threshold}/20** ({error_threshold_pct:.0f}%)  
- {dup_info}
- Alert status: {'🔴 ACTIVE' if overall_error_rate >= error_threshold_pct else '🟢 OK'}
""")

# Changed from > to >= so alert shows when error rate equals or exceeds threshold
if overall_error_rate >= error_threshold_pct:
	st.markdown(
		f"""
		<div style="margin:8px 0; border:1px solid rgba(124,58,237,.65); background: rgba(17,24,39,.85); color:#fff; padding:10px 12px; border-radius:12px; box-shadow:0 12px 28px rgba(124,58,237,.25);">
			<span style="font-weight:800; color:#fca5a5;">⚠ Data Quality Critical!</span>
			<span> Error rate (selected period): {overall_error_on_scale:.1f}/20 ({overall_error_rate:.1f}%) exceeds threshold: {error_threshold}/20 ({error_threshold_pct:.0f}%).</span>
		</div>
		""",
		unsafe_allow_html=True,
	)

# -------------------------
# Generate mock drill-down rows only when no file is uploaded
# -------------------------
if not use_uploaded:
    # Create empty rows_df when no file is uploaded to show zeros in all metrics
    rows_df = pd.DataFrame({
        "date": [],
        "record_id": [],
        "column": [],
        "issue": [],
        "status": [],
        "value": []
    })

# Apply filters
if column_filter:
    rows_df = rows_df[rows_df["column"].isin(column_filter)]

# Extra metrics
if len(rows_df) > 0:
    missing_pct = 100.0 * (rows_df["issue"].eq("missing").sum()) / max(1, len(rows_df))
    duplicates_cnt = int((rows_df["issue"].eq("duplicate")).sum())
else:
    # When no data is uploaded, show 0 for all metrics
    missing_pct = 0.0
    duplicates_cnt = 0
# Robust last update timestamp from the aggregated time series
try:
    last_update_ts = pd.to_datetime(df["date"].iloc[-1]) if ("date" in df.columns and len(df) > 0) else pd.to_datetime(datetime.utcnow().date())
except Exception:
    last_update_ts = pd.to_datetime(datetime.utcnow().date())

# -------------------------
# Tabs
# -------------------------
# Added Upload tab first
try:
	tab_upload, tab_overview, tab_details, tab_settings = st.tabs(["Upload & Validate", "Overview", "Details", "Settings"])
except Exception:
	# Fallback if tabs already created elsewhere
	tab_overview, tab_details, tab_settings = st.tabs(["Overview", "Details", "Settings"])
	tab_upload = None

if tab_upload is not None:
	with tab_upload:
		st.markdown("<div class='section-title'>Upload a file for quality checks</div>", unsafe_allow_html=True)
		uploaded = st.file_uploader("Choose CSV, Excel (xlsx), or TXT", type=["csv", "xlsx", "xls", "txt"], accept_multiple_files=False)
		
		# Check if file was removed (uploaded is None but we had data before)
		if uploaded is None and st.session_state.get("upload_df") is not None:
			# Clear all upload-related session state when file is removed
			st.session_state.pop("upload_df", None)
			st.session_state.pop("upload_date_col", None)
			st.session_state.pop("per_col_filters", None)
			# Force a rerun to update the UI immediately
			st.rerun()
		
		col_up_left, col_up_right = st.columns([0.6, 0.4])
		with col_up_right:
			# Advanced options in collapsible section
			with st.expander("Advanced Options", expanded=False):
				delim = st.selectbox("Delimiter (CSV/TXT)", ["Auto", ",", ";", "\t", "|"])
				date_cols_hint = st.text_input("Date columns (optional, comma-separated)", value="")
				max_rows_preview = st.slider("Preview rows", 10, 200, 100, 10)
		with col_up_left:
			if uploaded is not None:
				name = uploaded.name.lower()
				read_ok = True
				df_up = None
				try:
					if name.endswith((".xlsx", ".xls")):
						try:
							xl = pd.ExcelFile(uploaded)
							sheet = st.selectbox("Sheet", xl.sheet_names)
							parse_dates = [c.strip() for c in date_cols_hint.split(",") if c.strip()]
							df_up = pd.read_excel(xl, sheet_name=sheet, parse_dates=parse_dates or None)
						except Exception as ex_xl:
							st.warning("Install openpyxl to read Excel files: pip install openpyxl")
							read_ok = False
					else:
						# Robust CSV reader: read from buffer, sniff delimiter when Auto, tolerate bad lines
						data_bytes = uploaded.getvalue()
						if not data_bytes or len(data_bytes) == 0:
							raise ValueError("File is empty.")
						if delim == "Auto":
							sample = data_bytes[:8192].decode("utf-8", errors="ignore")
							try:
								sniff = csv.Sniffer().sniff(sample)
								sep = sniff.delimiter or ","
							except Exception:
								sep = ","
						else:
							sep = "\t" if delim == "\t" else delim
						parse_dates = [c.strip() for c in date_cols_hint.split(",") if c.strip()]
						df_up = pd.read_csv(io.BytesIO(data_bytes), sep=sep, engine="python", parse_dates=parse_dates or None, on_bad_lines="skip")
				except Exception as ex:
					read_ok = False
					st.error(f"Could not read file: {ex}")

				if read_ok and df_up is not None:
					# Let user pick a date column (optional) - hidden in advanced options
					with st.expander("Advanced Options", expanded=False):
						candidate_dates = [c for c in df_up.columns if pd.api.types.is_datetime64_any_dtype(df_up[c])]
						date_col = st.selectbox("Date column (optional)", options=["<None>"] + candidate_dates, index=0)
						if date_col != "<None>" and not pd.api.types.is_datetime64_any_dtype(df_up[date_col]):
							with st.spinner("Parsing dates..."):
								df_up[date_col] = pd.to_datetime(df_up[date_col], errors="coerce")
					st.session_state.upload_df = df_up.copy()
					st.session_state.upload_date_col = None if date_col == "<None>" else date_col

					st.markdown("<div class='section-title'>Preview</div>", unsafe_allow_html=True)
					st.dataframe(df_up.head(min(max_rows_preview, 50)), use_container_width=True)

					# Summary KPIs - optimized calculations
					n_rows, n_cols = df_up.shape
					# Limit calculations for very large files
					calc_df = df_up.head(10000) if n_rows > 10000 else df_up
					missing_total = int(calc_df.isna().sum().sum())
					# Calculate duplicate count based on selected mode
					if duplicate_mode == "By ID Column" and id_column_name and id_column_name in calc_df.columns:
						dup_count = int(calc_df.duplicated(subset=[id_column_name]).sum())
					else:
						dup_count = int(calc_df.duplicated().sum())
					if n_rows > 10000:
						# Scale up the estimates
						missing_total = int(missing_total * (n_rows / 10000))
						dup_count = int(dup_count * (n_rows / 10000))
					c1, c2, c3 = st.columns(3)
					with c1:
						st.metric("Rows", f"{n_rows:,}")
					with c2:
						st.metric("Columns", f"{n_cols:,}")
					with c3:
						st.metric("Missing (cells)", f"{missing_total:,}")

					# Missing by column - show all columns
					st.markdown("<div class='section-title'>Missing by column</div>", unsafe_allow_html=True)
					miss_col = calc_df.isna().sum().to_frame("missing")
					miss_col["missing_pct"] = (miss_col["missing"].astype(float) / max(1, len(calc_df))) * 100
					miss_col_sorted = miss_col.sort_values("missing_pct", ascending=False).reset_index().rename(columns={"index":"column"})
					st.dataframe(miss_col_sorted, use_container_width=True, hide_index=True)

					# Column profile - show all columns
					st.markdown("<div class='section-title'>Column profile</div>", unsafe_allow_html=True)
					profile_rows = []
					for col in calc_df.columns:  # Show all columns, not just first 50
						series = calc_df[col]
						dtype = str(series.dtype)
						nunique = int(series.nunique(dropna=True))
						missing = int(series.isna().sum())
						missing_pct = (missing / max(1, len(calc_df))) * 100
						row = {"column": col, "dtype": dtype, "unique": nunique, "missing": missing, "missing_pct": round(missing_pct, 2)}
						if pd.api.types.is_numeric_dtype(series) and series.notna().any():
							numeric_series = pd.to_numeric(series, errors="coerce")
							row.update({
								"min": float(numeric_series.min(skipna=True)),
								"max": float(numeric_series.max(skipna=True)),
								"mean": float(numeric_series.mean(skipna=True)),
							})
						profile_rows.append(row)
					profile_df = pd.DataFrame(profile_rows)
					st.dataframe(profile_df, use_container_width=True, hide_index=True)

					# Duplicates sample - show all duplicates, not just samples
					if dup_count > 0:
						st.markdown("<div class='section-title'>Duplicate rows</div>", unsafe_allow_html=True)
						# Show ALL duplicate rows based on selected mode (not just samples)
						if duplicate_mode == "By ID Column" and id_column_name and id_column_name in df_up.columns:
							dups = df_up[df_up.duplicated(subset=[id_column_name], keep=False)]
						else:
							dups = df_up[df_up.duplicated(keep=False)]
						
						# Show all duplicates, but limit display to prevent UI issues
						if len(dups) > 100:
							st.info(f"Showing first 100 of {len(dups)} duplicate rows. Download CSV to see all duplicates.")
							dups_display = dups.head(100)
						else:
							dups_display = dups
						
						st.dataframe(dups_display, use_container_width=True, hide_index=True)

					# Exports
					st.markdown("<div class='section-title'>Download quality report</div>", unsafe_allow_html=True)
					csv_miss = miss_col_sorted.to_csv(index=False).encode("utf-8")
					csv_prof = profile_df.to_csv(index=False).encode("utf-8")
					# Generate CSV export based on selected duplicate detection mode
					if dup_count > 0:
						if duplicate_mode == "By ID Column" and id_column_name and id_column_name in df_up.columns:
							csv_dups = (df_up[df_up.duplicated(subset=[id_column_name], keep=False)]).to_csv(index=False).encode("utf-8")
						else:
							csv_dups = (df_up[df_up.duplicated(keep=False)]).to_csv(index=False).encode("utf-8")
					else:
						csv_dups = b""
					b1, b2, b3 = st.columns(3)
					with b1:
						st.download_button("Missing by column (CSV)", data=csv_miss, file_name="missing_by_column.csv", mime="text/csv")
					with b2:
						st.download_button("Column profile (CSV)", data=csv_prof, file_name="column_profile.csv", mime="text/csv")
					with b3:
						if dup_count>0:
							st.download_button("Duplicate rows (CSV)", data=csv_dups, file_name="duplicates.csv", mime="text/csv")

with tab_overview:
	# KPI cards - show 0 when no file uploaded, real data when uploaded
	if not use_uploaded:
		# Default values when no CSV uploaded - all zeros
		valid_curr = 0
		warn_curr = 0
		err_curr = 0
		total_curr = 1  # Avoid division by zero
		dq_curr = 0.0
		# Create empty dataframe for charts
		df = pd.DataFrame({
			"date": [pd.to_datetime(datetime.utcnow().date())],
			"valid": [0],
			"warning": [0],
			"error": [0],
			"total": [0],
			"dq_score": [0.0]
		})
	else:
		# Real data from uploaded CSV - calculate KPIs from the actual filtered data
		# Use the date_filtered_df which contains the actual row counts
		if 'date_filtered_df' in locals() and not date_filtered_df.empty:
			# Calculate KPIs from the actual data rows
			if duplicate_mode == "By ID Column" and id_column_name and id_column_name in date_filtered_df.columns:
				dup_mask_kpi = date_filtered_df.duplicated(subset=[id_column_name], keep=False)
			else:
				dup_mask_kpi = date_filtered_df.duplicated(keep=False)
			
			if quality_cols:
				missing_mask_kpi = date_filtered_df[quality_cols].isna().any(axis=1)
			else:
				missing_mask_kpi = date_filtered_df.isna().any(axis=1)
			
			warning_mask_kpi = missing_mask_kpi & (~dup_mask_kpi)
			error_mask_kpi = dup_mask_kpi
			valid_mask_kpi = ~(warning_mask_kpi | error_mask_kpi)
			
			valid_curr = int(valid_mask_kpi.sum())
			warn_curr = int(warning_mask_kpi.sum())
			err_curr = int(error_mask_kpi.sum())
		else:
			# Fallback to aggregated data if date_filtered_df not available
			valid_curr = int(pd.to_numeric(df["valid"], errors="coerce").sum())
			warn_curr = int(pd.to_numeric(df["warning"], errors="coerce").sum())
			err_curr = int(pd.to_numeric(df["error"], errors="coerce").sum())
		
		total_curr = max(1, valid_curr + warn_curr + err_curr)
		dq_curr = (valid_curr / total_curr) * 100.0
		

	# Previous period calculation based on preset
	if preset == "Last 7 days":
		delta_label = "7d change"
	elif preset == "Last 30 days":
		delta_label = "30d change"
	else:  # Custom
		delta_label = "vs prev period"

	# For now, set previous period to None (no comparison data available)
	# This could be enhanced to compare with previous periods if historical data is available
	valid_prev = None; warn_prev = None; err_prev = None; dq_prev = None

	valid_delta, valid_sign = compute_delta(valid_curr, valid_prev)
	warn_delta, warn_sign = compute_delta(warn_curr, warn_prev)
	err_delta, err_sign = compute_delta(err_curr, err_prev)
	dq_delta_val = None if dq_prev in (None, 0) else dq_curr - dq_prev
	dq_delta = "–" if dq_delta_val is None else f"{dq_delta_val:+.1f}pp"
	dq_sign = "pos" if (dq_delta_val or 0) >= 0 else "neg"

	k1, k2, k3, k4 = st.columns(4)
	with k1:
		st.markdown(f"""
		<div class="kpi-card">
			<div class="kpi-title">Valid Records</div>
			<div class="kpi-value">{format_int(valid_curr)} {'▲' if valid_sign=='pos' else ('▼' if valid_sign=='neg' else '')}</div>
			<div class="kpi-delta {valid_sign} small-muted">{delta_label}: {valid_delta}</div>
		</div>
		""", unsafe_allow_html=True)
		with st.container():
			st.markdown("<div class='drill-actions'>", unsafe_allow_html=True)
			# Download Valid rows
			try:
				_valid_rows = rows_df[rows_df["status"]=="valid"] if "status" in rows_df.columns else rows_df
				_valid_csv = _valid_rows.to_csv(index=False).encode("utf-8")
				st.download_button("Download Valid Rows", data=_valid_csv, file_name="valid_rows.csv", mime="text/csv", key="dl_valid")
			except Exception:
				pass
			st.markdown("</div>", unsafe_allow_html=True)
	with k2:
		st.markdown(f"""
		<div class="kpi-card">
			<div class="kpi-title">Warnings</div>
			<div class="kpi-value">{format_int(warn_curr)} {'▲' if warn_sign=='pos' else ('▼' if warn_sign=='neg' else '')}</div>
			<div class="kpi-delta {warn_sign} small-muted">{delta_label}: {warn_delta}</div>
		</div>
		""", unsafe_allow_html=True)
		with st.container():
			st.markdown("<div class='drill-actions'>", unsafe_allow_html=True)
			# Download Warning rows
			try:
				_warn_rows = rows_df[rows_df["status"]=="warning"] if "status" in rows_df.columns else rows_df.iloc[0:0]
				_warn_csv = _warn_rows.to_csv(index=False).encode("utf-8")
				st.download_button("Download Warnings", data=_warn_csv, file_name="warnings.csv", mime="text/csv", key="dl_warn")
			except Exception:
				pass
			st.markdown("</div>", unsafe_allow_html=True)
	with k3:
		st.markdown(f"""
		<div class="kpi-card">
			<div class="kpi-title">Errors</div>
			<div class="kpi-value">{format_int(err_curr)} {'▲' if err_sign=='pos' else ('▼' if err_sign=='neg' else '')}</div>
			<div class="kpi-delta {err_sign} small-muted">{delta_label}: {err_delta}</div>
		</div>
		""", unsafe_allow_html=True)
		with st.container():
			st.markdown("<div class='drill-actions'>", unsafe_allow_html=True)
			# Download Error rows
			try:
				_err_rows = rows_df[rows_df["status"]=="error"] if "status" in rows_df.columns else rows_df.iloc[0:0]
				_err_csv = _err_rows.to_csv(index=False).encode("utf-8")
				st.download_button("Download Errors", data=_err_csv, file_name="errors.csv", mime="text/csv", key="dl_err")
			except Exception:
				pass
			st.markdown("</div>", unsafe_allow_html=True)
	with k4:
		st.markdown(f"""
		<div class="kpi-card">
			<div class="kpi-title">DQ Score</div>
			<div class="kpi-value">{dq_curr:.1f}%</div>
			<div class="kpi-delta pos small-muted">{delta_label}: {dq_delta}</div>
		</div>
		""", unsafe_allow_html=True)
		# progress bar caption below, small and muted
		st.markdown(
			f"""
			<div class='dq-progress' style='margin-top:6px;'>
				<div class='fill' style='width:{max(0, min(100, dq_curr)):.1f}%;'></div>
			</div>
			<div class='small-muted' style='font-size:12px; margin-top:4px;'>Higher is better (Valid / Total) • Last update: {last_update_ts:%Y-%m-%d}</div>
			""",
			unsafe_allow_html=True,
		)

	st.write("")

	# Trend area (Plotly optional) - Robust version with error handling
	lc, rc = st.columns([0.48, 0.48])
	with lc:
		# If no CSV is uploaded, suppress the trend chart entirely
		if not use_uploaded:
			st.info("Upload a CSV file to see the bar chart.")
		else:
			# Show the actual date range being displayed
			date_range_text = f"<span style='color: #3b82f6; font-weight: 600;'>{preset}: {start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}</span>"
			st.markdown(f"<div class='section-title'>Data Quality Trend</div>", unsafe_allow_html=True)
			st.markdown(f"<div style='font-size: 14px; color: #9ca3af; margin-bottom: 10px; padding: 8px 12px; background: rgba(59, 130, 246, 0.1); border-radius: 6px; border-left: 3px solid #3b82f6;'>{date_range_text}</div>", unsafe_allow_html=True)
			
			# Robust data validation and preparation
			try:
				# Ensure df exists and has required columns
				if df is None or df.empty:
					st.info("No data available for the selected date range to display trend chart.")
				else:
					# Ensure required columns exist with default values
					required_cols = ["date", "valid", "warning", "error"]
					for col in required_cols:
						if col not in df.columns:
							if col == "date":
								df[col] = pd.to_datetime(datetime.utcnow().date())
							else:
								df[col] = 0
					
					# SIMPLE CHART - Just show current KPI values as bars
					# This will always work and display the data clearly
					
					# Create simple data for the chart
					chart_data = {
						'Metric': ['Valid Records', 'Warnings', 'Errors'],
						'Count': [valid_curr, warn_curr, err_curr],
						'Color': ['#10b981', '#f59e0b', '#ef4444']
					}
					
					# Only show metrics with values > 0
					filtered_data = []
					for i, count in enumerate(chart_data['Count']):
						if count > 0:
							filtered_data.append({
								'Metric': chart_data['Metric'][i],
								'Count': count,
								'Color': chart_data['Color'][i]
							})
					
					
					if filtered_data:
						# Try Plotly first, fallback to matplotlib
						if px is not None:
							try:
								# Create a simple bar chart with Plotly
								fig_pl = px.bar(
									x=[item['Metric'] for item in filtered_data],
									y=[item['Count'] for item in filtered_data],
									color=[item['Metric'] for item in filtered_data],
									color_discrete_map={
										'Valid Records': '#10b981',
										'Warnings': '#f59e0b', 
										'Errors': '#ef4444'
									},
									template="plotly_dark"
								)
								
								# Update layout
								fig_pl.update_layout(
									title="Data Quality Overview",
									xaxis_title="Metrics",
									yaxis_title="Count",
									height=400,
									showlegend=False
								)
								
								# Display the chart
								st.plotly_chart(fig_pl, use_container_width=True)
							except Exception:
								# Fallback to matplotlib
								pass
						
						# Matplotlib fallback
						if px is None:
							try:
								import matplotlib.pyplot as plt
								
								fig, ax = plt.subplots(figsize=(2.5, 2))
								
								# Extract data
								metrics = [item['Metric'] for item in filtered_data]
								counts = [item['Count'] for item in filtered_data]
								colors = [item['Color'] for item in filtered_data]
								
								# Create bar chart with thinner bars
								bars = ax.bar(metrics, counts, color=colors, alpha=0.8, width=0.6)
								
								# Add value labels on bars
								for bar, count in zip(bars, counts):
									height = bar.get_height()
									ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
											f'{int(count):,}', ha='center', va='bottom', fontweight='bold')
								
								# Styling with original theme - smaller fonts for compact chart
								ax.set_title("Data Quality Overview", fontsize=10, fontweight='bold', pad=8)
								ax.set_xlabel("Metrics", fontsize=8)
								ax.set_ylabel("Count", fontsize=8)
								
								# Set axis colors to default
								ax.tick_params(colors='black', labelsize=7)
								
								# Remove grid lines completely to avoid border issues
								ax.grid(False)
								
								# Remove all spines for cleaner look
								for spine in ["top", "right", "left", "bottom"]:
									ax.spines[spine].set_visible(False)
								
								# Format y-axis with commas
								ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
								
								# Tight margins to keep everything inside
								plt.subplots_adjust(left=0.15, right=0.9, top=0.9, bottom=0.15)
								st.pyplot(fig, use_container_width=True)
								
								# Download button for bar chart
								try:
									buf = io.BytesIO()
									fig.savefig(buf, format="png", bbox_inches="tight", dpi=200)
									st.download_button("Download Bar Chart PNG", data=buf.getvalue(), 
													 file_name="bar_chart.png", mime="image/png")
								except Exception:
									pass  # Download button is optional
								
								plt.close(fig)
								
							except Exception as e:
								st.error(f"Error creating chart: {str(e)}")
								# Show data as table if chart fails
								st.write("**Data Quality Overview:**")
								for item in filtered_data:
									st.write(f"- {item['Metric']}: {item['Count']:,}")
					else:
						st.info("No data available for the selected time period.")
			
			except Exception as e:
				st.error(f"Error processing chart data: {str(e)}")
				st.info("Unable to display trend chart. Please try uploading your data again.")

	with rc:
		st.markdown("<div class='section-title'>Latest Composition</div>", unsafe_allow_html=True)
		
		# Robust composition chart with error handling
		try:
			# Sanitize composition values to avoid NaN/None and negatives
			vals_raw = [valid_curr, warn_curr, err_curr]
			comp_values = []
			for v in vals_raw:
				try:
					fv = float(v) if v is not None else 0.0
				except Exception:
					fv = 0.0
				comp_values.append(max(0.0, 0.0 if pd.isna(fv) else fv))
			
			total_comp = sum(comp_values)
			labels = ["Valid", "Warnings", "Errors"]
			colors = ["#10b981", "#f59e0b", "#ef4444"]
			
			if total_comp <= 0:
				st.info("Upload a CSV file to see the pie chart.")
			else:
				try:
					# Get the exact values from KPI cards to ensure consistency
					kpi_values = [valid_curr, warn_curr, err_curr]
					
					# Filter out zero values for cleaner pie chart
					non_zero_values = []
					non_zero_labels = []
					non_zero_colors = []
					
					for i, val in enumerate(kpi_values):
						if val > 0:
							non_zero_values.append(val)
							non_zero_labels.append(labels[i])
							non_zero_colors.append(colors[i])
					
					if not non_zero_values:
						st.info("No data to display in composition chart.")
					else:
						# Calculate total from kpi_values before using it
						total = sum(kpi_values) if kpi_values else 0
						percentages = [(val / total) * 100 for val in kpi_values] if total > 0 else [0] * len(kpi_values)
						
						# Function to format percentage with 1 decimal place
						def make_autopct(values):
							total = sum(values)
							if total == 0:
								return lambda p: ''
							return lambda p: f'{p:.1f}%'
						
						# Create the pie chart with KPI values
						fig2, ax2 = plt.subplots(figsize=(1.8, 1.8))
						wedges, _, autotexts = ax2.pie(
							kpi_values,
							labels=labels if len(kpi_values) > 1 else [''],
							colors=colors,
							autopct=make_autopct(kpi_values),
							startangle=90,
							counterclock=False,
							explode=[0.03] * len(kpi_values),
							wedgeprops=dict(width=0.5, edgecolor="#0c1326", linewidth=2),
							textprops={'fontsize': 10, 'fontweight': 'bold', 'color': 'black'}
						)
						
						# Set text color based on background for better visibility
						for text in autotexts:
							try:
								# Get the color of the corresponding wedge
								wedge = [w for w in wedges if w.get_center() == text.get_position()][0]
								# Calculate brightness of the wedge color
								r, g, b, _ = wedge.get_facecolor()
								brightness = (0.299 * r + 0.587 * g + 0.114 * b)
								# Use white text on dark colors, black on light colors
								text.set_color('white' if brightness < 0.6 else 'black')
							except (IndexError, AttributeError):
								text.set_color('black')  # Fallback to black if something goes wrong
						
						ax2.axis('equal')
						
						# Add legend only if we have multiple categories
						if len(kpi_values) > 1:
							ax2.legend(wedges, labels, title="Categories", 
									 loc="center left", bbox_to_anchor=(1.15, 0.5), frameon=False)
						
						# Tight margins to keep pie chart completely inside blue border
						plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
						st.pyplot(fig2, use_container_width=True)
						
						# Download button with error handling
						try:
							buf2 = io.BytesIO()
							fig2.savefig(buf2, format="png", bbox_inches="tight", dpi=200)
							st.download_button("Download Pie Chart PNG", data=buf2.getvalue(), 
											 file_name="pie_chart.png", mime="image/png")
						except Exception:
							pass  # Download button is optional
						
						# Clean up
						plt.close(fig2)
						
				except Exception as e:
					st.error(f"Error creating composition chart: {str(e)}")
					st.info("Unable to display composition chart.")
		
		except Exception as e:
			st.error(f"Error processing composition data: {str(e)}")
			st.info("Unable to display composition chart.")

with tab_details:
	if not use_uploaded:
		# Show empty state when no CSV uploaded
		st.info("📁 **Upload a CSV file** in the 'Upload & Validate' tab to see detailed data analysis.")
		st.markdown("### What you'll see after uploading:")
		st.markdown("- **Detailed Data View** - Row-by-row analysis with status indicators")
		st.markdown("- **Export Options** - Download filtered data as CSV, Excel, or JSON")
		st.markdown("- **Extra Metrics** - Missing percentages and duplicate counts")
		
		# Show empty metrics
		left, right = st.columns([0.6, 0.4])
		with right:
			st.markdown("<div class='section-title'>Extra Metrics</div>", unsafe_allow_html=True)
			st.metric("% Missing (rows shown)", "0.0%")
			st.metric("Duplicate rows", "0")
	else:
		# Show real data when CSV uploaded
		st.markdown("<div class='section-title'>Drill-down</div>", unsafe_allow_html=True)
		left, right = st.columns([0.6, 0.4])
		with left:
			# Show only duplicate rows in Details tab
			if 'upload_df' in st.session_state and not st.session_state['upload_df'].empty:
				upload_df = st.session_state['upload_df']
				
				# Apply date filtering if available and if date filtering is enabled
				date_col = st.session_state.get('upload_date_col')
				if date_col and date_col in upload_df.columns and apply_date_filter:
					col_dt = pd.to_datetime(upload_df[date_col], errors='coerce')
					upload_df = upload_df[(col_dt >= start_dt) & (col_dt <= end_dt)]
				
				# Apply duplicate detection based on mode
				if duplicate_mode == "By ID Column" and id_column_name and id_column_name in upload_df.columns:
					dup_mask = upload_df.duplicated(subset=[id_column_name], keep=False)
					mode_label = f"ID column: {id_column_name}"
				else:
					dup_mask = upload_df.duplicated(keep=False)
					mode_label = "all columns"
				
				duplicates_df = upload_df[dup_mask]
				
				if len(duplicates_df) > 0:
					st.info(f"Showing {len(duplicates_df)} duplicate rows (by {mode_label})")
					view_df = duplicates_df  # Show ALL columns of duplicate rows
				else:
					st.info(f"No duplicates found (by {mode_label})")
					view_df = upload_df.iloc[0:0]
			else:
				st.warning("No uploaded data available")
				view_df = rows_df.iloc[0:0]  # Empty dataframe

			# Apply column filtering if user selected specific columns
			if column_filter:
				try:
					# Show only selected columns from the duplicate data
					visible_cols = [c for c in column_filter if c in view_df.columns]
					if visible_cols:
						view_df = view_df[visible_cols]
					else:
						st.warning("Selected columns not found in data.")
				except Exception as e:
					st.error(f"Error filtering columns: {str(e)}")
					pass

		# Style rows by status (only if we have status column)
		def _row_style(row):
			status = str(row.get("status", ""))
			if status == "valid":
				return ["background-color: rgba(16,185,129,0.12); color: #e8eaf1;"] * len(row)
			if status == "warning":
				return ["background-color: rgba(245,158,11,0.12); color: #e8eaf1;"] * len(row)
			if status == "error":
				return ["background-color: rgba(239,68,68,0.12); color: #e8eaf1;"] * len(row)
			return [""] * len(row)

		# Only apply styling if we have status column, otherwise show plain table
		if "status" in view_df.columns:
			# Sort by date only if present
			styled_base = view_df.sort_values("date", ascending=False) if "date" in view_df.columns else view_df
			styled = styled_base.style.apply(_row_style, axis=1)
		else:
			# For uploaded data without status, sort by date if available
			styled = (view_df.sort_values("date", ascending=False) if "date" in view_df.columns else view_df).style

		# Emphasize selected columns (from quality_cols) with a subtle border highlight without overriding row backgrounds
		try:
			_emph_cols = quality_cols if 'quality_cols' in locals() else []
			safe_emph_cols = [c for c in _emph_cols if c in view_df.columns]
			if safe_emph_cols:
				styled = styled.set_properties(
					subset=safe_emph_cols,
					**{
						"border-left": "2px solid rgba(147,197,253,.45)",
						"border-right": "2px solid rgba(147,197,253,.45)",
					}
				)
		except Exception:
			pass

		# Always highlight the 'filtered_by' context column if present
		try:
			if "filtered_by" in view_df.columns:
				styled = styled.set_properties(
					subset=["filtered_by"],
					**{
						"background-color": "rgba(79,70,229,.25)",
						"color": "#ffffff",
						"font-weight": "800",
					}
				)
		except Exception:
			pass

		# Highlight cells that satisfy active per-column filters
		try:
			pcf = st.session_state.get('per_col_filters', {})
			for c, cfg in pcf.items():
				if c not in view_df.columns:
					continue
				kind = cfg[0]
				if kind == 'range':
					lo, hi = cfg[1], cfg[2]
					mask = pd.to_numeric(view_df[c], errors='coerce').between(lo, hi)
					styled = styled.apply(lambda col: ["background-color: rgba(59,130,246,.22); font-weight:700;" if m else "" for m in mask], subset=[c])
				elif kind == 'daterange':
					start_d, end_d = cfg[1], cfg[2]
					col_dt = pd.to_datetime(view_df[c], errors='coerce')
					mask = (col_dt >= start_d) & (col_dt <= end_d)
					styled = styled.apply(lambda col: ["background-color: rgba(59,130,246,.22); font-weight:700;" if m else "" for m in mask], subset=[c])
				elif kind == 'contains':
					needle = str(cfg[1]).lower()
					mask = view_df[c].astype(str).str.lower().str.contains(needle, na=False)
					styled = styled.apply(lambda col: ["background-color: rgba(59,130,246,.22); font-weight:700;" if m else "" for m in mask], subset=[c])
		except Exception:
			pass


		# If the styled dataframe is too large, fall back to plain dataframe to avoid Styler limits
		try:
			max_elements = pd.get_option("styler.render.max_elements")
		except Exception:
			max_elements = 262144
		num_cells = int(view_df.shape[0] * max(1, view_df.shape[1]))
		if num_cells > int(max_elements):
			st.info(f"Showing plain table (size {num_cells:,} cells) due to styling limit of {int(max_elements):,} cells.")
			# Sort by date if available
			if "date" in view_df.columns:
				st.dataframe(view_df.sort_values("date", ascending=False), use_container_width=True, hide_index=True)
			else:
				st.dataframe(view_df, use_container_width=True, hide_index=True)
		else:
			st.dataframe(styled, use_container_width=True, hide_index=True)
		# export buttons
		csv_bytes = view_df.to_csv(index=False).encode("utf-8")
		excel_bytes = None
		try:
			buf_xlsx = io.BytesIO()
			with pd.ExcelWriter(buf_xlsx, engine="openpyxl") as writer:
				view_df.to_excel(writer, index=False, sheet_name="data")
			buf_xlsx.seek(0)
			excel_bytes = buf_xlsx.getvalue()
		except Exception:
			try:
				buf_xlsx = io.BytesIO()
				with pd.ExcelWriter(buf_xlsx, engine="xlsxwriter") as writer:
					view_df.to_excel(writer, index=False, sheet_name="data")
				buf_xlsx.seek(0)
				excel_bytes = buf_xlsx.getvalue()
			except Exception:
				excel_bytes = None

		c1, c2, c3 = st.columns(3)
		with c1:
			st.download_button("CSV", data=csv_bytes, file_name="export.csv", mime="text/csv")
		with c2:
			if excel_bytes is not None:
				st.download_button("Excel", data=excel_bytes, file_name="export.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
			else:
				st.caption("Install openpyxl or xlsxwriter to enable Excel export")
		with c3:
			st.download_button("JSON", data=view_df.to_json(orient="records").encode("utf-8"), file_name="export.json", mime="application/json")
	with right:
		st.markdown("<div class='section-title'>Extra Metrics</div>", unsafe_allow_html=True)
		st.metric("% Missing (rows shown)", f"{missing_pct:.1f}%")
		st.metric("Duplicate rows", f"{duplicates_cnt}")
		# removed compare vs last month metrics

with tab_settings:
	st.caption("💡 Adjust controls in the sidebar. API base URL is editable there.")
	# removed smoothing caption
	st.caption("🎯 Click KPI cards to drill down into specific data quality issues.")

	# Admin Feedback Dashboard Section
	st.markdown("---")
	st.markdown("<div class='section-title'>🔒 Admin: Feedback Dashboard</div>", unsafe_allow_html=True)
	
	# Admin password protection
	admin_password = st.text_input("Admin Password", type="password", help="Enter admin password to access feedback data")
	load_btn = st.button("Load Feedback Data", key="load_feedback_btn")
	
	if admin_password == "admin123":  # Change this to your preferred password
		st.success("✅ Admin access granted")
		
		if load_btn:
			try:
				import requests
				feedback_url = f"{api_base_url}/api/feedback"
				response = requests.get(feedback_url, timeout=10)
				
				if response.status_code == 200:
					feedback_data = response.json()
					feedback_list = feedback_data.get('feedback', [])
					
					if feedback_list:
						st.success(f"Found {len(feedback_list)} feedback entries")
						
						# Convert to DataFrame for better display
						feedback_df = pd.DataFrame(feedback_list)
						
						# Parse timestamp robustly (mixed formats) and avoid exceptions
						if 'timestamp' in feedback_df.columns:
							feedback_df['timestamp'] = pd.to_datetime(
								feedback_df['timestamp'], infer_datetime_format=True, errors='coerce'
							)
						
						# Reorder columns for better display
						column_order = ['timestamp', 'rating', 'text', 'session_id', 'user_id', '_id']
						available_columns = [col for col in column_order if col in feedback_df.columns]
						feedback_df = feedback_df[available_columns]
						
						st.dataframe(feedback_df, use_container_width=True, hide_index=True)
						
						# Show summary statistics
						st.markdown("### Feedback Summary")
						col1, col2, col3 = st.columns(3)
						with col1:
							avg_rating = feedback_df['rating'].mean()
							st.metric("Average Rating", f"{avg_rating:.1f}/5")
						with col2:
							total_feedback = len(feedback_df)
							st.metric("Total Feedback", total_feedback)
						with col3:
							rating_counts = feedback_df['rating'].value_counts().sort_index(ascending=False)
							most_common_rating = rating_counts.index[0] if not rating_counts.empty else "N/A"
							st.metric("Most Common Rating", f"{most_common_rating} stars")
						
						# Download feedback as CSV
						csv_data = feedback_df.to_csv(index=False).encode('utf-8')
						st.download_button(
							"📥 Download Feedback CSV",
							data=csv_data,
							file_name=f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
							mime="text/csv"
						)
					else:
						st.info("No feedback entries found.")
				else:
					st.error(f"Failed to load feedback: {response.status_code}")
			except requests.exceptions.RequestException as e:
				st.error(f"Error connecting to API: {str(e)}")
			except Exception as e:
				st.error(f"Error loading feedback: {str(e)}")
	elif admin_password:
		st.error("❌ Incorrect admin password. Access denied.")
	else:
		st.info("💡 Enter admin password to view feedback data and analytics.")
	
	# User Feedback Section
	st.markdown("---")
	st.markdown("<div class='section-title'>📝 Submit Feedback</div>", unsafe_allow_html=True)
	
	# Create feedback form using Streamlit widgets
	with st.form("feedback_form", clear_on_submit=True):
		rating = st.selectbox("Rating", [5, 4, 3, 2, 1], index=0, help="Rate your experience (1=Poor, 5=Excellent)")
		feedback_text = st.text_area("Your Feedback", placeholder="Share your thoughts about the dashboard...", height=100)
		submitted = st.form_submit_button("Submit Feedback")
		
		if submitted:
			if feedback_text.strip():
				try:
					import requests
					feedback_data = {
						"rating": rating,
						"text": feedback_text.strip(),
						"session_id": f"user_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
					}
					response = requests.post(f"{api_base_url}/api/feedback", json=feedback_data, timeout=5)
					if response.status_code == 201:
						st.success("✅ Thank you for your feedback! We appreciate your input.")
					else:
						st.error(f"❌ Error submitting feedback: {response.status_code}")
				except Exception as e:
					st.error(f"❌ Connection error: {str(e)}")
			else:
				st.warning("Please enter some feedback text before submitting.")

# -------------------------
# Footer links (pinned at bottom)
# -------------------------
st.markdown(
	"""
	<div id="app-footer" class="app-footer">
		<div class="footer-links">
			<!-- hidden none state to allow closing all popovers -->
			<input name="ft-tabs" id="ft-none" type="radio" checked style="display:none;"/>
			<div class="footer-item">
				<input name="ft-tabs" id="ft-help" type="radio" />
				<label class="footer-title" for="ft-help">Help Center</label>
				<div class="footer-desc">
					<label class="footer-close" for="ft-none">×</label>
					<strong>📋 How to Use:</strong><br/>
					• Upload CSV files for quality analysis<br/>
					• View metrics in Overview tab<br/>
					• Export results as CSV/Excel/JSON<br/>
					• Submit feedback in Settings tab<br/>
					<strong>🔧 Troubleshooting:</strong><br/>
					• Ensure CSV has proper date column<br/>
					• Check date range matches your data<br/>
					• Contact support for technical issues
				</div>
			</div>
			<div class="footer-item">
				<input name="ft-tabs" id="ft-services" type="radio" />
				<label class="footer-title" for="ft-services">Services</label>
				<div class="footer-desc">
					<label class="footer-close" for="ft-none">×</label>
					<strong>🔍 Data Quality Analysis:</strong><br/>
					• Missing value detection<br/>
					• Duplicate row identification<br/>
					• Data type validation<br/>
					• Statistical quality scoring<br/>
					<strong>📊 Reporting Features:</strong><br/>
					• Interactive dashboards<br/>
					• Export capabilities<br/>
					• Historical trend analysis<br/>
					• Custom date range filtering
				</div>
			</div>
			<div class="footer-item">
				<input name="ft-tabs" id="ft-contact" type="radio" />
				<label class="footer-title" for="ft-contact">Contact Us</label>
				<div class="footer-desc">
					<label class="footer-close" for="ft-none">×</label>
					<strong>📧 Email:</strong><br/>
					<a href="mailto:fabb.nawab@gmail.com">fabb.nawab@gmail.com</a><br/>
					<strong>📱 Phone:</strong><br/>
					<a href="tel:+917892601125">+91 7892601125</a><br/>
					<strong>⏰ Support Hours:</strong><br/>
					Monday - Friday: 9 AM - 6 PM IST<br/>
					<strong>🚀 For:</strong><br/>
					Technical support, feature requests, bug reports, and general inquiries
				</div>
			</div>
			<div class="footer-item">
				<input name="ft-tabs" id="ft-docs" type="radio" />
				<label class="footer-title" for="ft-docs">Documentation</label>
				<div class="footer-desc">
					<label class="footer-close" for="ft-none">×</label>
					<strong>📖 User Guide:</strong><br/>
					• Getting started tutorial<br/>
					• Feature explanations<br/>
					• Best practices for data upload<br/>
					<strong>🔧 Technical Docs:</strong><br/>
					• API endpoints reference<br/>
					• Database schema<br/>
					• Configuration options<br/>
					<strong>📝 Updates:</strong><br/>
					• Version changelog<br/>
					• New feature announcements<br/>
					• Performance improvements
				</div>
			</div>
		</div>
	</div>
	""",
	unsafe_allow_html=True,
)

# Global click-away: close footer panels when clicking outside
components.html(
	"""
	<script>
		(function(){
			document.addEventListener('click', function(e){
				try{
					var footer = document.getElementById('app-footer');
					if(!footer) return;
					var within = footer.contains(e.target);
					if(!within){
						var none = document.getElementById('ft-none');
						if(none) none.checked = true;
					}
				}catch(err){}
			}, true);
		})();
	</script>
	""",
	height=0,
)
# End of app
