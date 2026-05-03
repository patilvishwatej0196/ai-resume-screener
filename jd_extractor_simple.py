# jd_extractor_simple.py
# SpaCy-free JD keyword extractor

SKILLS_DB = [
    "python", "java", "javascript", "c++", "c#", "r", "sql",
    "typescript", "kotlin", "swift", "go", "rust", "scala",
    "html", "css", "react", "angular", "vue", "nodejs", "flask",
    "django", "fastapi", "rest api", "graphql", "bootstrap",
    "machine learning", "deep learning", "nlp", "computer vision",
    "pandas", "numpy", "matplotlib", "seaborn", "scikit-learn",
    "tensorflow", "pytorch", "keras", "opencv", "hugging face",
    "bert", "transformers", "nltk",
    "mysql", "postgresql", "mongodb", "sqlite", "oracle",
    "redis", "elasticsearch", "firebase",
    "aws", "azure", "gcp", "docker", "kubernetes", "git",
    "github", "linux", "jenkins",
    "excel", "power bi", "tableau", "jupyter", "google colab",
    "spark", "hadoop"
]

def extract_jd_keywords(text):
    # Extracts skill keywords from job description text
    text_lower = text.lower()
    found = set()
    for skill in SKILLS_DB:
        if skill.lower() in text_lower:
            found.add(skill)
    return sorted(list(found))