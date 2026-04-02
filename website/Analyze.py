# website/Analyze.py
from flask import Blueprint, render_template, request, current_app
import os
import sys
from werkzeug.utils import secure_filename

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'NLP_logic'))

from NLP import extract_text_from_pdf, extract_email, analyze_resume
from promtlogic import extract_keywords_from_jd

analyze_bp = Blueprint('analyze_bp', __name__)


@analyze_bp.route('/analyze', methods=['POST'])
def start_analysis():
    job_file     = request.files.get('job_pdf')
    resume_files = request.files.getlist('resume_pdfs')
    results      = []

    if job_file and resume_files:

        # ── STEP 1: อ่าน JD → LLM extract keywords ─────────────────────
        job_name = secure_filename(job_file.filename)
        job_path = os.path.join(current_app.config['Descript_FOLDER'], job_name)
        job_file.save(job_path)

        jd_text  = extract_text_from_pdf(job_path)
        keywords = extract_keywords_from_jd(jd_text)

        # ── STEP 2: วนลูปแต่ละ Resume ───────────────────────────────────
        for i, resume in enumerate(resume_files):
            if resume.filename == '':
                continue

            res_name = secure_filename(resume.filename)
            res_path = os.path.join(current_app.config['UPLOAD_FOLDER'], res_name)
            resume.save(res_path)

            # อ่าน PDF ครั้งเดียว
            resume_text = extract_text_from_pdf(res_path)

            # ดึง email
            email = extract_email(resume_text)

            # รัน NLP Pipeline
            nlp_result = analyze_resume(resume_text, jd_text, keywords)

            # top 3 matched skills + fuzzy score จริง
            keyword_scores = nlp_result["keyword_scores"]
            matched        = nlp_result["matched"]
            top_skills     = (matched + ["N/A", "N/A", "N/A"])[:3]
            top_skill_scores = [
                keyword_scores.get(s, 0) if s != "N/A" else 0
                for s in top_skills
            ]

            keyword_match  = round(nlp_result["match_rate"] * 100)
            missing_skills = max(0, 100 - keyword_match)

            results.append({
                "id":             str(i + 1),
                "name":           email,
                "score":          nlp_result["score"],
                "skills":         top_skill_scores[:3],
                "matched_skills": top_skills,
                "breakdown":      [keyword_match, missing_skills],
                "tfidf_sim":      round(nlp_result["tfidf_sim"] * 100),
                "matched":        nlp_result["matched"],
                "missing":        nlp_result["missing"],
            })

        # เรียงจากคะแนนสูงสุด
        results.sort(key=lambda x: x["score"], reverse=True)
        for rank, r in enumerate(results, 1):
            r["id"] = str(rank)

        keywords_str = ", ".join(keywords)
        return render_template(
            'index.html',
            message=f" วิเคราะห์สำเร็จ {len(results)} คน | Keywords: {len(keywords)} คำ → {keywords_str}",
            candidates=results
        )

    return render_template('index.html', message="⚠️ กรุณาเลือกไฟล์ให้ครบทั้ง JD และ Resume")