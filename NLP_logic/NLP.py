# NLP_logic/NLP.py
# NLP Pipeline สำหรับ Smart Resume Analyzer
#
# STEP 1: extract_text_from_pdf()  — อ่าน PDF → plain text
# STEP 2: preprocess()             — Tokenization + Preprocessing
# STEP 3: fuzzy_match_keywords()   — Fuzzy Matching กับ keyword list จาก LLM
# STEP 4: tfidf_score()            — TF-IDF วัดความสำคัญของ keyword ใน Resume
# STEP 5: compute_score()          — รวมผลจาก fuzzy + tfidf → score 0-100

import re
import pypdf
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pdfminer.high_level import extract_text

# ดาวน์โหลด resource ที่ nltk ต้องการ (รันครั้งแรกเท่านั้น)
nltk.download('punkt',        quiet=True)
nltk.download('punkt_tab',    quiet=True)
nltk.download('stopwords',    quiet=True)

STOP_WORDS = set(stopwords.words('english'))
FUZZY_THRESHOLD = 75  # คะแนน fuzzy ขั้นต่ำที่ถือว่า "ตรง" (0-100)


# ─────────────────────────────────────────────
# STEP 1: PDF Extraction
# ─────────────────────────────────────────────
def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        text = extract_text(pdf_path)
        return text.strip()
    except Exception as e:
        return f"[PDF Error: {e}]"

# ─────────────────────────────────────────────
# STEP 2: Tokenization + Preprocessing
# ─────────────────────────────────────────────
def preprocess(text: str) -> list:
    """
    รับ raw text คืน list of cleaned tokens
    ขั้นตอน:
      1. lowercase ทั้งหมด
      2. ตัดเครื่องหมายพิเศษออก (เก็บ + และ # ไว้ เช่น C++, C#)
      3. tokenize ด้วย nltk word_tokenize
      4. ลบ stopwords (the, a, is, ...)
      5. ลบ token ที่สั้นเกินไป (< 2 ตัวอักษร)
    """
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s\+\#]', ' ', text)
    tokens = word_tokenize(text)
    tokens = [t for t in tokens if t not in STOP_WORDS and len(t) >= 2]
    return tokens


# ─────────────────────────────────────────────
# STEP 3: Fuzzy Matching
# ─────────────────────────────────────────────
def fuzzy_match_keywords(resume_tokens: list, keywords: list) -> dict:
    """
    จับคู่ keyword แต่ละตัวกับ token ใน Resume แบบ fuzzy
    ใช้ fuzz.partial_ratio เพื่อจับ:
      - "Python"  vs "python3"    → match
      - "React"   vs "ReactJS"    → match
      - "Java"    vs "JavaScript" → ไม่ match (score ต่ำกว่า threshold)

    คืน dict:
      {
        "matched":    ["Python", "SQL", ...],
        "missing":    ["AWS", ...],
        "match_rate": 0.75
      }
    """
    resume_text_joined = " ".join(resume_tokens)
    matched = []
    missing = []

    for kw in keywords:
        kw_clean = kw.lower().strip()
        score = fuzz.partial_ratio(kw_clean, resume_text_joined)
        if score >= FUZZY_THRESHOLD:
            matched.append(kw)
        else:
            missing.append(kw)

    total = len(keywords)
    match_rate = len(matched) / total if total > 0 else 0.0

    return {
        "matched":    matched,
        "missing":    missing,
        "match_rate": round(match_rate, 4)
    }


# ─────────────────────────────────────────────
# STEP 4: TF-IDF Similarity
# ─────────────────────────────────────────────
def tfidf_score(resume_text: str, jd_text: str) -> float:
    """
    วัดความคล้ายคลึงระหว่าง Resume กับ JD ด้วย TF-IDF + Cosine Similarity

    แนวคิด:
      - TF-IDF แปลง text เป็น vector โดยให้น้ำหนักคำที่สำคัญมากกว่า stopwords
      - Cosine Similarity วัดมุมระหว่าง vector → 1.0 = เหมือนกันทุกอย่าง

    คืนค่า float 0.0 - 1.0
    """
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([jd_text, resume_text])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return round(float(similarity[0][0]), 4)
    except Exception:
        return 0.0


# ─────────────────────────────────────────────
# STEP 5: Compute Final Score
# ─────────────────────────────────────────────
def compute_score(match_rate: float, tfidf_sim: float) -> int:
    """
    รวมผลจาก 2 วิธีเป็น score เดียว 0-100

    สูตร (Weighted Average):
      - Fuzzy Match Rate  → น้ำหนัก 60%  (ตรงกับ keyword ที่ HR กำหนด)
      - TF-IDF Similarity → น้ำหนัก 40%  (ความใกล้เคียงโดยรวมกับ JD)

    เหตุผลที่ Fuzzy มีน้ำหนักมากกว่า:
      keyword ที่ LLM ดึงมาจาก JD คือสิ่งที่ HR ต้องการจริงๆ
      TF-IDF เป็น bonus สำหรับ Resume ที่เขียนสอดคล้องกับ JD โดยรวม
    """
    score = (match_rate * 0.60) + (tfidf_sim * 0.40)
    return round(score * 100)


# ─────────────────────────────────────────────
# Public Function: analyze_resume (เรียกจาก Analyze.py)
# ─────────────────────────────────────────────
def analyze_resume(resume_path: str, jd_text: str, keywords: list) -> dict:
    """
    รัน NLP Pipeline ทั้งหมดสำหรับ Resume 1 ไฟล์

    Parameters:
      resume_path : path ของไฟล์ PDF
      jd_text     : ข้อความ JD (plain text)
      keywords    : list ของ keyword ที่ LLM extract จาก JD

    Returns dict:
      {
        "score":       78,
        "match_rate":  0.75,
        "tfidf_sim":   0.62,
        "matched":     ["Python", "SQL", ...],
        "missing":     ["AWS", ...]
      }
    """
    # STEP 1
    resume_text = extract_text_from_pdf(resume_path)

    # STEP 2
    resume_tokens = preprocess(resume_text)

    # STEP 3
    fuzzy_result = fuzzy_match_keywords(resume_tokens, keywords)

    # STEP 4
    sim = tfidf_score(resume_text, jd_text)

    # STEP 5
    score = compute_score(fuzzy_result["match_rate"], sim)

    return {
        "score":      score,
        "match_rate": fuzzy_result["match_rate"],
        "tfidf_sim":  sim,
        "matched":    fuzzy_result["matched"],
        "missing":    fuzzy_result["missing"]
    }