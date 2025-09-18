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
		
		/* Ensure main content doesn't overlap footer */
		.main .block-container { padding-bottom: 120px !important; }
		
		/* Mobile Responsive Styles */
		@media screen and (max-width: 768px) {
			/* Main container adjustments */
			.main .block-container { 
				padding-bottom: 180px !important; 
				padding-left: 1rem !important;
				padding-right: 1rem !important;
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
			.stSelectbox, .stTextInput, .stTextArea { 
				margin-bottom: 0.5rem !important; 
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
			}
			
			.footer-links { 
				flex-wrap: wrap !important; 
			}
			.footer-item { 
				flex: 1 1 45% !important; 
				margin: 0 5px 10px 5px !important;
			}
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

default_api = os.getenv("BACKEND_URL", "https://distinguished-imagination-production.up.railway.app")
api_base_url = st.sidebar.text_input("API Base URL", value=default_api).rstrip("/")

# Date presets with awareness of uploaded dataset date range
preset = st.sidebar.selectbox("Date Preset", ["Last 7 days", "Last 30 days", "Custom"], index=1)
today = datetime.utcnow().date()

# Detect uploaded dataset date bounds (if available)
uploaded_df = st.session_state.get("upload_df") if "upload_df" in st.session_state else None
uploaded_date_col = st.session_state.get("upload_date_col") if "upload_date_col" in st.session_state else None
data_min_date = None
data_max_date = None
if uploaded_df is not None and uploaded_date_col and uploaded_date_col in uploaded_df.columns:
	try:
		_col_dt = pd.to_datetime(uploaded_df[uploaded_date_col], errors="coerce")
		if _col_dt.notna().any():
			data_min_date = pd.to_datetime(_col_dt.min()).date()
			data_max_date = pd.to_datetime(_col_dt.max()).date()
	except Exception:
		pass

overall_min = data_min_date if data_min_date is not None else (today - timedelta(days=365))
overall_max = data_max_date if data_max_date is not None else today

if preset == "Last 7 days":
	default_end = overall_max
	default_start = max(overall_min, default_end - timedelta(days=6))
elif preset == "Last 30 days":
	default_end = overall_max
	default_start = max(overall_min, default_end - timedelta(days=29))
else:
	default_start = overall_min
	default_end = overall_max

if preset == "Custom":
	date_range = st.sidebar.date_input(
		"Date Range",
		value=(default_start, default_end),
		min_value=overall_min,
		max_value=overall_max,
	)

# Authoritative start/end based on preset (Custom uses widget)
if preset == "Custom":
	# Streamlit may return a tuple or list; guard against single-date cases
	if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
		start_dt, end_dt = date_range[0], date_range[1]
	else:
		start_dt, end_dt = default_start, default_end
else:
	start_dt = default_start
	end_dt = default_end
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
focus_column = st.sidebar.text_input("Column to focus (optional)", value="")

# Chart controls
show_points = st.sidebar.checkbox("Show data points", value=False)
plotly_mode = st.sidebar.checkbox("Interactive charts (Plotly)", value=bool(px))

# Refresh controls (manual only)
refresh_now = st.sidebar.button("Refresh Now")
# Reset views
reset_clicked = st.sidebar.button("Reset Views", key="reset_views_btn")
if reset_clicked:
	st.session_state.show_valid = False
	st.session_state.show_warnings = False
	st.session_state.show_errors = False

# Thresholds
error_threshold = st.sidebar.number_input("Error rate alert threshold (%)", min_value=1, max_value=20, value=10, step=1)

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
col_left, col_center, col_right = st.columns([0.2, 0.6, 0.2])
with col_center:
	st.markdown(
		f"""
		<div style='text-align:center;'>
			<div class='hero-title'>Quality Control Dashboard</div>
			<div class='small-muted'>API: {api_base_url}</div>
		</div>
		""",
		unsafe_allow_html=True
	)

# -------------------------
# Data load
# -------------------------
with st.spinner("Loading data..."):
	df = fetch_quality_data(api_base_url, start_dt, end_dt)

# If a user uploaded a file, override Overview/Details data with that upload (fully reflective of filters/date range)
use_uploaded = bool(st.session_state.get("upload_df") is not None)
if use_uploaded:
	df_up = st.session_state.get("upload_df").copy()
	date_col = st.session_state.get("upload_date_col")
	# If no date column selected, try to auto-detect a likely date column
	if not date_col:
		try:
			candidates = []
			for c in df_up.columns:
				ser = df_up[c]
				parsed = pd.to_datetime(ser, errors="coerce")
				valid_ratio = float(parsed.notna().mean()) if len(parsed) else 0.0
				unique_days = parsed.dt.normalize().nunique() if parsed.notna().any() else 0
				if valid_ratio >= 0.5 and unique_days >= 2:
					candidates.append((c, valid_ratio, unique_days))
			if candidates:
				candidates.sort(key=lambda x: (x[1], x[2]), reverse=True)
				date_col = candidates[0][0]
				# persist detection
				st.session_state.upload_date_col = date_col
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

	# Focus column behavior: if provided and exists, emphasize; if provided and doesn't exist, stop with message
	if focus_column:
		_fc = focus_column.strip()
		# Try exact (case-insensitive) then partial contains
		_fc_matches = [c for c in filtered_df.columns if c.lower() == _fc.lower()]
		if not _fc_matches:
			_fc_matches = [c for c in filtered_df.columns if _fc.lower() in str(c).lower()]
		if _fc_matches:
			# Use the exact match for emphasis
			_fc_exact = _fc_matches[0]
			if _fc_exact not in quality_cols:
				quality_cols = list(dict.fromkeys(quality_cols + [_fc_exact]))
		else:
			st.warning(f"No column found named '{focus_column}'.")
			st.stop()

	# Classification on filtered rows
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
		# Ensure datetime
		if not pd.api.types.is_datetime64_any_dtype(filtered_df[date_col]):
			filtered_df[date_col] = pd.to_datetime(filtered_df[date_col], errors="coerce")
		# Drop rows without a valid date
		filtered_df = filtered_df.dropna(subset=[date_col])
		if filtered_df.empty:
			st.warning("No rows match current filters/date range for the uploaded file.")
			st.stop()
		# Aggregate by day
		agg = pd.DataFrame({
			"date": pd.to_datetime(filtered_df[date_col]).dt.normalize(),
			"valid": valid_mask.astype(int),
			"warning": warning_mask.astype(int),
			"error": error_mask.astype(int),
		})
		df = agg.groupby("date", as_index=False).sum().sort_values("date")
		# Apply date range from sidebar (respect presets)
		start_norm = pd.to_datetime(start_dt).normalize()
		end_norm = pd.to_datetime(end_dt).normalize() + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
		df = df[(df["date"] >= start_norm) & (df["date"] <= end_norm)]
		if df.empty:
			st.warning("No data points in the selected date range for the uploaded file.")
			st.stop()
	else:
		# Single snapshot (no date column)
		valid_count = int(valid_mask.sum())
		warning_count = int(warning_mask.sum())
		error_count = int(error_mask.sum())
		_snapshot_date = pd.to_datetime(datetime.utcnow().date())
		df = pd.DataFrame([{ "date": _snapshot_date, "valid": valid_count, "warning": warning_count, "error": error_count }])

	# Rebuild rows_df for Details based on filtered_df
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
	# If date column exists keep it for details; else set snapshot date
	if date_col and date_col in filtered_df.columns:
		rows_df["date"] = pd.to_datetime(filtered_df[date_col]).dt.normalize()
		# Apply date range to rows_df too
		start_norm = pd.to_datetime(start_dt).normalize()
		end_norm = pd.to_datetime(end_dt).normalize() + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
		rows_df = rows_df[(rows_df["date"] >= start_norm) & (rows_df["date"] <= end_norm)]
	else:
		rows_df["date"] = df["date"].iloc[-1] if len(df)>0 else pd.to_datetime(datetime.utcnow().date())
	if "value" not in rows_df.columns:
		rows_df["value"] = ""
	# Build filtered_by context column
	ctx_parts = []
	if quality_cols:
		ctx_parts.append("cols:" + ", ".join(quality_cols[:5]) + ("…" if len(quality_cols) > 5 else ""))
	pcf = st.session_state.get('per_col_filters', {})
	for c, cfg in pcf.items():
		kind = cfg[0]
		if kind == 'range':
			ctx_parts.append(f"{c}: {cfg[1]:g}-{cfg[2]:g}")
		elif kind == 'daterange':
			ctx_parts.append(f"{c}: {cfg[1].date()}→{cfg[2].date()}")
		elif kind == 'contains':
			ctx_parts.append(f"{c}: contains '{cfg[1]}'")
	if focus_column:
		ctx_parts.append(f"focus_column: '{focus_column}'")
	rows_df["filtered_by"] = ",  ".join(ctx_parts) if ctx_parts else "filtered_by: none"

if df.empty:
	st.warning("No data available for the selected range.")
	st.stop()

# Derived columns
	df = df.copy()
	df["total"] = df[["valid", "warning", "error"]].sum(axis=1)
	df["dq_score"] = (df["valid"] / df["total"]).fillna(0) * 100
	err_mean, err_std = df["error"].mean(), df["error"].std(ddof=0)
	threshold = err_mean + 2 * (err_std if (err_std and err_std > 0) else 1)
	df["error_anomaly"] = df["error"] > threshold
# Smoothing and month comparison removed per request

# Alert banner based on error rate threshold (latest)
latest_row = df.iloc[-1]
# Recompute total from components to avoid NaN or smoothing artifacts
_latest_valid = float(latest_row.get("valid", 0) or 0)
_latest_warn = float(latest_row.get("warning", 0) or 0)
_latest_err = float(latest_row.get("error", 0) or 0)
latest_total = max(1, int(round(_latest_valid + _latest_warn + _latest_err)))
latest_error_rate = min(100.0, 100.0 * (_latest_err / latest_total))
if latest_error_rate > error_threshold:
	st.markdown(
		f"""
		<div style="margin:8px 0; border:1px solid rgba(124,58,237,.65); background: rgba(17,24,39,.85); color:#fff; padding:10px 12px; border-radius:12px; box-shadow:0 12px 28px rgba(124,58,237,.25);">
			<span style="font-weight:800; color:#fca5a5;">⚠ Data Quality Critical!</span>
			<span> Error rate {latest_error_rate:.1f}% exceeds {error_threshold}%.</span>
		</div>
		""",
		unsafe_allow_html=True,
	)

# -------------------------
# Generate mock drill-down rows only when no file is uploaded
# -------------------------
if not use_uploaded:
    np.random.seed(42)
    last_date = pd.to_datetime(df["date"].iloc[-1])
    num_rows = 200
    mock_ids = np.arange(1, num_rows + 1)
    mock_cols = np.random.choice(["Name", "Age", "Salary", "Department", "JoinDate"], size=num_rows)
    mock_issue = np.random.choice(["missing", "invalid_format", "out_of_range", "duplicate", "ok"], size=num_rows, p=[0.2,0.2,0.2,0.1,0.3])
    mock_status = np.where(mock_issue=="ok", "valid", np.where(np.isin(mock_issue, ["missing","invalid_format"]) , "warning", "error"))
    rows_df = pd.DataFrame({
        "date": [last_date]*num_rows,
        "record_id": mock_ids,
        "column": mock_cols,
        "issue": mock_issue,
        "status": mock_status,
        "value": np.random.randint(0, 100000, size=num_rows)
    })

# Apply filters
if column_filter:
    rows_df = rows_df[rows_df["column"].isin(column_filter)]
if focus_column:
    _fc_in = focus_column.strip().lower()
    if "column" in rows_df.columns:
        # try exact then partial match against the issue column name
        exact_mask = rows_df["column"].astype(str).str.lower() == _fc_in
        partial_mask = rows_df["column"].astype(str).str.lower().str.contains(_fc_in, na=False)
        match_mask = exact_mask | partial_mask
        if match_mask.any():
            rows_df = rows_df[match_mask]
        else:
            # If not found as issue column, verify if it exists as a dataframe column; if not, stop
            if not any(_fc_in in c.lower() for c in rows_df.columns):
                st.warning(f"No column found named '{focus_column}'.")
                st.stop()

# Extra metrics
missing_pct = 100.0 * (rows_df["issue"].eq("missing").sum()) / max(1, len(rows_df))
duplicates_cnt = int((rows_df["issue"].eq("duplicate")).sum())
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
					dup_count = int(calc_df.duplicated().sum())
					if n_rows > 10000:
						# Scale up the estimates
						missing_total = int(missing_total * (n_rows / 10000))
						dup_count = int(dup_count * (n_rows / 10000))
					c1, c2, c3, c4 = st.columns(4)
					with c1:
						st.metric("Rows", f"{n_rows:,}")
					with c2:
						st.metric("Columns", f"{n_cols:,}")
					with c3:
						st.metric("Missing (cells)", f"{missing_total:,}")
					with c4:
						st.metric("Duplicate rows", f"{dup_count:,}")

					# Missing by column - optimized
					st.markdown("<div class='section-title'>Missing by column</div>", unsafe_allow_html=True)
					miss_col = calc_df.isna().sum().to_frame("missing")
					miss_col["missing_pct"] = (miss_col["missing"].astype(float) / max(1, len(calc_df))) * 100
					miss_col_sorted = miss_col.sort_values("missing_pct", ascending=False).reset_index().rename(columns={"index":"column"})
					st.dataframe(miss_col_sorted.head(20), use_container_width=True, hide_index=True)

					# Column profile - optimized for speed
					st.markdown("<div class='section-title'>Column profile</div>", unsafe_allow_html=True)
					profile_rows = []
					for col in calc_df.columns[:50]:  # Limit to first 50 columns for speed
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

					# Duplicates sample - optimized
					if dup_count > 0:
						st.markdown("<div class='section-title'>Duplicate rows (sample)</div>", unsafe_allow_html=True)
						dups = calc_df[calc_df.duplicated(keep=False)].head(25)
						st.dataframe(dups, use_container_width=True, hide_index=True)

					# Exports
					st.markdown("<div class='section-title'>Download quality report</div>", unsafe_allow_html=True)
					csv_miss = miss_col_sorted.to_csv(index=False).encode("utf-8")
					csv_prof = profile_df.to_csv(index=False).encode("utf-8")
					csv_dups = (df_up[df_up.duplicated(keep=False)]).to_csv(index=False).encode("utf-8") if dup_count>0 else b""
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
		# Default values when no CSV uploaded
		valid_curr = 0
		warn_curr = 0
		err_curr = 0
		total_curr = 1
		dq_curr = 0.0
	else:
		# Real data from uploaded CSV
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

	# Trend area (Plotly optional)
	lc, rc = st.columns([0.62, 0.38])
	with lc:
		st.markdown("<div class='section-title'>Data Quality Trend</div>", unsafe_allow_html=True)
		if plotly_mode and px is not None:
			melted = df.melt(id_vars=["date"], value_vars=["valid","warning","error"], var_name="metric", value_name="count")
			fig_pl = px.line(melted, x="date", y="count", color="metric",
				color_discrete_map={"valid":"#10b981","warning":"#f59e0b","error":"#ef4444"},
				template="plotly_dark")
			# Respect Show data points: toggle markers on/off
			fig_pl.update_traces(mode="lines+markers" if show_points else "lines", marker=dict(size=6 if show_points else 0))
			fig_pl.update_layout(margin=dict(l=10,r=10,t=10,b=40), legend_orientation="h", legend_y=-0.2)
			st.plotly_chart(fig_pl, use_container_width=True)
		else:
			fig, ax = plt.subplots(figsize=(9.2, 4.0))
			ax.plot(df["date"], df["valid"], label="Valid", color="#10b981", linewidth=2.2, marker="o" if show_points else None, markersize=4, alpha=0.95)
			ax.plot(df["date"], df["warning"], label="Warnings", color="#f59e0b", linewidth=2.0, marker="o" if show_points else None, markersize=4, alpha=0.95)
			ax.plot(df["date"], df["error"], label="Errors", color="#ef4444", linewidth=2.0, marker="o" if show_points else None, markersize=4, alpha=0.95)
			anom = df[df["error_anomaly"]] if "error_anomaly" in df.columns else df.iloc[0:0]
			if not anom.empty:
				ax.scatter(anom["date"], anom["error"], color="#ef4444", s=28, zorder=5, label="Error anomaly")
			ax.set_xlabel("")
			ax.set_ylabel("Count")
			ax.grid(True, linestyle="--", alpha=0.25)
			for spine in ["top", "right"]:
				ax.spines[spine].set_visible(False)
			ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=False)
			plt.tight_layout()
			st.pyplot(fig, use_container_width=True)
			buf = io.BytesIO(); fig.savefig(buf, format="png", bbox_inches="tight", dpi=200)
			st.download_button("Download Trend PNG", data=buf.getvalue(), file_name="trend.png", mime="image/png")

	with rc:
		st.markdown("<div class='section-title'>Latest Composition</div>", unsafe_allow_html=True)
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
			st.info("No composition data to display for the current filters/date range.")
		else:
			fig2, ax2 = plt.subplots(figsize=(4.8, 4.8))
			wedges = ax2.pie(
				comp_values,
				colors=colors,
				startangle=90,
				counterclock=False,
				explode=[0.03, 0.03, 0.03],
				wedgeprops=dict(width=0.5, edgecolor="#0c1326", linewidth=2),
			)[0]
			ax2.axis('equal')
			ax2.legend(wedges, labels, title="Categories", loc="center left", bbox_to_anchor=(1.15, 0.5), frameon=False)
			plt.tight_layout()
			st.pyplot(fig2, use_container_width=True)
			buf2 = io.BytesIO(); fig2.savefig(buf2, format="png", bbox_inches="tight", dpi=200)
			st.download_button("Download Composition PNG", data=buf2.getvalue(), file_name="composition.png", mime="image/png")

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
			# show filtered table depending on selection
			view_df = rows_df
			if st.session_state.show_errors:
				view_df = rows_df[rows_df["status"]=="error"]
			elif st.session_state.show_warnings:
				view_df = rows_df[rows_df["status"]=="warning"]
			elif st.session_state.show_valid:
				view_df = rows_df[rows_df["status"]=="valid"]

			# If user selected columns in the sidebar, limit Details to those columns
			try:
				if column_filter:
					# For Details tab, we need to show the original uploaded data columns
					# not the validation results columns
					if 'upload_df' in st.session_state and not st.session_state['upload_df'].empty:
						upload_df = st.session_state['upload_df']
					# Apply date filtering if selected or detected date column exists
					date_col = st.session_state.get('upload_date_col')
					if date_col and date_col in upload_df.columns:
						col_dt = pd.to_datetime(upload_df[date_col], errors='coerce')
						upload_df = upload_df[(col_dt >= start_dt) & (col_dt <= end_dt)]
					# Show only selected columns from uploaded data regardless of date filtering presence
					visible_cols = [c for c in column_filter if c in upload_df.columns]
					if visible_cols:
						view_df = upload_df[visible_cols]
					else:
						st.warning("Selected columns not found in uploaded data.")
						view_df = upload_df
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

		# If focus_column provided and exists in the data, emphasize that column
		try:
			if focus_column:
				_fc_input = focus_column.strip().lower()
				_fc_matches = [c for c in view_df.columns if c.lower() == _fc_input]
				if not _fc_matches:
					_fc_matches = [c for c in view_df.columns if _fc_input in c.lower()]
				if _fc_matches:
					# Move the focused column to the front so it's visible without horizontal scroll
					front_cols = [_fc_matches[0]] + [c for c in view_df.columns if c != _fc_matches[0]]
					styled = styled.reindex(columns=front_cols)
					styled = styled.set_properties(
						subset=_fc_matches,
						**{
							"outline": "2px solid rgba(250,204,21,.65)",
							"border-radius": "6px",
							"font-weight": "800",
						}
					)
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
	
	if admin_password == "admin123":  # Change this to your preferred password
		st.success("✅ Admin access granted")
		
		if st.button("Load Feedback Data", key="load_feedback_btn"):
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
						
						# Format timestamp for better readability
						if 'timestamp' in feedback_df.columns:
							feedback_df['timestamp'] = pd.to_datetime(feedback_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
						
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
		col1, col2 = st.columns([0.3, 0.7])
		with col1:
			rating = st.selectbox("Rating", [1, 2, 3, 4, 5], index=4, help="Rate your experience (1=Poor, 5=Excellent)")
		with col2:
			feedback_text = st.text_area("Your Feedback", placeholder="Share your thoughts about the dashboard...", height=100)
		
		submitted = st.form_submit_button("Submit Feedback", use_container_width=True)
		
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
