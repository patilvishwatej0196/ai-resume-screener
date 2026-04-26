# jd_extractor.py
# This file extracts required skills and keywords from job descriptions
# We use spaCy NLP + our skills database to find what a job needs
# Later this is compared against resume skills to calculate match score

# Import spaCy for NLP processing
import spacy

# Import os for reading files from folders
import os

# Import re for pattern matching
import re

# Load the English language model
nlp = spacy.load("en_core_web_sm")

# -------------------------------------------------------
# SKILLS DATABASE - same as parser.py
# We check job descriptions against this list too
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

    # Soft Skills
    "communication", "teamwork", "leadership", "problem solving",
    "critical thinking", "time management"
]

# -------------------------------------------------------
# STOP WORDS - common words we want to ignore
# These add no value to skill matching
# -------------------------------------------------------

STOP_WORDS = [
    # Common English words
    "the", "and", "or", "in", "of", "to", "a", "an", "is",
    "are", "with", "for", "on", "at", "by", "we", "you",
    "our", "your", "will", "have", "has", "be", "this",
    "that", "from", "as", "it", "its", "not", "but", "if",

    # Job description filler words
    "experience", "required", "looking", "candidate", "good",
    "strong", "ability", "knowledge", "understanding", "must",
    "should", "preferred", "plus", "bonus", "excellent",
    "working", "work", "role", "position", "team", "company",

    # Action words that are not skills
    "build", "built", "develop", "create", "design", "manage",
    "train", "training", "deploy", "monitor", "write", "support",
    "collaborate", "participate", "maintain", "implement", "use",
    "ensure", "provide", "define", "analyze", "lead", "drive",

    # Generic nouns that are not skills
    "year", "years", "fresher", "fresher", "job", "title",
    "skill", "skills", "responsibility", "qualification",
    "business", "product", "science", "field", "concept",
    "library", "tool", "platform", "framework", "basic",
    "fundamental", "familiarity", "proficiency", "understanding",
    "result", "performance", "accuracy", "metric", "dataset",
    "model", "network", "system", "pipeline", "production",
    "pattern", "insight", "finding", "decision", "report",
    "task", "function", "module", "project", "program",

    # Location words
    "india", "pune", "bangalore", "hyderabad", "mumbai",
    "delhi", "maharashtra", "karnataka", "telangana", "location",

    # Company name words
    "pvt", "ltd", "techsoft", "ventures", "analytics",
    "solutions", "technologies", "services",

    # Numbers and misc
    "non", "per", "via", "etc", "e.g", "i.e",

    # Partial words that appear due to splitting
    "panda", "scikit", "transformer", "mlop", "apis",
    "rnns", "cnns", "oop", "gcp", "datum",

    # Partial skill words — not actual skills
    "computer", "rest", "version", "control",
    "core", "concept", "framework", "language"
]

# -------------------------------------------------------
# FUNCTION 1: Clean raw text
# -------------------------------------------------------

def clean_text(text):
    # This function cleans up job description text
    # before we extract keywords from it

    # Convert everything to lowercase
    # so Python = python = PYTHON
    text = text.lower()

    # Remove special characters like *, #, -, bullets
    # Keep only letters, numbers, spaces, dots, slashes
    # re.sub replaces the pattern with empty string ""
    text = re.sub(r'[^\w\s./]', ' ', text)

    # Remove extra whitespace and newlines
    # split() splits on any whitespace
    # join() puts it back together with single spaces
    text = ' '.join(text.split())

    return text


# -------------------------------------------------------
# FUNCTION 2: Extract keywords from job description text
# -------------------------------------------------------

def extract_jd_keywords(text):
    # This function extracts required skill keywords
    # from a job description text string

    # Step 1: Clean the text first
    cleaned = clean_text(text)

    # Step 2: Create empty set for found keywords
    # Set automatically removes duplicates
    keywords = set()

    # Step 3: Direct skill matching
    # Check every skill in our database against the JD text
    for skill in SKILLS_DB:

        # Check if this skill appears in the cleaned JD text
        if skill.lower() in cleaned:

            # Add to keywords set
            keywords.add(skill.lower())

    # Step 4: spaCy processing for additional keywords
    # Process the cleaned text through spaCy NLP pipeline
    doc = nlp(cleaned[:5000])  # limit to 5000 chars for speed

    # Step 5: Extract individual meaningful tokens
    for token in doc:
        if (not token.is_stop and
            not token.is_punct and
            token.is_alpha and
            len(token.text) > 3 and        # increased from 2 to 3
            token.pos_ in ["NOUN", "PROPN"]):

            word = token.lemma_.lower()

            # Extra check - skip if in our stop words
            if word not in STOP_WORDS:

                # Only add if it matches something in SKILLS_DB
                # This prevents random nouns from being added
                if any(word in skill for skill in SKILLS_DB):
                    keywords.add(word)

    # Step 6: Extract noun chunks (multi-word phrases)
    for chunk in doc.noun_chunks:

        # Get chunk text cleaned up
        chunk_text = chunk.text.lower().strip()

        # Only keep 2-3 word chunks
        word_count = len(chunk_text.split())
        if 2 <= word_count <= 3:

            # Check if any skill from our DB is in this chunk
            for skill in SKILLS_DB:
                if skill in chunk_text:
                    keywords.add(skill)

    # Step 7: Remove any remaining stop words from final set
    final_keywords = {
        kw for kw in keywords
        if kw not in STOP_WORDS and len(kw) > 2
    }

    # Return as a sorted list
    return sorted(list(final_keywords))


# -------------------------------------------------------
# FUNCTION 3: Read a JD file and extract its keywords
# -------------------------------------------------------

def process_jd_file(file_path):
    # This function reads a .txt job description file
    # and returns its extracted keywords

    try:
        # Open and read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        # Extract keywords from the text
        keywords = extract_jd_keywords(text)

        # Return both the raw text and extracted keywords
        return {
            "file": os.path.basename(file_path),  # just filename, not full path
            "raw_text": text,
            "keywords": keywords,
            "keyword_count": len(keywords)
        }

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


# -------------------------------------------------------
# FUNCTION 4: Process all JD files in a folder
# -------------------------------------------------------

def process_all_jd_files(folder_path):
    # This function reads all .txt files in the
    # job_descriptions folder and processes each one

    # Empty list to store results
    all_jds = []

    # Check the folder exists
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return all_jds

    # Loop through every file in the folder
    for filename in os.listdir(folder_path):

        # Only process .txt files
        if filename.endswith('.txt'):

            # Build full file path
            full_path = os.path.join(folder_path, filename)

            # Process this JD file
            result = process_jd_file(full_path)

            # Only add if processing was successful
            if result:
                all_jds.append(result)
                print(f"Processed: {filename} -> {result['keyword_count']} keywords")

    return all_jds


# -------------------------------------------------------
# MAIN: Test everything when run directly
# -------------------------------------------------------

if __name__ == "__main__":

    print("=" * 55)
    print("JD EXTRACTOR - TEST RUN")
    print("=" * 55)

    # Test 1: Test on sample JD text
    print("\n[TEST 1] Extracting from sample JD text...")
    print("-" * 40)

    sample_jd = """
    Job Title: Machine Learning Engineer
    Experience: 0-2 years (Freshers welcome)

    Required Skills:
    Python programming with strong fundamentals
    Machine learning libraries: scikit-learn, pandas, numpy
    Deep learning basics using TensorFlow or PyTorch
    NLP concepts: tokenization, embeddings, text classification
    Model training, evaluation, and tuning using scikit-learn
    Git and GitHub for version control

    Good to Have:
    Knowledge of Hugging Face transformers and BERT
    Familiarity with Flask or FastAPI for model deployment
    Understanding of Docker and cloud platforms like AWS

    Responsibilities:
    Build and train machine learning models
    Process and clean training datasets using pandas
    Deploy models as REST APIs using Flask
    """

    keywords = extract_jd_keywords(sample_jd)
    print(f"Keywords found: {len(keywords)}")
    print(f"Keywords: {', '.join(keywords)}")

    # Test 2: Process all real JD files
    print("\n[TEST 2] Processing all job description files...")
    print("-" * 40)

    jd_folder = "data/job_descriptions"
    all_jds = process_all_jd_files(jd_folder)

    if all_jds:
        print(f"\nSuccessfully processed {len(all_jds)} job descriptions")

        # Show keywords for each JD
        for jd in all_jds:
            print(f"\n{jd['file']}:")
            print(f"  Keywords ({jd['keyword_count']}): {', '.join(jd['keywords'][:10])}...")
    else:
        print("No .txt files found in data/job_descriptions/")

    print("\n" + "=" * 55)
    print("JD EXTRACTOR TEST COMPLETE")
    print("=" * 55)