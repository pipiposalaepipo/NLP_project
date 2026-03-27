from flask import Blueprint, render_template, request, current_app
import os
from werkzeug.utils import secure_filename # เพิ่มตัวนี้เพื่อความปลอดภัย

# 1. เปลี่ยนชื่อตัวแปร Blueprint เป็นตัวเล็ก (กันสับสน)
analyze_bp = Blueprint('analyze_bp', __name__)

# 2. ชื่อฟังก์ชันต้องไม่ซ้ำกับ analyze_bp
@analyze_bp.route('/analyze', methods=['POST'])
def start_analysis(): 
    job_file = request.files.get('job_pdf')
    resume_file = request.files.get('resume_pdf')

    if job_file and resume_file:
        # ใช้ current_app.config แทน app.config
        job_name = secure_filename(job_file.filename)
        job_path = os.path.join(current_app.config['Descript_FOLDER'], job_name)
        job_file.save(job_path)

        res_name = secure_filename(resume_file.filename)
        res_path = os.path.join(current_app.config['UPLOAD_FOLDER'], res_name)
        resume_file.save(res_path)

        return render_template('index.html', message="อัปโหลดสำเร็จทั้ง 2 ไฟล์! แยกโฟลเดอร์เรียบร้อย")
    
    return render_template('index.html', message="กรุณาเลือกไฟล์ให้ครบ")