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
