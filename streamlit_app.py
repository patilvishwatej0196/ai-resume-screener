# streamlit_app.py
# This is the web interface for our AI Resume Screening Platform
# Streamlit turns Python scripts into interactive web apps
# No HTML or CSS needed — everything is Python

# Import streamlit — the web framework
import streamlit as st

# Import our custom modules built in Days 2-4
from resume_reader import extract_text_from_pdf
from parser import parse_resume
from jd_extractor import extract_jd_keywords
from matcher import get_bert_score, get_combined_score

# Import other libraries
import tempfile  # creates temporary files for uploaded PDFs
import os        # file path handling
import time      # for loading animations


# -------------------------------------------------------
# PAGE CONFIGURATION
# Must be the first streamlit command in the file
# -------------------------------------------------------

st.set_page_config(
    page_title="AI Resume Screener",   # browser tab title
    page_icon="🤖",                    # browser tab icon
    layout="wide",                     # use full screen width
    initial_sidebar_state="expanded"   # sidebar open by default
)


# -------------------------------------------------------
# CUSTOM CSS STYLING
# Makes the app look professional
# -------------------------------------------------------

st.markdown("""
<style>
    /* Main background */
    .main { background-color: #f8f9fa; }

    /* Score cards */
    .score-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
        margin: 8px 0;
    }

    /* Big score number */
    .score-number {
        font-size: 42px;
        font-weight: bold;
        margin: 0;
    }

    /* Score label */
    .score-label {
        font-size: 13px;
        color: #666;
        margin-top: 4px;
    }

    /* Green score */
    .score-green { color: #28a745; }

    /* Yellow score */
    .score-yellow { color: #ffc107; }

    /* Red score */
    .score-red { color: #dc3545; }

    /* Skill tag */
    .skill-tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        margin: 3px;
        font-size: 13px;
        font-weight: 500;
    }

    /* Matched skill - green */
    .skill-matched {
        background: #d4edda;
        color: #155724;
    }

    /* Missing skill - red */
    .skill-missing {
        background: #f8d7da;
        color: #721c24;
    }

    /* Candidate card */
    .candidate-card {
        background: white;
        padding: 16px 20px;
        border-radius: 10px;
        border-left: 5px solid #2E74B5;
        margin: 10px 0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }

    /* Header banner */
    .header-banner {
        background: linear-gradient(135deg, #1F3864, #2E74B5);
        color: white;
        padding: 24px 32px;
        border-radius: 12px;
        margin-bottom: 24px;
    }
</style>
""", unsafe_allow_html=True)


# -------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------

def get_score_color(score):
    # Returns color class based on score value
    if score >= 70:
        return "score-green"    # green for strong match
    elif score >= 50:
        return "score-yellow"   # yellow for moderate match
    else:
        return "score-red"      # red for weak match


def get_decision(score):
    # Returns shortlist decision based on score
    if score >= 70:
        return "✅ SHORTLISTED", "#28a745"
    elif score >= 50:
        return "🟡 REVIEW MANUALLY", "#ffc107"
    else:
        return "❌ NOT SHORTLISTED", "#dc3545"


def score_to_bar(score, width=200):
    # Creates an HTML progress bar for a score
    color = "#28a745" if score >= 70 else "#ffc107" if score >= 50 else "#dc3545"
    filled = int((score / 100) * width)
    return f"""
    <div style="background:#e9ecef;border-radius:10px;height:12px;width:{width}px;display:inline-block;">
        <div style="background:{color};width:{filled}px;height:12px;border-radius:10px;"></div>
    </div>
    <span style="font-size:14px;font-weight:bold;color:{color};margin-left:8px;">{score}%</span>
    """


# -------------------------------------------------------
# HEADER SECTION
# -------------------------------------------------------

# Main header banner
st.markdown("""
<div class="header-banner">
    <h1 style="margin:0;font-size:28px;">🤖 AI Resume Screening Platform</h1>
    <p style="margin:6px 0 0 0;opacity:0.85;font-size:15px;">
        Powered by Sentence-BERT + spaCy NLP | Built by Vishwatej Patil
    </p>
</div>
""", unsafe_allow_html=True)


# -------------------------------------------------------
# SIDEBAR — Job Description Input
# -------------------------------------------------------

# st.sidebar puts everything in the left panel
with st.sidebar:

    # Sidebar title
    st.markdown("## 📋 Job Description")
    st.markdown("---")

    # Text area for job description input
    # height=300 makes it tall enough for full JD
    jd_text = st.text_area(
        "Paste the Job Description here",
        height=300,
        placeholder="""Job Title: Python Developer
Required Skills:
- Python, Flask, FastAPI
- SQL, MySQL
- Git, GitHub, Docker
- REST APIs
Experience: 0-2 years"""
    )

    st.markdown("---")

    # Shortlist threshold slider
    # Recruiter can adjust what score = shortlisted
    st.markdown("### ⚙️ Settings")
    threshold = st.slider(
        "Shortlist Threshold (%)",
        min_value=30,    # minimum score to show
        max_value=90,    # maximum threshold
        value=60,        # default value
        step=5,          # moves in steps of 5
        help="Candidates above this score are shortlisted"
    )

    st.markdown("---")

    # Show what the threshold means
    st.markdown(f"""
    **Score Guide:**
    - 🟢 ≥ {threshold}% → Shortlisted
    - 🟡 ≥ 50% → Review
    - 🔴 < 50% → Rejected
    """)

    st.markdown("---")
    st.markdown("**Tech Stack:**")
    st.markdown("🧠 Sentence-BERT")
    st.markdown("📝 spaCy NLP")
    st.markdown("📄 pdfplumber")
    st.markdown("🐍 Python 3.x")


# -------------------------------------------------------
# MAIN AREA — Resume Upload
# -------------------------------------------------------

# Main title
st.markdown("## 📄 Upload Resumes")

# File uploader — accepts multiple PDF files
# accept_multiple_files=True lets user upload many at once
uploaded_files = st.file_uploader(
    "Upload one or more PDF resumes",
    type=["pdf"],                    # only PDF files
    accept_multiple_files=True,      # allow multiple uploads
    help="Upload PDF resumes to screen and rank"
)

# Show instructions if nothing uploaded yet
if not uploaded_files:
    st.info("👆 Upload PDF resumes above and paste a job description in the sidebar to start screening")

    # Show example of what the results will look like
    with st.expander("📖 How it works"):
        st.markdown("""
        1. **Paste** the job description in the sidebar
        2. **Upload** one or more PDF resumes above
        3. **Click** the Analyze button
        4. **See** BERT score, keyword score, and final match score
        5. **Review** matched skills and skill gaps
        6. **Download** the ranked shortlist
        """)


# -------------------------------------------------------
# ANALYZE BUTTON + RESULTS
# -------------------------------------------------------

# Only show the Analyze button if files are uploaded
if uploaded_files and jd_text:

    # Center the analyze button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Big analyze button
        analyze = st.button(
            "🔍 Analyze Resumes",
            use_container_width=True,
            type="primary"   # makes it blue and prominent
        )

    # When button is clicked
    if analyze:

        # ── Extract JD keywords first ──
        with st.spinner("Extracting job requirements..."):
            # Get keywords from the job description text
            jd_keywords = extract_jd_keywords(jd_text)

        # Show extracted JD keywords
        st.markdown("### 🎯 Job Requirements Detected")
        if jd_keywords:
            # Display each keyword as a colored tag
            tags_html = " ".join([
                f'<span class="skill-tag skill-matched">{kw}</span>'
                for kw in jd_keywords[:20]  # show max 20
            ])
            st.markdown(tags_html, unsafe_allow_html=True)
        else:
            st.warning("No specific skill keywords detected in JD")

        st.markdown("---")
        st.markdown("## 👥 Candidate Results")

        # List to store all results for leaderboard
        all_results = []

        # ── Process each uploaded resume ──
        for uploaded_file in uploaded_files:

            # Get the filename without extension for display
            candidate_name = uploaded_file.name.replace('.pdf', '')

            # Show processing status
            with st.spinner(f"Analyzing {uploaded_file.name}..."):

                # Save uploaded file to a temporary location
                # pdfplumber needs a real file path, not a stream
                with tempfile.NamedTemporaryFile(
                    delete=False,         # keep file until we delete it
                    suffix='.pdf'         # give it .pdf extension
                ) as tmp_file:

                    # Write the uploaded file content to temp file
                    tmp_file.write(uploaded_file.read())
                    tmp_path = tmp_file.name  # save the temp file path

                # Extract text from the PDF
                resume_text = extract_text_from_pdf(tmp_path)

                # Delete the temp file after reading
                os.unlink(tmp_path)

                # If we got text from the PDF
                if resume_text:

                    # Parse the resume for name, email, skills
                    resume_data = parse_resume(resume_text)

                    # Get BERT semantic similarity score
                    bert_score = get_bert_score(resume_text, jd_text)

                    # Calculate keyword match score
                    resume_skills = set(resume_data['skills'])
                    jd_set = set(jd_keywords)
                    matched = resume_skills & jd_set
                    missing = jd_set - resume_skills

                    if len(jd_set) > 0:
                        keyword_score = round(
                            len(matched) / len(jd_set) * 100, 1
                        )
                    else:
                        keyword_score = 0.0

                    # Calculate combined final score
                    final_score = get_combined_score(bert_score, keyword_score)

                    # Get shortlist decision
                    decision, decision_color = get_decision(final_score)

                    # Store result for leaderboard
                    all_results.append({
                        "file": uploaded_file.name,
                        "name": resume_data['name'],
                        "email": resume_data['email'],
                        "bert_score": bert_score,
                        "keyword_score": keyword_score,
                        "final_score": final_score,
                        "matched": sorted(list(matched)),
                        "missing": sorted(list(missing)),
                        "decision": decision,
                        "skills_count": resume_data['skill_count']
                    })

                else:
                    # PDF had no extractable text
                    st.error(f"Could not extract text from {uploaded_file.name}")
                    continue

            # ── Display result for this candidate ──
            with st.container():

                # Candidate header
                st.markdown(f"""
                <div class="candidate-card">
                    <h3 style="margin:0;color:#1F3864;">
                        👤 {resume_data['name']}
                    </h3>
                    <p style="margin:4px 0;color:#666;font-size:14px;">
                        📧 {resume_data['email']} &nbsp;|&nbsp;
                        📄 {uploaded_file.name} &nbsp;|&nbsp;
                        🔧 {resume_data['skill_count']} skills detected
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # Score cards in 4 columns
                c1, c2, c3, c4 = st.columns(4)

                with c1:
                    color = get_score_color(bert_score)
                    st.markdown(f"""
                    <div class="score-card">
                        <p class="score-number {color}">{bert_score}%</p>
                        <p class="score-label">🤖 BERT Score<br>Semantic Match</p>
                    </div>
                    """, unsafe_allow_html=True)

                with c2:
                    color = get_score_color(keyword_score)
                    st.markdown(f"""
                    <div class="score-card">
                        <p class="score-number {color}">{keyword_score}%</p>
                        <p class="score-label">🔑 Keyword Score<br>{len(matched)}/{len(jd_set)} skills</p>
                    </div>
                    """, unsafe_allow_html=True)

                with c3:
                    color = get_score_color(final_score)
                    st.markdown(f"""
                    <div class="score-card">
                        <p class="score-number {color}">{final_score}%</p>
                        <p class="score-label">⭐ Final Score<br>60% BERT + 40% KW</p>
                    </div>
                    """, unsafe_allow_html=True)

                with c4:
                    st.markdown(f"""
                    <div class="score-card">
                        <p style="font-size:22px;font-weight:bold;
                                  color:{decision_color};margin:8px 0;">
                            {decision}
                        </p>
                        <p class="score-label">Threshold: {threshold}%</p>
                    </div>
                    """, unsafe_allow_html=True)

                # Skills section in 2 columns
                sk1, sk2 = st.columns(2)

                with sk1:
                    st.markdown(f"**✅ Matched Skills ({len(matched)})**")
                    if matched:
                        tags = " ".join([
                            f'<span class="skill-tag skill-matched">{s}</span>'
                            for s in sorted(matched)
                        ])
                        st.markdown(tags, unsafe_allow_html=True)
                    else:
                        st.markdown("*No skills matched*")

                with sk2:
                    st.markdown(f"**❌ Missing Skills ({len(missing)})**")
                    if missing:
                        tags = " ".join([
                            f'<span class="skill-tag skill-missing">{s}</span>'
                            for s in sorted(missing)
                        ])
                        st.markdown(tags, unsafe_allow_html=True)
                    else:
                        st.markdown("*No skills missing — perfect match!*")

                st.markdown("---")

        # ── LEADERBOARD ──
        if all_results:

            # Sort by final score highest first
            all_results.sort(
                key=lambda x: x['final_score'],
                reverse=True
            )

            st.markdown("## 🏆 Candidate Leaderboard")
            st.markdown("*Ranked by Final Score (60% BERT + 40% Keyword)*")

            # Medal emojis for top 3
            medals = ["🥇", "🥈", "🥉"]

            # Display each candidate in the leaderboard
            for i, r in enumerate(all_results):

                # Get medal or rank number
                medal = medals[i] if i < 3 else f"#{i+1}"

                # Determine if shortlisted
                is_shortlisted = r['final_score'] >= threshold
                bg_color = "#f0fff4" if is_shortlisted else "#fff5f5"
                border = "#28a745" if is_shortlisted else "#dc3545"

                # Build score bar HTML
                bar_html = score_to_bar(r['final_score'])

                st.markdown(f"""
                <div style="background:{bg_color};padding:14px 20px;
                            border-radius:10px;border-left:5px solid {border};
                            margin:8px 0;">
                    <div style="display:flex;align-items:center;gap:16px;">
                        <span style="font-size:24px;">{medal}</span>
                        <div style="flex:1;">
                            <strong style="font-size:16px;">{r['name']}</strong>
                            <span style="color:#666;font-size:13px;
                                         margin-left:12px;">{r['file']}</span>
                            <br>
                            {bar_html}
                            <span style="font-size:12px;color:#666;margin-left:16px;">
                                BERT: {r['bert_score']}% |
                                Keywords: {r['keyword_score']}% |
                                Skills: {r['skills_count']}
                            </span>
                        </div>
                        <div style="text-align:right;">
                            <span style="font-size:13px;
                                         color:{'#28a745' if is_shortlisted else '#dc3545'};
                                         font-weight:bold;">
                                {r['decision']}
                            </span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # ── Summary stats ──
            st.markdown("---")
            shortlisted = [r for r in all_results
                          if r['final_score'] >= threshold]

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Total Resumes", len(all_results))
            with m2:
                st.metric("Shortlisted", len(shortlisted))
            with m3:
                st.metric("Rejected",
                         len(all_results) - len(shortlisted))
            with m4:
                avg = round(
                    sum(r['final_score'] for r in all_results)
                    / len(all_results), 1
                )
                st.metric("Avg Score", f"{avg}%")

# Show message if JD is missing
elif uploaded_files and not jd_text:
    st.warning("⚠️ Please paste a job description in the sidebar to start analysis")