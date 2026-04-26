# matcher.py
# This file is the AI brain of our resume screening platform
# It uses Sentence-BERT to understand MEANING of text, not just keywords
# Example: "Python developer" and "Python programmer" score 94% similar
# Simple keyword matching would score these 0% because words differ

# Import SentenceTransformer - the Sentence-BERT model loader
from sentence_transformers import SentenceTransformer

# Import cosine_similarity from scikit-learn
# Cosine similarity measures how similar two vectors are
# Returns a value between 0 (completely different) and 1 (identical)
from sklearn.metrics.pairwise import cosine_similarity

# Import numpy for array operations
import numpy as np

# Import time to measure how long the model takes to load
import time


# -------------------------------------------------------
# LOAD THE SENTENCE-BERT MODEL
# -------------------------------------------------------

# Print a message so we know the model is loading
print("Loading Sentence-BERT model...")

# Record the start time
start = time.time()

# Load the pre-trained Sentence-BERT model
# 'all-MiniLM-L6-v2' is the best choice for beginners because:
# - Small size (80MB) — downloads and loads fast
# - Very accurate for sentence similarity tasks
# - Used in production by many companies
# This line downloads the model on first run (takes 1-2 min)
# After first run it is cached locally — loads in seconds
model = SentenceTransformer('all-MiniLM-L6-v2')

# Calculate how long loading took
load_time = round(time.time() - start, 2)
print(f"Model loaded in {load_time} seconds")


# -------------------------------------------------------
# FUNCTION 1: Get BERT similarity score between two texts
# -------------------------------------------------------

def get_bert_score(resume_text, jd_text):
    # This is the core AI function
    # It takes resume text and job description text
    # and returns a similarity score from 0 to 100

    # Step 1: Encode resume text into a vector
    # encode() converts text into a list of 384 numbers
    # These numbers capture the MEANING of the text
    # Similar meanings = similar number patterns
    resume_vector = model.encode([resume_text])

    # Step 2: Encode job description text into a vector
    # Both vectors are now in the same 384-dimensional space
    jd_vector = model.encode([jd_text])

    # Step 3: Calculate cosine similarity between the two vectors
    # cosine_similarity returns a 2D array like [[0.82]]
    # so we use [0][0] to get just the number
    similarity = cosine_similarity(resume_vector, jd_vector)[0][0]

    # Step 4: Convert from 0-1 scale to 0-100 percentage
    # round() keeps only 1 decimal place
    score = round(float(similarity) * 100, 1)

    # Return the final score
    return score


# -------------------------------------------------------
# FUNCTION 2: Get scores for a specific section only
# -------------------------------------------------------

def get_skills_bert_score(resume_skills_list, jd_keywords_list):
    # This function compares just the SKILLS sections
    # instead of entire resume and JD texts
    # More focused = more accurate skill matching

    # If either list is empty, return 0
    if not resume_skills_list or not jd_keywords_list:
        return 0.0

    # Join the skills lists into single strings
    # Example: ["python", "flask", "git"] -> "python flask git"
    resume_skills_text = ' '.join(resume_skills_list)
    jd_skills_text = ' '.join(jd_keywords_list)

    # Use our main function to compare just the skill texts
    score = get_bert_score(resume_skills_text, jd_skills_text)

    return score


# -------------------------------------------------------
# FUNCTION 3: Calculate combined final score
# -------------------------------------------------------

def get_combined_score(bert_score, keyword_score):
    # This function combines two scores into one final score
    # We weight BERT score higher because it understands meaning
    # Keyword score is still useful for exact skill matches

    # BERT score = 60% weight (understands synonyms and context)
    bert_weight = 0.60

    # Keyword score = 40% weight (exact skill matches)
    keyword_weight = 0.40

    # Calculate weighted average
    combined = (bert_score * bert_weight) + (keyword_score * keyword_weight)

    # Round to 1 decimal place
    return round(combined, 1)


# -------------------------------------------------------
# FUNCTION 4: Rank multiple resumes for one job
# -------------------------------------------------------

def rank_resumes(resumes_dict, jd_text, jd_keywords=None):
    # This function takes multiple resumes and one job description
    # and ranks all resumes from best match to worst match

    # resumes_dict format: { "filename": "full resume text" }
    # jd_text: the full job description text as string
    # jd_keywords: optional list of JD keywords for keyword scoring

    # Empty list to store results
    results = []

    # Total resumes to process
    total = len(resumes_dict)
    current = 0

    # Loop through every resume
    for filename, resume_text in resumes_dict.items():

        # Update progress counter
        current += 1
        print(f"  Scoring resume {current}/{total}: {filename}")

        # Get BERT semantic similarity score
        # This compares full text meaning
        bert_score = get_bert_score(resume_text, jd_text)

        # Get keyword overlap score if keywords provided
        # Default to bert_score if no keywords given
        if jd_keywords:
            # Import here to avoid circular imports
            from parser import extract_skills
            from jd_extractor import extract_jd_keywords

            # Extract skills from this resume
            resume_skills = extract_skills(resume_text)

            # Calculate keyword overlap manually
            resume_set = set(resume_skills)
            jd_set = set(jd_keywords)
            matched = resume_set & jd_set

            # Keyword score = matched / total JD keywords * 100
            if len(jd_set) > 0:
                keyword_score = round(len(matched) / len(jd_set) * 100, 1)
            else:
                keyword_score = 0.0
        else:
            # If no keywords given, use bert score for both
            keyword_score = bert_score

        # Calculate combined final score
        combined = get_combined_score(bert_score, keyword_score)

        # Store result as dictionary
        results.append({
            "filename": filename,
            "bert_score": bert_score,
            "keyword_score": keyword_score,
            "combined_score": combined
        })

    # Sort results by combined score — highest first
    # reverse=True means descending order (100 to 0)
    results.sort(key=lambda x: x['combined_score'], reverse=True)

    # Return the sorted list
    return results


# -------------------------------------------------------
# FUNCTION 5: Print ranking results in clean format
# -------------------------------------------------------

def print_ranking(results, jd_name):
    # This function prints the ranked resume results
    # in a clean, readable terminal format

    print("\n" + "=" * 60)
    print(f"  RESUME RANKING FOR: {jd_name.upper()}")
    print("=" * 60)
    print(f"  {'RANK':<6} {'RESUME':<25} {'BERT':>6} {'KEYWORD':>8} {'FINAL':>7}")
    print("-" * 60)

    # Loop through results (already sorted best to worst)
    for i, result in enumerate(results):

        # Rank number (1st, 2nd, 3rd etc)
        rank = i + 1

        # Shorten filename if too long for display
        name = result['filename'][:23]

        # Get scores
        bert = result['bert_score']
        kw = result['keyword_score']
        final = result['combined_score']

        # Print one row per resume
        print(f"  #{rank:<5} {name:<25} {bert:>5}%  {kw:>6}%  {final:>6}%")

    print("=" * 60)

    # Show the winner
    if results:
        winner = results[0]
        print(f"\n  BEST MATCH: {winner['filename']}")
        print(f"  Final Score: {winner['combined_score']}%")
        print(f"  (BERT: {winner['bert_score']}% | Keywords: {winner['keyword_score']}%)")


# -------------------------------------------------------
# MAIN: Test everything when run directly
# -------------------------------------------------------

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("  MATCHER.PY - SENTENCE-BERT TEST")
    print("=" * 60)

    # ── TEST 1: Basic similarity between two sentences ──
    print("\n[TEST 1] Semantic similarity — same meaning, different words")
    print("-" * 60)

    # These pairs have same meaning but different words
    # BERT should score them HIGH
    # Simple keyword matching would score them LOW or ZERO
    pairs = [
        ("Python developer with Flask experience",
         "Python programmer who knows Flask framework",
         "Same meaning, different words"),

        ("Machine learning engineer with TensorFlow",
         "AI developer using deep learning and neural networks",
         "Related but different terms"),

        ("Data analyst with Excel and SQL skills",
         "Software engineer with Java and Android",
         "Completely different roles"),
    ]

    for text1, text2, label in pairs:
        score = get_bert_score(text1, text2)

        # Show score with a visual bar
        filled = int(score / 5)
        bar = "█" * filled + "░" * (20 - filled)
        print(f"\n  {label}")
        print(f"  Text 1: {text1[:50]}")
        print(f"  Text 2: {text2[:50]}")
        print(f"  Score : [{bar}] {score}%")

    # ── TEST 2: Resume vs Job Description ──
    print("\n\n[TEST 2] Full resume vs job description scoring")
    print("-" * 60)

    sample_resume = """
    Vishwatej Patil - AI/ML Engineer
    Skills: Python, Machine Learning, Deep Learning, NLP
    TensorFlow, PyTorch, scikit-learn, pandas, numpy
    Flask, FastAPI, Git, GitHub, Docker
    SQL, MySQL, MongoDB, Power BI
    Projects: Sentiment Analysis using BERT,
    Object Detection using OpenCV,
    Customer Churn Prediction using scikit-learn
    Experience: Data Science Intern - built ML models,
    deployed Flask REST APIs, worked with pandas
    """

    ml_jd = """
    Machine Learning Engineer - Freshers Welcome
    Required: Python programming, machine learning libraries
    scikit-learn, pandas, numpy, deep learning basics
    TensorFlow or PyTorch, NLP concepts, Git, GitHub
    Deploy models as REST APIs using Flask or FastAPI
    """

    python_jd = """
    Python Developer - Freshers Welcome
    Required: Python programming, Flask or FastAPI
    SQL and database knowledge MySQL or PostgreSQL
    Git and GitHub for version control
    Basic HTML and JSON, REST APIs
    Unit testing and code reviews
    """

    data_jd = """
    Data Analyst - Freshers Welcome
    Required: Python or R for data analysis
    pandas and numpy, SQL for databases
    Data visualization: matplotlib, seaborn, Power BI
    Excel, statistics and probability, Tableau
    Create dashboards and visual reports
    """

    print("\n  Scoring resume against 3 job descriptions...")
    print()

    for jd_name, jd_text in [("ML Engineer", ml_jd),
                               ("Python Developer", python_jd),
                               ("Data Analyst", data_jd)]:
        score = get_bert_score(sample_resume, jd_text)
        filled = int(score / 5)
        bar = "█" * filled + "░" * (20 - filled)
        print(f"  {jd_name:<20} [{bar}] {score}%")

    # ── TEST 3: Rank multiple resumes ──
    print("\n\n[TEST 3] Ranking multiple candidates for ML Engineer role")
    print("-" * 60)

    # Simulate 3 different candidates
    candidates = {
        "vishwatej_resume.pdf": sample_resume,

        "candidate_2.pdf": """
        Rahul Sharma - Web Developer
        Skills: HTML, CSS, JavaScript, React, NodeJS
        MongoDB, Express, REST APIs, Git
        Experience building web applications and dashboards
        """,

        "candidate_3.pdf": """
        Priya Desai - Data Scientist
        Skills: Python, Machine Learning, Deep Learning
        NLP, scikit-learn, TensorFlow, pandas, numpy
        Research in neural networks and computer vision
        Published paper on BERT fine-tuning
        """
    }

    # Rank all candidates for ML Engineer role
    ranked = rank_resumes(candidates, ml_jd)

    # Print the ranking
    print_ranking(ranked, "ML Engineer")

    print("\n" + "=" * 60)
    print("  MATCHER TEST COMPLETE")
    print("=" * 60)
    print("\n  Key insight:")
    print("  BERT understands MEANING — not just word overlap")
    print("  'Python developer' ≈ 'Python programmer' (high score)")
    print("  'Web developer' vs 'ML engineer' (low score)")
    print("=" * 60)