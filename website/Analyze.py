from flask import Blueprint, render_template, request, current_app
import os
from werkzeug.utils import secure_filename 


analyze_bp = Blueprint('analyze_bp', __name__)


@analyze_bp.route('/analyze', methods=['POST'])
def start_analysis(): 
    job_file = request.files.get('job_pdf')
    # เปลี่ยนมาใช้ getlist และชื่อต้องตรงกับ name="resume_pdfs" ใน HTML
    resume_files = request.files.getlist('resume_pdfs') 
    
    results = []
    
    if job_file and resume_files:
        # 1. จัดการไฟล์ Job Description (ไฟล์เดียว)
        job_name = secure_filename(job_file.filename)
        job_path = os.path.join(current_app.config['Descript_FOLDER'], job_name)
        job_file.save(job_path)

        # 2. วนลูปจัดการ Resume (หลายไฟล์)
        for i, resume in enumerate(resume_files):
            if resume.filename == '': continue # กันกรณีส่งไฟล์ว่างมา
            
            res_name = secure_filename(resume.filename)
            res_path = os.path.join(current_app.config['UPLOAD_FOLDER'], res_name)
            resume.save(res_path)

            # 3. จำลองการวิเคราะห์ NLP (ใส่ Logic จริงของคุณตรงนี้)
            # เราใช้ i+1 เป็น ID ชั่วคราวเพื่อให้ JS ในหน้าเว็บหาเจอ
            results.append({
                "id": str(i + 1), 
                "name": resume.filename, 
                "score": 85 - (i * 10),
                "skills": [90-(i*3), 75+(i*2), 30],  
                "breakdown": [40, 30-(i*5), 30] 
            })

        # ส่งผลลัพธ์กลับไปที่หน้าเดิมพร้อมข้อมูล candidates
        return render_template('index.html', 
                               message=f"วิเคราะห์สำเร็จ {len(results)} คน", 
                               candidates=results)

    # กรณีเลือกไฟล์ไม่ครบ
    return render_template('index.html', message="กรุณาเลือกไฟล์ให้ครบทั้ง JD และ Resume")