# NLP_logic/gemini_client.py
from google import genai

class GeminiManager:
    def __init__(self, api_key):
        # สร้าง Client ครั้งเดียวใช้ได้ทั้งโปรเจกต์
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash" # หรือตัวที่หนุ่มรันผ่าน

    def send_request(self, prompt):
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Error connecting to Gemini: {e}"