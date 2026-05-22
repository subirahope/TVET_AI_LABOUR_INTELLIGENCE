"""
TVET Labour Market Intelligence System
Complete Streamlit Dashboard
Author: Hope Subira
"""

import streamlit as st

# ============================================================
# PAGE CONFIGURATION — must be the VERY FIRST st.* call
# ============================================================
st.set_page_config(
    page_title="TVET Skills Intel",
    page_icon="🎓",  
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
# INJECT FAVICON (replaces graduation cap)
# ============================================================
favicon_base64 = get_favicon_base64()
if favicon_base64:
    st.markdown(f'''
    <link rel="icon" type="image/png" href="data:image/png;base64,{favicon_base64}">
    ''', unsafe_allow_html=True)

# ============================================================
# CSS STYLES
# ============================================================
def inject_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    :root {
        --primary:        #1E3A8A;
        --primary-dark:   #172554;
        --primary-light:  #3B82F6;
        --primary-bg:     #DBEAFE;
        --primary-subtle: #EFF6FF;
        --accent:         #10B981;
        --accent-dark:    #059669;
        --accent-bg:      #D1FAE5;
        --warning:        #F59E0B;
        --warning-bg:     #FEF3C7;
        --danger:         #EF4444;
        --danger-bg:      #FEE2E2;
        --purple:         #8B5CF6;
        --purple-bg:      #EDE9FE;
        --bg:             #F1F5F9;
        --surface:        #FFFFFF;
        --surface-2:      #F8FAFC;
        --border:         #E2E8F0;
        --border-2:       #CBD5E1;
        --text-1:         #1E293B;
        --text-2:         #475569;
        --text-3:         #64748B;
        --text-4:         #94A3B8;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
        --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.10);
        --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.10);
        --r-sm: 8px; --r-md: 12px; --r-lg: 16px;
    }

    *, *::before, *::after { box-sizing: border-box; }

    html, body, .stApp {
        font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
        background-color: var(--bg) !important;
        color: var(--text-1) !important;
    }

    /* Make all chart text black for readability */
    .js-plotly-plot .plotly .main-svg text,
    .plotly .xtick text, .plotly .ytick text,
    .plotly .legend text, .plotly .gtitle,
    .plotly .annotation-text {
        fill: #1E293B !important;
        color: #1E293B !important;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1400px !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--surface) !important;
        border-right: 1px solid var(--border) !important;
    }
    [data-testid="stSidebar"] * {
        font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
        color: var(--text-1) !important;
    }

    /* Logo container in sidebar */
    .sidebar-logo {
        text-align: center;
        margin-bottom: 20px;
        padding: 10px;
    }
    .sidebar-logo img {
        max-width: 180px;
        border-radius: 12px;
    }

    /* Headers */
    h1 { font-size: 1.5rem !important; font-weight: 700 !important; color: var(--text-1) !important; }
    h2 { font-size: 1.2rem !important; font-weight: 600 !important; color: var(--text-1) !important; }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--r-md) !important;
        padding: 20px !important;
        box-shadow: var(--shadow-sm) !important;
    }
    [data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 700 !important; color: var(--text-1) !important; }
    [data-testid="stMetricLabel"] { font-size: 0.85rem !important; color: var(--text-3) !important; }

    /* Buttons - Light Grey */
    .stButton > button {
        background: #E2E8F0 !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: var(--r-sm) !important;
        font-weight: 600 !important;
        padding: 10px 22px !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background: #CBD5E1 !important;
        transform: translateY(-1px) !important;
    }

    /* KPI Cards */
    .kpi-card {
        background: var(--surface);
        border-radius: var(--r-md);
        padding: 20px;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border);
        position: relative;
        overflow: hidden;
        margin-bottom: 8px;
    }
    .kpi-card::before { content:''; position:absolute; top:0; left:0; width:4px; height:100%; }
    .kpi-card.blue::before   { background: var(--primary-light); }
    .kpi-card.green::before  { background: var(--accent); }
    .kpi-card.amber::before  { background: var(--warning); }
    .kpi-card.purple::before { background: var(--purple); }

    .kpi-value { font-size: 2.1rem; font-weight: 700; color: var(--text-1); line-height: 1; }
    .kpi-label { font-size: 0.85rem; color: var(--text-3); margin-top: 4px; }

    /* Badges */
    .badge-high    { background: var(--danger-bg); color: var(--danger); padding: 3px 10px; border-radius: 99px; font-size: 0.7rem; font-weight: 700; display: inline-block; }
    .badge-medium  { background: var(--warning-bg); color: var(--warning); padding: 3px 10px; border-radius: 99px; font-size: 0.7rem; font-weight: 700; display: inline-block; }
    .badge-low     { background: var(--accent-bg); color: var(--accent); padding: 3px 10px; border-radius: 99px; font-size: 0.7rem; font-weight: 700; display: inline-block; }

    .chip { display: inline-block; background: var(--primary-bg); color: var(--primary); padding: 3px 10px; border-radius: 99px; font-size: 0.7rem; font-weight: 600; margin: 2px; }

    .course-card { background: var(--surface-2); border-radius: var(--r-sm); padding: 14px 16px; border: 1px solid var(--border); margin-bottom: 10px; }

    .app-footer { text-align: center; padding: 20px 0 8px; font-size: 0.75rem; color: var(--text-4); border-top: 1px solid var(--border); margin-top: 48px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">', unsafe_allow_html=True)

inject_styles()

if not MODULES_LOADED:
    st.error(f"❌ Failed to load modules: {MODULE_ERROR}")
    st.stop()

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
# SIDEBAR WITH LOGO
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
        st.markdown("### 🎓 TVET Skills Intel")
    
    st.markdown("---")
    page = st.radio("Navigation", ["📊 Dashboard", "🔧 Skills Analysis", "🎓 Courses", "📄 Reports", "🗄️ Data Sources"], index=0)
    st.markdown("---")
    st.markdown("### 📊 System Status")
    if st.session_state.processed_jobs is not None:
        st.success(f"✅ Jobs loaded: {len(st.session_state.processed_jobs)}")
    else:
        st.info("⏳ No job data loaded")
    if st.session_state.curriculum_skills:
        st.success(f"✅ Curriculum: {len(st.session_state.curriculum_skills)} skills")
    else:
        st.info("⏳ No curriculum loaded")

# ============================================================
# DATA UPLOAD
# ============================================================
def render_data_upload():
    st.markdown("### 📤 Data Upload")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Job Postings")
        job_file = st.file_uploader("Upload job postings (CSV)", type=['csv'], key="job_upload")
        if job_file:
            df = st.session_state.data_loader.load_job_postings(job_file)
            if df is not None:
                st.success(f"✅ Loaded {len(df)} job postings")
                if st.button("🔧 Extract Skills from Jobs"):
                    with st.spinner("Extracting skills…"):
                        st.session_state.processed_jobs = st.session_state.nlp_pipeline.process_dataframe(df, text_column='description')
                        skill_freq = st.session_state.nlp_pipeline.get_skill_frequencies(st.session_state.processed_jobs)
                        st.session_state.gap_analyzer.set_market_frequencies(skill_freq)
                        st.success("✅ Skills extracted!")
                        st.rerun()
        else:
            if st.button("📊 Use Sample Job Data"):
                df = st.session_state.data_loader.generate_sample_job_data()
                st.session_state.processed_jobs = st.session_state.nlp_pipeline.process_dataframe(df, text_column='description')
                skill_freq = st.session_state.nlp_pipeline.get_skill_frequencies(st.session_state.processed_jobs)
                st.session_state.gap_analyzer.set_market_frequencies(skill_freq)
                st.success("✅ Sample data loaded!")
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
                    st.success(f"✅ {file.name} — {len(result['normalized_skills'])} skills")
            curriculum_freq = dict(Counter(all_skills))
            st.session_state.curriculum_skills = all_skills
            st.session_state.gap_analyzer.set_curriculum_frequencies(curriculum_freq)
            st.success(f"✅ Total: {len(set(all_skills))} unique curriculum skills")

# ============================================================
# RUN ANALYSIS
# ============================================================
def run_full_analysis():
    if st.session_state.processed_jobs is None:
        st.error("Please load job postings first")
        return False

    with st.spinner("Running gap analysis…"):
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
            st.success("✅ Analysis complete!")
            return True
    return False

# ============================================================
# TREND ANALYSIS FUNCTION
# ============================================================
def get_trend_analysis():
    """Analyze job posting trends over time"""
    if st.session_state.processed_jobs is None:
        return None, None, None
    
    df = st.session_state.processed_jobs.copy()
    
    # Look for date column
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
            growth = ((last_count - first_count) / first_count * 100) if first_count > 0 else 0
        else:
            growth = 0
        
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
# PDF REPORT GENERATION WITH LETTERHEAD
# ============================================================
def generate_pdf_report():
    """Generate a professional PDF report with letterhead and logo"""
    if not REPORTLAB_AVAILABLE:
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_file.close()
    
    # Create a temporary logo file for the PDF
    temp_logo_path = None
    logo_base64 = get_logo_base64()
    if logo_base64:
        temp_logo = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        temp_logo.write(base64.b64decode(logo_base64))
        temp_logo.close()
        temp_logo_path = temp_logo.name
    
    def add_letterhead(canvas, doc):
        """Add logo and header to each page"""
        canvas.saveState()
        
        # Add logo
        if temp_logo_path and os.path.exists(temp_logo_path):
            try:
                canvas.drawImage(temp_logo_path, 0.75*inch, letter[1] - 0.8*inch, width=1.2*inch, height=0.6*inch, preserveAspectRatio=True)
            except:
                pass
        
        # Add title text
        canvas.setFont("Helvetica-Bold", 14)
        canvas.setFillColor(colors.HexColor("#1E3A8A"))
        canvas.drawString(2.2*inch, letter[1] - 0.65*inch, "TVET Skills Intel")
        
        # Add subtitle
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.HexColor("#64748B"))
        canvas.drawString(2.2*inch, letter[1] - 0.8*inch, "AI-Powered Labour Market Intelligence for Kenyan TVET Institutions")
        
        # Horizontal line
        canvas.setStrokeColor(colors.HexColor("#E2E8F0"))
        canvas.line(0.75*inch, letter[1] - 0.95*inch, letter[0] - 0.75*inch, letter[1] - 0.95*inch)
        
        # Footer
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#94A3B8"))
        canvas.drawString(0.75*inch, 0.5*inch, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        canvas.drawRightString(letter[0] - 0.75*inch, 0.5*inch, f"Page {doc.page}")
        
        canvas.restoreState()
    
    doc = SimpleDocTemplate(temp_file.name, pagesize=letter,
                           topMargin=1.2*inch, bottomMargin=0.75*inch,
                           leftMargin=0.75*inch, rightMargin=0.75*inch)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                 fontSize=18, textColor=colors.HexColor('#1E3A8A'), spaceAfter=20)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'],
                                   fontSize=14, textColor=colors.HexColor('#1E40AF'), spaceAfter=12)
    normal_style = styles['Normal']
    
    story = []
    
    # Title
    story.append(Paragraph("Labour Market Intelligence Report", title_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", normal_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    total_jobs = len(st.session_state.processed_jobs) if st.session_state.processed_jobs is not None else 0
    total_gaps = len(st.session_state.gap_matrix) if st.session_state.gap_matrix is not None else 0
    total_courses = len(st.session_state.generated_courses)
    story.append(Paragraph(f"This report analyses {total_jobs} job postings, identifying {total_gaps} skills gaps and generating {total_courses} short course recommendations.", normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Trend Analysis
    story.append(Paragraph("Job Posting Trends", heading_style))
    monthly_counts, peak_month, trend_stats = get_trend_analysis()
    if monthly_counts is not None and len(monthly_counts) > 0:
        story.append(Paragraph(f"<b>Total jobs analysed:</b> {trend_stats['total']}", normal_style))
        story.append(Paragraph(f"<b>Peak month:</b> {peak_month['year_month_str']} ({peak_month['count']} jobs)", normal_style))
        story.append(Paragraph(f"<b>Growth rate:</b> {trend_stats['growth']:.1f}%", normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Top Skills
    story.append(Paragraph("Top 10 In-Demand Skills", heading_style))
    all_skills = []
    if st.session_state.processed_jobs is not None and 'normalized_skills' in st.session_state.processed_jobs.columns:
        for skills in st.session_state.processed_jobs['normalized_skills']:
            all_skills.extend(skills)
    skill_counts = Counter(all_skills)
    top_skills = skill_counts.most_common(10)
    
    skills_data = [['Rank', 'Skill', 'Frequency']]
    for i, (skill, count) in enumerate(top_skills, 1):
        skills_data.append([str(i), skill, str(count)])
    skills_table = Table(skills_data, colWidths=[0.8*inch, 3.5*inch, 1.2*inch])
    skills_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DBEAFE')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    story.append(skills_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Skills Gaps
    story.append(Paragraph("Prioritised Skills Gaps", heading_style))
    if st.session_state.prioritized_gaps is not None:
        gaps_data = [['Rank', 'Skill', 'Priority', 'Score']]
        for i, row in st.session_state.prioritized_gaps.head(10).iterrows():
            gaps_data.append([str(i+1), row['skill'], row['priority_tier'], f"{row['priority_score']:.2f}"])
        gaps_table = Table(gaps_data, colWidths=[0.8*inch, 3.0*inch, 1.0*inch, 1.0*inch])
        gaps_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DBEAFE')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        story.append(gaps_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Course Recommendations
    story.append(Paragraph("Recommended Short Courses", heading_style))
    for course in st.session_state.generated_courses[:5]:
        story.append(Paragraph(f"<b>📘 {course.get('title', 'N/A')}</b>", normal_style))
        story.append(Paragraph(f"Duration: {course.get('duration', 'N/A')} weeks | Level: {course.get('level', 'N/A')} | Priority: {course.get('priority', 'N/A')}", normal_style))
        story.append(Spacer(1, 0.1*inch))
    
    # Footer
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"TVET Skills Intel System | {datetime.now().strftime('%B %Y')}", 
                          ParagraphStyle('Footer', parent=normal_style, alignment=1, fontSize=8, textColor=colors.HexColor('#94A3B8'))))
    
    doc.build(story, onFirstPage=add_letterhead, onLaterPages=add_letterhead)
    
    # Clean up temp logo file
    if temp_logo_path and os.path.exists(temp_logo_path):
        os.unlink(temp_logo_path)
    
    return temp_file.name

# ============================================================
# DASHBOARD PAGE
# ============================================================
def render_dashboard():
    st.markdown('<h1>Labour Market Intelligence Dashboard</h1><p>AI-powered analysis of TVET skills demand across Kenya</p>', unsafe_allow_html=True)
    render_data_upload()
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Run Complete Analysis", use_container_width=True):
            run_full_analysis()
    st.markdown("---")
    
    if not (st.session_state.analysis_complete and st.session_state.processed_jobs is not None):
        st.info("Upload job data and click **Run Complete Analysis** to see results.")
        return
    
    # KPI Cards
    all_skills_flat = []
    if 'normalized_skills' in st.session_state.processed_jobs.columns:
        for skills in st.session_state.processed_jobs['normalized_skills']:
            all_skills_flat.extend(skills)
    
    cols = st.columns(4)
    kpi_data = [
        ("blue", len(st.session_state.processed_jobs), "Jobs Analysed"),
        ("green", len(set(all_skills_flat)), "Skills Extracted"),
        ("amber", len(st.session_state.gap_matrix) if st.session_state.gap_matrix is not None else 0, "Skills Gaps"),
        ("purple", len(st.session_state.generated_courses), "Courses Recommended"),
    ]
    for col, (color, value, label) in zip(cols, kpi_data):
        with col:
            st.markdown(f"""
            <div class="kpi-card {color}">
              <div class="kpi-value">{value:,}</div>
              <div class="kpi-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("---")
    
    # Trend Analysis Section
    st.markdown("### 📈 Job Posting Trends")
    monthly_counts, peak_month, trend_stats = get_trend_analysis()
    if monthly_counts is not None and len(monthly_counts) > 0:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Jobs", trend_stats['total'])
        col2.metric("Peak Month", f"{peak_month['year_month_str']}", f"{peak_month['count']} jobs")
        col3.metric("Growth Rate", f"{trend_stats['growth']:.1f}%")
        col4.metric("Monthly Avg", f"{trend_stats['avg']:.0f}")
        
        fig = px.line(monthly_counts, x='year_month_str', y='count', 
                      title='Job Postings Over Time',
                      markers=True, labels={'year_month_str': 'Month', 'count': 'Number of Jobs'})
        fig.update_traces(line_color='#1E3A8A', marker_color='#3B82F6')
        fig.update_layout(height=350, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Trend analysis requires a date column in your dataset.")
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📊 Top 10 In-Demand Skills")
        if all_skills_flat:
            skill_counts = Counter(all_skills_flat)
            top_df = pd.DataFrame(skill_counts.most_common(10), columns=['Skill', 'Count'])
            fig = px.bar(top_df, x='Count', y='Skill', orientation='h',
                         color='Count', color_continuous_scale='Blues', text='Count')
            fig.update_traces(textposition='outside', textfont_color='#1E293B')
            fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 Skills Gap Summary")
        if st.session_state.prioritized_gaps is not None:
            gap_df = st.session_state.prioritized_gaps.head(8)[['skill','priority_tier','priority_score']].copy()
            gap_df.columns = ['Skill','Priority','Score']
            color_map = {'High': '#EF4444', 'Medium': '#F59E0B', 'Low': '#10B981'}
            fig = px.bar(gap_df, x='Score', y='Skill', orientation='h',
                         color='Priority', color_discrete_map=color_map)
            fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    
    # Tables
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### ⚠️ Prioritised Skills Gaps")
        if st.session_state.prioritized_gaps is not None:
            disp = st.session_state.prioritized_gaps.head(8)[['skill','priority_tier','priority_score']].copy()
            disp.columns = ['Skill','Priority','Score']
            st.dataframe(disp, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### 🎓 Recommended Short Courses")
        for course in st.session_state.generated_courses[:4]:
            priority = course.get('priority','N/A')
            badge_cls = 'badge-high' if priority == 'High' else 'badge-medium'
            chips = ''.join(f'<span class="chip">{s}</span>' for s in course.get('skills',[])[:3])
            st.markdown(f"""
            <div class="course-card">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div style="font-weight:600;">📘 {course.get('title','N/A')}</div>
                <span class="{badge_cls}">{priority}</span>
              </div>
              <div style="font-size:0.78rem; color:var(--text-3); margin:8px 0;">⏱ {course.get('duration','N/A')} weeks | 📶 {course.get('level','N/A')}</div>
              <div>{chips}</div>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# SKILLS ANALYSIS PAGE
# ============================================================
def render_skills_analysis():
    st.markdown('<h1>Skills Analysis</h1><p>Analyze and compare skills demand across sectors</p>', unsafe_allow_html=True)
    st.markdown("---")
    render_data_upload()
    if st.session_state.processed_jobs is None or 'normalized_skills' not in st.session_state.processed_jobs.columns:
        st.info("Load job postings to see skills analysis.")
        return
    all_skills_flat = []
    for skills in st.session_state.processed_jobs['normalized_skills']:
        all_skills_flat.extend(skills)
    skill_counts = Counter(all_skills_flat)
    st.markdown("#### 📋 Compare Skills")
    selected = st.multiselect("Select skills to compare", list(skill_counts.keys()), default=list(skill_counts.keys())[:3])
    if selected:
        sel_df = pd.DataFrame([(s, skill_counts[s]) for s in selected], columns=['Skill','Frequency'])
        fig = px.bar(sel_df, x='Skill', y='Frequency', color='Skill',
                     color_discrete_sequence=['#1E3A8A','#10B981','#F59E0B','#EF4444','#8B5CF6'])
        fig.update_layout(height=380, showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    st.markdown("#### 📊 Top 20 Skills")
    top_df = pd.DataFrame(skill_counts.most_common(20), columns=['Skill','Frequency'])
    fig = px.bar(top_df, x='Frequency', y='Skill', orientation='h', color='Frequency', color_continuous_scale='Blues')
    fig.update_layout(height=560, coloraxis_showscale=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# COURSES PAGE
# ============================================================
def render_courses():
    st.markdown('<h1>Course Recommendations</h1><p>AI-generated short courses to address skills gaps</p>', unsafe_allow_html=True)
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
        priority = course.get('priority','N/A')
        badge_cls = 'badge-high' if priority == 'High' else 'badge-medium'
        with st.expander(f"📘 {course.get('title','N/A')}"):
            col1, col2 = st.columns([2,1])
            with col1:
                st.markdown(f"**Skill Gap:** `{course.get('skill_gap','N/A')}`")
                st.markdown(f"**Duration:** {course.get('duration','N/A')} weeks | **Level:** {course.get('level','N/A')}")
                st.markdown(f"**Prerequisites:** {', '.join(course.get('prerequisites',['None']))}")
                st.markdown("**Learning Outcomes:**")
                for o in course.get('learning_outcomes', []):
                    st.markdown(f"- {o}")
            with col2:
                st.markdown(f'<span class="{badge_cls}">{priority} Priority</span>', unsafe_allow_html=True)
                st.markdown(f"**Market Demand:** {course.get('market_demand',0)} mentions")
                st.markdown(f"**Gap Score:** {course.get('gap_score',0):.2f}")
            st.markdown("**Modules:** " + " · ".join(course.get('modules',[])))

# ============================================================
# REPORTS PAGE
# ============================================================
def render_reports():
    st.markdown('<h1>Reports</h1><p>Generate and download comprehensive market intelligence reports</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    if not st.session_state.analysis_complete:
        st.info("Run analysis first to generate reports.")
        return
    
    st.markdown("### 📈 Trend Analysis Preview")
    monthly_counts, peak_month, trend_stats = get_trend_analysis()
    if monthly_counts is not None and len(monthly_counts) > 0:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Jobs", trend_stats['total'])
        col2.metric("Peak Month", f"{peak_month['year_month_str']}", f"{peak_month['count']} jobs")
        col3.metric("Growth Rate", f"{trend_stats['growth']:.1f}%")
        col4.metric("Monthly Avg", f"{trend_stats['avg']:.0f}")
        fig = px.line(monthly_counts, x='year_month_str', y='count', 
                      title='Job Postings Over Time', markers=True)
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Trend data not available. Add a date column to your dataset.")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2,1])
    with col1:
        report_type = st.selectbox("Report Type", ["Full Analysis Report", "Skills Gap Summary", "Course Recommendations Only"])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📥 Generate PDF Report", use_container_width=True):
            pdf_file = generate_pdf_report()
            if pdf_file:
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=f,
                        file_name=f"tvet_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                os.unlink(pdf_file)
            else:
                st.error("PDF generation failed.")
    
    st.markdown("---")
    st.markdown("#### 📋 Report Preview")
    st.info("The PDF report includes: Executive Summary, Job Posting Trends, Top Skills, Skills Gaps, and Course Recommendations.")

# ============================================================
# DATA SOURCES PAGE
# ============================================================
def render_data_sources():
    st.markdown('<h1>Data Sources</h1><p>Job posting data from Kenya\'s leading employment platforms</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    sources = [
        ("LinkedIn", "fab fa-linkedin", "#0077B5", "3,847", "2h ago"),
        ("BrighterMonday", "fas fa-briefcase", "#FF6B35", "4,125", "1h ago"),
        ("Fuzu", "fas fa-search", "#10B981", "2,891", "3h ago"),
        ("MyJobMag", "fas fa-newspaper", "#3B82F6", "2,156", "4h ago"),
        ("IkoKazi", "fas fa-bullhorn", "#8B5CF6", "1,489", "5h ago"),
    ]
    cols = st.columns(5)
    for col, (name, icon, color, count, updated) in zip(cols, sources):
        with col:
            st.markdown(f"""
            <div style="background:white; border-radius:12px; padding:20px; text-align:center; border:1px solid #E2E8F0;">
              <div style="background:{color}; width:50px; height:50px; border-radius:12px; display:flex; align-items:center; justify-content:center; margin:0 auto 14px;">
                <i class="{icon}" style="color:white; font-size:1.3rem;"></i>
              </div>
              <div style="font-weight:600;">{name}</div>
              <div style="font-size:1.3rem; font-weight:700;">{count}</div>
              <div style="font-size:0.75rem; color:#64748B;">Jobs</div>
              <div style="font-size:0.7rem; color:#94A3B8;">⏱ Updated {updated}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    render_data_upload()
    st.markdown("---")
    st.markdown("### 📊 System Information")
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
if page == "📊 Dashboard":
    render_dashboard()
elif page == "🔧 Skills Analysis":
    render_skills_analysis()
elif page == "🎓 Courses":
    render_courses()
elif page == "📄 Reports":
    render_reports()
elif page == "🗄️ Data Sources":
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