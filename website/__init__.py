from flask import Flask
import os

from .Analyze import analyze_bp 

def create_app():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(base_dir, 'templates')
    
    app = Flask(__name__, template_folder=template_dir)
    
    app.config['SECRET_KEY'] = 'Eieiza'
    app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, 'uploads')
    app.config['Descript_FOLDER'] = os.path.join(base_dir, 'job_descriptions')
    
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(app.config['Descript_FOLDER']):
        os.makedirs(app.config['Descript_FOLDER'])

    # ลงทะเบียนโดยใช้ตัวแปร Blueprint (analyze_bp)
    app.register_blueprint(analyze_bp, url_prefix='/') 

    return app