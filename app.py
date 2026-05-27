"""
TVET Labour Market Intelligence System
Complete Streamlit Dashboard — Redesigned Visual Layer
Author: Hope Subira
"""

import streamlit as st

# ============================================================
# PAGE CONFIGURATION 
# ============================================================
st.set_page_config(
    page_title="TVET Skills Intel",
    page_icon="assets/logo.png",  
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# REMAINING IMPORTS — after set_page_config
# ============================================================
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import io
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import base64
from collections import Counter
import tempfile
import os

# PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    st.warning("ReportLab not installed. PDF reports unavailable. Run: pip install reportlab")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Import custom modules
try:
    from src.data_loader import DataLoader
    from src.nlp_pipeline import NLPPipeline
    from src.gap_analyzer import GapAnalyzer
    from src.prioritizer import GapPrioritizer
    from src.course_generator import CourseGenerator
    MODULES_LOADED = True
except Exception as e:
    MODULES_LOADED = False
    MODULE_ERROR = str(e)

# ============================================================
# LOGO HELPER FUNCTIONS
# ============================================================
def get_logo_base64():
    """Load logo from assets folder and convert to base64"""
    logo_path = Path(__file__).parent / "assets" / "logo.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def get_favicon_base64():
    """Load logo as favicon"""
    logo_path = Path(__file__).parent / "assets" / "logo.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def logo_exists():
    """Check if logo file exists"""
    logo_path = Path(__file__).parent / "assets" / "logo.png"
    return logo_path.exists()


# ============================================================
# REDESIGNED STYLES
# ============================================================
def inject_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=DM+Serif+Display:ital@0;1&display=swap');

    /* ── TOKENS ─────────────────────────────────────────── */
    :root {
        --navy:        #1B2A4A;
        --navy-mid:    #243558;
        --navy-light:  #2E4A80;
        --gold:        #C9A84C;
        --gold-light:  #E8C96A;
        --gold-pale:   #FBF5E6;
        --danger:      #C0392B;
        --danger-bg:   #FDECEA;
        --warning:     #D97706;
        --warning-bg:  #FEF3C7;
        --success:     #047857;
        --success-bg:  #D1FAE5;
        --info:        #1D4ED8;
        --info-bg:     #DBEAFE;
        --bg:          #F4F6FA;
        --surface:     #FFFFFF;
        --surface-2:   #F8FAFC;
        --border:      #DDE3EF;
        --border-2:    #C8D0E0;
        --text-1:      #1B2A4A;
        --text-2:      #3D526B;
        --text-3:      #64748B;
        --text-4:      #94A3B8;
        --shadow-sm:  0 1px 3px rgba(27,42,74,.08);
        --shadow-md:  0 4px 12px rgba(27,42,74,.10);
        --shadow-lg:  0 10px 28px rgba(27,42,74,.12);
        --r-sm: 8px;  --r-md: 12px;  --r-lg: 16px;  --r-xl: 24px;
    }

    *, *::before, *::after { box-sizing: border-box; }

    html, body, .stApp {
        font-family: 'DM Sans', system-ui, sans-serif !important;
        background-color: var(--bg) !important;
        color: var(--text-1) !important;
        -webkit-font-smoothing: antialiased;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
        max-width: 1380px !important;
    }

    /* ── SIDEBAR ─────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: var(--navy) !important;
        border-right: none !important;
    }
    [data-testid="stSidebar"] * {
        font-family: 'DM Sans', system-ui, sans-serif !important;
        color: rgba(255,255,255,.85) !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: rgba(255,255,255,.85) !important;
        font-size: .9rem !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,.12) !important;
    }
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h2 {
        color: var(--gold-light) !important;
        font-family: 'DM Serif Display', serif !important;
    }

    .sidebar-logo {
        text-align: center;
        padding: 16px 12px 8px;
    }
    .sidebar-logo img {
        max-width: 160px;
        border-radius: var(--r-md);
    }
    .sidebar-logo-text {
        font-family: 'DM Serif Display', serif !important;
        font-size: 1.2rem;
        color: var(--gold-light) !important;
        margin-top: 8px;
        letter-spacing: .5px;
    }

    /* ── TYPOGRAPHY ──────────────────────────────────────── */
    h1 {
        font-family: 'DM Serif Display', serif !important;
        font-size: 1.75rem !important;
        font-weight: 400 !important;
        color: var(--navy) !important;
        line-height: 1.25 !important;
    }
    h2, h3 {
        font-family: 'DM Sans', system-ui, sans-serif !important;
        font-weight: 600 !important;
        color: var(--navy) !important;
    }
    h2 { font-size: 1.15rem !important; }
    h3 { font-size: 1rem !important; }

    /* ── PAGE HEADER BLOCK ───────────────────────────────── */
    .page-header {
        padding: 0 0 20px;
        border-bottom: 2px solid var(--border);
        margin-bottom: 28px;
    }
    .page-header-subtitle {
        color: var(--text-3);
        font-size: .9rem;
        margin-top: 4px;
    }
    .gold-line {
        height: 3px;
        background: linear-gradient(90deg, var(--gold), var(--gold-light), transparent);
        border-radius: 99px;
        margin: 16px 0;
    }

    /* ── KPI CARDS ───────────────────────────────────────── */
    .kpi-card {
        background: var(--surface);
        border-radius: var(--r-md);
        padding: 20px 22px;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-sm);
        position: relative;
        overflow: hidden;
        transition: box-shadow .25s, transform .25s;
        margin-bottom: 4px;
    }
    .kpi-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 3px;
    }
    .kpi-card.blue::before   { background: linear-gradient(90deg, #1B2A4A, #3B82F6); }
    .kpi-card.green::before  { background: linear-gradient(90deg, #047857, #10B981); }
    .kpi-card.amber::before  { background: linear-gradient(90deg, #92400E, #F59E0B); }
    .kpi-card.purple::before { background: linear-gradient(90deg, #5B21B6, #8B5CF6); }

    .kpi-icon {
        width: 42px; height: 42px;
        border-radius: var(--r-sm);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.15rem;
        margin-bottom: 12px;
    }
    .kpi-icon.blue   { background: #EFF6FF; color: #1D4ED8; }
    .kpi-icon.green  { background: var(--success-bg); color: var(--success); }
    .kpi-icon.amber  { background: var(--warning-bg); color: var(--warning); }
    .kpi-icon.purple { background: #EDE9FE; color: #6D28D9; }

    .kpi-value {
        font-family: 'DM Serif Display', serif;
        font-size: 2.4rem;
        font-weight: 400;
        color: var(--navy);
        line-height: 1;
        letter-spacing: -.5px;
    }
    .kpi-label {
        font-size: .82rem;
        color: var(--text-3);
        margin-top: 5px;
        font-weight: 500;
    }
    .kpi-delta {
        font-size: .72rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 99px;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        margin-top: 10px;
    }
    .kpi-delta.up     { background: var(--success-bg); color: var(--success); }
    .kpi-delta.neutral{ background: var(--border); color: var(--text-3); }

    /* ── SECTION CARDS ───────────────────────────────────── */
    .section-card-title {
        font-weight: 600;
        font-size: .95rem;
        color: var(--navy);
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 9px;
        padding-bottom: 12px;
        border-bottom: 1px solid var(--border);
    }
    .section-card-title i { color: var(--gold); }

    /* ── BADGES ──────────────────────────────────────────── */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 10px;
        border-radius: 99px;
        font-size: .72rem;
        font-weight: 700;
    }
    .badge-high    { background: var(--danger-bg);  color: var(--danger);  }
    .badge-medium  { background: var(--warning-bg); color: var(--warning); }
    .badge-low     { background: var(--success-bg); color: var(--success); }

    /* ── SKILL CHIPS ─────────────────────────────────────── */
    .chip {
        display: inline-block;
        background: #EFF6FF;
        color: var(--navy-light);
        border: 1px solid #BFDBFE;
        padding: 3px 10px;
        border-radius: 99px;
        font-size: .72rem;
        font-weight: 600;
        margin: 2px;
    }

    /* ── COURSE CARDS ────────────────────────────────────── */
    .course-card {
        background: var(--surface-2);
        border-radius: var(--r-md);
        padding: 16px 18px;
        border: 1px solid var(--border);
        margin-bottom: 12px;
        transition: border-color .2s, box-shadow .2s;
    }
    .course-card:hover {
        border-color: var(--gold);
        box-shadow: var(--shadow-sm);
    }
    .course-card-title {
        font-weight: 600;
        font-size: .95rem;
        color: var(--navy);
        margin-bottom: 6px;
    }
    .course-card-meta {
        font-size: .78rem;
        color: var(--text-3);
        margin-bottom: 10px;
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
    }

    /* ── DATA SOURCE CARDS ───────────────────────────────── */
    .source-card {
        background: var(--surface);
        border-radius: var(--r-md);
        padding: 22px 16px;
        border: 1px solid var(--border);
        text-align: center;
        transition: transform .25s, box-shadow .25s;
    }
    .source-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-md);
    }
    .source-icon {
        width: 52px; height: 52px;
        border-radius: var(--r-md);
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto 14px;
        font-size: 1.3rem;
    }
    .source-name  { font-weight: 600; font-size: .9rem; color: var(--navy); }
    .source-stat  { font-size: 1.4rem; font-weight: 700; color: var(--navy); margin-top: 6px; }
    .source-label { font-size: .73rem; color: var(--text-3); }
    .source-time  { font-size: .7rem; color: var(--text-4); margin-top: 8px; }
    .status-dot {
        display: inline-block;
        width: 8px; height: 8px;
        border-radius: 50%;
        margin-right: 6px;
    }
    .status-dot.active { background: var(--success); box-shadow: 0 0 0 3px var(--success-bg); }

    /* ── BUTTONS ─────────────────────────────────────────── */
    .stButton > button {
        background: var(--navy) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: var(--r-sm) !important;
        font-weight: 600 !important;
        font-size: .88rem !important;
        padding: 10px 22px !important;
        transition: background .2s, transform .2s !important;
    }
    .stButton > button:hover {
        background: var(--navy-light) !important;
        transform: translateY(-1px) !important;
    }

    /* ── FILE UPLOADER ───────────────────────────────────── */
    [data-testid="stFileUploader"] {
        border: 2px dashed var(--border-2) !important;
        border-radius: var(--r-md) !important;
        background: var(--surface-2) !important;
        padding: 16px !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: var(--gold) !important;
    }

    /* ── METRICS ─────────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--r-md) !important;
        padding: 18px 20px !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'DM Serif Display', serif !important;
        font-size: 2rem !important;
        font-weight: 400 !important;
        color: var(--navy) !important;
    }

    /* ── CHART TEXT ──────────────────────────────────────── */
    .js-plotly-plot .plotly text,
    .js-plotly-plot .plotly .xtick text,
    .js-plotly-plot .plotly .ytick text,
    .js-plotly-plot .plotly .legend text {
        fill: var(--text-1) !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    /* ── FOOTER ──────────────────────────────────────────── */
    .app-footer {
        text-align: center;
        padding: 24px 0 8px;
        font-size: .75rem;
        color: var(--text-4);
        border-top: 1px solid var(--border);
        margin-top: 56px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">', unsafe_allow_html=True)


inject_styles()

if not MODULES_LOADED:
    st.error(f"Failed to load modules: {MODULE_ERROR}")
    st.stop()

# ============================================================
# REDESIGNED HELPER COMPONENTS
# ============================================================

def render_page_header(title: str, subtitle: str, icon: str = ""):
    icon_html = f'<i class="{icon}" style="color:var(--gold);margin-right:10px;"></i>' if icon else ""
    st.markdown(f"""
    <div class="page-header">
      <h1>{icon_html}{title}</h1>
      <div class="page-header-subtitle">{subtitle}</div>
      <div class="gold-line"></div>
    </div>
    """, unsafe_allow_html=True)

def render_section_header(title: str, icon: str = "fas fa-chart-bar"):
    st.markdown(f"""
    <div class="section-card-title">
      <i class="{icon}"></i>{title}
    </div>
    """, unsafe_allow_html=True)

def render_kpi(color: str, icon: str, value, label: str, delta: str = None, delta_dir: str = "up"):
    delta_html = ""
    if delta:
        arrow = "↑" if delta_dir == "up" else "→"
        delta_html = f'<div class="kpi-delta {delta_dir}">{arrow} {delta}</div>'
    st.markdown(f"""
    <div class="kpi-card {color}">
      <div class="kpi-icon {color}"><i class="{icon}"></i></div>
      <div class="kpi-value">{value:,}</div>
      <div class="kpi-label">{label}</div>
      {delta_html}
    </div>
    """, unsafe_allow_html=True)

def render_course_card(course: dict):
    priority = course.get('priority', 'N/A')
    badge_cls = 'badge-high' if priority == 'High' else 'badge-medium' if priority == 'Medium' else 'badge-low'
    chips = ''.join(f'<span class="chip">{s}</span>' for s in course.get('skills', [])[:4])
    st.markdown(f"""
    <div class="course-card">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;">
        <div class="course-card-title">
          <i class="fas fa-book-open" style="color:var(--gold);margin-right:8px;font-size:.85rem;"></i>
          {course.get('title','N/A')}
        </div>
        <span class="badge {badge_cls}">{priority}</span>
      </div>
      <div class="course-card-meta">
        <span><i class="fas fa-clock" style="margin-right:4px"></i>{course.get('duration','N/A')} weeks</span>
        <span><i class="fas fa-layer-group" style="margin-right:4px"></i>{course.get('level','N/A')}</span>
        <span><i class="fas fa-industry" style="margin-right:4px"></i>{course.get('skill_gap','N/A')}</span>
      </div>
      <div>{chips}</div>
    </div>
    """, unsafe_allow_html=True)

def render_source_cards():
    sources = [
        ("LinkedIn",      "fab fa-linkedin", "#0077B5", "3,847"),
        ("BrighterMonday","fas fa-briefcase","#E85D26",  "4,125"),
        ("Fuzu",          "fas fa-search",   "#047857",  "2,891"),
        ("MyJobMag",      "fas fa-newspaper","#1D4ED8",  "2,156"),
        ("IkoKazi",       "fas fa-bullhorn", "#7C3AED",  "1,489"),
    ]
    cols = st.columns(5)
    for col, (name, icon, color, count) in zip(cols, sources):
        with col:
            st.markdown(f"""
            <div class="source-card">
              <div class="source-icon" style="background:{color}20;color:{color}">
                <i class="{icon}"></i>
              </div>
              <div class="source-name">{name}</div>
              <div class="source-stat">{count}</div>
              <div class="source-label">Jobs</div>
              <div class="source-time">
                <span class="status-dot active"></span>Active
              </div>
            </div>
            """, unsafe_allow_html=True)

def apply_chart_theme(fig):
    """Apply consistent theme to plotly figures"""
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_family='DM Sans',
        font_color='#1B2A4A',
        title_font_family='DM Serif Display',
        title_font_color='#1B2A4A',
        margin=dict(l=0, r=0, t=40, b=0),
    )
    fig.update_xaxes(gridcolor='#DDE3EF', linecolor='#DDE3EF')
    fig.update_yaxes(gridcolor='#DDE3EF', linecolor='#DDE3EF')
    return fig

# ============================================================
# SESSION STATE
# ============================================================
defaults = {
    'data_loader': DataLoader(),
    'nlp_pipeline': NLPPipeline(),
    'gap_analyzer': GapAnalyzer(),
    'prioritizer': GapPrioritizer(),
    'course_generator': CourseGenerator(),
    'processed_jobs': None,
    'gap_matrix': None,
    'prioritized_gaps': None,
    'generated_courses': [],
    'curriculum_skills': [],
    'analysis_complete': False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================================
# SIDEBAR
# ============================================================
logo_base64 = get_logo_base64()

with st.sidebar:
    if logo_base64:
        st.markdown(f'''
        <div class="sidebar-logo">
            <img src="data:image/png;base64,{logo_base64}" alt="TVET Skills Intel Logo">
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown('''
        <div class="sidebar-logo-text">
          <i class="fas fa-brain" style="color:#C9A84C;margin-right:8px"></i>
          TVET Skills Intel
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("---")
    page = st.radio("Navigation", ["Dashboard", "Skills Analysis", "Courses", "Reports", "Data Sources"], index=0)
    st.markdown("---")
    st.markdown("### System Status")
    if st.session_state.processed_jobs is not None:
        st.success(f"Jobs loaded: {len(st.session_state.processed_jobs)}")
    else:
        st.info("No job data loaded")
    if st.session_state.curriculum_skills:
        st.success(f"Curriculum: {len(st.session_state.curriculum_skills)} skills")
    else:
        st.info("No curriculum loaded")

# ============================================================
# DATA UPLOAD
# ============================================================
def render_data_upload():
    st.markdown("### Data Upload")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Job Postings")
        job_file = st.file_uploader("Upload job postings (CSV)", type=['csv'], key="job_upload")
        if job_file:
            df = st.session_state.data_loader.load_job_postings(job_file)
            if df is not None:
                st.success(f"Loaded {len(df)} job postings")
                if st.button("Extract Skills from Jobs"):
                    with st.spinner("Extracting skills..."):
                        st.session_state.processed_jobs = st.session_state.nlp_pipeline.process_dataframe(df, text_column='description')
                        skill_freq = st.session_state.nlp_pipeline.get_skill_frequencies(st.session_state.processed_jobs)
                        st.session_state.gap_analyzer.set_market_frequencies(skill_freq)
                        st.success("Skills extracted!")
                        st.rerun()
        else:
            if st.button("Use Sample Job Data"):
                df = st.session_state.data_loader.generate_sample_job_data()
                st.session_state.processed_jobs = st.session_state.nlp_pipeline.process_dataframe(df, text_column='description')
                skill_freq = st.session_state.nlp_pipeline.get_skill_frequencies(st.session_state.processed_jobs)
                st.session_state.gap_analyzer.set_market_frequencies(skill_freq)
                st.success("Sample data loaded!")
                st.rerun()

    with col2:
        st.markdown("#### Curriculum Documents")
        curriculum_files = st.file_uploader("Upload curriculum (PDF/TXT)", type=['pdf', 'txt'], accept_multiple_files=True, key="curriculum_upload")
        if curriculum_files:
            all_skills = []
            for file in curriculum_files:
                text = st.session_state.data_loader.load_curriculum_document(file, file.name)
                if text:
                    result = st.session_state.nlp_pipeline.process_job_description(text)
                    all_skills.extend(result['normalized_skills'])
                    st.success(f"{file.name} — {len(result['normalized_skills'])} skills")
            curriculum_freq = dict(Counter(all_skills))
            st.session_state.curriculum_skills = all_skills
            st.session_state.gap_analyzer.set_curriculum_frequencies(curriculum_freq)
            st.success(f"Total: {len(set(all_skills))} unique curriculum skills")

# ============================================================
# TREND ANALYSIS FUNCTION
# ============================================================
def get_trend_analysis():
    if st.session_state.processed_jobs is None:
        return None, None, None
    
    df = st.session_state.processed_jobs.copy()
    
    date_col = None
    for col in ['publishedAt', 'postedTime', 'created', 'date', 'published_at', 'posted_time', 'created_at', 'Date', 'Published At']:
        if col in df.columns:
            date_col = col
            break
    
    if date_col is None:
        return None, None, None
    
    try:
        df['parsed_date'] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=['parsed_date'])
        
        if len(df) == 0:
            return None, None, None
        
        df['year_month'] = df['parsed_date'].dt.to_period('M')
        monthly_counts = df.groupby('year_month').size().reset_index(name='count')
        monthly_counts['year_month_str'] = monthly_counts['year_month'].astype(str)
        
        peak_month = monthly_counts.loc[monthly_counts['count'].idxmax()]
        
        if len(monthly_counts) > 1:
            first_count = monthly_counts.iloc[0]['count']
            last_count = monthly_counts.iloc[-1]['count']
            if first_count >= 5:
                growth = ((last_count - first_count) / first_count * 100)
            else:
                growth = None
        else:
            growth = None
        
        avg_count = monthly_counts['count'].mean()
        high_seasons = monthly_counts[monthly_counts['count'] > avg_count]['year_month_str'].tolist()
        
        return monthly_counts, peak_month, {
            'growth': growth, 
            'avg': avg_count, 
            'high_seasons': high_seasons, 
            'total': len(df),
            'date_column_used': date_col
        }
    except Exception as e:
        return None, None, None

# ============================================================
# RUN ANALYSIS
# ============================================================
def run_full_analysis():
    if st.session_state.processed_jobs is None:
        st.error("Please load job postings first")
        return False

    with st.spinner("Running gap analysis..."):
        st.session_state.gap_matrix = st.session_state.gap_analyzer.generate_gap_matrix()
        if st.session_state.gap_matrix is not None:
            st.session_state.prioritized_gaps = st.session_state.prioritizer.prioritize_gaps(st.session_state.gap_matrix)
            if st.session_state.prioritized_gaps is not None:
                if 'gap_score' not in st.session_state.prioritized_gaps.columns:
                    st.session_state.prioritized_gaps['gap_score'] = st.session_state.prioritized_gaps.get('priority_score', 0)
                st.session_state.generated_courses = st.session_state.course_generator.generate_courses_from_prioritized_gaps(
                    st.session_state.prioritized_gaps, max_courses=8
                )
            st.session_state.analysis_complete = True
            st.success("Analysis complete!")
            return True
    return False
# ============================================================
# PDF REPORT GENERATION 
# ============================================================

def generate_pdf_report():
    """
    Generate a professional corporate/executive PDF report.
    Returns the path to a temporary PDF file, or None on failure.
    """
    if not REPORTLAB_AVAILABLE:
        st.error("ReportLab not installed. PDF generation unavailable.")
        return None

    import os
    import base64
    import tempfile
    from collections import Counter
    from datetime import datetime

    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, KeepInFrame,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.pdfgen import canvas as cv_mod
    from pypdf import PdfReader, PdfWriter

    # ── PALETTE ───────────────────────────────────────────────────────────
    C = {
        'navy':       colors.HexColor('#0B1829'),
        'navy_mid':   colors.HexColor('#162B47'),
        'navy_light': colors.HexColor('#1E3A5F'),
        'gold':       colors.HexColor('#C9A84C'),
        'gold_light': colors.HexColor('#E2C070'),
        'slate':      colors.HexColor('#3D526B'),
        'steel':      colors.HexColor('#64748B'),
        'silver':     colors.HexColor('#94A3B8'),
        'rule':       colors.HexColor('#CBD5E1'),
        'bg_card':    colors.HexColor('#FFFFFF'),
        'bg_stripe':  colors.HexColor('#F0F4F9'),
        'white':      colors.white,
    }

    PAGE_W, PAGE_H = A4
    L_MARGIN  = 1.6 * cm
    R_MARGIN  = 1.6 * cm
    T_MARGIN  = 2.2 * cm
    B_MARGIN  = 1.6 * cm
    CONTENT_W = PAGE_W - L_MARGIN - R_MARGIN

    # ── DATA COLLECTION ───────────────────────────────────────────────────
    total_jobs = (
        len(st.session_state.processed_jobs)
        if st.session_state.processed_jobs is not None else 0
    )

    all_skills = []
    if (st.session_state.processed_jobs is not None
            and 'normalized_skills' in st.session_state.processed_jobs.columns):
        for skills in st.session_state.processed_jobs['normalized_skills']:
            all_skills.extend(skills)
    skill_counts  = Counter(all_skills)
    unique_skills = len(skill_counts)
    top_skills    = skill_counts.most_common(10)

    total_gaps    = (len(st.session_state.gap_matrix)
                     if st.session_state.gap_matrix is not None else 0)
    total_courses = len(st.session_state.generated_courses)

    monthly_counts, peak_month, trend_stats = get_trend_analysis()

    # ── LOGO ──────────────────────────────────────────────────────────────
    temp_logo_path = None
    logo_base64 = get_logo_base64()
    if logo_base64:
        tmp_logo = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp_logo.write(base64.b64decode(logo_base64))
        tmp_logo.close()
        temp_logo_path = tmp_logo.name

    # ═════════════════════════════════════════════════════════════════════
    # HELPERS
    # ═════════════════════════════════════════════════════════════════════

    def make_styles():
        styles = getSampleStyleSheet()

        def add(name, **kw):
            styles.add(ParagraphStyle(name=name, **kw))

        add('RptTitle',
            fontName='Helvetica-Bold', fontSize=18,
            textColor=C['navy'], leading=24, spaceBefore=0, spaceAfter=4)
        add('RptSubtitle',
            fontName='Helvetica', fontSize=9,
            textColor=C['steel'], leading=13, spaceAfter=14)
        add('SecHeading',
            fontName='Helvetica-Bold', fontSize=12,
            textColor=C['navy'], leading=16, spaceBefore=18, spaceAfter=6)
        add('Body',
            fontName='Helvetica', fontSize=9,
            textColor=C['slate'], leading=13.5,
            alignment=TA_JUSTIFY, spaceAfter=6)
        add('Caption',
            fontName='Helvetica-Oblique', fontSize=7.5,
            textColor=C['silver'], alignment=TA_CENTER, leading=10, spaceAfter=4)
        add('StatNum',
            fontName='Helvetica-Bold', fontSize=22,
            textColor=C['navy'], alignment=TA_CENTER, leading=26)
        add('StatLabel',
            fontName='Helvetica', fontSize=7.5,
            textColor=C['steel'], alignment=TA_CENTER, leading=10)
        add('TblHead',
            fontName='Helvetica-Bold', fontSize=8.5,
            textColor=C['white'], alignment=TA_LEFT, leading=11)
        add('TblCell',
            fontName='Helvetica', fontSize=8.5,
            textColor=C['slate'], alignment=TA_LEFT, leading=11)
        add('TblCellCenter',
            fontName='Helvetica', fontSize=8.5,
            textColor=C['slate'], alignment=TA_CENTER, leading=11)
        return styles

    def section_rule():
        return HRFlowable(width="100%", thickness=0.5, color=C['gold'],
                          spaceBefore=0, spaceAfter=8)

    def metric_cards(stats):
        """stats = [(value, label), ...]"""
        n = len(stats)
        card_w = CONTENT_W / n
        top_row   = [''] * n
        val_row   = [Paragraph(str(v), styles['StatNum'])  for v, _ in stats]
        label_row = [Paragraph(l.upper(), styles['StatLabel']) for _, l in stats]
        tbl = Table(
            [top_row, val_row, label_row],
            colWidths=[card_w] * n,
            rowHeights=[0.18 * cm, 1.2 * cm, 0.6 * cm],
        )
        tbl.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0), C['gold']),
            ('TOPPADDING',    (0, 0), (-1, 0), 0),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 0),
            ('BACKGROUND',    (0, 1), (-1, 2), C['bg_card']),
            ('TOPPADDING',    (0, 1), (-1, 1), 10),
            ('BOTTOMPADDING', (0, 2), (-1, 2), 10),
            ('TOPPADDING',    (0, 2), (-1, 2), 0),
            ('LINEAFTER',     (0, 0), (-2, -1), 0.5, C['rule']),
            ('BOX',           (0, 0), (-1, -1), 0.5, C['rule']),
            ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        return tbl

    def styled_table(data_rows, col_widths, has_rank=False):
        """data_rows[0] = header list of strings; rest = data."""
        header = [Paragraph(h, styles['TblHead']) for h in data_rows[0]]
        body = []
        for row in data_rows[1:]:
            cells = []
            for ci, cell in enumerate(row):
                s = styles['TblCellCenter'] if (has_rank and ci == 0) else styles['TblCell']
                cells.append(Paragraph(str(cell), s))
            body.append(cells)

        row_bgs = [
            ('BACKGROUND', (0, i + 1), (-1, i + 1),
             C['bg_card'] if i % 2 == 0 else C['bg_stripe'])
            for i in range(len(body))
        ]
        tbl = Table([header] + body, colWidths=col_widths, repeatRows=1)
        ts  = TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0), C['navy']),
            ('TOPPADDING',    (0, 0), (-1, 0), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 7),
            ('LEFTPADDING',   (0, 0), (-1, 0), 8),
            ('RIGHTPADDING',  (0, 0), (-1, 0), 8),
            ('TOPPADDING',    (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('LEFTPADDING',   (0, 1), (-1, -1), 8),
            ('RIGHTPADDING',  (0, 1), (-1, -1), 8),
            ('LINEBELOW',     (0, 0), (-1, -1), 0.3, C['rule']),
            ('BOX',           (0, 0), (-1, -1), 0.5, C['rule']),
            ('ALIGN',         (0, 1), (0, -1), 'CENTER') if has_rank
                else ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ] + row_bgs)
        ts.add('LINEAFTER', (0, 0), (0, 0), 1.5, C['gold'])
        tbl.setStyle(ts)
        return tbl

    def two_col(left_items, right_items, left_w, right_w):
        gap = CONTENT_W - left_w - right_w
        lf  = KeepInFrame(left_w,  40 * cm, left_items,  mode='shrink')
        rf  = KeepInFrame(right_w, 40 * cm, right_items, mode='shrink')
        tbl = Table([[lf, Spacer(gap, 1), rf]], colWidths=[left_w, gap, right_w])
        tbl.setStyle(TableStyle([
            ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING',   (0, 0), (-1, -1), 0),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
            ('TOPPADDING',    (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        return tbl

def course_card(course, idx):
    title = course.get('title', 'N/A')
    gap = course.get('skill_gap', 'N/A')
    dur = course.get('duration', '—')
    lvl = course.get('level', '—')
    pri = course.get('priority', '—')
    prereqs = course.get('prerequisites', ['None'])
    modules = course.get('modules', [])
    
    # Get learning outcomes (if available, otherwise provide defaults based on skill gap)
    outcomes = course.get('learning_outcomes', [])
    if not outcomes:
        # Provide sensible defaults based on skill gap
        if 'Machine Learning' in title or 'Machine Learning' in gap:
            outcomes = [
                "Implement supervised learning algorithms on real-world datasets",
                "Evaluate model performance using appropriate metrics",
                "Deploy trained models for inference"
            ]
        elif 'Python' in title or 'Python' in gap:
            outcomes = [
                "Write Python scripts for data manipulation and analysis",
                "Use Python libraries (pandas, numpy) for industry applications",
                "Debug and optimise Python code for performance"
            ]
        elif 'Artificial Intelligence' in title or 'AI' in gap:
            outcomes = [
                "Understand core AI concepts and search algorithms",
                "Implement knowledge representation and reasoning systems",
                "Apply AI techniques to solve practical problems"
            ]
        elif 'Go' in title or 'Go' in gap:
            outcomes = [
                "Write concurrent Go programs using goroutines and channels",
                "Build REST APIs using Go standard library and frameworks",
                "Implement error handling and testing in Go applications"
            ]
        elif 'Docker' in title:
            outcomes = [
                "Create and manage Docker containers and images",
                "Write Dockerfiles for application containerisation",
                "Orchestrate multi-container applications using Docker Compose"
            ]
        else:
            outcomes = [
                f"Apply {gap} concepts to practical industry scenarios",
                "Demonstrate proficiency in the target competency area",
                "Complete a capstone project demonstrating mastery"
            ]
    
    # Assessment strategy
    assessment = course.get('assessment', '')
    if not assessment:
        assessment = "Formative: Practical exercises and quizzes (40%); Summative: Capstone project (60%)"
    
    # Priority badge background
    pri_bg = {'High': C['navy'], 'Medium': C['slate'], 'Low': C['steel']}.get(str(pri), C['slate'])

    _s = lambda name, **kw: ParagraphStyle(name, **kw)
    
    # Header with title and priority
    title_p = Paragraph(f"<b>{idx}. {title}</b>",
        _s('cT', fontName='Helvetica-Bold', fontSize=11, textColor=C['navy'], leading=14))
    
    # Basic info line
    meta_p = Paragraph(f"<b>Duration:</b> {dur} weeks  |  <b>Level:</b> {lvl}  |  <b>Skill Gap:</b> {gap}",
        _s('cM', fontName='Helvetica', fontSize=8.5, textColor=C['slate'], leading=11))
    
    # Prerequisites
    prereq_text = ', '.join(prereqs) if isinstance(prereqs, list) else prereqs
    prereq_p = Paragraph(f"<b>Prerequisites:</b> {prereq_text}",
        _s('cR', fontName='Helvetica', fontSize=8.5, textColor=C['slate'], leading=11))
    
    # Learning outcomes (as bullet points)
    outcomes_lines = [f"• {o}" for o in outcomes[:4]]
    outcomes_text = "<b>Learning Outcomes:</b><br/>" + "<br/>".join(outcomes_lines)
    outcomes_p = Paragraph(outcomes_text,
        _s('cO', fontName='Helvetica', fontSize=8.5, textColor=C['slate'], leading=12))
    
    # Modules (as inline list)
    modules_text = "<b>Core Modules:</b> " + " → ".join(modules[:4])
    modules_p = Paragraph(modules_text,
        _s('cMod', fontName='Helvetica', fontSize=8.5, textColor=C['slate'], leading=11))
    
    # Assessment strategy
    assessment_p = Paragraph(f"<b>Assessment:</b> {assessment}",
        _s('cAs', fontName='Helvetica', fontSize=8.5, textColor=C['slate'], leading=11))
    
    # Priority pill
    pri_p = Paragraph(f"<b>{pri}</b>",
        _s('cP', fontName='Helvetica-Bold', fontSize=8,
           textColor=C['white'], alignment=TA_CENTER, leading=10))
    pri_tbl = Table([[pri_p]], colWidths=[2.0 * cm])
    pri_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), pri_bg),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))

    # Build the card
    content = Table([
        [title_p, pri_tbl],
        [meta_p, ''],
        [prereq_p, ''],
        [outcomes_p, ''],
        [modules_p, ''],
        [assessment_p, ''],
    ], colWidths=[CONTENT_W - 2.5 * cm, 2.5 * cm])
    
    content.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    card = Table([[content]], colWidths=[CONTENT_W])
    card.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, C['rule']),
        ('BACKGROUND', (0, 0), (-1, -1), C['bg_card']),
        ('LINEAFTER', (0, 0), (0, -1), 2.5, C['gold']),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    return card

    # ═════════════════════════════════════════════════════════════════════
    # HEADER / FOOTER (called by Platypus on every content page)
    # ═════════════════════════════════════════════════════════════════════

    def draw_header_footer(canv, doc):
        canv.saveState()

        # Header band
        HDR_H = 1.8 * cm
        canv.setFillColor(C['navy'])
        canv.rect(0, PAGE_H - HDR_H, PAGE_W, HDR_H, fill=1, stroke=0)

        # Gold rule under header
        canv.setFillColor(C['gold'])
        canv.rect(0, PAGE_H - HDR_H - 0.06 * cm, PAGE_W, 0.06 * cm, fill=1, stroke=0)

        # Optional logo
        if temp_logo_path and os.path.exists(temp_logo_path):
            try:
                canv.drawImage(temp_logo_path,
                               L_MARGIN, PAGE_H - HDR_H + 0.38 * cm,
                               width=1.0 * cm, height=1.0 * cm,
                               preserveAspectRatio=True, mask='auto')
                txt_x = L_MARGIN + 1.2 * cm
            except Exception:
                txt_x = L_MARGIN + 0.38 * cm
        else:
            # Gold square accent when no logo
            canv.setFillColor(C['gold'])
            canv.rect(L_MARGIN, PAGE_H - HDR_H + 0.55 * cm, 0.22 * cm, 0.22 * cm, fill=1, stroke=0)
            txt_x = L_MARGIN + 0.38 * cm

        canv.setFillColor(C['white'])
        canv.setFont("Helvetica-Bold", 10)
        canv.drawString(txt_x, PAGE_H - HDR_H + 0.62 * cm, "TVET SKILLS INTEL")
        canv.setFillColor(C['silver'])
        canv.setFont("Helvetica", 7.5)
        canv.drawString(txt_x, PAGE_H - HDR_H + 0.28 * cm,
                        "AI-Powered Labour Market Intelligence  ·  HSW")

        # Gold pill page number
        pg_text = f"PAGE  {doc.page}"
        pill_w, pill_h = 1.8 * cm, 0.45 * cm
        pill_x = PAGE_W - R_MARGIN - pill_w
        pill_y = PAGE_H - HDR_H + 0.33 * cm
        canv.setFillColor(C['gold'])
        canv.roundRect(pill_x, pill_y, pill_w, pill_h, 0.1 * cm, fill=1, stroke=0)
        canv.setFillColor(C['navy'])
        canv.setFont("Helvetica-Bold", 7.5)
        canv.drawCentredString(pill_x + pill_w / 2, pill_y + 0.14 * cm, pg_text)

        # Footer
        FTR_H = 0.9 * cm
        canv.setFillColor(C['gold'])
        canv.rect(0, FTR_H, PAGE_W, 0.04 * cm, fill=1, stroke=0)
        canv.setFillColor(C['bg_stripe'])
        canv.rect(0, 0, PAGE_W, FTR_H, fill=1, stroke=0)
        canv.setFillColor(C['steel'])
        canv.setFont("Helvetica", 6.5)
        eat_time = datetime.now(ZoneInfo('Africa/Nairobi')).strftime('%d %B %Y at %H:%M')  # ← new
        canv.drawString(L_MARGIN, 0.32 * cm, f"Generated {eat_time} EAT")                 # ← changed
        canv.drawRightString(PAGE_W - R_MARGIN, 0.32 * cm,
                             "Confidential  ·  Academic Research Use Only")
        
        canv.restoreState()

    # ═════════════════════════════════════════════════════════════════════
    # COVER PAGE (raw canvas, merged later)
    # ═════════════════════════════════════════════════════════════════════

    def build_cover(canv):
        # Full-page navy background
        canv.setFillColor(C['navy'])
        canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

        # Bottom-left mid-navy slab
        canv.setFillColor(C['navy_mid'])
        canv.rect(0, 0, PAGE_W * 0.45, PAGE_H * 0.38, fill=1, stroke=0)

        # Gold left-edge stripe
        canv.setFillColor(C['gold'])
        canv.rect(0, 0, 0.45 * cm, PAGE_H, fill=1, stroke=0)

        # Top-right angled light panel
        p = canv.beginPath()
        p.moveTo(PAGE_W * 0.55, PAGE_H)
        p.lineTo(PAGE_W, PAGE_H)
        p.lineTo(PAGE_W, PAGE_H * 0.62)
        p.lineTo(PAGE_W * 0.55, PAGE_H)
        canv.setFillColor(C['navy_light'])
        canv.drawPath(p, fill=1, stroke=0)

        # Mid-page gold rule
        rule_y = PAGE_H * 0.52
        canv.setFillColor(C['gold'])
        canv.rect(1.6 * cm, rule_y, PAGE_W * 0.55, 0.07 * cm, fill=1, stroke=0)

        # Main title — well above the gold rule and pill tag
        canv.setFillColor(C['white'])
        canv.setFont("Helvetica-Bold", 28)
        canv.drawString(1.6 * cm, rule_y + 4.2 * cm, "Skills Gap &")
        canv.drawString(1.6 * cm, rule_y + 3.2 * cm, "Curriculum Analysis")

        # Subtitle
        canv.setFillColor(C['silver'])
        canv.setFont("Helvetica", 10)
        canv.drawString(1.6 * cm, rule_y + 2.4 * cm,
                        f"TVET Skills Intel System  ·  {datetime.now().strftime('%B %Y')}")

        # Report-type pill tag — just above the gold rule
        canv.setFillColor(C['gold'])
        canv.roundRect(1.6 * cm, rule_y + 0.5 * cm, 5.2 * cm, 0.55 * cm, 0.12 * cm,
                       fill=1, stroke=0)
        canv.setFillColor(C['navy'])
        canv.setFont("Helvetica-Bold", 8)
        canv.drawString(1.6 * cm + 0.28 * cm, rule_y + 0.68 * cm, "LABOUR MARKET INTELLIGENCE")

        # Bottom meta block
        meta_y = 2.6 * cm
        canv.setFillColor(C['navy_light'])
        canv.rect(1.6 * cm, meta_y - 0.3 * cm, PAGE_W - 3.2 * cm, 1.8 * cm, fill=1, stroke=0)

        canv.setFillColor(C['gold'])
        canv.setFont("Helvetica-Bold", 8)
        canv.drawString(2.0 * cm, meta_y + 1.0 * cm, "PREPARED FOR")
        canv.setFillColor(C['white'])
        canv.setFont("Helvetica-Bold", 11)
        canv.drawString(2.0 * cm, meta_y + 0.55 * cm,
                        "The Nairobi National Polytechnic")
        canv.setFillColor(C['silver'])
        canv.setFont("Helvetica", 8)
        canv.drawString(2.0 * cm, meta_y + 0.2 * cm,
                        "Confidential  ·  Academic Research Use Only")

        # Decorative corner dots
        for i in range(4):
            canv.setFillColor(C['gold'] if i % 2 == 0 else C['navy_light'])
            canv.rect(PAGE_W - 1.4 * cm + i * 0.18 * cm,
                      PAGE_H * 0.38 + i * 0.18 * cm,
                      0.14 * cm, 0.14 * cm, fill=1, stroke=0)

    # ═════════════════════════════════════════════════════════════════════
    # BUILD STORY
    # ═════════════════════════════════════════════════════════════════════

    styles = make_styles()
    story  = []

    # Page title
    story.append(Paragraph("Labour Market Intelligence Report", styles['RptTitle']))
    story.append(Paragraph(
        f"TVET Skills Intel  ·  {datetime.now().strftime('%B %Y')}  ·  The Nairobi National Polytechnic",
        styles['RptSubtitle'],
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=C['gold'],
                             spaceBefore=0, spaceAfter=12))

    # Executive Summary
    story.append(Paragraph("Executive Summary", styles['SecHeading']))
    story.append(section_rule())
    story.append(Paragraph(
        f"This report presents findings from the AI-powered Labour Market Intelligence System "
        f"developed for Kenyan TVET institutions. A corpus of <b>{total_jobs}</b> job postings "
        f"was analysed, yielding <b>{unique_skills}</b> unique normalised skills mapped against "
        f"the ESCO taxonomy. Gap analysis identified <b>{total_gaps}</b> curriculum-market "
        f"mismatches, from which <b>{total_courses}</b> targeted short course recommendations "
        f"were generated to address the highest-priority deficits.",
        styles['Body'],
    ))
    story.append(Spacer(1, 0.3 * cm))

    # Key Metrics
    story.append(Paragraph("Key Metrics at a Glance", styles['SecHeading']))
    story.append(section_rule())
    story.append(metric_cards([
        (total_jobs,    "Jobs Analysed"),
        (unique_skills, "Skills Extracted"),
        (total_gaps,    "Gaps Identified"),
        (total_courses, "Courses Designed"),
    ]))
    story.append(Spacer(1, 0.5 * cm))

    # Two-column: Trends | Top Skills
    lw = CONTENT_W * 0.44
    rw = CONTENT_W * 0.52

    trend_items = [
        Paragraph("Job Posting Trends", styles['SecHeading']),
        HRFlowable(width="100%", thickness=0.5, color=C['gold'],
                   spaceBefore=0, spaceAfter=8),
    ]
    if monthly_counts is not None and len(monthly_counts) > 0:
        trend_rows = [["Month", "Postings"]]
        for _, row in monthly_counts.iterrows():
            trend_rows.append([row['year_month_str'], str(row['count'])])
        trend_items.append(styled_table(trend_rows, [lw * 0.58, lw * 0.38]))
        trend_items.append(Spacer(1, 4))

        # Safe growth display
        if trend_stats.get('growth') is not None and trend_stats['growth'] < 1000:
            growth_str = f"{trend_stats['growth']:.1f}%"
        elif len(monthly_counts) > 1:
            delta = monthly_counts.iloc[-1]['count'] - monthly_counts.iloc[0]['count']
            growth_str = f"+{delta} jobs" if delta >= 0 else f"{delta} jobs"
        else:
            growth_str = "N/A"

        trend_items.append(Paragraph(
            f"Peak: {peak_month['year_month_str']} ({peak_month['count']} postings)  ·  "
            f"Avg: {trend_stats['avg']:.0f} / month  ·  Growth: {growth_str}",
            styles['Caption'],
        ))
    else:
        trend_items.append(Paragraph("Trend data unavailable.", styles['Body']))

    skills_items = [
        Paragraph("Top 10 In-Demand Skills", styles['SecHeading']),
        HRFlowable(width="100%", thickness=0.5, color=C['gold'],
                   spaceBefore=0, spaceAfter=8),
    ]
    if top_skills:
        skill_rows = [["#", "Skill", "Freq", "%"]]
        for i, (sk, cnt) in enumerate(top_skills, 1):
            pct = f"{cnt / max(total_jobs, 1) * 100:.1f}%"
            skill_rows.append([str(i), sk, str(cnt), pct])
        skills_items.append(
            styled_table(skill_rows, [rw * 0.08, rw * 0.52, rw * 0.20, rw * 0.18],
                         has_rank=True)
        )
    else:
        skills_items.append(Paragraph("No skill data available.", styles['Body']))

    story.append(two_col(trend_items, skills_items, lw, rw))
    story.append(Spacer(1, 0.5 * cm))

    # Prioritised Gaps
    story.append(Paragraph("Prioritised Skills Gaps", styles['SecHeading']))
    story.append(section_rule())
    if st.session_state.prioritized_gaps is not None:
        gaps_rows = [["Rank", "Skill", "Priority Tier", "Priority Score"]]
        for i, row in enumerate(st.session_state.prioritized_gaps.head(10).itertuples(), 1):
            gaps_rows.append([str(i), row.skill, row.priority_tier, f"{row.priority_score:.3f}"])
        story.append(styled_table(
            gaps_rows,
            [1.1 * cm, CONTENT_W - 6.8 * cm, 2.8 * cm, 2.8 * cm],
            has_rank=True,
        ))
    else:
        story.append(Paragraph("No gaps identified.", styles['Body']))
    story.append(Spacer(1, 0.5 * cm))

    # Course Recommendations
    story.append(Paragraph("Short Course Recommendations", styles['SecHeading']))
    story.append(section_rule())
    if st.session_state.generated_courses:
        for i, course in enumerate(st.session_state.generated_courses[:5], 1):
            story.append(course_card(course, i))
            story.append(Spacer(1, 0.18 * cm))
    else:
        story.append(Paragraph("No courses generated.", styles['Body']))
    story.append(Spacer(1, 0.3 * cm))

    # Methodological Note
    story.append(Paragraph("Methodological Note", styles['SecHeading']))
    story.append(section_rule())
    story.append(Paragraph(
        "Skills were extracted using a BERT-based NLP pipeline and normalised against the "
        "ESCO occupational taxonomy (v1.1). Gap prioritisation used a multi-criteria classifier "
        "combining market frequency, wage premium signals, and curriculum coverage ratios. "
        "Course recommendations follow the constructive alignment framework (Biggs, 1996). "
        "All data is sourced from publicly available Kenyan job boards.",
        styles['Body'],
    ))

    # ═════════════════════════════════════════════════════════════════════
    # RENDER
    # ═════════════════════════════════════════════════════════════════════

    timestamp    = datetime.now().strftime("%Y%m%d_%H%M%S")
    tmp_out      = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp_out.close()
    tmp_cover    = tmp_out.name + ".cover.pdf"
    tmp_content  = tmp_out.name + ".content.pdf"

    # Cover page
    c = cv_mod.Canvas(tmp_cover, pagesize=A4)
    build_cover(c)
    c.showPage()
    c.save()

    # Content pages
    doc = SimpleDocTemplate(
        tmp_content,
        pagesize=A4,
        topMargin=T_MARGIN + 0.4 * cm,
        bottomMargin=B_MARGIN + 0.6 * cm,
        leftMargin=L_MARGIN,
        rightMargin=R_MARGIN,
        title="TVET Labour Market Intelligence Report",
        author="TVET Skills Intel",
        subject="Skills Gap Analysis and Course Recommendations",
    )
    doc.build(story, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)

    # Merge cover + content
    writer = PdfWriter()
    for src in [tmp_cover, tmp_content]:
        rdr = PdfReader(src)
        for pg in rdr.pages:
            writer.add_page(pg)
    with open(tmp_out.name, "wb") as f:
        writer.write(f)

    # Clean up
    for tmp in [tmp_cover, tmp_content]:
        try:
            os.unlink(tmp)
        except OSError:
            pass
    if temp_logo_path and os.path.exists(temp_logo_path):
        try:
            os.unlink(temp_logo_path)
        except OSError:
            pass

    return tmp_out.name

# ============================================================
# DASHBOARD PAGE
# ============================================================
def render_dashboard():
    render_page_header("Labour Market Intelligence Dashboard", "AI-powered analysis of TVET skills demand across Kenya", "fas fa-chart-line")
    render_data_upload()
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Run Complete Analysis", use_container_width=True):
            run_full_analysis()
    st.markdown("---")
    
    if not (st.session_state.analysis_complete and st.session_state.processed_jobs is not None):
        st.info("Upload job data and click Run Complete Analysis to see results.")
        return
    
    all_skills_flat = []
    if 'normalized_skills' in st.session_state.processed_jobs.columns:
        for skills in st.session_state.processed_jobs['normalized_skills']:
            all_skills_flat.extend(skills)
    
    cols = st.columns(4)
    kpi_data = [
        ("blue", "fas fa-briefcase", len(st.session_state.processed_jobs), "Jobs Analysed", None),
        ("green", "fas fa-cogs", len(set(all_skills_flat)), "Skills Extracted", None),
        ("amber", "fas fa-exclamation-triangle", len(st.session_state.gap_matrix) if st.session_state.gap_matrix is not None else 0, "Skills Gaps", None),
        ("purple", "fas fa-book-open", len(st.session_state.generated_courses), "Courses Recommended", None),
    ]
    for col, (color, icon, value, label, delta) in zip(cols, kpi_data):
        with col:
            render_kpi(color, icon, value, label, delta)
    st.markdown("---")
    
    # Trend Analysis
    st.markdown("### Job Posting Trends")
    monthly_counts, peak_month, trend_stats = get_trend_analysis()
    if monthly_counts is not None and len(monthly_counts) > 0:
        cols2 = st.columns(4)
        cols2[0].metric("Total Jobs", trend_stats['total'])
        cols2[1].metric("Peak Month", f"{peak_month['year_month_str']}", f"{peak_month['count']} jobs")
        
        if trend_stats.get('growth') is not None and trend_stats['growth'] < 1000:
            growth_display = f"{trend_stats['growth']:.1f}%"
        else:
            if len(monthly_counts) > 1:
                first_count = monthly_counts.iloc[0]['count']
                last_count = monthly_counts.iloc[-1]['count']
                abs_change = last_count - first_count
                growth_display = f"+{abs_change} jobs" if abs_change >= 0 else f"{abs_change} jobs"
            else:
                growth_display = "Insufficient data"
        
        cols2[2].metric("Growth Rate", growth_display)
        cols2[3].metric("Monthly Avg", f"{trend_stats['avg']:.0f}")
        
        fig = px.line(monthly_counts, x='year_month_str', y='count', 
                      title='Job Postings Over Time',
                      markers=True, labels={'year_month_str': 'Month', 'count': 'Number of Jobs'})
        fig.update_traces(line_color='#1B2A4A', marker_color='#C9A84C')
        fig = apply_chart_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Trend analysis requires a date column in your dataset.")
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    with col1:
        render_section_header("Top 10 In-Demand Skills", "fas fa-chart-bar")
        if all_skills_flat:
            skill_counts = Counter(all_skills_flat)
            top_df = pd.DataFrame(skill_counts.most_common(10), columns=['Skill', 'Count'])
            fig = px.bar(top_df, x='Count', y='Skill', orientation='h',
                         color='Count', color_continuous_scale='Blues', text='Count')
            fig.update_traces(textposition='outside', textfont_color='#1B2A4A')
            fig = apply_chart_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        render_section_header("Skills Gap Summary", "fas fa-exclamation-triangle")
        if st.session_state.prioritized_gaps is not None:
            gap_df = st.session_state.prioritized_gaps.head(8)[['skill','priority_tier','priority_score']].copy()
            gap_df.columns = ['Skill','Priority','Score']
            color_map = {'High': '#C0392B', 'Medium': '#D97706', 'Low': '#047857'}
            fig = px.bar(gap_df, x='Score', y='Skill', orientation='h',
                         color='Priority', color_discrete_map=color_map)
            fig = apply_chart_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    
    # Tables
    col1, col2 = st.columns(2)
    with col1:
        render_section_header("Prioritised Skills Gaps", "fas fa-list")
        if st.session_state.prioritized_gaps is not None:
            disp = st.session_state.prioritized_gaps.head(8)[['skill','priority_tier','priority_score']].copy()
            disp.columns = ['Skill','Priority','Score']
            st.dataframe(disp, use_container_width=True, hide_index=True)
    
    with col2:
        render_section_header("Recommended Short Courses", "fas fa-graduation-cap")
        for course in st.session_state.generated_courses[:4]:
            render_course_card(course)

# ============================================================
# SKILLS ANALYSIS PAGE
# ============================================================
def render_skills_analysis():
    render_page_header("Skills Analysis", "Analyze and compare skills demand across sectors", "fas fa-chart-pie")
    st.markdown("---")
    render_data_upload()
    if st.session_state.processed_jobs is None or 'normalized_skills' not in st.session_state.processed_jobs.columns:
        st.info("Load job postings to see skills analysis.")
        return
    all_skills_flat = []
    for skills in st.session_state.processed_jobs['normalized_skills']:
        all_skills_flat.extend(skills)
    skill_counts = Counter(all_skills_flat)
    st.markdown("#### Compare Skills")
    selected = st.multiselect("Select skills to compare", list(skill_counts.keys()), default=list(skill_counts.keys())[:3])
    if selected:
        sel_df = pd.DataFrame([(s, skill_counts[s]) for s in selected], columns=['Skill','Frequency'])
        fig = px.bar(sel_df, x='Skill', y='Frequency', color='Skill',
                     color_discrete_sequence=['#1B2A4A','#047857','#D97706','#C0392B','#6D28D9'])
        fig = apply_chart_theme(fig)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    st.markdown("#### Top 20 Skills")
    top_df = pd.DataFrame(skill_counts.most_common(20), columns=['Skill','Frequency'])
    fig = px.bar(top_df, x='Frequency', y='Skill', orientation='h', color='Frequency', color_continuous_scale='Blues')
    fig = apply_chart_theme(fig)
    fig.update_layout(coloraxis_showscale=False, height=560)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# COURSES PAGE
# ============================================================
def render_courses():
    render_page_header("Course Recommendations", "AI-generated short courses to address skills gaps", "fas fa-book-open")
    st.markdown("---")
    render_data_upload()
    if not (st.session_state.analysis_complete and st.session_state.generated_courses):
        st.info("Run analysis first to generate course recommendations.")
        return
    priority_filter = st.selectbox("Filter by Priority", ["All","High","Medium","Low"])
    courses = st.session_state.generated_courses
    if priority_filter != "All":
        courses = [c for c in courses if c.get('priority') == priority_filter]
    st.markdown(f"**{len(courses)} courses found**")
    st.markdown("---")
    for course in courses:
        with st.expander(f"Book: {course.get('title','N/A')}"):
            col1, col2 = st.columns([2,1])
            with col1:
                st.markdown(f"**Skill Gap:** `{course.get('skill_gap','N/A')}`")
                st.markdown(f"**Duration:** {course.get('duration','N/A')} weeks | **Level:** {course.get('level','N/A')}")
                st.markdown(f"**Prerequisites:** {', '.join(course.get('prerequisites',['None']))}")
                st.markdown("**Learning Outcomes:**")
                for o in course.get('learning_outcomes', []):
                    st.markdown(f"- {o}")
            with col2:
                priority = course.get('priority','N/A')
                badge_cls = 'badge-high' if priority == 'High' else 'badge-medium' if priority == 'Medium' else 'badge-low'
                st.markdown(f'<span class="badge {badge_cls}">{priority} Priority</span>', unsafe_allow_html=True)
                st.markdown(f"**Market Demand:** {course.get('market_demand',0)} mentions")
                st.markdown(f"**Gap Score:** {course.get('gap_score',0):.2f}")
            st.markdown("**Modules:** " + " · ".join(course.get('modules',[])))

# ============================================================
# REPORTS PAGE
# ============================================================
def render_reports():
    render_page_header("Reports", "Generate and download comprehensive market intelligence reports", "fas fa-file-alt")
    st.markdown("---")
    
    if not st.session_state.analysis_complete:
        st.info("Run analysis first to generate reports.")
        return
    
        st.markdown("### Trend Analysis Preview")
    monthly_counts, peak_month, trend_stats = get_trend_analysis()
    if monthly_counts is not None and len(monthly_counts) > 0:
        cols2 = st.columns(4)
        cols2[0].metric("Total Jobs", trend_stats['total'])
        cols2[1].metric("Peak Month", f"{peak_month['year_month_str']}", f"{peak_month['count']} jobs")
        
        # Handle growth display properly (avoid None value)
        if trend_stats.get('growth') is not None and trend_stats['growth'] < 1000:
            growth_display = f"{trend_stats['growth']:.1f}%"
        else:
            # Calculate absolute change instead
            if len(monthly_counts) > 1:
                first_count = monthly_counts.iloc[0]['count']
                last_count = monthly_counts.iloc[-1]['count']
                abs_change = last_count - first_count
                growth_display = f"+{abs_change} jobs" if abs_change >= 0 else f"{abs_change} jobs"
            else:
                growth_display = "Insufficient data"
        
        cols2[2].metric("Growth Rate", growth_display)
        cols2[3].metric("Monthly Avg", f"{trend_stats['avg']:.0f}")
        fig = px.line(monthly_counts, x='year_month_str', y='count', 
                      title='Job Postings Over Time', markers=True)
        fig = apply_chart_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Trend data not available. Add a date column to your dataset.")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2,1])
    with col1:
        report_type = st.selectbox("Report Type", ["Full Analysis Report", "Skills Gap Summary", "Course Recommendations Only"])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Generate PDF Report", use_container_width=True):
            pdf_file = generate_pdf_report()
            if pdf_file:
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="Download PDF Report",
                        data=f,
                        file_name=f"tvet_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                os.unlink(pdf_file)
            else:
                st.error("PDF generation failed.")
    
    st.markdown("---")
    st.markdown("#### Report Preview")
    st.info("The PDF report includes: Executive Summary, Job Posting Trends, Top Skills, Skills Gaps, and Course Recommendations.")

# ============================================================
# DATA SOURCES PAGE
# ============================================================
def render_data_sources():
    render_page_header("Data Sources", "Job posting data from Kenya's leading employment platforms", "fas fa-database")
    st.markdown("---")
    render_source_cards()
    st.markdown("---")
    render_data_upload()
    st.markdown("---")
    st.markdown("### System Information")
    st.json({
        "jobs_loaded": len(st.session_state.processed_jobs) if st.session_state.processed_jobs is not None else 0,
        "curriculum_skills": len(set(st.session_state.curriculum_skills)) if st.session_state.curriculum_skills else 0,
        "gaps_identified": len(st.session_state.gap_matrix) if st.session_state.gap_matrix is not None else 0,
        "courses_generated": len(st.session_state.generated_courses),
        "analysis_complete": st.session_state.analysis_complete,
    })

# ============================================================
# ROUTING
# ============================================================
if page == "Dashboard":
    render_dashboard()
elif page == "Skills Analysis":
    render_skills_analysis()
elif page == "Courses":
    render_courses()
elif page == "Reports":
    render_reports()
elif page == "Data Sources":
    render_data_sources()

# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div class="app-footer">
  <i class="fas fa-brain"></i> TVET Skills Intel | AI-Powered Labour Market Intelligence for Kenyan TVET Institutions<br>
  Data: LinkedIn · BrighterMonday · Fuzu · MyJobMag · IkoKazi | May 2026
</div>
""", unsafe_allow_html=True)
