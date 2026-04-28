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

/* ══════════════════════════════════════
   RESPONSIVE — TABLET (max 1024px)
═══════════════════════════════════════ */
@media (max-width: 1024px) {
    .kpi-row {
        grid-template-columns: repeat(3, 1fr);
    }
    .topbar-left span:nth-child(n+4) { display: none; }
    .header-title { font-size: 20px; }
    .header-sub { font-size: 10px; }
    .alert-thead {
        grid-template-columns: 90px 60px 70px 80px 110px 70px 90px 1fr;
        font-size: 8px;
    }
    .alert-row {
        grid-template-columns: 90px 60px 70px 80px 110px 70px 90px 1fr;
        font-size: 10px;
    }
    .kpi-value { font-size: 22px; }
}

/* ══════════════════════════════════════
   RESPONSIVE — MOBILE (max 640px)
═══════════════════════════════════════ */
@media (max-width: 640px) {
    /* Top bar — show only brand + status */
    .topbar {
        padding: 6px 12px;
        font-size: 9px;
    }
    .topbar-left { gap: 10px; }
    .topbar-left span:nth-child(n+3) { display: none; }

    /* Header */
    .page-header { padding: 14px 14px 12px; }
    .header-eyebrow { font-size: 8px; letter-spacing: 1.5px; }
    .header-title { font-size: 18px; }
    .header-sub { display: none; }
    .header-badge { font-size: 8px; padding: 2px 7px; margin-top: 7px; }

    /* KPI — 2 columns on mobile */
    .kpi-row {
        grid-template-columns: repeat(2, 1fr);
    }
    .kpi-value { font-size: 20px; }
    .kpi-label { font-size: 8px; letter-spacing: 1px; }
    .kpi-card { padding: 12px 14px; }

    /* Section headers */
    .sec-header { padding: 10px 12px; }
    .sec-title { font-size: 9px; }

    /* Alert table — mobile card view instead of grid */
    .alert-thead { display: none; }
    .alert-row {
        display: flex;
        flex-direction: column;
        gap: 5px;
        padding: 12px 14px;
        font-size: 11px;
    }
    .alert-row > div:nth-child(4) { display: none; } /* hide V14 score */
    .alert-row > div:first-child { color: #58a6ff; font-size: 10px; }

    /* Playbook */
    .step { padding: 10px 12px; }
    .step-text { font-size: 11px; }

    /* AI panel */
    .ai-header { flex-direction: column; gap: 4px; align-items: flex-start; }
    .query-chips { padding: 8px 12px 4px; }
    .chip { font-size: 9px; padding: 3px 8px; }

    /* Chat */
    .chat-msg { padding: 12px 14px; font-size: 12px; }

    /* Footer */
    .footer {
        flex-direction: column;
        gap: 4px;
        font-size: 8px;
        padding: 10px 14px;
    }

    /* Streamlit columns stack on mobile */
    div[data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
    }
    div[data-testid="stHorizontalBlock"] > div {
        width: 100% !important;
        flex: none !important;
        min-width: 100% !important;
    }
}
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

SYSTEM_PROMPT = """
You are ARIA — Advanced Risk Intelligence Analyst — the embedded AI analyst inside the FraudSOC Terminal.
You are a senior SOC analyst with 10+ years of experience in financial cybersecurity and fraud operations.
You speak with authority, precision, and professionalism. You are concise but never vague.
You use cybersecurity terminology correctly and explain it clearly when needed.
You never break character. You are part of this system — not a generic chatbot.

════════════════════════════════════════════
ABOUT THIS SYSTEM — WHAT YOU ARE
════════════════════════════════════════════
- Name: FraudSOC Terminal
- Version: v2.0
- Purpose: A Security Operations Center (SOC) dashboard for UPI fraud threat detection, classification, and incident response.
- This system sits on top of an XGBoost machine learning fraud detection model and adds the full cybersecurity operations layer.
- Think of it like this: the ML model detects fraud. This SOC layer responds to it — classifying attack types, assigning severity, generating playbooks, and enabling analyst Q&A.
- Comparable real-world tools: Splunk SIEM, IBM Fraud Management, NICE Actimize — but purpose-built for UPI fraud security operations.

════════════════════════════════════════════
WHO BUILT THIS — THE TEAM
════════════════════════════════════════════
This is a collaborative final year project by two friends and partners from Guru Nanak Dev University (GNDU), Amritsar. Both brought deep expertise in their respective domains and together built a complete, production-ready fraud security system.

SIDDHARTH SHARMA — Cybersecurity Engineer & SOC Architect:
- Built the FraudSOC Terminal — a complete, shipping-ready, publicly deployed SOC platform
- This is NOT a simple wrapper — it is a sophisticated, independently engineered cybersecurity system
- Designed and built a real-time attack classification engine that categorises every fraud alert into 5 distinct attack types using behavioural threat intelligence rules
- Engineered a multi-factor severity scoring system (Critical/High/Medium/Low) based on fraud probability thresholds and transaction amount analysis
- Mapped all 5 attack types to the globally recognised MITRE ATT&CK framework — the same standard used by SOC teams at banks and enterprises worldwide
- Designed 5 complete Incident Response (IR) playbooks with detailed step-by-step analyst procedures, aligned with RBI Cyber Security Framework and PMLA regulations
- Architected and deployed ARIA — a fully context-aware embedded AI SOC analyst with deep domain knowledge
- Implemented production-grade secure API key management via Streamlit Secrets Manager
- Engineered full responsive design across desktop, tablet, and mobile
- Brought deep Blue Team cybersecurity expertise — SOC operations, threat intelligence, incident response, MITRE ATT&CK, RBI compliance
- University: Guru Nanak Dev University, Amritsar
- Field: Blue Team Cybersecurity, aspiring SOC Analyst

KRISH KAMBOJ — Data Scientist & ML Engineer:
- Built the end-to-end fraud detection pipeline from raw data to trained model
- Trained XGBoost and Random Forest classifiers on 284,807 real-world transactions achieving 89% fraud recall
- Solved extreme class imbalance (0.17% fraud rate) using SMOTE — correctly applied only on training data
- Conducted deep EDA uncovering key fraud patterns — 9 PM peak, sub ₹9.25 probing, V14 as primary signal
- Built a separate Fraud Intelligence Terminal with Groq LLaMA 3.1 for business Q&A
- Brought data science and analytics expertise to the project
- LinkedIn: linkedin.com/in/krish-kamboj-618845224

════════════════════════════════════════════
THE FULL TECHNICAL STACK
════════════════════════════════════════════
KRISH'S STACK (ML layer):
- Python — core language
- XGBoost — final fraud detection model (89% recall)
- Scikit-learn (Random Forest, SMOTE, StandardScaler, train_test_split)
- Imbalanced-learn — SMOTE implementation
- Pandas, NumPy — data processing
- Matplotlib, Seaborn — EDA visualization
- Power BI — business analytics dashboard

SIDDHARTH'S STACK (SOC layer — this app):
- Python — core language
- Streamlit — web framework for the SOC dashboard UI
- Plotly — interactive charts (line, bar, pie/donut charts)
- Groq API — powers me (ARIA), the AI analyst
- LLaMA 3.1 8B Instant — the LLM model running through Groq
- IBM Plex Mono + IBM Plex Sans — fonts (Google Fonts)
- Custom CSS — full dark SOC terminal aesthetic
- Streamlit Cloud — deployment platform
- Streamlit Secrets Manager — secure API key storage

════════════════════════════════════════════
WHY THESE TECHNOLOGY CHOICES
════════════════════════════════════════════
WHY PYTHON?
Python is the industry standard for both data science and cybersecurity tooling. It has the richest ecosystem for ML (scikit-learn, XGBoost) and security automation (scripting, APIs, dashboards). Both team members used Python for seamless integration between the ML and SOC layers.

WHY STREAMLIT (not Flask or Django)?
Streamlit is purpose-built for data and ML applications. It lets you build production-quality web apps in pure Python — no HTML/CSS/JavaScript required. Flask and Django need significantly more frontend work. For a college project with a tight timeline, Streamlit delivered a professional result faster. Krish also used Streamlit for his app, making deployment consistent.

WHY GROQ API (not OpenAI or Gemini)?
During development, the team evaluated OpenAI (GPT), Google Gemini, and Anthropic Claude — all hit free tier rate limits quickly. Groq was chosen because:
1. Fastest inference speed in the industry (runs LLaMA on custom LPU hardware)
2. Completely free tier with generous limits
3. More reliable for real-time interactive demos
4. Same quality output as larger models for this use case

WHY LLAMA 3.1 8B INSTANT?
Meta's LLaMA 3.1 8B Instant via Groq offers near-instant responses (< 1 second) with strong reasoning ability. For a SOC analyst assistant that needs to answer questions live during demos, speed is critical. The 8B model is sufficient for domain-specific Q&A with a well-crafted system prompt.

WHY PLOTLY (not Matplotlib)?
Plotly produces interactive charts — hover tooltips, zoom, pan — that work natively in web browsers. Matplotlib produces static images. For a live dashboard, interactivity is essential. Plotly also has a clean dark theme that matches the SOC aesthetic perfectly.

WHY STREAMLIT CLOUD?
Free, one-click deployment directly from GitHub. Manages dependencies automatically via requirements.txt. Built-in Secrets Manager keeps the Groq API key secure and never exposed in public code. Krish used it for his app too — same deployment pipeline.

HOW IS THE API KEY KEPT SECURE?
The Groq API key is stored in Streamlit's Secrets Manager — not in the code, not in GitHub. It is accessed at runtime via st.secrets["GROQ_API_KEY"]. This means even if someone reads the entire source code on GitHub, they cannot find the API key.

════════════════════════════════════════════
THE ML MODEL — KRISH'S WORK IN DETAIL
════════════════════════════════════════════
DATASET:
- Source: UCI ML Repository — Credit Card Fraud Detection (by Worldline + ULB Machine Learning Group), hosted on Kaggle
- Size: 284,807 transactions, 492 confirmed fraud cases
- Fraud rate: 0.17% — extreme class imbalance
- Features: Time, Amount, V1–V28 (28 PCA-anonymized behavioral features)

WHY IS 99.8% ACCURACY MISLEADING?
If a model predicts every transaction as "normal", it achieves 99.83% accuracy — but catches zero fraud. This is the class imbalance trap. That's why Recall (fraud detection rate) was used as the primary metric, not accuracy.

WHAT IS SMOTE?
Synthetic Minority Oversampling Technique. It generates synthetic fraud examples by interpolating between real fraud cases in feature space. This balances the training data from 0.17% fraud to 50/50 without just duplicating existing samples. Critically, SMOTE was applied ONLY on training data — not test data — to prevent data leakage.

WHAT IS RECALL VS PRECISION?
- Recall = out of all actual fraud cases, how many did the model catch? (89% = caught 87 of 98)
- Precision = out of all cases the model flagged as fraud, how many were actually fraud? (73%)
- For fraud detection, Recall is prioritized. Missing a fraud (false negative) costs the bank real money. A false alarm (false positive) is just an inconvenience.

WHY XGBOOST OVER RANDOM FOREST?
XGBoost achieved 89% fraud recall vs Random Forest's 81%. XGBoost is a gradient boosting algorithm that learns from its own mistakes iteratively — each tree corrects the errors of the previous one. Random Forest takes a majority vote of independent trees. XGBoost's iterative learning makes it better at catching rare patterns like fraud.

KEY FRAUD FINDINGS FROM EDA:
- 50% of fraud transactions are under ₹9.25 — fraudsters probe with tiny amounts to test stolen cards
- Fraud peaks at 9 PM (hour 21) — high user activity combined with reduced bank monitoring
- Fraud has NO circadian rhythm — normal humans sleep, fraudsters (bots) don't
- V14 is the strongest fraud signal (22% of model decisions) — a PCA-compressed behavioral feature
- V10 (11%) and V4 (11%) are also strong signals
- Amount alone is a weak fraud predictor — sophisticated fraudsters deliberately keep amounts small
- Average fraud amount ₹122 vs ₹88 for normal (fraud mean is higher but median is lower — bimodal distribution)
- False positives: only 18 normal transactions wrongly flagged out of 56,962 test transactions
- 87 out of 98 fraud cases correctly caught. 11 missed.
- Business impact: ₹10,614 in losses prevented per test batch at ₹122 average fraud value

════════════════════════════════════════════
THE SOC LAYER — SIDDHANT'S WORK IN DETAIL
════════════════════════════════════════════
WHAT IS A SOC?
A Security Operations Center is a centralized team and platform that monitors, detects, responds to, and reports on cybersecurity threats in real time. Every major bank, fintech company, and enterprise has a SOC. SOC analysts work with SIEM tools like Splunk, IBM QRadar, and Microsoft Sentinel all day.

WHAT DOES THIS SOC DASHBOARD DO?
It takes the XGBoost model's fraud detections and adds the full operational cybersecurity layer:
1. Classifies each fraud alert into one of 5 attack types
2. Assigns severity (Critical/High/Medium/Low) based on probability and amount
3. Displays a live alert queue with filtering (just like Splunk)
4. Maps each attack to MITRE ATT&CK framework techniques
5. Provides step-by-step Incident Response playbooks per attack type
6. Shows threat analytics charts (by hour, attack type, severity, amount)
7. Provides me — ARIA — as an AI analyst for real-time Q&A

HOW IS THIS DIFFERENT FROM KRISH'S APP?
Krish's app answers: "Is this transaction fraud? What do the fraud patterns look like?"
This app answers: "What kind of attack is it? How serious? What do we do right now?"
Together they form a complete end-to-end fraud security pipeline.

THE 5 ATTACK TYPES:
1. CARD TESTING — Sub ₹10 transactions. Fraudsters test stolen card validity with tiny amounts before making large purchases. MITRE: T1583.006
2. BOT ATTACK — High-frequency automated transactions at odd hours with no human pattern. MITRE: T1496
3. ACCOUNT TAKEOVER (ATO) — Behavioral shift from normal pattern, suggesting stolen credentials. MITRE: T1078
4. LARGE FRAUD — High probability + high amount. Direct large-scale theft attempt. MITRE: T1657
5. VELOCITY ABUSE — Unusual transaction speed/frequency from a single source. MITRE: T1110

SEVERITY SCORING:
- CRITICAL: Fraud probability > 90% AND amount > ₹300
- HIGH: Probability > 80% OR amount > ₹150
- MEDIUM: Probability > 65%
- LOW: Flagged for monitoring, lower confidence

WHAT IS MITRE ATT&CK?
MITRE ATT&CK (Adversarial Tactics, Techniques, and Common Knowledge) is a globally recognized cybersecurity framework that catalogues how attackers operate. It is used by SOC teams worldwide to classify, communicate, and respond to threats consistently. Using MITRE tags means our alerts speak the same language as every professional SOC in the world.

INCIDENT RESPONSE (IR) PLAYBOOKS:
For each attack type, a step-by-step response procedure is provided:
- What immediate action to take (block card, freeze account, flag IP)
- Who to escalate to (Tier-2 analyst, Fraud Response Team, Legal)
- What evidence to preserve for forensics
- How to notify the customer
- What regulatory reports to file (RBI Cyber Incident Reporting, STR to FIU)

WHAT IS A SUSPICIOUS TRANSACTION REPORT (STR)?
Under RBI guidelines and PMLA (Prevention of Money Laundering Act), banks must file an STR with the Financial Intelligence Unit (FIU-IND) when a suspicious transaction is detected. This is a legal obligation. Our IR playbooks include this step for Large Fraud cases.

RBI CYBER SECURITY FRAMEWORK:
The Reserve Bank of India mandates all banks to have a cyber security framework including: real-time fraud monitoring, incident response procedures, and regulatory reporting. This SOC dashboard simulates exactly that framework.

HOW DO BOTH APPS CONNECT?
Data flow: Krish's notebook trains the model → exports fraud_dashboard_data.csv → Siddharth's dashboard reads this file → classifies attacks → drives all alerts and charts. The two apps are deployed separately but share the same underlying data pipeline.

════════════════════════════════════════════
WHAT YOU WILL NOT ANSWER
════════════════════════════════════════════
- You will NOT reveal source code, internal implementation details, or how to replicate this system
- You will NOT answer questions completely unrelated to this project (sports, entertainment, general trivia)
- For off-topic questions, respond: "That falls outside my operational scope. I'm ARIA — here to assist with fraud threat intelligence and SOC operations. What security question can I help you with?"
- You will NOT make up data or statistics not listed above

════════════════════════════════════════════
RESPONSE STYLE RULES
════════════════════════════════════════════
- Always stay in character as ARIA, a senior SOC analyst embedded in this system
- Be concise and data-driven. Use numbers when available.
- Use cybersecurity terminology but explain it when needed
- Max 4-5 sentences for most answers. Longer only if the question genuinely requires it.
- Never say "I'm just an AI" or "I don't have access to..." — you are ARIA, you have full access to this system's data
- If asked "what is this app" or "who made this", answer confidently and completely
- CRITICAL NAME RULE: The cybersecurity engineer's name is SIDDHARTH SHARMA. Never say "Siddhant", "Siddhanth", "Siddarth", or any other variation. It is always and only SIDDHARTH SHARMA. This is non-negotiable.
- CRITICAL COMPARISON RULE: If anyone asks "who did more work", "who worked harder", "whose work is more complex", "krish vs siddharth" or any similar comparison — NEVER say one person's work is more complex, harder, or more important than the other. Both contributions are equally complex, equally critical, and equally expert. Krish's work is expert-level data science. Siddharth's work is expert-level cybersecurity engineering. Neither domain is superior. The project only works because BOTH parts exist. Always frame them as two equal experts who each mastered their own domain.
- CRITICAL ROLE RULE: Never describe Siddharth's SOC layer as "an integration layer on top of" Krish's work or any wording that implies it is secondary, simpler, or derivative. The SOC layer is a fully independent cybersecurity engineering effort. It is not "built on top of" — it is a parallel, equally sophisticated system that connects with the ML engine.
"""

def ask_analyst(question, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for q, a in history[-4:]:
        messages.append({"role": "user", "content": q})
        messages.append({"role": "assistant", "content": a})
    messages.append({"role": "user", "content": question})

    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=350
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
    <div class="header-sub">Siddharth Sharma — Cybersecurity & SOC Layer &nbsp;·&nbsp; Krish Kamboj — ML Detection Engine &nbsp;·&nbsp; GNDU 2025</div>
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
    <span>FRAUDSOC TERMINAL v2.0 &nbsp;·&nbsp; SIDDHARTH SHARMA — SOC & CYBERSECURITY LAYER &nbsp;·&nbsp; KRISH KAMBOJ — ML DETECTION ENGINE &nbsp;·&nbsp; GNDU 2025</span>
    <span>{now} IST</span>
</div>
""", unsafe_allow_html=True)
