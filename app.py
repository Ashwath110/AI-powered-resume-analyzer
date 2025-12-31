# ui/app.py

import streamlit as st
from skill_extractor import SkillExtractor
from matcher import ResumeJDMatcher
from ats_scorer import ATSScorer
from ai_detector import AIContentDetector
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import PyPDF2
import pdfplumber
from docx import Document
import io

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #a78bfa 0%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .subtitle {
        text-align: center;
        color: #9ca3af;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border: 1px solid #2d1b69;
    }
    .skill-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        margin: 0.2rem;
        border-radius: 20px;
        background-color: #7c3aed;
        color: white;
        font-size: 0.9rem;
        border: 1px solid #a78bfa;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #7c3aed 0%, #a855f7 100%);
        color: white;
        font-weight: bold;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        border: 1px solid #a78bfa;
        font-size: 1.1rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(124, 58, 237, 0.4);
        background: linear-gradient(90deg, #8b5cf6 0%, #c084fc 100%);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1a2e;
        border-radius: 8px;
        padding: 10px 20px;
        border: 1px solid #2d1b69;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #7c3aed 0%, #a855f7 100%);
        border: 1px solid #a78bfa;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Load Models
# -------------------------------
@st.cache_resource
def load_models():
    with st.spinner("🔄 Loading AI models..."):
        extractor = SkillExtractor("skill_ontology.json")
        matcher = ResumeJDMatcher()
        scorer = ATSScorer()
        ai_detector = AIContentDetector()
    return extractor, matcher, scorer, ai_detector

# -------------------------------
# Helper Functions
# -------------------------------
def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file using pdfplumber"""
    try:
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error extracting PDF: {str(e)}")
        return ""

def extract_text_from_docx(docx_file):
    """Extract text from DOCX file"""
    try:
        doc = Document(docx_file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        st.error(f"Error extracting DOCX: {str(e)}")
        return ""

def extract_text_from_file(uploaded_file):
    """Extract text from uploaded file (PDF or DOCX)"""
    if uploaded_file is None:
        return ""
    
    file_type = uploaded_file.type
    
    if file_type == "application/pdf":
        return extract_text_from_pdf(uploaded_file)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(uploaded_file)
    elif file_type == "text/plain":
        return uploaded_file.read().decode("utf-8")
    else:
        st.error(f"Unsupported file type: {file_type}")
        return ""

def check_resume_length(text):
    """
    Check if resume is within one page limit
    Returns: (is_valid, word_count, char_count, estimated_pages)
    """
    if not text:
        return False, 0, 0, 0
    
    # Calculate metrics
    words = text.split()
    word_count = len(words)
    char_count = len(text.strip())
    
    # One page estimates:
    # - Standard: ~500-600 words
    # - Characters: ~3000-3500 characters (with spaces)
    # Using conservative limits
    MAX_WORDS_ONE_PAGE = 600
    MAX_CHARS_ONE_PAGE = 3500
    
    # Calculate estimated pages based on both metrics
    pages_by_words = word_count / MAX_WORDS_ONE_PAGE
    pages_by_chars = char_count / MAX_CHARS_ONE_PAGE
    
    # Use the higher estimate for safety
    estimated_pages = max(pages_by_words, pages_by_chars)
    
    # Resume is valid if within one page
    is_valid = word_count <= MAX_WORDS_ONE_PAGE and char_count <= MAX_CHARS_ONE_PAGE
    
    return is_valid, word_count, char_count, estimated_pages

def create_gauge_chart(score, title):
    """Create an interactive gauge chart for scores"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20}},
        delta={'reference': 70, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#ffebee'},
                {'range': [50, 70], 'color': '#fff9c4'},
                {'range': [70, 85], 'color': '#c8e6c9'},
                {'range': [85, 100], 'color': '#a5d6a7'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 85
            }
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    return fig

def create_breakdown_chart(breakdown):
    """Create a radar chart for score breakdown"""
    categories = [k.replace('_', ' ').title() for k in breakdown.keys()]
    values = [v * 100 for v in breakdown.values()]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(102, 126, 234, 0.5)',
        line=dict(color='rgb(102, 126, 234)', width=2)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        showlegend=False,
        height=400,
        title="Score Breakdown Analysis"
    )
    return fig

def create_skill_comparison(resume_skills, jd_skills):
    """Create a Venn-like visualization for skill matching"""
    matched = set(resume_skills) & set(jd_skills)
    resume_only = set(resume_skills) - set(jd_skills)
    jd_only = set(jd_skills) - set(resume_skills)
    
    data = {
        'Category': ['Matched Skills', 'Resume Only', 'JD Only'],
        'Count': [len(matched), len(resume_only), len(jd_only)],
        'Skills': [
            ', '.join(list(matched)[:10]),
            ', '.join(list(resume_only)[:10]),
            ', '.join(list(jd_only)[:10])
        ]
    }
    
    df = pd.DataFrame(data)
    fig = px.bar(df, x='Category', y='Count', 
                 color='Category',
                 color_discrete_map={
                     'Matched Skills': '#4CAF50',
                     'Resume Only': '#2196F3',
                     'JD Only': '#FF9800'
                 },
                 title="Skill Gap Analysis",
                 hover_data=['Skills'])
    fig.update_layout(height=400, showlegend=False)
    return fig, matched, resume_only, jd_only

# -------------------------------
# Header
# -------------------------------
st.markdown('<h1 class="main-header">🎯 AI-Powered Resume Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Optimize your resume with ATS-style evaluation using advanced NLP & AI</p>', unsafe_allow_html=True)

# -------------------------------
# Sidebar
# -------------------------------
with st.sidebar:
    st.header("📊 About This Tool")
    st.markdown("""
    This AI-powered tool analyzes your resume against job descriptions using:
    
    ✅ **Skill Extraction** - Identifies and categorizes skills
    
    ✅ **Semantic Matching** - Uses transformer models for deep text analysis
    
    ✅ **ATS Scoring** - Evaluates like real Applicant Tracking Systems
    
    ✅ **Gap Analysis** - Shows missing skills and opportunities
    """)
    
    st.divider()
    
    st.header("⚙️ Analysis Settings")
    show_detailed = st.checkbox("Show Detailed Analysis", value=True)
    show_skills = st.checkbox("Show Skill Breakdown", value=True)
    show_recommendations = st.checkbox("Show Recommendations", value=True)
    
    st.divider()
    
    st.header("📈 Statistics")
    st.metric("Resumes Analyzed", "962", "Dataset Size")
    st.metric("AI Model", "MPNet-v2", "Transformer")
    
    st.divider()
    st.markdown("---")
    st.markdown("💡 **Pro Tip:** Use specific keywords from the job description in your resume!")

# Load models
skill_extractor, matcher, scorer, ai_detector = load_models()

# -------------------------------
# Main Content - Two Columns
# -------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📄 Your Resume")
    
    # Upload option
    upload_tab1, text_tab1 = st.tabs(["📁 Upload File", "✍️ Paste Text"])
    
    with upload_tab1:
        resume_file = st.file_uploader(
            "Upload your resume (PDF, DOCX, or TXT)",
            type=["pdf", "docx", "txt"],
            help="Upload your resume file and we'll extract the text automatically",
            key="resume_upload"
        )
        
        if resume_file:
            with st.spinner("📄 Extracting text from file..."):
                resume_text = extract_text_from_file(resume_file)
            
            if resume_text:
                st.success(f"✅ Extracted {len(resume_text)} characters from {resume_file.name}")
                with st.expander("📝 Preview extracted text"):
                    st.text_area("Extracted content", resume_text, height=200, key="resume_preview", disabled=True)
            else:
                resume_text = ""
                st.warning("⚠️ Could not extract text. Please try pasting text manually.")
        else:
            resume_text = ""
    
    with text_tab1:
        resume_text_manual = st.text_area(
            "Paste your resume content here",
            height=300,
            placeholder="Enter your resume text including skills, experience, education, projects, and certifications...",
            help="Include all relevant sections: skills, work experience, education, projects, and certifications",
            key="resume_text"
        )
        
        if resume_text_manual:
            resume_text = resume_text_manual
            word_count = len(resume_text_manual.split())
            st.caption(f"📝 Word count: {word_count}")

with col2:
    st.markdown("### 💼 Job Description")
    
    # Upload option
    upload_tab2, text_tab2 = st.tabs(["📁 Upload File", "✍️ Paste Text"])
    
    with upload_tab2:
        jd_file = st.file_uploader(
            "Upload job description (PDF, DOCX, or TXT)",
            type=["pdf", "docx", "txt"],
            help="Upload the job description file and we'll extract the text automatically",
            key="jd_upload"
        )
        
        if jd_file:
            with st.spinner("📄 Extracting text from file..."):
                job_description = extract_text_from_file(jd_file)
            
            if job_description:
                st.success(f"✅ Extracted {len(job_description)} characters from {jd_file.name}")
                with st.expander("📝 Preview extracted text"):
                    st.text_area("Extracted content", job_description, height=200, key="jd_preview", disabled=True)
            else:
                job_description = ""
                st.warning("⚠️ Could not extract text. Please try pasting text manually.")
        else:
            job_description = ""
    
    with text_tab2:
        job_description_manual = st.text_area(
            "Paste the target job description here",
            height=300,
            placeholder="Enter the complete job description including required skills, qualifications, and responsibilities...",
            help="Include the full job posting for best results",
            key="jd_text"
        )
        
        if job_description_manual:
            job_description = job_description_manual
            word_count = len(job_description_manual.split())
            st.caption(f"📝 Word count: {word_count}")

# -------------------------------
# Analyze Button
# -------------------------------
st.markdown("<br>", unsafe_allow_html=True)

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    analyze_button = st.button("🚀 Analyze Resume", use_container_width=True)

# -------------------------------
# Analysis Results
# -------------------------------
if analyze_button:
    if not resume_text or not job_description:
        st.error("⚠️ Please provide both resume text and job description to proceed!")
    else:
        # Progress bar for user engagement
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 0A: Check Resume Length
        status_text.text("📏 Checking resume length...")
        progress_bar.progress(5)
        is_valid_length, word_count, char_count, estimated_pages = check_resume_length(resume_text)
        
        if not is_valid_length:
            # REJECT if resume is too long
            st.markdown("---")
            st.markdown("## 📏 Resume Length Check")
            st.error(f"### ❌ RESUME REJECTED - TOO LONG")
            st.error(f"**Your resume exceeds the one-page limit!**")
            
            col_len1, col_len2, col_len3 = st.columns(3)
            
            with col_len1:
                st.metric("Word Count", f"{word_count:,}", 
                         delta=f"+{word_count - 600:,}",
                         delta_color="inverse")
            
            with col_len2:
                st.metric("Character Count", f"{char_count:,}",
                         delta=f"+{char_count - 3500:,}",
                         delta_color="inverse")
            
            with col_len3:
                st.metric("Estimated Pages", f"{estimated_pages:.1f}",
                         delta=f"+{estimated_pages - 1.0:.1f}",
                         delta_color="inverse")
            
            st.warning("### 📋 One Page Resume Standards:")
            st.markdown("""
            - **Maximum Words:** 600 words
            - **Maximum Characters:** 3,500 characters
            - **Your Resume:** {:.1f} pages (estimated)
            
            **Why One Page?**
            - ✅ Recruiters spend 6-7 seconds on initial review
            - ✅ Forces you to highlight only relevant information
            - ✅ Shows you can communicate concisely
            - ✅ Industry standard for professionals with <10 years experience
            """.format(estimated_pages))
            
            st.error("### 💡 How to Reduce Your Resume Length:")
            st.markdown("""
            1. **Remove outdated experience** - Focus on last 5-7 years
            2. **Cut redundant details** - Avoid repeating similar points
            3. **Use bullet points** - Not paragraphs
            4. **Quantify achievements** - Replace long descriptions with metrics
            5. **Remove personal statements** - Let your experience speak
            6. **Eliminate references line** - "References available upon request" is unnecessary
            7. **Use action verbs** - Start bullets with strong verbs (Developed, Led, Increased)
            8. **Keep only relevant skills** - Remove outdated or basic skills
            
            **Example Reduction:**
            - ❌ "I was responsible for the development and implementation of a comprehensive marketing strategy that resulted in significant improvements in customer engagement and brand awareness across multiple digital platforms"
            - ✅ "Developed marketing strategy that increased customer engagement by 40%"
            """)
            
            with st.expander("📊 Detailed Length Analysis"):
                st.markdown(f"""
                **Current Statistics:**
                - Words: {word_count:,} (Limit: 600)
                - Characters: {char_count:,} (Limit: 3,500)
                - Estimated Pages: {estimated_pages:.2f}
                - Words per page: ~600
                - Characters per page: ~3,500
                
                **Reduction Needed:**
                - Remove approximately **{word_count - 600:,} words**
                - Or reduce by **{char_count - 3500:,} characters**
                - Target reduction: **{((estimated_pages - 1.0) / estimated_pages * 100):.1f}%**
                """)
            
            # Stop further processing
            progress_bar.empty()
            status_text.empty()
            st.stop()
        
        else:
            # Show length check passed
            st.markdown("---")
            st.markdown("## 📏 Resume Length Check")
            st.success(f"### ✅ LENGTH APPROVED - One Page Resume")
            
            col_len1, col_len2, col_len3 = st.columns(3)
            
            with col_len1:
                st.metric("Word Count", f"{word_count:,}",
                         delta=f"{600 - word_count:,} remaining")
            
            with col_len2:
                st.metric("Character Count", f"{char_count:,}",
                         delta=f"{3500 - char_count:,} remaining")
            
            with col_len3:
                st.metric("Estimated Pages", f"{estimated_pages:.2f}",
                         delta="Within limit ✓",
                         delta_color="off")
        
        # Step 0B: AI Detection
        status_text.text("🔍 Checking if resume is human-written...")
        progress_bar.progress(10)
        is_ai, ai_score, ai_details = ai_detector.detect_ai_content(resume_text)
        recommendation = ai_detector.get_recommendation(is_ai, ai_details['confidence'])
        
        # Display AI Detection Results
        st.markdown("---")
        st.markdown("## 🤖 AI Content Detection")
        
        if is_ai and ai_details['confidence'] > 60:
            # REJECT if AI-generated with high confidence
            st.error(f"### ❌ RESUME REJECTED")
            st.error(recommendation)
            
            col_ai1, col_ai2 = st.columns(2)
            
            with col_ai1:
                st.metric("AI Probability", f"{ai_details['ai_probability']:.1f}%", 
                         delta=f"{ai_details['ai_probability'] - 50:.1f}%",
                         delta_color="inverse")
                st.metric("Confidence", f"{ai_details['confidence']:.1f}%")
            
            with col_ai2:
                st.metric("Human Probability", f"{ai_details['human_probability']:.1f}%",
                         delta=f"{ai_details['human_probability'] - 50:.1f}%")
                st.metric("Verdict", ai_details['verdict'])
            
            # Show detailed metrics
            with st.expander("📊 Detection Metrics Details"):
                metrics_df = pd.DataFrame([
                    {"Metric": "Perplexity", "Value": ai_details['metrics']['perplexity'], "Indicator": "Lower = More AI-like"},
                    {"Metric": "Burstiness", "Value": ai_details['metrics']['burstiness'], "Indicator": "Higher = More Human-like"},
                    {"Metric": "AI Phrases Found", "Value": ai_details['metrics']['ai_phrases_found'], "Indicator": "Higher = More AI-like"},
                    {"Metric": "Repetition Rate", "Value": f"{ai_details['metrics']['repetition_rate']:.1f}%", "Indicator": "Higher = More AI-like"},
                    {"Metric": "Formality Score", "Value": f"{ai_details['metrics']['formality_score']:.1f}%", "Indicator": "Higher = More AI-like"}
                ])
                st.dataframe(metrics_df, use_container_width=True)
            
            st.warning("### 💡 How to Fix This:")
            st.markdown("""
            1. **Rewrite in your own words** - Add personal experiences and specific examples
            2. **Use natural language** - Write like you speak, avoid overly formal phrases
            3. **Add specifics** - Include concrete numbers, project names, and real outcomes
            4. **Show personality** - Let your unique voice and experience shine through
            5. **Avoid generic phrases** - Remove clichés like "results-driven" and "proven track record"
            """)
            
            # Stop further processing
            progress_bar.empty()
            status_text.empty()
            st.stop()
        
        elif is_ai:
            # Warning but continue
            st.warning(f"### ⚠️ AI Detection Warning")
            st.warning(recommendation)
            
            col_ai1, col_ai2 = st.columns(2)
            with col_ai1:
                st.metric("AI Probability", f"{ai_details['ai_probability']:.1f}%")
            with col_ai2:
                st.metric("Human Probability", f"{ai_details['human_probability']:.1f}%")
            
            st.info("📝 **Continuing with analysis**, but consider rewriting for better authenticity...")
        
        else:
            # Accepted - Human-written
            st.success(f"### ✅ RESUME ACCEPTED")
            st.success(recommendation)
            
            col_ai1, col_ai2 = st.columns(2)
            with col_ai1:
                st.metric("Human Probability", f"{ai_details['human_probability']:.1f}%",
                         delta=f"+{ai_details['confidence']:.1f}%")
            with col_ai2:
                st.metric("Authenticity", "Verified ✓")
        
        # Step 1: Skill Extraction
        status_text.text("🔍 Extracting skills from resume...")
        progress_bar.progress(25)
        skill_output = skill_extractor.extract(resume_text)
        
        # Step 2: JD Analysis
        status_text.text("📋 Analyzing job description...")
        progress_bar.progress(50)
        jd_skill_output = skill_extractor.extract(job_description)
        jd_skills = jd_skill_output["normalized_skills"]
        
        # Step 3: Semantic Matching
        status_text.text("🤖 Running AI semantic analysis...")
        progress_bar.progress(75)
        semantic_score = matcher.match(resume_text, job_description)
        
        # Step 4: ATS Scoring
        status_text.text("📊 Calculating ATS score...")
        progress_bar.progress(90)
        resume_json = {
            "skills": skill_output["normalized_skills"],
            "experience": resume_text,
            "education": resume_text,
            "projects": resume_text
        }
        
        final_score, breakdown = scorer.calculate_score(
            resume_json=resume_json,
            skill_output=skill_output,
            jd_skills=jd_skills,
            semantic_score=semantic_score,
            resume_text=resume_text
        )
        
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        
        # Clear progress indicators
        import time
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        # -------------------------------
        # Display Results
        # -------------------------------
        st.markdown("---")
        st.markdown("## 📊 Analysis Results")
        
        # Overall Score with visual indicator
        score_color = "🟢" if final_score >= 85 else "🟡" if final_score >= 70 else "🔴"
        st.markdown(f"### {score_color} Overall ATS Score: **{final_score:.1f}/100**")
        
        if final_score >= 85:
            st.success("🎉 **Excellent!** Your resume is a strong match – highly likely to be shortlisted!")
        elif final_score >= 70:
            st.info("👍 **Good!** Your resume is a decent match – minor improvements could help!")
        else:
            st.warning("⚠️ **Needs Work!** Your resume needs optimization to improve your chances!")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gauge Chart for Overall Score
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.plotly_chart(create_gauge_chart(final_score, "ATS Score"), use_container_width=True)
        
        with col_g2:
            st.plotly_chart(create_breakdown_chart(breakdown), use_container_width=True)
        
        # Detailed Breakdown
        if show_detailed:
            st.markdown("---")
            st.markdown("### 📈 Detailed Score Breakdown")
            
            cols = st.columns(5)
            metrics = [
                ("Skill Match", breakdown["skill_match"], "🎯"),
                ("Semantic Match", breakdown["semantic_match"], "🤖"),
                ("Completeness", breakdown["section_completeness"], "📋"),
                ("Balance", breakdown["category_balance"], "⚖️"),
                ("Formatting", breakdown["formatting"], "✨")
            ]
            
            for col, (name, value, icon) in zip(cols, metrics):
                with col:
                    st.metric(
                        label=f"{icon} {name}",
                        value=f"{value * 100:.1f}%",
                        delta=f"{(value * 100) - 70:.1f}%" if value * 100 != 70 else "0%"
                    )
        
        # Skill Analysis
        if show_skills:
            st.markdown("---")
            st.markdown("### 🎯 Skill Gap Analysis")
            
            fig_skills, matched, resume_only, jd_only = create_skill_comparison(
                skill_output["normalized_skills"],
                jd_skills
            )
            
            st.plotly_chart(fig_skills, use_container_width=True)
            
            col_sk1, col_sk2, col_sk3 = st.columns(3)
            
            with col_sk1:
                st.markdown("#### ✅ Matched Skills")
                st.success(f"**{len(matched)}** skills matched")
                if matched:
                    for skill in sorted(matched):
                        st.markdown(f"<span class='skill-badge'>✓ {skill}</span>", unsafe_allow_html=True)
                else:
                    st.info("No matched skills found")
            
            with col_sk2:
                st.markdown("#### 💼 Your Extra Skills")
                st.info(f"**{len(resume_only)}** additional skills")
                if resume_only:
                    for skill in sorted(list(resume_only)[:10]):
                        st.markdown(f"<span class='skill-badge'>• {skill}</span>", unsafe_allow_html=True)
                    if len(resume_only) > 10:
                        st.caption(f"...and {len(resume_only) - 10} more")
            
            with col_sk3:
                st.markdown("#### ⚠️ Missing Skills")
                st.warning(f"**{len(jd_only)}** skills needed")
                if jd_only:
                    for skill in sorted(list(jd_only)[:10]):
                        st.markdown(f"<span class='skill-badge'>! {skill}</span>", unsafe_allow_html=True)
                    if len(jd_only) > 10:
                        st.caption(f"...and {len(jd_only) - 10} more")
        
        # Skill Categories
        st.markdown("---")
        st.markdown("### 🏷️ Your Skills by Category")
        
        if skill_output.get("skill_categories"):
            cat_cols = st.columns(len(skill_output["skill_categories"]))
            for col, (category, skills) in zip(cat_cols, skill_output["skill_categories"].items()):
                with col:
                    st.markdown(f"**{category}**")
                    for skill in skills:
                        st.markdown(f"• {skill}")
        
        # Recommendations
        if show_recommendations:
            st.markdown("---")
            st.markdown("### 💡 Recommendations to Improve Your Score")
            
            recommendations = []
            
            if breakdown["skill_match"] < 0.7:
                recommendations.append(("🎯 **Add Missing Skills**", 
                    f"Your skill match is {breakdown['skill_match']*100:.1f}%. Add these skills: {', '.join(list(jd_only)[:5])}"))
            
            if breakdown["semantic_match"] < 0.7:
                recommendations.append(("📝 **Improve Content Relevance**",
                    f"Your semantic match is {breakdown['semantic_match']*100:.1f}%. Use more keywords from the job description in context."))
            
            if breakdown["section_completeness"] < 1.0:
                recommendations.append(("📋 **Complete All Sections**",
                    "Make sure your resume includes: Experience, Education, Skills, and Projects sections."))
            
            if breakdown["category_balance"] < 0.7:
                recommendations.append(("⚖️ **Balance Skill Categories**",
                    "Diversify your skills across Programming, Frameworks, Tools, and Domain Knowledge."))
            
            if breakdown["formatting"] < 0.7:
                recommendations.append(("✨ **Improve Formatting**",
                    "Ensure your resume is well-structured with clear sections and bullet points."))
            
            if not recommendations:
                st.success("🎉 **Excellent work!** Your resume is well-optimized!")
            else:
                for i, (title, desc) in enumerate(recommendations, 1):
                    with st.expander(f"{i}. {title}"):
                        st.write(desc)
        
        # Download Results
        st.markdown("---")
        st.markdown("### 📥 Export Results")
        
        results_text = f"""
ATS RESUME ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
========================

OVERALL SCORE: {final_score:.1f}/100

SCORE BREAKDOWN:
- Skill Match: {breakdown['skill_match']*100:.1f}%
- Semantic Match: {breakdown['semantic_match']*100:.1f}%
- Section Completeness: {breakdown['section_completeness']*100:.1f}%
- Category Balance: {breakdown['category_balance']*100:.1f}%
- Formatting: {breakdown['formatting']*100:.1f}%

MATCHED SKILLS ({len(matched)}):
{', '.join(sorted(matched))}

MISSING SKILLS ({len(jd_only)}):
{', '.join(sorted(jd_only))}

YOUR ADDITIONAL SKILLS ({len(resume_only)}):
{', '.join(sorted(resume_only))}
"""
        
        st.download_button(
            label="📄 Download Analysis Report",
            data=results_text,
            file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>AI-Powered Resume Analyzer</strong> | Built with Streamlit, Transformers & NLP</p>
    <p>📊 Analyzed 962+ resumes | 🤖 Powered by MPNet-v2 Transformer</p>
</div>
""", unsafe_allow_html=True)

