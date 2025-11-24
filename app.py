# app.py
import streamlit as st
from io import BytesIO
import pdfplumber

from agent import tailor_resume, extract_pdf_text_from_bytes

# Page configuration
st.set_page_config(
    page_title="Resume Tailor AI",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f3d7a;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2E86AB;
        border-bottom: 2px solid #2E86AB;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-card h3 {
        margin: 0 0 10px 0;
        color: #1f3d7a;
        font-size: 1.3rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .metric-card p {
        margin: 0;
        color: #6c757d;
        line-height: 1.5;
    }
    .skill-match {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 10px;
        margin: 5px 0;
        border-radius: 0 5px 5px 0;
    }
    .skill-missing {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 10px;
        margin: 5px 0;
        border-radius: 0 5px 5px 0;
    }
    .bullet-improved {
        background-color: #e7f3ff;
        border-left: 5px solid #007bff;
        padding: 10px;
        margin: 5px 0;
        border-radius: 0 5px 5px 0;
    }
    .cover-letter-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .progress-container {
        background-color: #e9ecef;
        border-radius: 10px;
        padding: 3px;
        margin: 10px 0;
    }
    .progress-bar {
        background-color: #2E86AB;
        height: 20px;
        border-radius: 8px;
        text-align: center;
        color: white;
        font-weight: bold;
        line-height: 20px;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .upload-box {
        border: 2px dashed #2E86AB;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }
    .stButton button {
        background-color: #2E86AB;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #1f3d7a;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Header section
st.markdown('<h1 class="main-header">💼 Resume Tailor AI</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #6c757d;'>Optimize your resume for any job description using AI-powered analysis</p>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("<h2 style='color: #1f3d7a;'>📁 Upload & Options</h2>", unsafe_allow_html=True)
    
    st.markdown("<div class='upload-box'>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"], help="Upload a text-based PDF resume for analysis")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='color: #2E86AB; margin-top: 30px;'>📋 Job Description</h3>", unsafe_allow_html=True)
    jd = st.text_area(
        "Paste the job description here", 
        height=300, 
        placeholder="Paste the full job description including required skills, qualifications, and responsibilities...",
        help="The more detailed the job description, the better the analysis will be"
    )
    
    analyze_btn = st.button("🚀 Analyze & Tailor Resume")
    
    st.markdown("---")
    st.markdown("<h4 style='color: #1f3d7a;'>💡 Tips for Best Results</h4>", unsafe_allow_html=True)
    st.markdown("""
    - Ensure your resume PDF is text-based (not scanned)
    - Include a detailed job description with required skills
    - Review and customize the AI suggestions before using
    """)

# Main content area
if analyze_btn:
    if not jd or not uploaded_file:
        st.error("❌ Please provide both a job description and upload your resume to proceed.")
    else:
        # Process the uploaded file
        with st.spinner("🔄 Processing your resume and analyzing against the job description..."):
            pdf_bytes = uploaded_file.read()
            resume_text = extract_pdf_text_from_bytes(pdf_bytes)

        if resume_text.strip() == "":
            st.error("❌ Could not extract text from your PDF. It may be a scanned document or image-based PDF.")
            st.markdown("""
            **Solutions:**
            - Upload a text-based PDF (not scanned)
            - Use OCR software to convert your scanned PDF to text first
            - Copy and paste your resume text directly into the job description field
            """)
        else:
            with st.spinner("🤖 AI is analyzing your resume and generating tailored content..."):
                response = tailor_resume(jd, resume_text)

            st.markdown("---")
            
            if "error" in response and response.get("error") != "parse_failure":
                st.error(f"❌ Error: {response['error']}")
            elif "result" in response:
                r = response["result"]
                
                # Match Score Section
                st.markdown('<div class="sub-header">📈 Resume Match Score</div>', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    match_score = min(max(r.get("match_score", 0), 0), 100)
                    st.markdown(f'<div class="progress-container"><div class="progress-bar" style="width: {match_score}%">{match_score}% Match</div></div>', unsafe_allow_html=True)
                
                with col2:
                    st.metric("Match Score", f"{match_score}%")
                
                with col3:
                    st.metric("Status", "Good Fit" if match_score >= 70 else "Needs Improvement")
                
                # Skills Analysis Section
                st.markdown('<div class="sub-header">🔍 Skills Analysis</div>', unsafe_allow_html=True)
                
                c1, c2 = st.columns([1, 1])
                
                with c1:
                    st.markdown("### ✅ Matched Skills")
                    if isinstance(r["matched_skills"], list):
                        for s in r["matched_skills"]:
                            st.markdown(f'<div class="skill-match">{s}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="skill-match">{r["matched_skills"]}</div>', unsafe_allow_html=True)
                
                with c2:
                    st.markdown("### ❌ Missing Skills")
                    if isinstance(r["missing_skills"], list):
                        for s in r["missing_skills"]:
                            st.markdown(f'<div class="skill-missing">{s}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="skill-missing">{r["missing_skills"]}</div>', unsafe_allow_html=True)
                
                # Improved Resume Section
                st.markdown('<div class="sub-header">📝 Improved Resume Bullet Points</div>', unsafe_allow_html=True)
                st.markdown("<p>Use these AI-suggested bullet points to strengthen your resume:</p>", unsafe_allow_html=True)
                
                if isinstance(r["improved_bullets"], list):
                    for i, b in enumerate(r["improved_bullets"]):
                        st.markdown(f'<div class="bullet-improved">{b}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="bullet-improved">{r["improved_bullets"]}</div>', unsafe_allow_html=True)
                
                # Cover Letter Section
                st.markdown('<div class="sub-header">📮 Tailored Cover Letter</div>', unsafe_allow_html=True)
                st.markdown("<p>Customize this AI-generated cover letter for your application:</p>", unsafe_allow_html=True)
                
                st.markdown('<div class="cover-letter-box">', unsafe_allow_html=True)
                st.write(r["cover_letter"])
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Download Section
                st.markdown('<div class="sub-header">💾 Export Results</div>', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.download_button(
                        label="📄 Download Analysis Report",
                        data=f"""
Resume Match Analysis Report

Match Score: {match_score}%

MATCHED SKILLS:
{chr(10).join(['• ' + skill for skill in (r['matched_skills'] if isinstance(r['matched_skills'], list) else [r['matched_skills']])])}

MISSING SKILLS:
{chr(10).join(['• ' + skill for skill in (r['missing_skills'] if isinstance(r['missing_skills'], list) else [r['missing_skills']])])}

IMPROVED BULLET POINTS:
{chr(10).join(['• ' + bullet for bullet in (r['improved_bullets'] if isinstance(r['improved_bullets'], list) else [r['improved_bullets']])])}

COVER LETTER:
{r['cover_letter']}
                        """,
                        file_name="resume_analysis_report.txt",
                        mime="text/plain"
                    )
                
                with col2:
                    st.download_button(
                        label="📝 Download Cover Letter",
                        data=r["cover_letter"],
                        file_name="tailored_cover_letter.txt",
                        mime="text/plain"
                    )
                
                with col3:
                    st.download_button(
                        label="🔍 Download Skills Analysis",
                        data=f"""
Matched Skills:
{chr(10).join(['• ' + skill for skill in (r['matched_skills'] if isinstance(r['matched_skills'], list) else [r['matched_skills']])])}

Missing Skills:
{chr(10).join(['• ' + skill for skill in (r['missing_skills'] if isinstance(r['missing_skills'], list) else [r['missing_skills']])])}
                        """,
                        file_name="skills_analysis.txt",
                        mime="text/plain"
                    )

            else:
                # Parse failure - show raw text for debugging
                st.error("❌ Agent response could not be parsed. Showing raw output for debugging.")
                raw = response.get("raw", "")
                st.text_area("Raw agent output", raw, height=400)
                st.write("Exception:", response.get("exception", ""))

# Default state - before analysis
else:
    st.markdown("---")
    
    # Features section
    st.markdown('<div class="sub-header">✨ How It Works</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Skills Analysis")
        st.markdown("Identifies which of your skills match the job requirements and highlights gaps you should address.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### ✍️ Resume Optimization")
        st.markdown("Provides improved bullet points that better showcase your experience for the specific role.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 📝 Cover Letter Generation")
        st.markdown("Creates a tailored cover letter that highlights your most relevant qualifications.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Instructions
    st.markdown("---")
    st.markdown('<div class="sub-header">🚀 Get Started</div>', unsafe_allow_html=True)
    
    st.markdown("""
    1. **Upload** your current resume as a PDF file
    2. **Paste** the job description you're targeting
    3. **Click** the "Analyze & Tailor Resume" button
    4. **Review** the AI-generated insights and suggestions
    5. **Customize** and use the recommendations to strengthen your application
    """)