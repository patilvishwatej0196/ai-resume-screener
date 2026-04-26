# parser.py
# This file extracts useful information from resume text
# It finds: candidate name, email address, and skills
# We use spaCy for NLP and re (regex) for email detection

# Import spaCy - the NLP library that understands human language
import spacy

# Import re - Python's built-in regex library for pattern matching
import re

# Import os - for file path handling
import os

# Load the English language model we downloaded on Day 1
# This model knows grammar, named entities, and word types
nlp = spacy.load("en_core_web_sm")

# -------------------------------------------------------
# SKILLS DATABASE
# A list of common tech skills we want to detect in resumes
# spaCy alone cannot know what is a "skill" vs normal word
# so we give it this reference list to check against
# -------------------------------------------------------

SKILLS_DB = [
    # Programming Languages
    "python", "java", "javascript", "c++", "c#", "r", "sql",
    "typescript", "kotlin", "swift", "go", "rust", "scala",

    # Web Development
    "html", "css", "react", "angular", "vue", "nodejs", "flask",
    "django", "fastapi", "rest api", "graphql", "bootstrap",

    # Data Science & ML
    "machine learning", "deep learning", "nlp", "computer vision",
    "pandas", "numpy", "matplotlib", "seaborn", "scikit-learn",
    "tensorflow", "pytorch", "keras", "opencv", "hugging face",
    "bert", "transformers", "spacy", "nltk",

    # Databases
    "mysql", "postgresql", "mongodb", "sqlite", "oracle",
    "redis", "elasticsearch", "firebase",

    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "git",
    "github", "linux", "jenkins", "ci/cd",

    # Data Tools
    "excel", "power bi", "tableau", "jupyter", "google colab",
    "airflow", "spark", "hadoop",

    # Soft skills (optional but useful)
    "communication", "teamwork", "leadership", "problem solving",
    "critical thinking", "time management"
]


# -------------------------------------------------------
# FUNCTION 1: Extract candidate name from resume text
# -------------------------------------------------------

def extract_name(text):
    # Get only the first 3 lines of the resume
    # Name is always in the first 1-3 lines
    lines = text.strip().split('\n')

    # Clean each line — remove extra spaces
    clean_lines = [line.strip() for line in lines if line.strip()]

    # Common words that are NEVER part of a person's name
    # If a line contains these words, skip it
    not_name_words = [
        "python", "java", "sql", "html", "css", "git", "docker",
        "machine", "learning", "deep", "data", "engineer", "developer",
        "analyst", "scientist", "intern", "skills", "experience",
        "education", "project", "email", "phone", "location",
        "tensorflow", "pytorch", "flask", "numpy", "pandas",
        "ai", "ml", "nlp", "api", "rest", "aws", "gcp", "azure",
        "resume", "curriculum", "vitae", "objective", "summary"
    ]

    # Loop through first 3 lines only
    for line in clean_lines[:3]:

        line_lower = line.lower()

        # Skip if line contains any non-name word
        if any(word in line_lower for word in not_name_words):
            continue

        # Skip if line contains @ (email address)
        if '@' in line:
            continue

        # Skip if line is too short (less than 4 chars)
        if len(line) < 4:
            continue

        # Skip if line is too long (names are short)
        if len(line) > 40:
            continue

        # Skip lines that are all uppercase — likely a section header
        if line.isupper():
            continue

        # This line is likely the name — return it
        return line

    # Last fallback — return first clean line
    return clean_lines[0] if clean_lines else "Unknown"


# -------------------------------------------------------
# FUNCTION 2: Extract email address from resume text
# -------------------------------------------------------

def extract_email(text):
    # This function uses regex to find email addresses
    # Regex is a pattern-matching system
    # The pattern below matches standard email formats

    # Email pattern explained:
    # [a-zA-Z0-9._%+-]+  = one or more letters/numbers/dots/symbols
    # @                   = literal @ symbol
    # [a-zA-Z0-9.-]+     = domain name (like gmail, yahoo)
    # \.                  = literal dot
    # [a-zA-Z]{2,}        = domain extension (com, org, in) minimum 2 chars
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

    # re.findall returns a list of all matches found in the text
    emails = re.findall(email_pattern, text)

    # If at least one email was found, return the first one
    if emails:
        return emails[0]

    # If no email found, return Not found
    return "Not found"


# -------------------------------------------------------
# FUNCTION 3: Extract skills from resume text
# -------------------------------------------------------

def extract_skills(text):
    # This function checks which skills from our SKILLS_DB
    # appear in the resume text
    # It uses both exact matching and spaCy token analysis

    # Convert the entire resume text to lowercase
    # so "Python" and "python" both match
    text_lower = text.lower()

    # Create an empty set to store found skills
    # We use a set so duplicate skills are removed automatically
    found_skills = set()

    # METHOD 1: Direct keyword matching
    # Loop through every skill in our database
    for skill in SKILLS_DB:

        # Check if this skill appears anywhere in the resume text
        if skill.lower() in text_lower:

            # Add it to our found skills set
            found_skills.add(skill)

    # METHOD 2: spaCy noun chunk matching
    # spaCy can identify noun phrases like "machine learning", "data analysis"
    # These may be skills not in our database

    # Process the text through spaCy
    doc = nlp(text[:5000])  # limit to 5000 chars for speed

    # Loop through noun chunks (multi-word phrases spaCy identifies)
    for chunk in doc.noun_chunks:

        # Get the chunk text in lowercase
        chunk_text = chunk.text.lower().strip()

        # Only add chunks that are 2-4 words long
        # Single words are too generic, 5+ words are sentences
        word_count = len(chunk_text.split())
        if 2 <= word_count <= 4:

            # Check if any skill keyword is inside this chunk
            for skill in SKILLS_DB:
                if skill in chunk_text:
                    found_skills.add(skill)

    # Convert the set to a sorted list for clean output
    return sorted(list(found_skills))


# -------------------------------------------------------
# FUNCTION 4: Parse entire resume - combines all 3 functions
# -------------------------------------------------------

def parse_resume(text):
    # This is the main function that runs all extractors
    # and returns a clean dictionary with all candidate info

    # Call each extraction function
    name = extract_name(text)
    email = extract_email(text)
    skills = extract_skills(text)

    # Build and return a dictionary with all parsed data
    # This dictionary format is easy to use in other files
    resume_data = {
        "name": name,
        "email": email,
        "skills": skills,
        "skill_count": len(skills),
        "text_length": len(text)
    }

    return resume_data


# -------------------------------------------------------
# MAIN: Test everything when we run this file directly
# -------------------------------------------------------

if __name__ == "__main__":

    print("=" * 55)
    print("PARSER.PY - TEST RUN")
    print("=" * 55)

    # Sample resume text for testing
    # We use this so you can test even without a PDF
    sample_resume = """
    Vishwatej Patil
    AI/ML Engineer
    Email: vishwatej@gmail.com
    Phone: 9876543210
    Location: Sangli, Maharashtra

    EDUCATION
    B.E. in Artificial Intelligence and Machine Learning
    XYZ Engineering College, Pune - 2025

    SKILLS
    Python, Machine Learning, Deep Learning, NLP
    TensorFlow, PyTorch, scikit-learn, pandas, numpy
    Flask, FastAPI, Git, GitHub, Docker
    SQL, MySQL, MongoDB
    Data Analysis, Computer Vision

    PROJECTS
    1. Sentiment Analysis using BERT
       Built a text classifier using Hugging Face transformers
       Achieved 91% accuracy on movie review dataset

    2. Object Detection using OpenCV
       Real-time detection using YOLOv5 and Python

    EXPERIENCE
    Intern - Data Science | ABC Tech Pvt Ltd | June 2024
    - Worked on customer churn prediction using scikit-learn
    - Built data pipelines using pandas and numpy
    - Created dashboards in Power BI
    """

    # Test 1: Extract name
    print("\n[TEST 1] Extracting Name...")
    print("-" * 40)
    name = extract_name(sample_resume)
    print(f"Name found: {name}")

    # Test 2: Extract email
    print("\n[TEST 2] Extracting Email...")
    print("-" * 40)
    email = extract_email(sample_resume)
    print(f"Email found: {email}")

    # Test 3: Extract skills
    print("\n[TEST 3] Extracting Skills...")
    print("-" * 40)
    skills = extract_skills(sample_resume)
    print(f"Total skills found: {len(skills)}")
    print(f"Skills: {', '.join(skills)}")

    # Test 4: Full parse
    print("\n[TEST 4] Full Resume Parse...")
    print("-" * 40)
    result = parse_resume(sample_resume)
    print(f"Candidate  : {result['name']}")
    print(f"Email      : {result['email']}")
    print(f"Skills     : {result['skill_count']} skills found")
    print(f"Text length: {result['text_length']} characters")

    # Test 5: Try on a real PDF if available
    print("\n[TEST 5] Trying on real PDF resume...")
    print("-" * 40)

    # Import resume_reader to read actual PDF
    try:
        # Import our Day 2 file
        from resume_reader import extract_text_from_pdf

        # Path to resumes folder
        resumes_folder = "data/resumes"

        # Check if any PDF exists in the folder
        if os.path.exists(resumes_folder):
            pdf_files = [f for f in os.listdir(resumes_folder)
                        if f.lower().endswith('.pdf')]

            if pdf_files:
                # Pick the first PDF
                first_pdf = os.path.join(resumes_folder, pdf_files[0])
                print(f"Reading: {pdf_files[0]}")

                # Extract text from PDF
                pdf_text = extract_text_from_pdf(first_pdf)

                if pdf_text:
                    # Parse it
                    pdf_result = parse_resume(pdf_text)
                    print(f"Name   : {pdf_result['name']}")
                    print(f"Email  : {pdf_result['email']}")
                    print(f"Skills : {pdf_result['skill_count']} found")
                    print(f"List   : {', '.join(pdf_result['skills'])}")
                else:
                    print("PDF text extraction returned empty")
            else:
                print("No PDF files in data/resumes/ — add a PDF to test this")
        else:
            print("data/resumes/ folder not found")

    except Exception as e:
        print(f"Could not test on PDF: {e}")

    print("\n" + "=" * 55)
    print("PARSER TEST COMPLETE")
    print("=" * 55)