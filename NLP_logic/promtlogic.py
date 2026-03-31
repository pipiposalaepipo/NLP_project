# NLP_logic/promtlogic.py
import json
import re
from Call_API import GeminiManager

API_KEY = "AIzaSyCnpJ3c5F4o_FucVaXI-YoM5bTsJsRy2jk"
ai_assistant = GeminiManager(API_KEY)


def analyze_resume_against_jd(resume_text: str, jd_text: str) -> dict:
    """
    ส่ง Resume + Job Description ให้ Gemini วิเคราะห์
    คืนค่าเป็น dict ที่พร้อมใช้งานใน Analyze.py
    """

    prompt = f"""
คุณคือผู้เชี่ยวชาญด้าน HR และ NLP
เปรียบเทียบ Resume กับ Job Description ที่ให้มา แล้วตอบเป็น JSON เท่านั้น
ห้ามมีคำอธิบายหรือ markdown อื่นใดนอกจาก JSON

รูปแบบ JSON ที่ต้องการ (ตัวเลขทั้งหมดเป็น integer 0-100):
{{
  "overall_score": <คะแนนรวมความเหมาะสม 0-100>,
  "technical_score": <คะแนนทักษะเทคนิค 0-100>,
  "softskill_score": <คะแนน soft skills 0-100>,
  "experience_score": <คะแนนประสบการณ์ 0-100>,
  "matched_skills": [<ทักษะที่ตรงกับ JD สูงสุด 3 อย่าง>],
  "skill_scores": [<คะแนนทักษะแต่ละอย่างใน matched_skills ตามลำดับ>],
  "summary": "<สรุปความเหมาะสมใน 1-2 ประโยคภาษาอังกฤษ>"
}}

Job Description:
{jd_text}

Resume:
{resume_text}
"""

    raw = ai_assistant.send_request(prompt)

    # ดึง JSON ออกจาก response (กัน Gemini แนบ markdown มาด้วย)
    try:
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            raise ValueError("No JSON found in response")
    except Exception:
        # Fallback กรณี parse ไม่ได้
        result = {
            "overall_score": 0,
            "technical_score": 0,
            "softskill_score": 0,
            "experience_score": 0,
            "matched_skills": ["N/A", "N/A", "N/A"],
            "skill_scores": [0, 0, 0],
            "summary": "Could not parse AI response."
        }

    return result