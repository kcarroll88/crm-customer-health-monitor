import streamlit as st
import streamlit.components.v1 as components
import json
import time
import asyncio
from datetime import datetime
from agent import analyze_customer, load_customers

st.set_page_config(
    page_title="Apex CRM — Health Monitor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── SVG ICONS ─────────────────────────────────────────────────────────────────
ICO_PULSE = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>'
ICO_ALERT = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
ICO_WARN  = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>'
ICO_CHECK = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>'
ICO_GEAR  = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>'
ICO_CAL   = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>'
ICO_MAIL  = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>'
ICO_CLOCK = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>'
ICO_USERS = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>'
ICO_DOLLAR= '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>'
ICO_LIST  = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>'
ICO_USER  = '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>'
ICO_FIRE  = '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>'

# ── RISK CONFIG ────────────────────────────────────────────────────────────────
RISK = {
    "critical": {"color": "#DC2626", "bg": "#FEF2F2", "border": "#FCA5A5", "track": "#FEE2E2", "label": "Critical", "icon": ICO_ALERT},
    "warning":  {"color": "#D97706", "bg": "#FFFBEB", "border": "#FCD34D", "track": "#FEF3C7", "label": "Warning",  "icon": ICO_WARN},
    "healthy":  {"color": "#059669", "bg": "#ECFDF5", "border": "#6EE7B7", "track": "#D1FAE5", "label": "Healthy",  "icon": ICO_CHECK},
}

URGENCY_MAP = {"high": ("#7F1D1D", "#FEE2E2", "High"), "medium": ("#78350F", "#FEF3C7", "Medium"), "low": ("#064E3B", "#D1FAE5", "Low")}

# ── CSS ────────────────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

/* ── BACKGROUND ─────────────────────────────────────────────────────────── */
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse at 20% 0%, rgba(199,210,254,0.35) 0%, transparent 55%),
        radial-gradient(ellipse at 80% 10%, rgba(167,243,208,0.25) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 100%, rgba(224,231,255,0.2) 0%, transparent 60%),
        #F1F5F9 !important;
    min-height: 100vh;
}

[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.78) !important;
    backdrop-filter: blur(28px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(28px) saturate(180%) !important;
    border-right: 1px solid rgba(226,232,240,0.7) !important;
    box-shadow: 4px 0 24px rgba(0,0,0,0.04) !important;
}

[data-testid="stSidebarContent"] { padding-top: 12px !important; }

/* Hide chrome */
#MainMenu, footer, [data-testid="stHeader"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

/* ── MAIN CONTENT PADDING ───────────────────────────────────────────────── */
.main .block-container {
    padding-top: 12px !important;
    padding-bottom: 40px !important;
    max-width: 1400px !important;
}

/* ── ANIMATIONS ─────────────────────────────────────────────────────────── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes slideInRight {
    from { opacity: 0; transform: translateX(10px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes pulseRing {
    0%, 100% { transform: scale(1); opacity: 1; }
    50%       { transform: scale(1.5); opacity: 0.5; }
}
@keyframes spin {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
@keyframes drawRing {
    from { stroke-dashoffset: 220; }
}
@keyframes countUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes shimmer {
    0%   { background-position: -400px 0; }
    100% { background-position: 400px 0; }
}

/* ── GLASS SURFACE ──────────────────────────────────────────────────────── */
.glass {
    background: rgba(255,255,255,0.70);
    backdrop-filter: blur(24px) saturate(160%);
    -webkit-backdrop-filter: blur(24px) saturate(160%);
    border: 1px solid rgba(255,255,255,0.88);
    border-radius: 18px;
    box-shadow: 0 4px 24px rgba(15,23,42,0.06), 0 1px 2px rgba(15,23,42,0.04);
}

/* ── APP HEADER ─────────────────────────────────────────────────────────── */
.app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 0 18px;
    margin-bottom: 6px;
    border-bottom: 1px solid rgba(226,232,240,0.6);
    animation: fadeIn 0.5s ease;
}
.app-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}
.app-logo {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 4px 12px rgba(79,70,229,0.3);
    flex-shrink: 0;
}
.app-title { font-size: 20px; font-weight: 700; color: #0F172A; letter-spacing: -0.025em; line-height: 1.1; }
.app-tagline { font-size: 12px; color: #94A3B8; margin-top: 1px; font-weight: 400; }
.run-badge {
    display: flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(226,232,240,0.8);
    border-radius: 20px;
    padding: 7px 14px;
    font-size: 12px; color: #64748B;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

/* ── METRIC GRID ─────────────────────────────────────────────────────────── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin: 20px 0 24px;
}
.metric-card {
    background: rgba(255,255,255,0.70);
    backdrop-filter: blur(24px) saturate(160%);
    -webkit-backdrop-filter: blur(24px) saturate(160%);
    border: 1px solid rgba(255,255,255,0.88);
    border-radius: 16px;
    padding: 18px 20px;
    box-shadow: 0 4px 20px rgba(15,23,42,0.05);
    animation: fadeInUp 0.5s ease both;
    position: relative;
    overflow: hidden;
    transition: box-shadow 0.2s, transform 0.2s;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 16px 16px 0 0;
}
.metric-card.total::before   { background: linear-gradient(90deg, #6366F1, #818CF8); }
.metric-card.critical::before { background: linear-gradient(90deg, #EF4444, #F87171); }
.metric-card.warning::before  { background: linear-gradient(90deg, #F59E0B, #FBBF24); }
.metric-card.healthy::before  { background: linear-gradient(90deg, #10B981, #34D399); }
.metric-card:nth-child(2) { animation-delay: 0.07s; }
.metric-card:nth-child(3) { animation-delay: 0.14s; }
.metric-card:nth-child(4) { animation-delay: 0.21s; }

.metric-icon {
    width: 34px; height: 34px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 12px;
}
.metric-icon.total    { background: rgba(99,102,241,0.1); color: #6366F1; }
.metric-icon.critical { background: rgba(239,68,68,0.1);  color: #EF4444; }
.metric-icon.warning  { background: rgba(245,158,11,0.1); color: #F59E0B; }
.metric-icon.healthy  { background: rgba(16,185,129,0.1); color: #10B981; }

.metric-value {
    font-size: 30px; font-weight: 800; line-height: 1;
    letter-spacing: -0.03em; color: #0F172A;
    animation: countUp 0.4s ease both;
    margin-bottom: 4px;
}
.metric-label { font-size: 12px; font-weight: 500; color: #64748B; }
.metric-sub   { font-size: 11px; color: #94A3B8; margin-top: 3px; }

/* ── PANEL ───────────────────────────────────────────────────────────────── */
.panel {
    background: rgba(255,255,255,0.70);
    backdrop-filter: blur(24px) saturate(160%);
    -webkit-backdrop-filter: blur(24px) saturate(160%);
    border: 1px solid rgba(255,255,255,0.88);
    border-radius: 18px;
    box-shadow: 0 4px 24px rgba(15,23,42,0.06);
    padding: 22px;
    animation: fadeInUp 0.5s ease both;
}
.panel-header {
    display: flex; align-items: center; gap: 8px;
    font-size: 13px; font-weight: 600; color: #0F172A;
    letter-spacing: -0.01em; margin-bottom: 18px;
    padding-bottom: 14px;
    border-bottom: 1px solid rgba(226,232,240,0.5);
}
.panel-icon {
    width: 28px; height: 28px;
    background: rgba(79,70,229,0.08);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    color: #4F46E5;
}

/* ── FEED ITEM ───────────────────────────────────────────────────────────── */
.feed-item {
    display: flex; align-items: flex-start; gap: 10px;
    padding: 9px 0;
    border-bottom: 1px solid rgba(226,232,240,0.4);
    animation: slideInRight 0.3s ease both;
}
.feed-item:last-child { border-bottom: none; padding-bottom: 0; }
.feed-dot {
    width: 7px; height: 7px; border-radius: 50%;
    margin-top: 5px; flex-shrink: 0;
    transition: all 0.3s;
}
.feed-dot.analyzing { background: #6366F1; animation: pulseRing 1.2s ease infinite; }
.feed-dot.critical  { background: #EF4444; }
.feed-dot.warning   { background: #F59E0B; }
.feed-dot.healthy   { background: #10B981; }
.feed-dot.info      { background: #CBD5E1; }
.feed-text  { flex: 1; font-size: 13px; color: #334155; line-height: 1.45; }
.feed-score {
    font-size: 12px; font-weight: 600;
    padding: 2px 8px; border-radius: 20px;
    flex-shrink: 0; margin-top: 1px;
}
.feed-score.critical { color: #DC2626; background: #FEF2F2; }
.feed-score.warning  { color: #D97706; background: #FFFBEB; }
.feed-score.healthy  { color: #059669; background: #ECFDF5; }

/* ── EMPTY STATE ─────────────────────────────────────────────────────────── */
.empty-state {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    padding: 48px 24px; animation: fadeIn 0.4s ease;
}
.empty-glyph {
    width: 52px; height: 52px;
    background: rgba(99,102,241,0.07);
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    color: #A5B4FC; margin-bottom: 14px;
}
.empty-title { font-size: 14px; font-weight: 600; color: #475569; margin-bottom: 4px; }
.empty-sub   { font-size: 12px; color: #94A3B8; text-align: center; line-height: 1.5; }

/* ── SECTION HEADING ─────────────────────────────────────────────────────── */
.section-heading {
    display: flex; align-items: center; gap: 7px;
    font-size: 11px; font-weight: 700; letter-spacing: 0.07em;
    text-transform: uppercase; margin: 18px 0 10px;
}
.section-heading:first-child { margin-top: 0; }

/* ── ACCOUNT CARD ────────────────────────────────────────────────────────── */
.account-card {
    background: rgba(255,255,255,0.55);
    border: 1px solid rgba(255,255,255,0.8);
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 10px;
    transition: box-shadow 0.2s, transform 0.2s;
    animation: fadeInUp 0.4s ease both;
    position: relative;
    overflow: hidden;
}
.account-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    border-radius: 14px 0 0 14px;
}
.account-card.critical::before { background: #EF4444; }
.account-card.warning::before  { background: #F59E0B; }
.account-card.healthy::before  { background: #10B981; }
.account-card:hover {
    box-shadow: 0 6px 28px rgba(15,23,42,0.1);
    transform: translateY(-1px);
}

.card-top {
    display: flex; align-items: flex-start; justify-content: space-between;
    gap: 12px; margin-bottom: 10px;
}
.card-name  { font-size: 14px; font-weight: 600; color: #0F172A; letter-spacing: -0.01em; }
.card-meta  { display: flex; align-items: center; gap: 12px; margin-top: 4px; }
.card-meta-item {
    display: flex; align-items: center; gap: 4px;
    font-size: 11px; color: #94A3B8; font-weight: 500;
}

.risk-pill {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 9px; border-radius: 20px;
    font-size: 11px; font-weight: 600; letter-spacing: 0.04em;
    border: 1px solid transparent;
    text-transform: uppercase; flex-shrink: 0;
}
.risk-pill.critical { color: #DC2626; background: #FEF2F2; border-color: #FCA5A5; }
.risk-pill.warning  { color: #D97706; background: #FFFBEB; border-color: #FCD34D; }
.risk-pill.healthy  { color: #059669; background: #ECFDF5; border-color: #6EE7B7; }

.urgency-pill {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 2px 7px; border-radius: 4px;
    font-size: 10px; font-weight: 600; letter-spacing: 0.05em;
    text-transform: uppercase;
}

.concerns {
    display: flex; flex-wrap: wrap; gap: 5px;
    margin: 8px 0 10px;
}
.concern-tag {
    font-size: 11px; color: #475569;
    background: rgba(71,85,105,0.07);
    border: 1px solid rgba(71,85,105,0.1);
    padding: 3px 8px; border-radius: 5px;
    line-height: 1.4;
}
.action-box {
    background: rgba(79,70,229,0.04);
    border: 1px solid rgba(79,70,229,0.1);
    border-radius: 9px;
    padding: 10px 12px;
    font-size: 12.5px; color: #3730A3;
    line-height: 1.55;
}

/* ── SCORE RING ──────────────────────────────────────────────────────────── */
.ring-wrap {
    display: flex; flex-direction: column; align-items: center;
    flex-shrink: 0;
}
.ring-wrap svg circle.track { transition: stroke-dasharray 0.8s ease; }
.ring-wrap svg circle.fill  {
    transition: stroke-dasharray 0.8s ease;
    animation: drawRing 0.8s ease both;
}

/* ── RUN BUTTON ──────────────────────────────────────────────────────────── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #4F46E5 0%, #6D28D9 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 11px !important;
    font-size: 13.5px !important;
    font-weight: 600 !important;
    padding: 10px 26px !important;
    box-shadow: 0 4px 16px rgba(79,70,229,0.35), 0 1px 3px rgba(79,70,229,0.2) !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.01em !important;
}
[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #4338CA 0%, #5B21B6 100%) !important;
    box-shadow: 0 6px 22px rgba(79,70,229,0.45), 0 2px 6px rgba(79,70,229,0.25) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stButton"] > button:active { transform: translateY(0) !important; }

/* ── SIDEBAR STYLING ─────────────────────────────────────────────────────── */
[data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] {
    border-radius: 9px !important;
    border-color: rgba(226,232,240,0.8) !important;
    background: rgba(255,255,255,0.6) !important;
    font-size: 13px !important;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] input {
    border-radius: 9px !important;
    border-color: rgba(226,232,240,0.8) !important;
    background: rgba(255,255,255,0.6) !important;
    font-size: 13px !important;
}

/* ── SUCCESS TOAST ───────────────────────────────────────────────────────── */
.toast {
    display: flex; align-items: center; gap: 10px;
    background: rgba(236,253,245,0.9);
    backdrop-filter: blur(12px);
    border: 1px solid #6EE7B7;
    border-radius: 12px;
    padding: 14px 18px;
    font-size: 13px; color: #065F46;
    animation: fadeInUp 0.4s ease;
    margin-top: 16px;
}
.toast-icon {
    width: 28px; height: 28px;
    background: rgba(16,185,129,0.12);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    color: #059669; flex-shrink: 0;
}

/* ── FILTER TABS ─────────────────────────────────────────────────────────── */
.filter-tabs {
    display: flex; gap: 6px; margin-bottom: 16px;
}
.filter-tab {
    padding: 5px 12px; border-radius: 20px;
    font-size: 11.5px; font-weight: 600; cursor: pointer;
    border: 1px solid rgba(226,232,240,0.8);
    background: rgba(255,255,255,0.5);
    color: #64748B; letter-spacing: 0.02em;
    transition: all 0.15s;
}
.filter-tab.active-all      { background: #0F172A; color: #fff; border-color: #0F172A; }
.filter-tab.active-critical { background: #DC2626; color: #fff; border-color: #DC2626; }
.filter-tab.active-warning  { background: #D97706; color: #fff; border-color: #D97706; }
.filter-tab.active-healthy  { background: #059669; color: #fff; border-color: #059669; }

/* ── DIVIDER ─────────────────────────────────────────────────────────────── */
.hr { height: 1px; background: rgba(226,232,240,0.5); margin: 6px 0 20px; }

/* ── REPORT ENTRY ANIMATION (expands from right after analysis) ──────────── */
@keyframes reportExpandCenter {
    0%   { opacity: 0;   transform: translateX(5%) scale(0.975); }
    100% { opacity: 1;   transform: translateX(0)  scale(1); }
}
.report-entry {
    animation: reportExpandCenter 0.7s cubic-bezier(0.22, 1, 0.36, 1) both;
}

/* ── MAC-STYLE NOTIFICATION ──────────────────────────────────────────────── */
@keyframes macNotifSlide {
    0%   { opacity: 0;   transform: translateX(calc(100% + 30px)); }
    12%  { opacity: 1;   transform: translateX(0); }
    80%  { opacity: 1;   transform: translateX(0); }
    100% { opacity: 0;   transform: translateX(calc(100% + 30px)); }
}
.mac-notif {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 99999;
    min-width: 300px;
    max-width: 360px;
    background: rgba(44, 44, 46, 0.94);
    backdrop-filter: blur(28px) saturate(180%);
    -webkit-backdrop-filter: blur(28px) saturate(180%);
    border: 0.5px solid rgba(255,255,255,0.14);
    border-radius: 16px;
    padding: 14px 16px;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.4), 0 2px 8px rgba(0,0,0,0.15);
    animation: macNotifSlide 4.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
    pointer-events: none;
}
.mac-notif-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #4F46E5, #7C3AED);
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(79,70,229,0.5);
}
.mac-notif-body { flex: 1; min-width: 0; }
.mac-notif-app {
    font-size: 10.5px; font-weight: 700;
    color: rgba(255,255,255,0.45);
    margin-bottom: 3px;
    text-transform: uppercase; letter-spacing: 0.08em;
}
.mac-notif-title {
    font-size: 13px; font-weight: 600;
    color: rgba(255,255,255,0.95);
    margin-bottom: 2px;
}
.mac-notif-text {
    font-size: 12px;
    color: rgba(255,255,255,0.55);
    line-height: 1.4;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
</style>
"""

# ── HELPERS ────────────────────────────────────────────────────────────────────
def fmt_usd(n):
    if n >= 1_000_000:
        return f"${n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"${n//1_000}K"
    return f"${n}"

def score_ring(score, risk, size=54):
    r = size / 2 - 5
    circ = 2 * 3.14159265 * r
    filled = (score / 100) * circ
    empty = circ - filled
    c = RISK[risk]["color"]
    track = RISK[risk]["track"]
    cx = cy = size / 2
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
        f'<circle class="track" cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{track}" stroke-width="4.5"/>'
        f'<circle class="fill" cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{c}" stroke-width="4.5" '
        f'stroke-dasharray="{filled:.2f} {empty:.2f}" stroke-linecap="round" '
        f'transform="rotate(-90 {cx} {cy})"/>'
        f'<text x="{cx}" y="{cy+4}" text-anchor="middle" font-size="12" font-weight="700" '
        f'fill="{c}" font-family="Inter,sans-serif">{score}</text>'
        f'</svg>'
    )

def account_card(result, customer_map, delay=0):
    risk = result["risk_level"]
    cfg = RISK[risk]
    name = result["company_name"]
    score = result["health_score"]
    cust = customer_map.get(name, {})
    manager = cust.get("account_manager", "—")
    contract = cust.get("contract_value", 0)
    urgency = result.get("urgency", "medium")
    urg_cfg = URGENCY_MAP.get(urgency, ("#1E293B", "#F1F5F9", urgency.title()))

    ring = score_ring(score, risk)
    concerns_html = "".join(f'<span class="concern-tag">{c}</span>' for c in result.get("top_concerns", []))
    urg_style = f'color:{urg_cfg[0]};background:{urg_cfg[1]}'

    return f"""
    <div class="account-card {risk}" style="animation-delay:{delay}ms">
        <div class="card-top">
            <div>
                <div class="card-name">{name}</div>
                <div class="card-meta">
                    <span class="card-meta-item">{ICO_USER} {manager}</span>
                    <span class="card-meta-item">{ICO_DOLLAR} {fmt_usd(contract)}</span>
                </div>
            </div>
            <div class="ring-wrap">{ring}</div>
        </div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
            <span class="risk-pill {risk}">{cfg['icon']}&nbsp;{cfg['label']}</span>
            <span class="urgency-pill" style="{urg_style}">{ICO_FIRE}&nbsp;{urg_cfg[2]} Urgency</span>
        </div>
        <div class="concerns">{concerns_html}</div>
        <div class="action-box">{result['recommended_action']}</div>
    </div>"""

def render_feed(items):
    rows = ""
    for text, dot, score, risk, ts in items:
        score_html = f'<span class="feed-score {risk}">{score}/100</span>' if score else ""
        rows += f'<div class="feed-item"><div class="feed-dot {dot}"></div><div class="feed-text">{text}</div>{score_html}</div>'
    empty = ('<div class="empty-state"><div class="empty-glyph"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div><div class="empty-title">No activity yet</div><div class="empty-sub">Click Run Analysis to begin</div></div>')
    return f'<div class="panel-header"><div class="panel-icon">{ICO_CLOCK}</div>Live Analysis Feed</div>' + (rows or empty)

def render_report(results, customer_map, active_filter="all"):
    critical = sorted([r for r in results if r["risk_level"] == "critical"], key=lambda x: x["health_score"])
    warning  = sorted([r for r in results if r["risk_level"] == "warning"],  key=lambda x: x["health_score"])
    healthy  = sorted([r for r in results if r["risk_level"] == "healthy"],  key=lambda x: x["health_score"], reverse=True)

    n_crit = len(critical); n_warn = len(warning); n_hlth = len(healthy)

    html = f'<div class="panel-header"><div class="panel-icon">{ICO_LIST}</div>Health Report</div>'

    delay = 0
    if active_filter in ("all", "critical") and critical:
        html += f'<div class="section-heading" style="color:#DC2626">{ICO_ALERT}&nbsp;Immediate Action</div>'
        for r in critical:
            html += account_card(r, customer_map, delay)
            delay += 50

    if active_filter in ("all", "warning") and warning:
        html += f'<div class="section-heading" style="color:#D97706">{ICO_WARN}&nbsp;Needs Attention</div>'
        for r in warning:
            html += account_card(r, customer_map, delay)
            delay += 50

    if active_filter in ("all", "healthy") and healthy:
        html += f'<div class="section-heading" style="color:#059669">{ICO_CHECK}&nbsp;On Track</div>'
        for r in healthy:
            html += account_card(r, customer_map, delay)
            delay += 50

    if not html.strip().endswith('</div>'):
        html += '<div class="empty-state"><div class="empty-sub">No accounts in this category</div></div>'

    return html

def render_metrics(results=None, customers=None):
    if results is None:
        total = len(customers) if customers else "—"
        return f"""
        <div class="metric-grid">
            <div class="metric-card total">
                <div class="metric-icon total">{ICO_USERS}</div>
                <div class="metric-value">{total}</div>
                <div class="metric-label">Accounts</div>
                <div class="metric-sub">Total portfolio</div>
            </div>
            <div class="metric-card critical">
                <div class="metric-icon critical">{ICO_ALERT}</div>
                <div class="metric-value" style="color:#DC2626">—</div>
                <div class="metric-label">Critical</div>
                <div class="metric-sub">Run to score</div>
            </div>
            <div class="metric-card warning">
                <div class="metric-icon warning">{ICO_WARN}</div>
                <div class="metric-value" style="color:#D97706">—</div>
                <div class="metric-label">Warning</div>
                <div class="metric-sub">Needs attention</div>
            </div>
            <div class="metric-card healthy">
                <div class="metric-icon healthy">{ICO_CHECK}</div>
                <div class="metric-value" style="color:#059669">—</div>
                <div class="metric-label">Healthy</div>
                <div class="metric-sub">On track</div>
            </div>
        </div>"""

    n_crit = len([r for r in results if r["risk_level"] == "critical"])
    n_warn = len([r for r in results if r["risk_level"] == "warning"])
    n_hlth = len([r for r in results if r["risk_level"] == "healthy"])
    avg = sum(r["health_score"] for r in results) / len(results)
    at_risk_arr = sum(
        c.get("contract_value", 0)
        for c in customers
        if any(r["company_name"] == c["company_name"] and r["risk_level"] in ("critical", "warning") for r in results)
    )

    return f"""
    <div class="metric-grid">
        <div class="metric-card total">
            <div class="metric-icon total">{ICO_USERS}</div>
            <div class="metric-value">{len(results)}</div>
            <div class="metric-label">Accounts</div>
            <div class="metric-sub">Avg score: {avg:.0f}/100</div>
        </div>
        <div class="metric-card critical">
            <div class="metric-icon critical">{ICO_ALERT}</div>
            <div class="metric-value" style="color:#DC2626">{n_crit}</div>
            <div class="metric-label">Critical</div>
            <div class="metric-sub">Immediate action needed</div>
        </div>
        <div class="metric-card warning">
            <div class="metric-icon warning">{ICO_WARN}</div>
            <div class="metric-value" style="color:#D97706">{n_warn}</div>
            <div class="metric-label">Warning</div>
            <div class="metric-sub">Closely monitor</div>
        </div>
        <div class="metric-card healthy">
            <div class="metric-icon healthy">{ICO_CHECK}</div>
            <div class="metric-value" style="color:#059669">{n_hlth}</div>
            <div class="metric-label">Healthy</div>
            <div class="metric-sub">{fmt_usd(at_risk_arr)} ARR at risk</div>
        </div>
    </div>"""

def render_email_report(results, customer_map):
    date = datetime.now().strftime("%B %d, %Y")
    n_crit = len([r for r in results if r["risk_level"] == "critical"])
    n_warn = len([r for r in results if r["risk_level"] == "warning"])
    n_hlth = len([r for r in results if r["risk_level"] == "healthy"])
    avg = sum(r["health_score"] for r in results) / len(results) if results else 0

    critical = sorted([r for r in results if r["risk_level"] == "critical"], key=lambda x: x["health_score"])
    warning  = sorted([r for r in results if r["risk_level"] == "warning"],  key=lambda x: x["health_score"])
    healthy  = sorted([r for r in results if r["risk_level"] == "healthy"],  key=lambda x: x["health_score"], reverse=True)

    def email_row(r, bg, border, color, label):
        name     = r["company_name"]
        score    = r["health_score"]
        cust     = customer_map.get(name, {})
        manager  = cust.get("account_manager", "—")
        contract = cust.get("contract_value", 0)
        concerns = ", ".join(r.get("top_concerns", []))
        action   = r.get("recommended_action", "")
        return f"""
        <tr>
          <td style="padding:14px 0;border-bottom:1px solid #E2E8F0">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="width:50px;vertical-align:top;padding-top:2px">
                  <div style="width:44px;height:44px;border-radius:50%;background:{bg};border:2px solid {border};
                              font-size:13px;font-weight:800;color:{color};text-align:center;line-height:40px">
                    {score}
                  </div>
                </td>
                <td style="padding-left:12px;vertical-align:top">
                  <div style="font-size:14px;font-weight:600;color:#0F172A;margin-bottom:2px">{name}</div>
                  <div style="font-size:11px;color:#94A3B8;margin-bottom:6px">{manager} · {fmt_usd(contract)}</div>
                  <span style="display:inline-block;padding:2px 8px;border-radius:4px;
                               font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;
                               background:{bg};color:{color};border:1px solid {border};margin-bottom:8px">{label}</span>
                  {"" if not concerns else f'<div style="font-size:11px;color:#475569;margin-bottom:8px">{concerns}</div>'}
                  <div style="font-size:12px;color:#3730A3;background:rgba(79,70,229,0.05);
                              border-left:3px solid #4F46E5;padding:8px 10px;border-radius:0 6px 6px 0;line-height:1.5">{action}</div>
                </td>
              </tr>
            </table>
          </td>
        </tr>"""

    def section(rows_html, color, label, count):
        if not rows_html:
            return ""
        return f"""
        <tr><td style="padding:20px 0 4px">
          <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;
                      color:{color};border-left:3px solid {color};padding-left:8px">{label} ({count})</div>
        </td></tr>
        {rows_html}"""

    critical_rows = "".join(email_row(r, "#FEF2F2", "#FCA5A5", "#DC2626", "Critical") for r in critical)
    warning_rows  = "".join(email_row(r, "#FFFBEB", "#FCD34D", "#D97706", "Warning")  for r in warning)
    healthy_rows  = "".join(email_row(r, "#ECFDF5", "#6EE7B7", "#059669", "Healthy")  for r in healthy)

    at_risk_arr = sum(
        c.get("contract_value", 0)
        for c in customer_map.values()
        if any(r["company_name"] == c["company_name"] and r["risk_level"] in ("critical", "warning") for r in results)
    )

    return f"""
    <div style="max-width:620px;margin:0 auto;font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">

      <!-- Email client chrome -->
      <div style="background:rgba(255,255,255,0.75);backdrop-filter:blur(20px);
                  border:1px solid rgba(226,232,240,0.9);border-radius:16px 16px 0 0;
                  padding:16px 22px;border-bottom:1px solid rgba(226,232,240,0.6)">
        <div style="font-size:11px;color:#94A3B8;margin-bottom:10px;display:flex;align-items:center;gap:5px">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
          Email Preview
        </div>
        <div style="font-size:17px;font-weight:600;color:#0F172A;margin-bottom:10px;letter-spacing:-0.02em">
          Customer Health Report · {date}
        </div>
        <div style="display:flex;flex-direction:column;gap:4px">
          <div style="font-size:12px;color:#475569"><span style="color:#94A3B8;display:inline-block;width:46px">From</span>Apex CRM &lt;reports@apexcrm.ai&gt;</div>
          <div style="font-size:12px;color:#475569"><span style="color:#94A3B8;display:inline-block;width:46px">To</span>Your Team &lt;team@company.com&gt;</div>
          <div style="font-size:12px;color:#475569"><span style="color:#94A3B8;display:inline-block;width:46px">Date</span>{date}</div>
        </div>
      </div>

      <!-- Email body -->
      <div style="background:#ffffff;border:1px solid rgba(226,232,240,0.9);border-top:none;border-radius:0 0 16px 16px;overflow:hidden">

        <!-- Header banner -->
        <div style="background:linear-gradient(135deg,#4F46E5 0%,#7C3AED 100%);padding:28px 32px">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">
            <div style="width:34px;height:34px;background:rgba(255,255,255,0.18);border-radius:9px;
                        display:flex;align-items:center;justify-content:center">
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
            </div>
            <div>
              <div style="font-size:13px;font-weight:700;color:rgba(255,255,255,0.95)">Apex CRM</div>
              <div style="font-size:10px;color:rgba(255,255,255,0.5)">Customer Health Monitor</div>
            </div>
          </div>
          <div style="font-size:24px;font-weight:700;color:#fff;letter-spacing:-0.025em;margin-bottom:4px">Daily Health Report</div>
          <div style="font-size:13px;color:rgba(255,255,255,0.55)">{date} · AI-powered account analysis</div>
        </div>

        <!-- Summary stats -->
        <div style="padding:24px 32px 0">
          <table width="100%" cellpadding="0" cellspacing="8" border="0" style="margin-bottom:4px">
            <tr>
              <td style="width:25%;padding-right:6px">
                <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:14px;text-align:center">
                  <div style="font-size:26px;font-weight:800;color:#0F172A;letter-spacing:-0.03em">{len(results)}</div>
                  <div style="font-size:11px;color:#64748B;font-weight:500;margin-top:2px">Total</div>
                  <div style="font-size:10px;color:#94A3B8">avg {avg:.0f}/100</div>
                </div>
              </td>
              <td style="width:25%;padding:0 3px">
                <div style="background:#FEF2F2;border:1px solid #FCA5A5;border-radius:10px;padding:14px;text-align:center">
                  <div style="font-size:26px;font-weight:800;color:#DC2626;letter-spacing:-0.03em">{n_crit}</div>
                  <div style="font-size:11px;color:#DC2626;font-weight:500;margin-top:2px">Critical</div>
                  <div style="font-size:10px;color:#EF4444">act now</div>
                </div>
              </td>
              <td style="width:25%;padding:0 3px">
                <div style="background:#FFFBEB;border:1px solid #FCD34D;border-radius:10px;padding:14px;text-align:center">
                  <div style="font-size:26px;font-weight:800;color:#D97706;letter-spacing:-0.03em">{n_warn}</div>
                  <div style="font-size:11px;color:#D97706;font-weight:500;margin-top:2px">Warning</div>
                  <div style="font-size:10px;color:#F59E0B">watch closely</div>
                </div>
              </td>
              <td style="width:25%;padding-left:6px">
                <div style="background:#ECFDF5;border:1px solid #6EE7B7;border-radius:10px;padding:14px;text-align:center">
                  <div style="font-size:26px;font-weight:800;color:#059669;letter-spacing:-0.03em">{n_hlth}</div>
                  <div style="font-size:11px;color:#059669;font-weight:500;margin-top:2px">Healthy</div>
                  <div style="font-size:10px;color:#10B981">on track</div>
                </div>
              </td>
            </tr>
          </table>

          {"" if not at_risk_arr else f'<div style="background:#FEF2F2;border:1px solid #FCA5A5;border-radius:8px;padding:10px 14px;margin:16px 0 0;font-size:12px;color:#DC2626;font-weight:500">{fmt_usd(at_risk_arr)} ARR at risk across critical and warning accounts</div>'}

          <div style="height:1px;background:#E2E8F0;margin:20px 0 0"></div>

          <!-- Account rows -->
          <table width="100%" cellpadding="0" cellspacing="0" border="0">
            {section(critical_rows, "#DC2626", "Immediate Action Required", n_crit)}
            {section(warning_rows,  "#D97706", "Needs Attention",           n_warn)}
            {section(healthy_rows,  "#059669", "On Track",                  n_hlth)}
          </table>
        </div>

        <!-- Footer -->
        <div style="background:#F8FAFC;border-top:1px solid #E2E8F0;padding:18px 32px;text-align:center;margin-top:16px">
          <div style="font-size:11px;color:#94A3B8;line-height:1.6">
            This report was generated automatically by Apex CRM · {date}<br>
            Built with Claude · Python · Streamlit
          </div>
        </div>
      </div>
    </div>"""

# ── PAGE ───────────────────────────────────────────────────────────────────────
st.markdown(CSS, unsafe_allow_html=True)

customers = load_customers()
customer_map = {c["company_name"]: c for c in customers}

if "results" not in st.session_state:
    st.session_state.results = []
if "_pending_email" not in st.session_state:
    st.session_state._pending_email = ""
if "_just_finished" not in st.session_state:
    st.session_state._just_finished = False
if "_view_email_report" not in st.session_state:
    st.session_state._view_email_report = False

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:8px 0 24px">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:2px">
            <div style="width:32px;height:32px;background:linear-gradient(135deg,#4F46E5,#7C3AED);
                        border-radius:9px;display:flex;align-items:center;justify-content:center;
                        box-shadow:0 3px 10px rgba(79,70,229,0.3)">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white"
                     stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                </svg>
            </div>
            <div>
                <div style="font-size:15px;font-weight:700;color:#0F172A;letter-spacing:-0.02em">Apex CRM</div>
                <div style="font-size:11px;color:#94A3B8;font-weight:400">Health Monitor</div>
            </div>
        </div>
    </div>
    <div class="hr"></div>
    <div style="font-size:10.5px;font-weight:700;letter-spacing:0.09em;text-transform:uppercase;
                color:#94A3B8;margin-bottom:10px;display:flex;align-items:center;gap:6px">
        {ICO_GEAR}&nbsp; Schedule
    </div>
    """, unsafe_allow_html=True)

    scheduled_time = st.selectbox("Daily report time", ["6:00 AM", "7:00 AM", "8:00 AM", "9:00 AM"],
                                  index=2, label_visibility="collapsed")

    st.markdown(f"""
    <div style="background:rgba(79,70,229,0.05);border:1px solid rgba(79,70,229,0.12);
                border-radius:11px;padding:12px 14px;margin:12px 0">
        <div style="display:flex;align-items:center;gap:6px;font-size:11.5px;
                    font-weight:600;color:#4F46E5;margin-bottom:3px">
            {ICO_CAL}&nbsp; Next scheduled run
        </div>
        <div style="font-size:13px;color:#3730A3;font-weight:500">Tomorrow · {scheduled_time}</div>
    </div>
    <div class="hr"></div>
    <div style="font-size:10.5px;font-weight:700;letter-spacing:0.09em;text-transform:uppercase;
                color:#94A3B8;margin-bottom:10px;display:flex;align-items:center;gap:6px">
        {ICO_MAIL}&nbsp; Email Delivery
    </div>
    """, unsafe_allow_html=True)

    email = st.text_input("Email", placeholder="you@company.com", label_visibility="collapsed")

    st.markdown("""
    <div style="font-size:11px;color:#F59E0B;background:rgba(245,158,11,0.08);
                border:1px solid rgba(245,158,11,0.25);border-radius:6px;
                padding:7px 10px;margin-top:8px;line-height:1.5">
        <strong>Demo mode</strong> — report will be generated but email will not be sent.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="height:1px;background:linear-gradient(90deg,transparent,rgba(203,213,225,0.5),transparent);
                margin:24px 0 16px"></div>
    <div style="font-size:11px;color:#94A3B8;text-align:center;line-height:1.6">
        Built with Claude · Python · Streamlit
    </div>
    """, unsafe_allow_html=True)

# ── EMAIL REPORT VIEW ──────────────────────────────────────────────────────────
if st.session_state._view_email_report and st.session_state.results:
    ret_col, _ = st.columns([1, 5])
    with ret_col:
        if st.button("← Return to Dashboard", use_container_width=True):
            st.session_state._view_email_report = False
            st.session_state.results = []
            st.session_state._just_finished = False
            st.session_state._pending_email = ""
            st.rerun()
    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    _, center_col, _ = st.columns([1, 4, 1])
    with center_col:
        components.html(render_email_report(st.session_state.results, customer_map), height=900, scrolling=True)
    st.stop()

# ── HEADER ─────────────────────────────────────────────────────────────────────
now_str = datetime.now().strftime("%b %d, %Y · %I:%M %p")
st.markdown(f"""
<div class="app-header">
    <div class="app-brand">
        <div class="app-logo">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white"
                 stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
            </svg>
        </div>
        <div>
            <div class="app-title">Customer Health Monitor</div>
            <div class="app-tagline">AI-powered account analysis · surfaces what needs attention</div>
        </div>
    </div>
    <div class="run-badge">
        {ICO_CLOCK}&nbsp; {now_str}
    </div>
</div>
""", unsafe_allow_html=True)

# ── METRICS ────────────────────────────────────────────────────────────────────
metrics_slot = st.empty()
if st.session_state.results:
    metrics_slot.markdown(render_metrics(st.session_state.results, customers), unsafe_allow_html=True)
else:
    metrics_slot.markdown(render_metrics(customers=customers), unsafe_allow_html=True)

# ── RUN BUTTON ─────────────────────────────────────────────────────────────────
col_btn, col_hint = st.columns([1, 5])
run = False
with col_btn:
    if st.session_state.results:
        if st.button("View Report", type="primary", use_container_width=True):
            st.session_state._view_email_report = True
            st.rerun()
    else:
        run = st.button("Run Analysis", type="primary", use_container_width=True)
with col_hint:
    if st.session_state.results:
        st.markdown(
            "<div style='padding-top:11px;font-size:12px;color:#94A3B8'>"
            "Analysis complete · click to preview the email report</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div style='padding-top:11px;font-size:12px;color:#94A3B8'>"
            f"Simulates your {scheduled_time} scheduled run</div>",
            unsafe_allow_html=True
        )

st.markdown('<div class="hr" style="margin-top:18px"></div>', unsafe_allow_html=True)

# ── CONTENT ────────────────────────────────────────────────────────────────────
just_finished = st.session_state._just_finished
if just_finished:
    st.session_state._just_finished = False

# Create placeholder BEFORE the run check so its position in the element tree
# is identical on every render — this lets Streamlit correctly reconcile and
# replace the old report instead of leaving it orphaned in the DOM.
content_placeholder = st.empty()

if run:
    st.session_state.results = []
    st.session_state._should_run = True

should_run = st.session_state.get("_should_run", False)

if should_run or not st.session_state.results:
    # Two-column layout: live feed on left, report building on right
    content_placeholder.empty()
    with content_placeholder.container():
        left, right = st.columns([1, 1], gap="large")

        with left:
            feed_slot = st.empty()
            feed_slot.markdown(
                f'<div class="panel">{render_feed([])}</div>',
                unsafe_allow_html=True
            )

        with right:
            report_slot = st.empty()
            report_slot.markdown(
                f'<div class="panel"><div class="panel-header"><div class="panel-icon">{ICO_LIST}</div>Health Report</div><div class="empty-state"><div class="empty-glyph"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg></div><div class="empty-title">No report yet</div><div class="empty-sub">Results will appear here<br>as each account is scored</div></div></div>',
                unsafe_allow_html=True,
            )

else:
    # Centered full-width layout after analysis completes
    content_placeholder.empty()
    with content_placeholder.container():
        _res = st.session_state.results
        _nc = len([r for r in _res if r["risk_level"] == "critical"])
        _nw = len([r for r in _res if r["risk_level"] == "warning"])
        _nh = len([r for r in _res if r["risk_level"] == "healthy"])
        active_filter = st.segmented_control(
            "Filter",
            options=["all", "critical", "warning", "healthy"],
            format_func=lambda x: {
                "all": f"All ({len(_res)})",
                "critical": f"Critical ({_nc})",
                "warning": f"Watch ({_nw})",
                "healthy": f"Healthy ({_nh})",
            }[x],
            default="all",
            label_visibility="collapsed",
        )

        entry_class = "report-entry" if just_finished else ""
        _, center_col, _ = st.columns([1, 4, 1], gap="large")
        with center_col:
            report_slot = st.empty()
            report_slot.markdown(
                f'<div class="panel {entry_class}">{render_report(_res, customer_map, active_filter or "all")}</div>',
                unsafe_allow_html=True,
            )

# ── MAC NOTIFICATION (shown after analysis completes) ──────────────────────────
if st.session_state._pending_email and st.session_state.results:
    _notif_email = st.session_state._pending_email
    st.session_state._pending_email = ""
    st.markdown(f"""
<div class="mac-notif">
    <div class="mac-notif-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
            <polyline points="22,6 12,13 2,6"/>
        </svg>
    </div>
    <div class="mac-notif-body">
        <div class="mac-notif-app">Apex CRM</div>
        <div class="mac-notif-title">Report Sent</div>
        <div class="mac-notif-text">{_notif_email}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── RUN LOGIC ──────────────────────────────────────────────────────────────────
if should_run:
    st.session_state._should_run = False
    results = []
    feed_items = []  # (text, dot, score, risk, ts)

    ts = datetime.now().strftime("%H:%M:%S")
    feed_items.append((f"Starting analysis of <strong>{len(customers)}</strong> accounts", "info", None, "", ts))
    feed_slot.markdown(f'<div class="panel">{render_feed(feed_items)}</div>', unsafe_allow_html=True)

    for customer in customers:
        name = customer["company_name"]
        ts = datetime.now().strftime("%H:%M:%S")
        feed_items.append((f"Analyzing <strong>{name}</strong>…", "analyzing", None, "", ts))
        feed_slot.markdown(f'<div class="panel">{render_feed(feed_items)}</div>', unsafe_allow_html=True)

        result = asyncio.run(analyze_customer(customer))
        results.append(result)

        risk  = result["risk_level"]
        score = result["health_score"]
        feed_items[-1] = (f"<strong>{name}</strong>", risk, score, risk, ts)

        feed_slot.markdown(f'<div class="panel">{render_feed(feed_items)}</div>', unsafe_allow_html=True)
        report_slot.markdown(f'<div class="panel">{render_report(results, customer_map)}</div>', unsafe_allow_html=True)

        time.sleep(0.35)

    # Final feed line
    ts = datetime.now().strftime("%H:%M:%S")
    n_crit = len([r for r in results if r["risk_level"] == "critical"])
    feed_items.append((
        f"Analysis complete · <strong>{len(results)}</strong> accounts · "
        f"<strong style='color:#DC2626'>{n_crit} critical</strong>",
        "info", None, "", ts
    ))
    feed_slot.markdown(f'<div class="panel">{render_feed(feed_items)}</div>', unsafe_allow_html=True)

    # Store results so filter controls appear after rerun
    st.session_state.results = results
    st.session_state._pending_email = email if email else ""
    st.session_state._just_finished = True

    # Clear the two-column analysis layout before rerunning so the old report
    # doesn't ghost while Streamlit reconciles the new centered layout.
    content_placeholder.empty()
    st.rerun()
