import streamlit as st
from groq import Groq
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

st.set_page_config(
    page_title="FraudSOC Terminal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── STYLES ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

* { font-family: 'IBM Plex Sans', sans-serif; box-sizing: border-box; }
code, .mono { font-family: 'IBM Plex Mono', monospace !important; }

/* Reset Streamlit defaults */
.stApp { background-color: #080c10 !important; color: #c9d1d9; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }
.stButton > button {
    background: #0d1117 !important;
    color: #58a6ff !important;
    border: 1px solid #21262d !important;
    border-radius: 3px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 1px;
    padding: 6px 14px !important;
    transition: all 0.2s;
}
.stButton > button:hover {
    border-color: #58a6ff !important;
    background: #161b22 !important;
}
.stTextInput > div > div > input {
    background-color: #0d1117 !important;
    color: #c9d1d9 !important;
    border: 1px solid #21262d !important;
    border-radius: 3px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 12px !important;
}
.stTextInput > div > div > input:focus { border-color: #58a6ff !important; box-shadow: none !important; }
.stTextInput label { color: #8b949e !important; font-size: 11px !important; }
[data-testid="stMetricValue"] { color: #fff !important; }
[data-testid="stMetricLabel"] { color: #8b949e !important; }
div[data-testid="stHorizontalBlock"] { gap: 10px; }
.stSpinner > div > div { border-top-color: #58a6ff !important; }

/* ── TOP BAR ── */
.topbar {
    background: #0d1117;
    border-bottom: 1px solid #21262d;
    padding: 6px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: #8b949e;
    letter-spacing: 1.5px;
}
.topbar-left { display: flex; gap: 24px; align-items: center; }
.topbar-brand { color: #58a6ff; font-weight: 600; font-size: 11px; }
.status-live { color: #3fb950; display: flex; align-items: center; gap: 5px; }
.status-dot {
    width: 7px; height: 7px; background: #3fb950;
    border-radius: 50%; display: inline-block;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%,100% { opacity:1; box-shadow: 0 0 0 0 rgba(63,185,80,0.4); }
    50% { opacity:.7; box-shadow: 0 0 0 5px rgba(63,185,80,0); }
}

/* ── PAGE HEADER ── */
.page-header {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    border-bottom: 1px solid #21262d;
    padding: 22px 28px 18px;
    position: relative;
    overflow: hidden;
}
.page-header::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        0deg, transparent, transparent 30px,
        rgba(88,166,255,0.03) 30px, rgba(88,166,255,0.03) 31px
    );
}
.header-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px; color: #58a6ff;
    letter-spacing: 3px; text-transform: uppercase;
    margin-bottom: 6px;
}
.header-title {
    font-size: 26px; font-weight: 700; color: #ffffff;
    letter-spacing: -0.5px; line-height: 1;
}
.header-sub {
    font-size: 12px; color: #8b949e;
    margin-top: 4px; font-family: 'IBM Plex Mono', monospace;
}
.header-badge {
    display: inline-block;
    background: rgba(88,166,255,0.1);
    border: 1px solid rgba(88,166,255,0.3);
    color: #58a6ff;
    font-size: 9px; font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 2px; padding: 3px 10px;
    margin-top: 10px; margin-right: 6px;
    text-transform: uppercase;
}
.header-badge.green {
    background: rgba(63,185,80,0.1);
    border-color: rgba(63,185,80,0.3);
    color: #3fb950;
}
.header-badge.red {
    background: rgba(248,81,73,0.1);
    border-color: rgba(248,81,73,0.3);
    color: #f85149;
}

/* ── KPI CARDS ── */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1px;
    background: #21262d;
    border: 1px solid #21262d;
    margin: 0;
}
.kpi-card {
    background: #0d1117;
    padding: 18px 20px;
    position: relative;
}
.kpi-card::after {
    content: '';
    position: absolute; top: 0; left: 0; right: 0;
    height: 2px;
}
.kpi-card.blue::after { background: #58a6ff; }
.kpi-card.green::after { background: #3fb950; }
.kpi-card.red::after { background: #f85149; }
.kpi-card.orange::after { background: #d29922; }
.kpi-card.purple::after { background: #bc8cff; }

.kpi-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px; color: #8b949e;
    text-transform: uppercase; letter-spacing: 2px;
    margin-bottom: 8px;
}
.kpi-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 26px; font-weight: 600; color: #ffffff;
    line-height: 1; margin-bottom: 5px;
}
.kpi-delta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px; color: #3fb950;
}
.kpi-delta.down { color: #f85149; }

/* ── SECTION HEADER ── */
.sec-header {
    display: flex; align-items: center; gap: 10px;
    padding: 12px 20px;
    background: #0d1117;
    border-bottom: 1px solid #21262d;
    border-top: 1px solid #21262d;
}
.sec-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px; color: #8b949e;
    text-transform: uppercase; letter-spacing: 2px;
}
.sec-accent { width: 3px; height: 14px; background: #58a6ff; }

/* ── ALERT TABLE ── */
.alert-table-wrap {
    background: #0d1117;
    border: 1px solid #21262d;
}
.alert-thead {
    display: grid;
    grid-template-columns: 110px 70px 80px 90px 130px 80px 100px 1fr;
    gap: 0;
    background: #161b22;
    border-bottom: 1px solid #21262d;
    padding: 8px 16px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px; color: #8b949e;
    letter-spacing: 1.5px; text-transform: uppercase;
}
.alert-row {
    display: grid;
    grid-template-columns: 110px 70px 80px 90px 130px 80px 100px 1fr;
    gap: 0;
    padding: 10px 16px;
    border-bottom: 1px solid #161b22;
    font-size: 11px;
    font-family: 'IBM Plex Mono', monospace;
    align-items: center;
    transition: background 0.15s;
}
.alert-row:hover { background: #161b22; }
.alert-row.critical { border-left: 3px solid #f85149; }
.alert-row.high { border-left: 3px solid #d29922; }
.alert-row.medium { border-left: 3px solid #58a6ff; }
.alert-row.low { border-left: 3px solid #3fb950; }

.badge {
    display: inline-block;
    padding: 2px 8px;
    font-size: 9px; letter-spacing: 1px;
    font-family: 'IBM Plex Mono', monospace;
    text-transform: uppercase;
    border-radius: 2px;
}
.badge.critical { background: rgba(248,81,73,0.15); color: #f85149; border: 1px solid rgba(248,81,73,0.3); }
.badge.high { background: rgba(210,153,34,0.15); color: #d29922; border: 1px solid rgba(210,153,34,0.3); }
.badge.medium { background: rgba(88,166,255,0.15); color: #58a6ff; border: 1px solid rgba(88,166,255,0.3); }
.badge.low { background: rgba(63,185,80,0.15); color: #3fb950; border: 1px solid rgba(63,185,80,0.3); }
.badge.open { background: rgba(248,81,73,0.1); color: #f85149; border: 1px solid rgba(248,81,73,0.2); }
.badge.investigating { background: rgba(210,153,34,0.1); color: #d29922; border: 1px solid rgba(210,153,34,0.2); }
.badge.closed { background: rgba(63,185,80,0.1); color: #3fb950; border: 1px solid rgba(63,185,80,0.2); }

/* ── AI PANEL ── */
.ai-panel {
    background: #0d1117;
    border: 1px solid #21262d;
    border-top: 2px solid #58a6ff;
}
.ai-header {
    background: #161b22;
    padding: 10px 18px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px; color: #58a6ff;
    letter-spacing: 2px; text-transform: uppercase;
    border-bottom: 1px solid #21262d;
    display: flex; justify-content: space-between; align-items: center;
}
.chat-msg {
    padding: 14px 18px;
    border-bottom: 1px solid #161b22;
    font-size: 13px; line-height: 1.65; color: #c9d1d9;
}
.chat-query {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px; color: #58a6ff;
    letter-spacing: 1px; margin-bottom: 8px;
    text-transform: uppercase;
}
.chat-response { color: #c9d1d9; }

.query-chips { padding: 10px 18px 4px; }
.chip {
    display: inline-block;
    background: #161b22;
    border: 1px solid #21262d;
    color: #8b949e;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px; padding: 4px 12px;
    margin: 3px; cursor: pointer;
    border-radius: 2px;
    transition: all 0.2s;
}
.chip:hover { border-color: #58a6ff; color: #58a6ff; }

/* ── PLAYBOOK PANEL ── */
.playbook {
    background: #0d1117;
    border: 1px solid #21262d;
    border-top: 2px solid #f85149;
    padding: 0;
}
.playbook-title {
    background: #161b22;
    padding: 10px 18px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px; color: #f85149;
    letter-spacing: 2px;
    border-bottom: 1px solid #21262d;
}
.step {
    display: flex; gap: 12px; align-items: flex-start;
    padding: 12px 18px;
    border-bottom: 1px solid #161b22;
}
.step-num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px; color: #58a6ff;
    background: rgba(88,166,255,0.1);
    border: 1px solid rgba(88,166,255,0.2);
    padding: 2px 8px; min-width: 32px;
    text-align: center; flex-shrink: 0;
}
.step-text { font-size: 12px; color: #c9d1d9; line-height: 1.5; }
.step-label { font-size: 10px; color: #8b949e; font-family: 'IBM Plex Mono', monospace; }

/* ── MITRE TAGS ── */
.mitre-tag {
    display: inline-block;
    background: rgba(188,140,255,0.1);
    border: 1px solid rgba(188,140,255,0.25);
    color: #bc8cff;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px; letter-spacing: 1px;
    padding: 3px 10px; margin: 3px;
    border-radius: 2px; text-transform: uppercase;
}

/* ── FOOTER ── */
.footer {
    background: #0d1117;
    border-top: 1px solid #21262d;
    padding: 12px 28px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px; color: #484f58;
    display: flex; justify-content: space-between;
    letter-spacing: 1px;
}

/* ── PLOTLY FIX ── */
.js-plotly-plot .plotly { background: transparent !important; }
</style>
""", unsafe_allow_html=True)


# ── SYNTHETIC DATA ───────────────────────────────────────────────────────────
np.random.seed(42)
random.seed(42)

attack_types = ["Card Testing", "Bot Attack", "ATO", "Large Fraud", "Velocity Abuse"]
attack_weights = [0.30, 0.25, 0.20, 0.15, 0.10]
severities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
sev_weights = [0.15, 0.25, 0.35, 0.25]
statuses = ["OPEN", "INVESTIGATING", "CLOSED"]
status_weights = [0.4, 0.35, 0.25]

def gen_alerts(n=87):
    rows = []
    base_time = datetime.now() - timedelta(hours=8)
    for i in range(n):
        sev = random.choices(severities, sev_weights)[0]
        atk = random.choices(attack_types, attack_weights)[0]
        amt = round(random.uniform(1, 15), 2) if atk == "Card Testing" else round(random.uniform(50, 800), 2)
        t = base_time + timedelta(minutes=random.randint(0, 480))
        rows.append({
            "alert_id": f"FRD-{1000+i}",
            "time": t.strftime("%H:%M:%S"),
            "amount": f"₹{amt}",
            "amount_raw": amt,
            "attack_type": atk,
            "severity": sev,
            "status": random.choices(statuses, status_weights)[0],
            "v14_score": round(random.uniform(0.6, 0.99), 3),
            "fraud_prob": round(random.uniform(0.55, 0.999), 3),
        })
    return rows

alerts = gen_alerts(87)

# Hourly fraud data (based on Krish's actual findings)
hours = list(range(24))
fraud_counts = [2,1,1,0,1,2,3,4,5,6,5,4,5,6,7,8,9,10,12,15,14,11,8,5]
normal_counts = [120,90,70,60,80,150,300,480,520,510,490,505,530,520,510,490,480,470,450,430,410,380,320,200]

# Amount bucket data
amount_buckets = ["₹0-10", "₹10-50", "₹50-200", "₹200-500", "₹500+"]
fraud_by_amount = [49, 18, 12, 6, 3]  # fraud peaks in small amounts per Krish's findings

# Model comparison
models = ["Random Forest", "XGBoost"]
recall_vals = [81, 89]
precision_vals = [81, 73]
f1_vals = [81, 80]

# Severity counts
sev_counts = {"CRITICAL": sum(1 for a in alerts if a["severity"]=="CRITICAL"),
              "HIGH": sum(1 for a in alerts if a["severity"]=="HIGH"),
              "MEDIUM": sum(1 for a in alerts if a["severity"]=="MEDIUM"),
              "LOW": sum(1 for a in alerts if a["severity"]=="LOW")}


# ── PLOTLY THEME ─────────────────────────────────────────────────────────────
PLOT_BG = "#0d1117"
GRID_COLOR = "#21262d"
TEXT_COLOR = "#8b949e"
FONT = "IBM Plex Mono"

def base_layout(title=""):
    return dict(
        paper_bgcolor=PLOT_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(family=FONT, color=TEXT_COLOR, size=10),
        title=dict(text=title, font=dict(size=11, color="#c9d1d9"), x=0, pad=dict(l=4)),
        margin=dict(l=40, r=20, t=36, b=36),
        xaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, tickfont=dict(size=9)),
        yaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, tickfont=dict(size=9)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9)),
    )


# ── GROQ CLIENT ──────────────────────────────────────────────────────────────
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    groq_ok = True
except Exception:
    groq_ok = False

fraud_context = """
UPI Fraud Detection System Analysis Summary:
- Dataset: 284,807 transactions, 492 confirmed fraud (0.17% rate)
- Model: XGBoost — 89% fraud recall, 73% precision, 80% F1
- Comparison: Random Forest scored 81% recall/precision/F1
- SMOTE used on training data only to handle class imbalance
- Key findings:
  * 50% of fraud transactions are under ₹9.25 (card testing / probing behavior)
  * Fraud peaks at hour 21 (9 PM) — bots active during human leisure hours
  * Fraud has NO circadian rhythm (unlike normal human spending)
  * V14 is strongest predictor (22% feature importance), V10 (11%), V4 (11%)
  * Amount alone is a WEAK fraud signal — fraudsters deliberately keep amounts tiny
  * False positives: only 18 normal transactions wrongly flagged
  * 87 out of 98 fraud cases in test set correctly flagged (11 missed)
  * Average fraud amount ₹122 vs ₹88 for normal transactions
- Business impact: Model potentially prevents ₹10,614 loss per test batch
- MITRE techniques observed: T1078 (Account Takeover), T1110 (Brute Force), T1133 (Card Testing)
"""

def ask_analyst(question, history):
    messages = [{"role": "system", "content": f"""You are a senior fraud intelligence analyst at a fintech SOC.
Answer questions about UPI fraud detection with precision and business context.
Use data from the analysis below. Be concise (3-4 sentences). Use numbers when available.

{fraud_context}"""}]
    for q, a in history[-3:]:
        messages.append({"role": "user", "content": q})
        messages.append({"role": "assistant", "content": a})
    messages.append({"role": "user", "content": question})
    
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=220
    )
    return resp.choices[0].message.content


# ══════════════════════════════════════════════════════════════════════════════
# ── RENDER ───────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

# TOP BAR
now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
st.markdown(f"""
<div class="topbar">
    <div class="topbar-left">
        <span class="topbar-brand">▣ FRAUDSOC TERMINAL v2.0</span>
        <span>|</span>
        <span>XGBOOST + GROQ LLM</span>
        <span>|</span>
        <span>284,807 TXN ANALYZED</span>
        <span>|</span>
        <span style="color:#f85149;">FRAUD RATE: 0.17%</span>
    </div>
    <div class="status-live">
        <span class="status-dot"></span>
        <span>LIVE &nbsp;·&nbsp; {now}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# PAGE HEADER
st.markdown("""
<div class="page-header">
    <div class="header-eyebrow">UPI FRAUD INTELLIGENCE SYSTEM · SECURITY OPERATIONS CENTER</div>
    <div class="header-title">FraudSOC Terminal</div>
    <div class="header-sub">Built on Krish Kamboj's XGBoost Fraud Detection Model &nbsp;·&nbsp; Extended with SOC Operations Layer</div>
    <div>
        <span class="header-badge green">● MODEL LIVE</span>
        <span class="header-badge">XGBOOST 89% RECALL</span>
        <span class="header-badge red">87 ALERTS ACTIVE</span>
        <span class="header-badge">GROQ AI ANALYST</span>
    </div>
</div>
""", unsafe_allow_html=True)

# KPI ROW
st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-card blue">
        <div class="kpi-label">Total Transactions</div>
        <div class="kpi-value">284,807</div>
        <div class="kpi-delta">▲ Full Dataset</div>
    </div>
    <div class="kpi-card red">
        <div class="kpi-label">Fraud Detected</div>
        <div class="kpi-value">492</div>
        <div class="kpi-delta down">▲ 0.17% Rate</div>
    </div>
    <div class="kpi-card green">
        <div class="kpi-label">Model Recall</div>
        <div class="kpi-value">89%</div>
        <div class="kpi-delta">▲ XGBoost</div>
    </div>
    <div class="kpi-card orange">
        <div class="kpi-label">Active Alerts</div>
        <div class="kpi-value">{sev_counts['CRITICAL'] + sev_counts['HIGH']}</div>
        <div class="kpi-delta down">▲ Crit+High</div>
    </div>
    <div class="kpi-card purple">
        <div class="kpi-label">Fraud Prevented</div>
        <div class="kpi-value">₹10,614</div>
        <div class="kpi-delta">▲ Per Test Batch</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── CHARTS ROW 1 ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="sec-header">
    <div class="sec-accent"></div>
    <div class="sec-title">Analytics Overview</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 2])

with col1:
    # Fraud by hour line chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours, y=normal_counts,
        name="Normal", mode="lines",
        line=dict(color="#21262d", width=1.5),
        fill="tozeroy", fillcolor="rgba(33,38,45,0.3)"
    ))
    fig.add_trace(go.Scatter(
        x=hours, y=[v*12 for v in fraud_counts],
        name="Fraud (×12 scaled)", mode="lines",
        line=dict(color="#f85149", width=2),
        fill="tozeroy", fillcolor="rgba(248,81,73,0.08)"
    ))
    fig.add_vline(x=21, line_width=1, line_dash="dot", line_color="#d29922",
                  annotation_text="PEAK 9PM", annotation_font_size=9,
                  annotation_font_color="#d29922")
    layout = base_layout("FRAUD ACTIVITY BY HOUR OF DAY")
    layout["xaxis"]["tickvals"] = list(range(0, 24, 3))
    layout["xaxis"]["ticktext"] = ["00:00","03:00","06:00","09:00","12:00","15:00","18:00","21:00"]
    layout["height"] = 220
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with col2:
    # Severity donut
    fig2 = go.Figure(go.Pie(
        labels=list(sev_counts.keys()),
        values=list(sev_counts.values()),
        hole=0.6,
        marker=dict(colors=["#f85149","#d29922","#58a6ff","#3fb950"],
                    line=dict(color="#080c10", width=2)),
        textfont=dict(family=FONT, size=9),
        textinfo="label+percent",
        showlegend=False,
    ))
    layout2 = base_layout("ALERT SEVERITY DISTRIBUTION")
    layout2["height"] = 220
    layout2.pop("xaxis", None); layout2.pop("yaxis", None)
    fig2.update_layout(**layout2)
    fig2.add_annotation(text=f"<b>{len(alerts)}</b><br><span style='font-size:9px'>ALERTS</span>",
                        x=0.5, y=0.5, showarrow=False,
                        font=dict(size=14, color="#ffffff", family=FONT))
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

# ── CHARTS ROW 2 ─────────────────────────────────────────────────────────────
col3, col4 = st.columns([2, 3])

with col3:
    # Fraud by amount bucket
    fig3 = go.Figure(go.Bar(
        x=amount_buckets, y=fraud_by_amount,
        marker=dict(
            color=["#f85149","#d29922","#58a6ff","#3fb950","#bc8cff"],
            line=dict(color="#080c10", width=1)
        ),
        text=fraud_by_amount, textposition="outside",
        textfont=dict(size=9, color="#8b949e", family=FONT)
    ))
    layout3 = base_layout("FRAUD CASES BY AMOUNT RANGE")
    layout3["height"] = 200
    layout3["yaxis"]["showgrid"] = False
    fig3.update_layout(**layout3)
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

with col4:
    # Model comparison grouped bar
    fig4 = go.Figure()
    metrics = ["Recall", "Precision", "F1 Score"]
    rf_vals = [81, 81, 81]
    xgb_vals = [89, 73, 80]
    x = np.arange(3)
    fig4.add_trace(go.Bar(name="Random Forest", x=metrics, y=rf_vals,
                          marker_color="#21262d", marker_line=dict(color="#58a6ff", width=1),
                          text=rf_vals, textposition="outside",
                          textfont=dict(size=9, family=FONT, color="#8b949e")))
    fig4.add_trace(go.Bar(name="XGBoost ✓", x=metrics, y=xgb_vals,
                          marker_color="#58a6ff", marker_line=dict(color="#58a6ff", width=0),
                          text=xgb_vals, textposition="outside",
                          textfont=dict(size=9, family=FONT, color="#58a6ff")))
    layout4 = base_layout("MODEL PERFORMANCE COMPARISON (%)")
    layout4["height"] = 200
    layout4["barmode"] = "group"
    layout4["yaxis"]["range"] = [0, 105]
    layout4["yaxis"]["showgrid"] = False
    fig4.update_layout(**layout4)
    st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

# ── ALERT QUEUE ───────────────────────────────────────────────────────────────
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
<div class="sec-header">
    <div class="sec-accent" style="background:#f85149"></div>
    <div class="sec-title">Live Alert Queue</div>
    <div style="margin-left:auto; font-family:IBM Plex Mono; font-size:9px; color:#f85149">87 ACTIVE INCIDENTS</div>
</div>
""", unsafe_allow_html=True)

# Filter controls
fcol1, fcol2, fcol3, _ = st.columns([1.5, 1.5, 1.5, 5])
with fcol1:
    filter_sev = st.selectbox("SEVERITY", ["ALL"] + severities, key="fsev",
                               label_visibility="collapsed")
with fcol2:
    filter_atk = st.selectbox("ATTACK TYPE", ["ALL"] + attack_types, key="fatk",
                               label_visibility="collapsed")
with fcol3:
    filter_status = st.selectbox("STATUS", ["ALL"] + statuses, key="fstat",
                                  label_visibility="collapsed")

filtered = [a for a in alerts
            if (filter_sev == "ALL" or a["severity"] == filter_sev)
            and (filter_atk == "ALL" or a["attack_type"] == filter_atk)
            and (filter_status == "ALL" or a["status"] == filter_status)]

# Table
table_html = """
<div class="alert-table-wrap">
<div class="alert-thead">
    <div>ALERT ID</div><div>TIME</div><div>AMOUNT</div>
    <div>V14 SCORE</div><div>ATTACK TYPE</div>
    <div>SEVERITY</div><div>STATUS</div><div>FRAUD PROB</div>
</div>
"""
for a in filtered[:20]:
    sev_lower = a["severity"].lower()
    stat_lower = a["status"].lower()
    prob_color = "#f85149" if a["fraud_prob"] > 0.85 else "#d29922" if a["fraud_prob"] > 0.7 else "#8b949e"
    table_html += f"""
<div class="alert-row {sev_lower}">
    <div style="color:#58a6ff">{a['alert_id']}</div>
    <div>{a['time']}</div>
    <div style="color:#c9d1d9">{a['amount']}</div>
    <div style="color:#8b949e">{a['v14_score']}</div>
    <div style="color:#c9d1d9">{a['attack_type']}</div>
    <div><span class="badge {sev_lower}">{a['severity']}</span></div>
    <div><span class="badge {stat_lower}">{a['status']}</span></div>
    <div style="color:{prob_color}; font-weight:600">{a['fraud_prob']:.1%}</div>
</div>"""

if not filtered:
    table_html += '<div style="padding:20px; text-align:center; color:#484f58; font-family:IBM Plex Mono; font-size:11px;">NO ALERTS MATCH FILTER</div>'

table_html += "</div>"
st.markdown(table_html, unsafe_allow_html=True)

if len(filtered) > 20:
    st.markdown(f'<div style="font-family:IBM Plex Mono; font-size:9px; color:#484f58; padding:8px 16px; background:#0d1117; border:1px solid #21262d; border-top:none;">'
                f'SHOWING 20 OF {len(filtered)} ALERTS</div>', unsafe_allow_html=True)

# ── INCIDENT RESPONSE + MITRE ─────────────────────────────────────────────────
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
col_play, col_mitre = st.columns([1, 1])

with col_play:
    st.markdown("""
<div class="playbook">
    <div class="playbook-title">▶ INCIDENT RESPONSE PLAYBOOK — CARD TESTING ATTACK</div>
    <div class="step">
        <div class="step-num">01</div>
        <div>
            <div class="step-text">Immediately block IP range / device fingerprint associated with micro-transaction burst</div>
            <div class="step-label">ACTION: Network / WAF Rule</div>
        </div>
    </div>
    <div class="step">
        <div class="step-num">02</div>
        <div>
            <div class="step-text">Flag all transactions under ₹9.25 from same source within 60-minute window</div>
            <div class="step-label">ACTION: Rule Engine Update</div>
        </div>
    </div>
    <div class="step">
        <div class="step-num">03</div>
        <div>
            <div class="step-text">Escalate to Tier-2 analyst if V14 score exceeds 0.80 on any flagged transaction</div>
            <div class="step-label">ACTION: Human Escalation</div>
        </div>
    </div>
    <div class="step">
        <div class="step-num">04</div>
        <div>
            <div class="step-text">Issue temporary hold on affected card/UPI handle — notify user via SMS</div>
            <div class="step-label">ACTION: Account Protection</div>
        </div>
    </div>
    <div class="step">
        <div class="step-num">05</div>
        <div>
            <div class="step-text">Document incident, update XGBoost training queue with confirmed fraud label</div>
            <div class="step-label">ACTION: Model Feedback Loop</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

with col_mitre:
    st.markdown("""
<div style="background:#0d1117; border:1px solid #21262d; border-top:2px solid #bc8cff; height:100%;">
    <div style="background:#161b22; padding:10px 18px; font-family:IBM Plex Mono; font-size:10px; color:#bc8cff; letter-spacing:2px; border-bottom:1px solid #21262d;">
        ▶ MITRE ATT&CK TECHNIQUES OBSERVED
    </div>
    <div style="padding:14px 18px;">
        <div style="margin-bottom:12px;">
            <span class="mitre-tag">T1078</span>
            <div style="font-size:12px; color:#c9d1d9; margin-top:4px;">Valid Accounts — Account Takeover (ATO)</div>
            <div style="font-size:10px; color:#8b949e; font-family:IBM Plex Mono;">Adversaries obtain valid credentials to hijack UPI handles</div>
        </div>
        <div style="margin-bottom:12px;">
            <span class="mitre-tag">T1110</span>
            <div style="font-size:12px; color:#c9d1d9; margin-top:4px;">Brute Force — Credential Stuffing</div>
            <div style="font-size:10px; color:#8b949e; font-family:IBM Plex Mono;">Automated credential testing against payment APIs</div>
        </div>
        <div style="margin-bottom:12px;">
            <span class="mitre-tag">T1133</span>
            <div style="font-size:12px; color:#c9d1d9; margin-top:4px;">Card Testing — Micro Transaction Probing</div>
            <div style="font-size:10px; color:#8b949e; font-family:IBM Plex Mono;">Small transactions (sub ₹9.25) to verify card validity</div>
        </div>
        <div style="margin-bottom:12px;">
            <span class="mitre-tag">T1496</span>
            <div style="font-size:12px; color:#c9d1d9; margin-top:4px;">Resource Hijacking — Bot-Driven Velocity</div>
            <div style="font-size:10px; color:#8b949e; font-family:IBM Plex Mono;">High-frequency automated transactions bypassing rate limits</div>
        </div>
        <div style="padding:10px 0 4px;">
            <div style="font-family:IBM Plex Mono; font-size:9px; color:#484f58; letter-spacing:1px;">KEY FRAUD FEATURE SIGNALS</div>
        </div>
        <div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:6px;">
            <div style="background:#161b22; border:1px solid #21262d; padding:5px 12px; font-family:IBM Plex Mono; font-size:10px; color:#58a6ff;">V14 — 22%</div>
            <div style="background:#161b22; border:1px solid #21262d; padding:5px 12px; font-family:IBM Plex Mono; font-size:10px; color:#58a6ff;">V10 — 11%</div>
            <div style="background:#161b22; border:1px solid #21262d; padding:5px 12px; font-family:IBM Plex Mono; font-size:10px; color:#58a6ff;">V4 — 11%</div>
            <div style="background:#161b22; border:1px solid #21262d; padding:5px 12px; font-family:IBM Plex Mono; font-size:10px; color:#8b949e;">V17 — 8%</div>
            <div style="background:#161b22; border:1px solid #21262d; padding:5px 12px; font-family:IBM Plex Mono; font-size:10px; color:#8b949e;">V12 — 7%</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── AI ANALYST ────────────────────────────────────────────────────────────────
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
st.markdown("""
<div class="sec-header">
    <div class="sec-accent" style="background:#3fb950"></div>
    <div class="sec-title">AI Fraud Analyst — Groq LLM</div>
    <div style="margin-left:auto; font-family:IBM Plex Mono; font-size:9px; color:#3fb950">● ONLINE · llama-3.1-8b-instant</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="ai-panel">
    <div class="ai-header">
        <span>▶ INTELLIGENCE QUERY INTERFACE</span>
        <span style="color:#8b949e; font-size:9px">Ask anything about the fraud data</span>
    </div>
    <div class="query-chips">
        <span class="chip">Why fraud peaks at 9 PM?</span>
        <span class="chip">Should we block sub ₹10 transactions?</span>
        <span class="chip">Why is V14 so important?</span>
        <span class="chip">XGBoost vs Random Forest — which to deploy?</span>
        <span class="chip">How to reduce false positives?</span>
        <span class="chip">What is SMOTE?</span>
    </div>
</div>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

query = st.text_input("", placeholder="▶  Enter intelligence query...", key="query_input")

if query:
    if groq_ok:
        with st.spinner("Analyzing..."):
            answer = ask_analyst(query, st.session_state.chat_history)
        st.session_state.chat_history.append((query, answer))
    else:
        st.session_state.chat_history.append((query,
            "⚠ GROQ_API_KEY not found in Streamlit secrets. Add it via Settings → Secrets → GROQ_API_KEY = 'your_key'"))

for q, a in reversed(st.session_state.chat_history):
    st.markdown(f"""
<div class="chat-msg">
    <div class="chat-query">▶ {q}</div>
    <div class="chat-response">{a}</div>
</div>
""", unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
st.markdown(f"""
<div class="footer">
    <span>FRAUDSOC TERMINAL v2.0 &nbsp;·&nbsp; BUILT ON KRISH KAMBOJ'S XGBOOST FRAUD DETECTION MODEL &nbsp;·&nbsp; EXTENDED WITH SOC OPERATIONS LAYER</span>
    <span>{now} IST</span>
</div>
""", unsafe_allow_html=True)
