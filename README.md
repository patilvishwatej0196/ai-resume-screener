---
title: AI Resume Screener
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: "1.32.0"
app_file: streamlit_app.py
pinned: false
---

# 🤖 AI Resume Screening & Job Matching Platform

> An intelligent resume screening system that uses **Sentence-BERT** semantic matching and **spaCy NLP** to automatically rank candidates against job descriptions — built as a solo project during placement preparation.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red?style=flat&logo=streamlit)
![spaCy](https://img.shields.io/badge/spaCy-NLP-09A3D5?style=flat)
![BERT](https://img.shields.io/badge/Sentence--BERT-AI-orange?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

---

## 🎯 Problem Statement

Recruiters manually screen hundreds of resumes for every job opening — a process that takes days, is inconsistent, and is prone to human bias. This platform automates the screening process using AI, reducing manual review time by ~70% while improving matching accuracy through semantic understanding.

---

## ✨ Features

- 📄 **PDF Resume Parser** — extracts text, name, email and skills from any PDF resume
- 🧠 **Sentence-BERT Matching** — understands meaning, not just keywords ("Python developer" ≈ "Python programmer")
- 🔑 **Keyword Skill Matching** — matches resume skills against job description requirements
- ⭐ **Combined Scoring** — final score = 60% BERT semantic + 40% keyword overlap
- 🏆 **Candidate Ranking** — ranks all uploaded resumes from best to worst match
- ✅ **Auto Shortlisting** — automatically shortlists candidates above a score threshold
- 🎯 **Skill Gap Analysis** — shows exactly which skills are matched and which are missing
- 🌐 **Streamlit Web UI** — clean browser-based interface, no technical knowledge needed

---

