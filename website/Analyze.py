# website/Analyze.py
from flask import Blueprint, render_template, request, current_app
import os
import sys
from werkzeug.utils import secure_filename

# เพิ่ม path ของ NLP_logic เข้า sys.path เพื่อ import ได้
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'NLP_logic'))

from NLP import extract_text_from_pdf
from promtlogic import analyze_resume_against_jd

analyze_bp = Blueprint('analyze_bp', __name__)


@analyze_bp.route('/analyze', methods=['POST'])
def start_analysis():
    job_file = request.files.get('job_pdf')
    resume_files = request.files.getlist('resume_pdfs')

    results = []

    if job_file and resume_files:
        # 1. บันทึกและอ่านข้อความจาก Job Description PDF
        job_name = secure_filename(job_file.filename)
        job_path = os.path.join(current_app.config['Descript_FOLDER'], job_name)
        job_file.save(job_path)
        jd_text = extract_text_from_pdf(job_path)

        # 2. วนลูปแต่ละ Resume
        for i, resume in enumerate(resume_files):
            if resume.filename == '':
                continue

            res_name = secure_filename(resume.filename)
            res_path = os.path.join(current_app.config['UPLOAD_FOLDER'], res_name)
            resume.save(res_path)

            # 3. อ่านข้อความจาก Resume PDF
            resume_text = extract_text_from_pdf(res_path)

            # 4. ส่งให้ Gemini วิเคราะห์เทียบกับ JD
            analysis = analyze_resume_against_jd(resume_text, jd_text)

            # 5. แปลงผลลัพธ์ให้ตรงกับ format ที่ index.html ต้องการ
            results.append({
                "id": str(i + 1),
                "name": resume.filename,
                "score": analysis.get("overall_score", 0),
                "skills": analysis.get("skill_scores", [0, 0, 0]),
                "breakdown": [
                    analysis.get("technical_score", 0),
                    analysis.get("softskill_score", 0),
                    analysis.get("experience_score", 0)
                ],
                "matched_skills": analysis.get("matched_skills", ["N/A", "N/A", "N/A"]),
                "summary": analysis.get("summary", "")
            })

        # เรียงลำดับจากคะแนนสูงสุด
        results.sort(key=lambda x: x["score"], reverse=True)
        # ใส่ rank หลังเรียงแล้ว
        for rank, r in enumerate(results, 1):
            r["id"] = str(rank)

        return render_template(
            'index.html',
            message=f"✅ วิเคราะห์สำเร็จ {len(results)} คน",
            candidates=results
        )

    return render_template('index.html', message="⚠️ กรุณาเลือกไฟล์ให้ครบทั้ง JD และ Resume")