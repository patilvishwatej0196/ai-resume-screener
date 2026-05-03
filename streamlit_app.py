# streamlit_app.py
# Day 7 Update — Added CSV and Excel export feature
# Recruiters can now download ranked results as spreadsheet
# Also added summary statistics section

# Import streamlit — the web framework
import streamlit as st

# Import pandas — for creating DataFrames and exporting to CSV/Excel
import pandas as pd

# Import our custom modules
from resume_reader import extract_text
from resume_parser import parse_resume
from jd_extractor_simple import extract_jd_keywords
from matcher import get_bert_score, get_combined_score

# Import other libraries
import tempfile  # for saving uploaded files temporarily
import os        # for file path operations
import io        # for creating in-memory file buffers


# -------------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------------

st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# -------------------------------------------------------
# CUSTOM CSS
# -------------------------------------------------------

st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .score-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
        margin: 8px 0;
    }
    .score-number { font-size: 42px; font-weight: bold; margin: 0; }
    .score-label { font-size: 13px; color: #666; margin-top: 4px; }
    .score-green { color: #28a745; }
    .score-yellow { color: #ffc107; }
    .score-red { color: #dc3545; }
    .skill-tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        margin: 3px;
        font-size: 13px;
        font-weight: 500;
    }
    .skill-matched { background: #d4edda; color: #155724; }
    .skill-missing { background: #f8d7da; color: #721c24; }
    .candidate-card {
        background: white;
        padding: 16px 20px;
        border-radius: 10px;
        border-left: 5px solid #2E74B5;
        margin: 10px 0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }
    .header-banner {
        background: linear-gradient(135deg, #1F3864, #2E74B5);
        color: white;
        padding: 24px 32px;
        border-radius: 12px;
        margin-bottom: 24px;
    }
    /* Download button styling */
    .download-section {
        background: white;
        padding: 20px 24px;
        border-radius: 12px;
        border: 2px dashed #2E74B5;
        margin: 16px 0;
        text-align: center;
    }
    /* Summary stats box */
    .stats-box {
        background: linear-gradient(135deg, #1F3864, #2E74B5);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin: 16px 0;
    }
</style>
""", unsafe_allow_html=True)


# -------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------

def get_score_color(score):
    # Returns CSS color class based on score value
    if score >= 70:
        return "score-green"
    elif score >= 50:
        return "score-yellow"
    else:
        return "score-red"


def get_decision(score, threshold):
    # Returns shortlist decision based on score vs threshold
    # threshold is set by the recruiter using the slider
    if score >= threshold:
        return "✅ SHORTLISTED", "#28a745"
    elif score >= 50:
        return "🟡 REVIEW MANUALLY", "#ffc107"
    else:
        return "❌ NOT SHORTLISTED", "#dc3545"


def score_to_bar(score, width=200):
    # Creates an HTML progress bar for a score
    # Color changes based on score range
    color = "#28a745" if score >= 70 else "#ffc107" if score >= 50 else "#dc3545"
    filled = int((score / 100) * width)
    return f"""
    <div style="background:#e9ecef;border-radius:10px;height:12px;
                width:{width}px;display:inline-block;">
        <div style="background:{color};width:{filled}px;height:12px;
                    border-radius:10px;"></div>
    </div>
    <span style="font-size:14px;font-weight:bold;color:{color};
                 margin-left:8px;">{score}%</span>
    """


# -------------------------------------------------------
# NEW DAY 7 FUNCTION: Build results DataFrame
# -------------------------------------------------------

def build_results_df(all_results, jd_text):
    # Converts the all_results list into a pandas DataFrame
    # This is the data structure used for CSV and Excel export

    # Empty list to hold each row of data
    rows = []

    # Loop through every candidate result
    for i, r in enumerate(all_results):

        # Build one row dictionary per candidate
        # Each key becomes a column in the spreadsheet
        row = {
            # Basic ranking info
            "Rank"              : i + 1,
            "Candidate Name"    : r['name'],
            "Email"             : r['email'],
            "Resume File"       : r['file'],

            # Score columns
            "BERT Score (%)"    : r['bert_score'],
            "Keyword Score (%)": r['keyword_score'],
            "Final Score (%)"   : r['final_score'],

            # Decision
            "Decision"          : r['decision'].replace("✅ ", "").replace("🟡 ", "").replace("❌ ", ""),

            # Skills info
            "Skills Detected"   : r['skills_count'],
            "Matched Skills"    : ", ".join(r['matched']),
            "Missing Skills"    : ", ".join(r['missing']),
        }

        # Add the row to our list
        rows.append(row)

    # Convert list of dictionaries to pandas DataFrame
    # Each dictionary becomes one row in the table
    df = pd.DataFrame(rows)

    return df


# -------------------------------------------------------
# NEW DAY 7 FUNCTION: Convert DataFrame to CSV bytes
# -------------------------------------------------------

def df_to_csv(df):
    # Converts a pandas DataFrame to CSV format
    # Returns bytes that Streamlit can use for download

    # index=False means don't include row numbers (0,1,2...)
    # in the CSV — cleaner output for recruiters
    csv_bytes = df.to_csv(index=False)

    # Return as encoded bytes for download
    return csv_bytes.encode('utf-8')


# -------------------------------------------------------
# NEW DAY 7 FUNCTION: Convert DataFrame to Excel bytes
# -------------------------------------------------------

def df_to_excel(df):
    # Converts a pandas DataFrame to Excel (.xlsx) format
    # Returns bytes that Streamlit can use for download

    # io.BytesIO() creates an in-memory file buffer
    # This avoids saving to disk — everything stays in memory
    buffer = io.BytesIO()

    # ExcelWriter writes the DataFrame to the buffer
    # engine='openpyxl' is needed for .xlsx format
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:

        # Write DataFrame to Excel
        # sheet_name sets the tab name in the Excel file
        # index=False removes row numbers
        df.to_excel(writer, sheet_name='Screening Results', index=False)

    # Get the bytes from the buffer
    excel_bytes = buffer.getvalue()

    return excel_bytes


# -------------------------------------------------------
# NEW DAY 7 FUNCTION: Show summary statistics
# -------------------------------------------------------

def show_summary_stats(all_results, threshold):
    # Shows a summary statistics section above the download buttons
    # Gives recruiter a quick overview of the screening batch

    # Calculate statistics
    total      = len(all_results)
    shortlisted = len([r for r in all_results if r['final_score'] >= threshold])
    rejected   = total - shortlisted
    avg_score  = round(sum(r['final_score'] for r in all_results) / total, 1) if total > 0 else 0
    top_score  = max(r['final_score'] for r in all_results) if total > 0 else 0
    best_name  = all_results[0]['name'] if all_results else "N/A"

    # Display as 4 metric columns
    st.markdown("### 📊 Screening Summary")

    # First row — counts
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        # st.metric shows a number with a label
        st.metric("📄 Total Screened", total)
    with c2:
        # delta shows the change — here we show shortlist %
        shortlist_pct = round((shortlisted/total)*100) if total > 0 else 0
        st.metric("✅ Shortlisted", shortlisted, f"{shortlist_pct}% of total")
    with c3:
        st.metric("❌ Rejected", rejected)
    with c4:
        st.metric("⭐ Avg Score", f"{avg_score}%")

    # Second row — top candidate info
    st.markdown(f"""
    <div style="background:#EBF3FB;padding:12px 20px;border-radius:10px;
                border-left:4px solid #2E74B5;margin:8px 0;">
        <strong>🥇 Best Match:</strong> {best_name}
        &nbsp;|&nbsp;
        <strong>Top Score:</strong> {top_score}%
        &nbsp;|&nbsp;
        <strong>Threshold:</strong> {threshold}% (set by you)
    </div>
    """, unsafe_allow_html=True)


# -------------------------------------------------------
# HEADER
# -------------------------------------------------------

st.markdown("""
<div class="header-banner">
    <h1 style="margin:0;font-size:28px;">🤖 AI Resume Screening Platform</h1>
    <p style="margin:6px 0 0 0;opacity:0.85;font-size:15px;">
        Powered by Sentence-BERT + spaCy NLP | Built by Vishwatej Patil
    </p>
</div>
""", unsafe_allow_html=True)


# -------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------

with st.sidebar:
    st.markdown("## 📋 Job Description")
    st.markdown("---")

    # Job description text area
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
    st.markdown("### ⚙️ Settings")

    # Shortlist threshold slider
    threshold = st.slider(
        "Shortlist Threshold (%)",
        min_value=30,
        max_value=90,
        value=60,
        step=5,
        help="Candidates above this score are shortlisted"
    )

    st.markdown("---")
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
    st.markdown("📄 pdfplumber + python-docx")
    st.markdown("📊 pandas export")
    st.markdown("🐍 Python 3.x")


# -------------------------------------------------------
# MAIN AREA — Resume Upload
# -------------------------------------------------------

st.markdown("## 📄 Upload Resumes")

# File uploader — accepts PDF and DOCX (Day 6 update)
uploaded_files = st.file_uploader(
    "Upload one or more PDF or Word resumes",
    type=["pdf", "docx"],           # both formats supported
    accept_multiple_files=True,
    help="Upload PDF or DOCX resumes to screen and rank"
)

# Show instructions if nothing uploaded
if not uploaded_files:
    st.info("👆 Upload resumes above and paste a job description in the sidebar")

    with st.expander("📖 How it works"):
        st.markdown("""
        1. **Paste** the job description in the sidebar
        2. **Upload** one or more PDF or DOCX resumes
        3. **Click** Analyze Resumes
        4. **See** BERT score, keyword score, final match score
        5. **Download** results as CSV or Excel
        """)


# -------------------------------------------------------
# ANALYZE BUTTON + RESULTS
# -------------------------------------------------------

if uploaded_files and jd_text:

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze = st.button(
            "🔍 Analyze Resumes",
            use_container_width=True,
            type="primary"
        )

    if analyze:

        # Extract JD keywords
        with st.spinner("Extracting job requirements..."):
            jd_keywords = extract_jd_keywords(jd_text)

        # Show JD keywords
        st.markdown("### 🎯 Job Requirements Detected")
        if jd_keywords:
            tags_html = " ".join([
                f'<span class="skill-tag skill-matched">{kw}</span>'
                for kw in jd_keywords[:20]
            ])
            st.markdown(tags_html, unsafe_allow_html=True)
        else:
            st.warning("No specific skill keywords detected in JD")

        st.markdown("---")
        st.markdown("## 👥 Candidate Results")

        # List to store all results
        all_results = []

        # Process each uploaded resume
        for uploaded_file in uploaded_files:

            with st.spinner(f"Analyzing {uploaded_file.name}..."):

                # Get file extension to preserve it in temp file
                # This is the Day 6 fix for DOCX support
                file_ext = os.path.splitext(uploaded_file.name)[1]

                # Save to temp file with correct extension
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=file_ext
                ) as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_path = tmp_file.name

                # Extract text using auto-detect function (Day 6)
                resume_text = extract_text(tmp_path)

                # Delete temp file after reading
                os.unlink(tmp_path)

                if resume_text:

                    # Parse resume for name email skills
                    resume_data = parse_resume(resume_text)

                    # Get BERT semantic score
                    bert_score = get_bert_score(resume_text, jd_text)

                    # Calculate keyword score
                    resume_skills = set(resume_data['skills'])
                    jd_set        = set(jd_keywords)
                    matched       = resume_skills & jd_set
                    missing       = jd_set - resume_skills

                    if len(jd_set) > 0:
                        keyword_score = round(len(matched) / len(jd_set) * 100, 1)
                    else:
                        keyword_score = 0.0

                    # Calculate combined final score
                    final_score = get_combined_score(bert_score, keyword_score)

                    # Get shortlist decision using threshold
                    decision, decision_color = get_decision(final_score, threshold)

                    # Store result for leaderboard and export
                    all_results.append({
                        "file"         : uploaded_file.name,
                        "name"         : resume_data['name'],
                        "email"        : resume_data['email'],
                        "bert_score"   : bert_score,
                        "keyword_score": keyword_score,
                        "final_score"  : final_score,
                        "matched"      : sorted(list(matched)),
                        "missing"      : sorted(list(missing)),
                        "decision"     : decision,
                        "skills_count" : resume_data['skill_count']
                    })

                else:
                    st.error(f"Could not extract text from {uploaded_file.name}")
                    continue

            # Display candidate result card
            with st.container():

                st.markdown(f"""
                <div class="candidate-card">
                    <h3 style="margin:0;color:#1F3864;">👤 {resume_data['name']}</h3>
                    <p style="margin:4px 0;color:#666;font-size:14px;">
                        📧 {resume_data['email']} &nbsp;|&nbsp;
                        📄 {uploaded_file.name} &nbsp;|&nbsp;
                        🔧 {resume_data['skill_count']} skills detected
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # 4 score cards
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
                        <p style="font-size:20px;font-weight:bold;
                                  color:{decision_color};margin:8px 0;">
                            {decision}
                        </p>
                        <p class="score-label">Threshold: {threshold}%</p>
                    </div>
                    """, unsafe_allow_html=True)

                # Skills columns
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
                        st.markdown("*No skills missing!*")

                st.markdown("---")

        # ── LEADERBOARD ──
        if all_results:

            # Sort by final score
            all_results.sort(key=lambda x: x['final_score'], reverse=True)

            st.markdown("## 🏆 Candidate Leaderboard")
            st.markdown("*Ranked by Final Score (60% BERT + 40% Keyword)*")

            medals = ["🥇", "🥈", "🥉"]

            for i, r in enumerate(all_results):

                medal      = medals[i] if i < 3 else f"#{i+1}"
                is_short   = r['final_score'] >= threshold
                bg_color   = "#f0fff4" if is_short else "#fff5f5"
                border     = "#28a745" if is_short else "#dc3545"
                bar_html   = score_to_bar(r['final_score'])

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
                            <br>{bar_html}
                            <span style="font-size:12px;color:#666;margin-left:16px;">
                                BERT: {r['bert_score']}% |
                                Keywords: {r['keyword_score']}% |
                                Skills: {r['skills_count']}
                            </span>
                        </div>
                        <div style="text-align:right;">
                            <span style="font-size:13px;font-weight:bold;
                                         color:{'#28a745' if is_short else '#dc3545'};">
                                {r['decision']}
                            </span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # ── SUMMARY STATISTICS (NEW DAY 7) ──
            st.markdown("---")
            show_summary_stats(all_results, threshold)

            # ── DOWNLOAD SECTION (NEW DAY 7) ──
            st.markdown("---")
            st.markdown("## 📥 Download Results")
            st.markdown("Export the complete ranked leaderboard to share with your team")

            # Build the DataFrame from results
            df = build_results_df(all_results, jd_text)

            # Show preview of the DataFrame
            with st.expander("👀 Preview Export Data"):
                # Display first 5 rows of the table
                st.dataframe(
                    df[["Rank","Candidate Name","Email",
                        "Final Score (%)","Decision"]],
                    use_container_width=True
                )

            # Download buttons in 2 columns
            dl1, dl2 = st.columns(2)

            with dl1:
                # CSV download button
                csv_data = df_to_csv(df)

                # st.download_button creates a download button
                # When clicked, browser downloads the file
                st.download_button(
                    label="📊 Download as CSV",
                    data=csv_data,           # file content as bytes
                    file_name="screening_results.csv",  # download filename
                    mime="text/csv",         # file type
                    use_container_width=True,
                    help="Opens in Excel, Google Sheets, or any spreadsheet app"
                )

            with dl2:
                # Excel download button
                excel_data = df_to_excel(df)

                st.download_button(
                    label="📗 Download as Excel",
                    data=excel_data,         # file content as bytes
                    file_name="screening_results.xlsx", # download filename
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    help="Opens directly in Microsoft Excel"
                )

            st.success(f"✅ {len(all_results)} candidates screened | {len([r for r in all_results if r['final_score'] >= threshold])} shortlisted | Ready to download!")

elif uploaded_files and not jd_text:
    st.warning("⚠️ Please paste a job description in the sidebar to start analysis")