Day 1 Challenges:
- Windows blocked script execution → fixed with Set-ExecutionPolicy
- Git was pushing venv folder (392MB) → fixed with .gitignore + git rm --cached
- GitHub rejected large torch.dll file → fixed by wiping Git history and pushing clean

Day 2 Challenges:
- git push rejected (fetch first) → fixed with git pull origin main --allow-unrelated-histories
- Vim editor opened unexpectedly → exited with :wq command
- Typo: space before git command → CommandNotFoundException error

- Day 3 Challenges:
- jd_extractor picked up city names and filler words as skills
  → fixed by expanding STOP_WORDS list and adding SKILLS_DB filter
- Name extractor showed extra line (AI/ML Engineer after name)
  → fixed by splitting on \n and taking first part only
- Match scores were low (11-19%) before fix, improved after filtering
- 
Day 4 Challenges:
- Sentence-BERT model took 2-3 minutes to download on first run
  → after first download it caches locally and loads in seconds
  - "computer" and "rest" appearing as missing skills
  → partial words from "computer vision" and "rest api" being split
  → fixed by adding them to STOP_WORDS in jd_extractor.py

- BERT and keyword scores were identical in Test 3
  → because jd_keywords were not passed to rank_resumes()
  → fixed in updated app.py by passing parsed JD keywords properly

  Day 6 Challenges:
- ModuleNotFoundError: No module named 'docx'
  → installed python-docx with pip install python-docx
- DOCX temp file was being saved with .pdf extension
  → fixed by detecting uploaded file extension dynamically
  → file_ext = os.path.splitext(uploaded_file.name)[1]
- requirements.txt had old pinned spacy version
  → cleaned up to use unpinned versions for HF compatibility

  Day 7 Challenges:
- ModuleNotFoundError: No module named 'resume_parser'
  → resume_parser.py was missing from project
  → recreated the file with spaCy-free parse_resume() function
- jd_extractor_simple.py also missing
  → recreated with SKILLS_DB direct matching
- pip install pandas openpyxl needed for Excel export
  → added both to requirements.txt

Day 8 Challenges:
- Gmail App Password setup required 2-step verification first
  → enabled 2FA then created App Password at myaccount.google.com/apppasswords
- SMTPAuthenticationError when using real Gmail password
  → fixed by using 16-character App Password instead
- Candidate email not found when resume had no email
  → added validation: skip if email == "Not found" or "@" not in email
- .env credentials not loading in Streamlit
  → fixed by setting os.environ directly from sidebar inputs
