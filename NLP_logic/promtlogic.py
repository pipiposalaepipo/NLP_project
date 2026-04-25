# NLP_logic/promtlogic.py
# หน้าที่: ส่ง Job Description ให้ LLM extract keywords เท่านั้น
# NLP Pipeline ที่แท้จริงอยู่ใน NLP.py

import json
import re
from Call_API import GeminiManager
import os

API_KEY = os.environ.get("AIzaSyA3QuuM3gt9Cr4v-cLskfpJeDRgnAz5ERs")
ai_assistant = GeminiManager(API_KEY)


def extract_keywords_from_jd(jd_text: str) -> list:
    """
    ส่ง JD text ให้ Gemini extract keywords
    คืน list of keyword strings เช่น ["Python", "SQL", "3 years experience"]
    """
    prompt = f"""
You are an HR expert. Extract important keywords from the Job Description below.
Reply with JSON only — no explanation, no markdown.

Return this exact format:
{{
  "keywords": ["keyword1", "keyword2", "keyword3", ...]
}}

Rules:
- Include technical skills (e.g. Python, SQL, AWS)
- Include soft skills (e.g. teamwork, communication)
- Include experience requirements (e.g. 3 years experience)
- Maximum 15 keywords
- Use the exact words from the JD

Job Description:
{jd_text}
"""

    raw = ai_assistant.send_request(prompt)
    print("RAW:", raw) 

    try:
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            keywords = result.get("keywords", [])
            # กัน Gemini คืนค่าผิด format
            if isinstance(keywords, list) and len(keywords) > 0:
                return keywords
    except Exception:
        pass

    # Fallback: ถ้า parse ไม่ได้ คืน list ว่าง
    return []