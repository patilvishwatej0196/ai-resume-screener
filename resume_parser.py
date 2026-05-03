# resume_parser.py
# SpaCy-free resume parser — works locally and on HuggingFace
# Uses only regex and SKILLS_DB — no NLP model needed

# Import re for regex pattern matching
import re

# Skills database — list of all skills we detect
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
    "bert", "transformers", "nltk",
    # Databases
    "mysql", "postgresql", "mongodb", "sqlite", "oracle",
    "redis", "elasticsearch", "firebase",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "git",
    "github", "linux", "jenkins",
    # Data Tools
    "excel", "power bi", "tableau", "jupyter", "google colab",
    "spark", "hadoop"
]


def extract_name(text):
    # Gets name from first 3 lines of resume
    # Skips lines with technical words or emails
    lines = text.strip().split('\n')
    clean_lines = [l.strip() for l in lines if l.strip()]

    not_name_words = [
        "python", "java", "sql", "html", "css", "git", "docker",
        "machine", "learning", "deep", "data", "engineer", "developer",
        "analyst", "scientist", "intern", "skills", "experience",
        "education", "project", "email", "phone", "location",
        "tensorflow", "pytorch", "flask", "numpy", "pandas",
        "ai", "ml", "nlp", "api", "rest", "aws", "gcp", "azure",
        "resume", "curriculum", "vitae", "objective", "summary"
    ]

    for line in clean_lines[:3]:
        line_lower = line.lower()
        if any(word in line_lower for word in not_name_words):
            continue
        if '@' in line:
            continue
        if len(line) < 4 or len(line) > 40:
            continue
        if line.isupper():
            continue
        return line

    return clean_lines[0] if clean_lines else "Unknown"


def extract_email(text):
    # Finds email address using regex pattern
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(pattern, text)
    return emails[0] if emails else "Not found"


def extract_skills(text):
    # Checks which skills from SKILLS_DB appear in resume text
    text_lower = text.lower()
    found_skills = set()
    for skill in SKILLS_DB:
        if skill.lower() in text_lower:
            found_skills.add(skill)
    return sorted(list(found_skills))


def parse_resume(text):
    # Master function — runs all extractors
    # Returns clean dictionary with all candidate info
    skills = extract_skills(text)
    return {
        "name"        : extract_name(text),
        "email"       : extract_email(text),
        "skills"      : skills,
        "skill_count" : len(skills),
        "text_length" : len(text)
    }