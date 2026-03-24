from flask import Blueprint, render_template, request, current_app
import os

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        if 'pdf_file' in request.files:
            file = request.files['pdf_file']
            if file.filename != '' and file.filename.endswith('.pdf'):
                # ใช้ current_app เพื่อดึงค่า config จากตัวแปรหลัก
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
                file.save(upload_path)
                message = f"อัปโหลดไฟล์ {file.filename} สำเร็จแล้ว!"
            else:
                message = "กรุณาเลือกไฟล์ที่เป็น .pdf เท่านั้น"
    
    return render_template('index.html', message=message)