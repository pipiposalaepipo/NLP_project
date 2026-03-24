from flask import Flask
import os

def create_app():
    # ใช้ os.path.dirname(os.path.abspath(__file__)) เพื่อหาตำแหน่งที่แท้จริงของโฟลเดอร์ website
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(base_dir, 'templates')
    
    app = Flask(__name__, template_folder=template_dir)
    
    app.config['SECRET_KEY'] = 'Eieiza'
    app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, 'uploads')
    
    app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  
    
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    from .view import views 
    app.register_blueprint(views, url_prefix='/')

    return app