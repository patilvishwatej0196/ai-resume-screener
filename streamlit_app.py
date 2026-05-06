# streamlit_app.py
# Day 9 Update — Added Analytics Dashboard with 4 Plotly charts
# Charts: Score Distribution, Top Skills, Shortlist Pie, BERT vs Keyword scatter

# Import streamlit — the web framework
import streamlit as st

# Import pandas — for DataFrames and export
import pandas as pd

# Import plotly express — easy chart creation library
import plotly.express as px

# Import plotly graph objects — for advanced chart customization
import plotly.graph_objects as go

# Import our custom modules
from resume_reader import extract_text
from resume_parser import parse_resume
from jd_extractor_simple import extract_jd_keywords
from matcher import get_bert_score, get_combined_score

# Import other libraries
import tempfile   # for saving uploaded files temporarily
import os         # for file path operations
import io         # for in-memory file buffers
from collections import Counter  # for counting skill frequencies


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
    /* Analytics section styling */
    .analytics-header {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        color: white;
        padding: 20px 28px;
        border-radius: 12px;
        margin: 20px 0 16px 0;
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
    # Returns shortlist decision and color
    if score >= threshold:
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
    <div style="background:#e9ecef;border-radius:10px;height:12px;
                width:{width}px;display:inline-block;">
        <div style="background:{color};width:{filled}px;height:12px;
                    border-radius:10px;"></div>
    </div>
    <span style="font-size:14px;font-weight:bold;color:{color};
                 margin-left:8px;">{score}%</span>
    """


# -------------------------------------------------------
# DAY 7 FUNCTIONS: Export features
# -------------------------------------------------------

def build_results_df(all_results, jd_text):
    # Converts results list to pandas DataFrame for export
    rows = []
    for i, r in enumerate(all_results):
        row = {
            "Rank"             : i + 1,
            "Candidate Name"   : r['name'],
            "Email"            : r['email'],
            "Resume File"      : r['file'],
            "BERT Score (%)"   : r['bert_score'],
            "Keyword Score (%)": r['keyword_score'],
            "Final Score (%)"  : r['final_score'],
            "Decision"         : r['decision'].replace("✅ ","").replace("🟡 ","").replace("❌ ",""),
            "Skills Detected"  : r['skills_count'],
            "Matched Skills"   : ", ".join(r['matched']),
            "Missing Skills"   : ", ".join(r['missing']),
        }
        rows.append(row)
    return pd.DataFrame(rows)


def df_to_csv(df):
    # Converts DataFrame to CSV bytes
    return df.to_csv(index=False).encode('utf-8')


def df_to_excel(df):
    # Converts DataFrame to Excel bytes using openpyxl
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Screening Results', index=False)
    return buffer.getvalue()


def show_summary_stats(all_results, threshold):
    # Shows summary statistics metrics
    total       = len(all_results)
    shortlisted = len([r for r in all_results if r['final_score'] >= threshold])
    rejected    = total - shortlisted
    avg_score   = round(sum(r['final_score'] for r in all_results) / total, 1) if total > 0 else 0
    top_score   = max(r['final_score'] for r in all_results) if total > 0 else 0
    best_name   = all_results[0]['name'] if all_results else "N/A"

    st.markdown("### 📊 Screening Summary")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("📄 Total Screened", total)
    with c2:
        shortlist_pct = round((shortlisted/total)*100) if total > 0 else 0
        st.metric("✅ Shortlisted", shortlisted, f"{shortlist_pct}% of total")
    with c3:
        st.metric("❌ Rejected", rejected)
    with c4:
        st.metric("⭐ Avg Score", f"{avg_score}%")

    st.markdown(f"""
    <div style="background:#EBF3FB;padding:12px 20px;border-radius:10px;
                border-left:4px solid #2E74B5;margin:8px 0;">
        <strong>🥇 Best Match:</strong> {best_name}
        &nbsp;|&nbsp;
        <strong>Top Score:</strong> {top_score}%
        &nbsp;|&nbsp;
        <strong>Threshold:</strong> {threshold}%
    </div>
    """, unsafe_allow_html=True)


# -------------------------------------------------------
# DAY 9 NEW FUNCTIONS: Analytics charts
# -------------------------------------------------------

def chart_score_distribution(all_results):
    # CHART 1: Score Distribution Histogram
    # Shows how scores are spread across all candidates
    # Helps recruiter understand the quality of the applicant pool

    # Extract final scores from all results
    scores = [r['final_score'] for r in all_results]

    # Create histogram using plotly express
    # x=scores means each score becomes a bar
    # nbins=10 means we divide scores into 10 groups (0-10, 10-20, etc)
    fig = px.histogram(
        x=scores,
        nbins=10,
        title="📊 Score Distribution — All Candidates",
        labels={'x': 'Final Score (%)', 'y': 'Number of Candidates'},
        color_discrete_sequence=['#2E74B5']  # blue bars
    )

    # Add a vertical line showing the shortlist threshold
    # This helps recruiter see how many are above/below cutoff
    fig.add_vline(
        x=60,                          # threshold at 60%
        line_dash="dash",              # dashed line style
        line_color="red",             # red color
        annotation_text="Threshold",  # label on the line
        annotation_position="top right"
    )

    # Update layout for clean professional look
    fig.update_layout(
        plot_bgcolor='white',          # white chart background
        paper_bgcolor='white',         # white outer background
        font=dict(family="Arial"),     # Arial font throughout
        showlegend=False,              # hide legend (not needed)
        height=350                     # chart height in pixels
    )

    # Update bar appearance
    fig.update_traces(
        marker_line_color='white',    # white border between bars
        marker_line_width=1.5         # border width
    )

    # Display the chart in Streamlit
    # use_container_width=True makes chart fill the column width
    st.plotly_chart(fig, use_container_width=True)


def chart_top_skills(all_results):
    # CHART 2: Top Skills Bar Chart
    # Shows which skills appear most frequently across all resumes
    # Helps recruiter understand what skills the applicant pool has

    # Collect all skills from all candidates into one list
    all_skills = []
    for r in all_results:
        # r['matched'] contains skills that matched the JD
        all_skills.extend(r['matched'])

    # If no skills found, show a message
    if not all_skills:
        st.info("Upload more resumes to see skill frequency chart")
        return

    # Count how many times each skill appears
    # Counter({'python': 5, 'git': 4, 'sql': 3, ...})
    skill_counts = Counter(all_skills)

    # Get top 10 most common skills
    # most_common(10) returns [(skill, count), ...] sorted by count
    top_skills = skill_counts.most_common(10)

    # Separate skills and counts into two lists for the chart
    skills_list = [s[0] for s in top_skills]   # ['python', 'git', ...]
    counts_list = [s[1] for s in top_skills]   # [5, 4, ...]

    # Create horizontal bar chart
    # This is easier to read for long skill names
    fig = px.bar(
        x=counts_list,                          # counts on x-axis
        y=skills_list,                          # skills on y-axis
        orientation='h',                        # horizontal bars
        title="🔧 Top Skills Across All Candidates",
        labels={'x': 'Number of Candidates', 'y': 'Skill'},
        color=counts_list,                      # color by count value
        color_continuous_scale='Blues'          # blue color scale
    )

    # Update layout
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial"),
        showlegend=False,
        height=350,
        yaxis={'categoryorder': 'total ascending'}  # sort bars by value
    )

    # Display chart
    st.plotly_chart(fig, use_container_width=True)


def chart_shortlist_pie(all_results, threshold):
    # CHART 3: Shortlist Distribution Pie Chart
    # Shows the ratio of shortlisted vs review vs rejected
    # Quick visual for recruiter to see overall batch quality

    # Count candidates in each category
    shortlisted   = len([r for r in all_results if r['final_score'] >= threshold])
    review        = len([r for r in all_results if 50 <= r['final_score'] < threshold])
    rejected      = len([r for r in all_results if r['final_score'] < 50])

    # Only keep categories that have at least 1 candidate
    labels = []
    values = []

    if shortlisted > 0:
        labels.append('Shortlisted')
        values.append(shortlisted)

    if review > 0:
        labels.append('Manual Review')
        values.append(review)

    if rejected > 0:
        labels.append('Rejected')
        values.append(rejected)

    # Colors matching our app theme
    colors = ['#28a745', '#ffc107', '#dc3545']

    # Create pie chart using plotly graph objects
    # go.Pie gives more control than px.pie
    fig = go.Figure(data=[go.Pie(
        labels=labels,           # category names
        values=values,           # category counts
        hole=0.4,                # creates a donut chart (hole in center)
        marker_colors=colors[:len(labels)]  # apply colors
    )])

    # Update layout
    fig.update_layout(
        title="🎯 Shortlist Distribution",
        font=dict(family="Arial"),
        height=350,
        legend=dict(
            orientation="h",     # horizontal legend
            yanchor="bottom",    # anchor at bottom
            y=-0.2               # position below chart
        )
    )

    # Update trace styling
    fig.update_traces(
        textposition='inside',           # show percentages inside slices
        textinfo='percent+label',        # show both % and label
        hovertemplate='%{label}: %{value} candidates<extra></extra>'
    )

    # Display chart
    st.plotly_chart(fig, use_container_width=True)


def chart_bert_vs_keyword(all_results):
    # CHART 4: BERT Score vs Keyword Score Scatter Plot
    # Shows the relationship between semantic score and keyword score
    # Each dot = one candidate — hover to see their name and scores

    # Need at least 2 candidates for a meaningful scatter plot
    if len(all_results) < 2:
        st.info("Upload at least 2 resumes to see comparison scatter plot")
        return

    # Build lists for each axis and labels
    bert_scores    = [r['bert_score']    for r in all_results]
    keyword_scores = [r['keyword_score'] for r in all_results]
    final_scores   = [r['final_score']   for r in all_results]
    names          = [r['name']          for r in all_results]

    # Create scatter plot
    # Each candidate is one point on the chart
    fig = px.scatter(
        x=bert_scores,               # x-axis: BERT scores
        y=keyword_scores,            # y-axis: keyword scores
        color=final_scores,          # color dots by final score
        size=final_scores,           # size dots by final score
        hover_name=names,            # show name on hover
        color_continuous_scale='RdYlGn',  # red-yellow-green color scale
        title="🤖 BERT Score vs Keyword Score",
        labels={
            'x': 'BERT Semantic Score (%)',
            'y': 'Keyword Match Score (%)',
            'color': 'Final Score (%)'
        }
    )

    # Add reference lines showing 50% mark on both axes
    # This creates 4 quadrants on the chart
    fig.add_hline(
        y=50,
        line_dash="dot",
        line_color="gray",
        opacity=0.5
    )
    fig.add_vline(
        x=50,
        line_dash="dot",
        line_color="gray",
        opacity=0.5
    )

    # Update layout
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial"),
        height=350
    )

    # Make dots larger and more visible
    fig.update_traces(
        marker=dict(
            line=dict(width=1, color='white')  # white border on dots
        )
    )

    # Display chart
    st.plotly_chart(fig, use_container_width=True)


def show_analytics_dashboard(all_results, threshold):
    # MAIN ANALYTICS FUNCTION
    # Displays all 4 charts in a structured layout
    # Called after all resumes have been processed

    # Analytics section header
    st.markdown("""
    <div class="analytics-header">
        <h2 style="margin:0;font-size:22px;">📈 Analytics Dashboard</h2>
        <p style="margin:6px 0 0 0;opacity:0.8;font-size:14px;">
            Visual insights from the current screening batch
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Only show charts if we have enough data
    if len(all_results) < 1:
        st.info("Upload and analyze resumes to see analytics")
        return

    # Row 1: Score Distribution + Shortlist Pie
    # These two charts side by side in 2 columns
    col1, col2 = st.columns(2)

    with col1:
        # Chart 1: Score histogram
        chart_score_distribution(all_results)

    with col2:
        # Chart 3: Pie chart
        chart_shortlist_pie(all_results, threshold)

    # Row 2: Top Skills + Scatter Plot
    col3, col4 = st.columns(2)

    with col3:
        # Chart 2: Skills frequency
        chart_top_skills(all_results)

    with col4:
        # Chart 4: BERT vs keyword scatter
        chart_bert_vs_keyword(all_results)

    # Key insights section below charts
    st.markdown("### 💡 Key Insights")

    # Calculate insights automatically
    avg   = round(sum(r['final_score'] for r in all_results) / len(all_results), 1)
    best  = max(all_results, key=lambda x: x['final_score'])
    worst = min(all_results, key=lambda x: x['final_score'])

    # Get most common skill across all candidates
    all_skills = []
    for r in all_results:
        all_skills.extend(r['matched'])
    top_skill = Counter(all_skills).most_common(1)[0][0] if all_skills else "N/A"

    # Display insights in 3 columns
    i1, i2, i3 = st.columns(3)

    with i1:
        st.markdown(f"""
        <div style="background:white;padding:14px;border-radius:10px;
                    border-left:4px solid #2E74B5;text-align:center;">
            <p style="margin:0;font-size:13px;color:#666;">Average Score</p>
            <p style="margin:4px 0;font-size:28px;font-weight:bold;
                      color:#2E74B5;">{avg}%</p>
        </div>
        """, unsafe_allow_html=True)

    with i2:
        st.markdown(f"""
        <div style="background:white;padding:14px;border-radius:10px;
                    border-left:4px solid #28a745;text-align:center;">
            <p style="margin:0;font-size:13px;color:#666;">Best Candidate</p>
            <p style="margin:4px 0;font-size:18px;font-weight:bold;
                      color:#28a745;">{best['name']}</p>
            <p style="margin:0;font-size:13px;color:#28a745;">{best['final_score']}%</p>
        </div>
        """, unsafe_allow_html=True)

    with i3:
        st.markdown(f"""
        <div style="background:white;padding:14px;border-radius:10px;
                    border-left:4px solid #ffc107;text-align:center;">
            <p style="margin:0;font-size:13px;color:#666;">Top Common Skill</p>
            <p style="margin:4px 0;font-size:22px;font-weight:bold;
                      color:#856404;">{top_skill}</p>
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

    jd_text = st.text_area(
        "Paste the Job Description here",
        height=250,
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

    threshold = st.slider(
        "Shortlist Threshold (%)",
        min_value=30,
        max_value=90,
        value=60,
        step=5
    )

    st.markdown("---")
    st.markdown("### 📧 Email Notifications")

    sender_email = st.text_input(
        "Your Gmail address",
        placeholder="yourgmail@gmail.com"
    )
    sender_password = st.text_input(
        "Gmail App Password",
        type="password",
        placeholder="16 character app password"
    )
    job_role_input = st.text_input(
        "Job Role (for email)",
        placeholder="Python Developer"
    )
    send_emails = st.checkbox(
        "Send email notifications",
        value=False
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
    st.markdown("📊 Plotly Analytics")
    st.markdown("📄 pdfplumber + python-docx")
    st.markdown("🐍 Python 3.x")


# -------------------------------------------------------
# MAIN AREA
# -------------------------------------------------------

st.markdown("## 📄 Upload Resumes")

uploaded_files = st.file_uploader(
    "Upload one or more PDF or Word resumes",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

if not uploaded_files:
    st.info("👆 Upload resumes above and paste a job description in the sidebar")

    with st.expander("📖 How it works"):
        st.markdown("""
        1. **Paste** the job description in the sidebar
        2. **Upload** one or more PDF or DOCX resumes
        3. **Click** Analyze Resumes
        4. **See** scores, rankings, and analytics charts
        5. **Download** results as CSV or Excel
        6. **Email** shortlisted candidates automatically
        """)


# -------------------------------------------------------
# ANALYZE + RESULTS
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

        st.markdown("### 🎯 Job Requirements Detected")
        if jd_keywords:
            tags_html = " ".join([
                f'<span class="skill-tag skill-matched">{kw}</span>'
                for kw in jd_keywords[:20]
            ])
            st.markdown(tags_html, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("## 👥 Candidate Results")

        # Store all results
        all_results = []

        # Process each resume
        for uploaded_file in uploaded_files:

            with st.spinner(f"Analyzing {uploaded_file.name}..."):

                # Get file extension for temp file
                file_ext = os.path.splitext(uploaded_file.name)[1]

                # Save to temp file
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=file_ext
                ) as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_path = tmp_file.name

                # Extract text using auto-detect
                resume_text = extract_text(tmp_path)
                os.unlink(tmp_path)

                if resume_text:

                    resume_data   = parse_resume(resume_text)
                    bert_score    = get_bert_score(resume_text, jd_text)
                    resume_skills = set(resume_data['skills'])
                    jd_set        = set(jd_keywords)
                    matched       = resume_skills & jd_set
                    missing       = jd_set - resume_skills

                    keyword_score = round(len(matched)/len(jd_set)*100, 1) if jd_set else 0.0
                    final_score   = get_combined_score(bert_score, keyword_score)
                    decision, decision_color = get_decision(final_score, threshold)

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

            # Display candidate card
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

                c1, c2, c3, c4 = st.columns(4)

                with c1:
                    color = get_score_color(bert_score)
                    st.markdown(f"""
                    <div class="score-card">
                        <p class="score-number {color}">{bert_score}%</p>
                        <p class="score-label">🤖 BERT Score<br>Semantic Match</p>
                    </div>""", unsafe_allow_html=True)

                with c2:
                    color = get_score_color(keyword_score)
                    st.markdown(f"""
                    <div class="score-card">
                        <p class="score-number {color}">{keyword_score}%</p>
                        <p class="score-label">🔑 Keyword Score<br>{len(matched)}/{len(jd_set)} skills</p>
                    </div>""", unsafe_allow_html=True)

                with c3:
                    color = get_score_color(final_score)
                    st.markdown(f"""
                    <div class="score-card">
                        <p class="score-number {color}">{final_score}%</p>
                        <p class="score-label">⭐ Final Score<br>60% BERT + 40% KW</p>
                    </div>""", unsafe_allow_html=True)

                with c4:
                    st.markdown(f"""
                    <div class="score-card">
                        <p style="font-size:20px;font-weight:bold;
                                  color:{decision_color};margin:8px 0;">
                            {decision}
                        </p>
                        <p class="score-label">Threshold: {threshold}%</p>
                    </div>""", unsafe_allow_html=True)

                sk1, sk2 = st.columns(2)

                with sk1:
                    st.markdown(f"**✅ Matched Skills ({len(matched)})**")
                    if matched:
                        tags = " ".join([f'<span class="skill-tag skill-matched">{s}</span>' for s in sorted(matched)])
                        st.markdown(tags, unsafe_allow_html=True)
                    else:
                        st.markdown("*No skills matched*")

                with sk2:
                    st.markdown(f"**❌ Missing Skills ({len(missing)})**")
                    if missing:
                        tags = " ".join([f'<span class="skill-tag skill-missing">{s}</span>' for s in sorted(missing)])
                        st.markdown(tags, unsafe_allow_html=True)
                    else:
                        st.markdown("*No skills missing!*")

                st.markdown("---")

        # ── LEADERBOARD ──
        if all_results:

            all_results.sort(key=lambda x: x['final_score'], reverse=True)

            st.markdown("## 🏆 Candidate Leaderboard")

            medals = ["🥇", "🥈", "🥉"]

            for i, r in enumerate(all_results):
                medal    = medals[i] if i < 3 else f"#{i+1}"
                is_short = r['final_score'] >= threshold
                bg       = "#f0fff4" if is_short else "#fff5f5"
                border   = "#28a745" if is_short else "#dc3545"
                bar_html = score_to_bar(r['final_score'])

                st.markdown(f"""
                <div style="background:{bg};padding:14px 20px;
                            border-radius:10px;border-left:5px solid {border};margin:8px 0;">
                    <div style="display:flex;align-items:center;gap:16px;">
                        <span style="font-size:24px;">{medal}</span>
                        <div style="flex:1;">
                            <strong style="font-size:16px;">{r['name']}</strong>
                            <span style="color:#666;font-size:13px;margin-left:12px;">{r['file']}</span>
                            <br>{bar_html}
                            <span style="font-size:12px;color:#666;margin-left:16px;">
                                BERT: {r['bert_score']}% | Keywords: {r['keyword_score']}%
                            </span>
                        </div>
                        <div>
                            <span style="font-size:13px;font-weight:bold;
                                         color:{'#28a745' if is_short else '#dc3545'};">
                                {r['decision']}
                            </span>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

            # Summary stats
            st.markdown("---")
            show_summary_stats(all_results, threshold)

            # ── ANALYTICS DASHBOARD (NEW DAY 9) ──
            st.markdown("---")
            show_analytics_dashboard(all_results, threshold)

            # ── DOWNLOAD SECTION ──
            st.markdown("---")
            st.markdown("## 📥 Download Results")

            df = build_results_df(all_results, jd_text)

            with st.expander("👀 Preview Export Data"):
                st.dataframe(
                    df[["Rank","Candidate Name","Email","Final Score (%)","Decision"]],
                    use_container_width=True
                )

            dl1, dl2 = st.columns(2)

            with dl1:
                st.download_button(
                    label="📊 Download as CSV",
                    data=df_to_csv(df),
                    file_name="screening_results.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            with dl2:
                st.download_button(
                    label="📗 Download as Excel",
                    data=df_to_excel(df),
                    file_name="screening_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            st.success(f"✅ {len(all_results)} candidates screened | {len([r for r in all_results if r['final_score'] >= threshold])} shortlisted")

            # ── EMAIL NOTIFICATIONS ──
            if send_emails:
                if not sender_email or not sender_password:
                    st.warning("⚠️ Enter Gmail and App Password in sidebar")
                elif not job_role_input:
                    st.warning("⚠️ Enter Job Role in sidebar for email notifications")
                else:
                    st.markdown("---")
                    st.markdown("## 📧 Sending Email Notifications")
                    os.environ["SENDER_EMAIL"]    = sender_email
                    os.environ["SENDER_PASSWORD"] = sender_password
                    from email_sender import send_bulk_notifications
                    with st.spinner("Sending emails..."):
                        success_list, failed_list = send_bulk_notifications(
                            all_results, job_role_input, threshold
                        )
                    if success_list:
                        st.success(f"✅ {len(success_list)} emails sent!")
                        for msg in success_list:
                            st.write(f"  ✅ {msg}")
                    if failed_list:
                        st.error(f"❌ {len(failed_list)} emails failed")
                        for msg in failed_list:
                            st.write(f"  ❌ {msg}")

elif uploaded_files and not jd_text:
    st.warning("⚠️ Please paste a job description in the sidebar")