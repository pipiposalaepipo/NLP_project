from flask import render_template # เพิ่ม import ตัวนี้ด้วย
from website import create_app

app = create_app()

# --- เพิ่มส่วนนี้เข้าไป ---
@app.route('/')
def home():
    return render_template('index.html')
# -----------------------

if __name__ == "__main__":
    app.run(debug=True)