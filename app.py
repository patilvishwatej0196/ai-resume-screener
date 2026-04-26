# app.py
# Day 4 - Main orchestrator - connects ALL modules together
# Shows both BERT semantic score + keyword score side by side
# Ranks multiple resumes for each job from best to worst match

# Import resume reader from Day 2
from resume_reader import read_all_resumes, read_job_description

# Import NLP parser from Day 3
from parser import parse_resume, extract_skills

# Import JD extractor from Day 3
from jd_extractor import extract_jd_keywords, process_all_jd_files

# Import our new AI matcher from Day 4
from matcher import get_bert_score, get_combined_score, rank_resumes, print_ranking

# Import os for file handling
import os


# -------------------------------------------------------
# FUNCTION 1: Full comparison - one resume vs one JD
# -------------------------------------------------------

def full_comparison(resume_text, resume_data, jd_text, jd_data):
    # This function runs the complete comparison pipeline
    # combining both BERT score and keyword score

    # Get BERT semantic similarity score
    # This compares the full meaning of resume vs JD
    bert_score = get_bert_score(resume_text, jd_text)

    # Get keyword match score from Day 3 logic
    resume_skills = set(resume_data['skills'])
    jd_keywords   = set(jd_data['keywords'])

    # Find matching skills using set intersection
    matched = resume_skills & jd_keywords

    # Find missing skills using set difference
    missing = jd_keywords - resume_skills

    # Calculate keyword score percentage
    if len(jd_keywords) > 0:
        keyword_score = round(len(matched) / len(jd_keywords) * 100, 1)
    else:
        keyword_score = 0.0

    # Calculate combined final score
    # 60% BERT + 40% keyword
    combined = get_combined_score(bert_score, keyword_score)

    # Return everything as one dictionary
    return {
        "bert_score"      : bert_score,
        "keyword_score"   : keyword_score,
        "combined_score"  : combined,
        "matched_skills"  : sorted(list(matched)),
        "missing_skills"  : sorted(list(missing)),
        "match_count"     : len(matched),
        "total_jd_skills" : len(jd_keywords)
    }


# -------------------------------------------------------
# FUNCTION 2: Print full comparison result
# -------------------------------------------------------

def print_full_result(resume_data, result, jd_name):
    # Prints a beautiful comparison block in the terminal

    print("\n" + "=" * 62)
    print(f"  CANDIDATE : {resume_data['name']}")
    print(f"  EMAIL     : {resume_data['email']}")
    print(f"  JOB ROLE  : {jd_name}")
    print("=" * 62)

    # ── Score display ──
    bert    = result['bert_score']
    kw      = result['keyword_score']
    final   = result['combined_score']

    # Visual bar for BERT score
    bert_bar = "█" * int(bert/5) + "░" * (20 - int(bert/5))

    # Visual bar for keyword score
    kw_bar = "█" * int(kw/5) + "░" * (20 - int(kw/5))

    # Visual bar for final score
    fin_bar = "█" * int(final/5) + "░" * (20 - int(final/5))

    print(f"\n  🤖 BERT Score    : [{bert_bar}] {bert}%")
    print(f"     (semantic meaning match)")
    print(f"\n  🔑 Keyword Score : [{kw_bar}] {kw}%")
    print(f"     ({result['match_count']}/{result['total_jd_skills']} skill keywords matched)")
    print(f"\n  ⭐ FINAL Score   : [{fin_bar}] {final}%")
    print(f"     (60% BERT + 40% Keyword)")

    # ── Shortlist decision ──
    print()
    if final >= 70:
        print("  ✅ DECISION: SHORTLISTED — Strong match")
    elif final >= 50:
        print("  🟡 DECISION: MAYBE — Moderate match, review manually")
    else:
        print("  ❌ DECISION: NOT SHORTLISTED — Weak match")

    # ── Matched skills ──
    print(f"\n  ✅ MATCHED SKILLS ({result['match_count']}):")
    if result['matched_skills']:
        skills = result['matched_skills']
        # Print 5 per line
        for i in range(0, len(skills), 5):
            print(f"     {', '.join(skills[i:i+5])}")
    else:
        print("     None matched")

    # ── Missing skills ──
    print(f"\n  ❌ MISSING SKILLS ({len(result['missing_skills'])}):")
    if result['missing_skills']:
        missing = result['missing_skills']
        for i in range(0, len(missing), 5):
            print(f"     {', '.join(missing[i:i+5])}")
    else:
        print("     None — perfect match!")

    print("-" * 62)


# -------------------------------------------------------
# MAIN: Run the full Day 4 pipeline
# -------------------------------------------------------

if __name__ == "__main__":

    print("=" * 62)
    print("   AI RESUME SCREENING PLATFORM — DAY 4")
    print("   Sentence-BERT + Keyword Matching Combined")
    print("=" * 62)

    # ── Sample resumes for testing ──
    # Using 3 candidates to show ranking
    candidates = {
        "vishwatej_patil.txt": """
        Vishwatej Patil - AI/ML Engineer
        Email: vishwatej@gmail.com
        Skills: Python, Machine Learning, Deep Learning, NLP
        TensorFlow, PyTorch, scikit-learn, pandas, numpy
        Flask, FastAPI, Git, GitHub, Docker
        SQL, MySQL, MongoDB, Power BI, Jupyter
        BERT, Hugging Face, Transformers, OpenCV
        Projects: Sentiment Analysis using BERT,
        Object Detection using OpenCV and Python,
        Customer Churn Prediction using scikit-learn
        Experience: Data Science Intern - built ML models,
        deployed Flask REST APIs, worked with pandas and numpy
        """,

        "rahul_sharma.txt": """
        Rahul Sharma - Web Developer
        Email: rahul@gmail.com
        Skills: HTML, CSS, JavaScript, React, NodeJS
        MongoDB, Express, REST APIs, Git, GitHub
        MySQL, Bootstrap, TypeScript
        Experience building web applications and dashboards
        Internship at web startup, built React components
        """,

        "priya_desai.txt": """
        Priya Desai - Data Scientist
        Email: priya@gmail.com
        Skills: Python, Machine Learning, Deep Learning, NLP
        scikit-learn, TensorFlow, pandas, numpy, matplotlib
        Research in neural networks and computer vision
        SQL, Jupyter, Google Colab, Git
        Published research on BERT fine-tuning for NLP tasks
        Experience: Research intern, data analysis projects
        """
    }

    # ── STEP 1: Parse all candidate resumes ──
    print("\n📄 STEP 1: Parsing candidate resumes...")
    print("-" * 62)

    # Dictionary to store parsed data for each candidate
    parsed_candidates = {}

    for name, text in candidates.items():
        # Parse each resume
        data = parse_resume(text)
        parsed_candidates[name] = {
            "text": text,
            "data": data
        }
        print(f"  {name}: {data['skill_count']} skills | {data['name']}")

    # ── STEP 2: Load all job descriptions ──
    print("\n\n📋 STEP 2: Loading job descriptions...")
    print("-" * 62)

    # Process all JD files from our folder
    jd_folder = "data/job_descriptions"
    all_jds   = process_all_jd_files(jd_folder)

    if not all_jds:
        print("  No job descriptions found!")
    else:
        print(f"  Loaded {len(all_jds)} job descriptions")

    # ── STEP 3: Full comparison - each candidate vs each JD ──
    print("\n\n🔍 STEP 3: Comparing each candidate against each job...")
    print("-" * 62)

    for jd in all_jds:

        # Get clean JD name from filename
        jd_name = jd['file'].replace('.txt','').replace('_',' ').title()

        print(f"\n\n  {'='*58}")
        print(f"  JOB: {jd_name}")
        print(f"  {'='*58}")

        # Store scores for ranking
        ranking_data = []

        for cand_name, cand_info in parsed_candidates.items():

            # Run full comparison
            result = full_comparison(
                cand_info['text'],
                cand_info['data'],
                jd['raw_text'],
                jd
            )

            # Print detailed result
            print_full_result(cand_info['data'], result, jd_name)

            # Store for ranking
            ranking_data.append({
                "filename"      : cand_name,
                "name"          : cand_info['data']['name'],
                "bert_score"    : result['bert_score'],
                "keyword_score" : result['keyword_score'],
                "combined_score": result['combined_score']
            })

        # ── Rank all candidates for this JD ──
        ranking_data.sort(key=lambda x: x['combined_score'], reverse=True)

        print(f"\n  📊 FINAL RANKING FOR {jd_name.upper()}")
        print(f"  {'RANK':<5} {'CANDIDATE':<20} {'BERT':>6} {'KW':>6} {'FINAL':>7}")
        print(f"  {'-'*50}")

        for i, r in enumerate(ranking_data):
            medal = ["🥇","🥈","🥉"][i] if i < 3 else "  "
            print(f"  {medal} #{i+1:<3} {r['name']:<20} "
                  f"{r['bert_score']:>5}%  "
                  f"{r['keyword_score']:>5}%  "
                  f"{r['combined_score']:>5}%")

    # ── STEP 4: Try on real PDF resumes if available ──
    print("\n\n📁 STEP 4: Testing with real PDF resumes...")
    print("-" * 62)

    resumes_folder = "data/resumes"

    if os.path.exists(resumes_folder):
        pdf_files = [f for f in os.listdir(resumes_folder)
                     if f.lower().endswith('.pdf')]

        if pdf_files:
            print(f"  Found {len(pdf_files)} PDF resume(s) — scoring against all JDs")
            all_pdfs = read_all_resumes(resumes_folder)

            for pdf_name, pdf_text in all_pdfs.items():
                pdf_data = parse_resume(pdf_text)
                print(f"\n  Processing: {pdf_name}")
                print(f"  Name: {pdf_data['name']} | Skills: {pdf_data['skill_count']}")

                if all_jds:
                    first_jd = all_jds[0]
                    jd_name  = first_jd['file'].replace('.txt','').replace('_',' ').title()
                    result   = full_comparison(pdf_text, pdf_data, first_jd['raw_text'], first_jd)
                    print_full_result(pdf_data, result, jd_name)
        else:
            print("  No PDFs found in data/resumes/")
            print("  Add your own resume PDF to test real matching!")
    else:
        print("  data/resumes/ folder not found")

    # ── SUMMARY ──
    print("\n" + "=" * 62)
    print("   DAY 4 COMPLETE — PLATFORM CAPABILITIES:")
    print("=" * 62)
    print("  ✅ Read and parse PDF resumes")
    print("  ✅ Extract skills using spaCy NLP")
    print("  ✅ Extract JD requirements")
    print("  ✅ Sentence-BERT semantic matching")
    print("  ✅ Keyword overlap scoring")
    print("  ✅ Combined score (60% BERT + 40% keyword)")
    print("  ✅ Auto shortlist / reject decision")
    print("  ✅ Rank multiple candidates for one job")
    print()
    print("  Tomorrow — Day 5:")
    print("  🔜 Build Streamlit web UI")
    print("  🔜 Upload resume via browser")
    print("  🔜 See scores on a beautiful dashboard")
    print("  🔜 Deploy to Hugging Face Spaces")
    print("=" * 62)