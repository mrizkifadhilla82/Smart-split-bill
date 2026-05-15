import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiExtractor:
    def __init__(self):
        # Menggunakan API Key sesuai yang kamu pakai di code sebelumnya
        genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 
        # Mengembalikan ke versi yang kamu gunakan tadi
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def extract_nota(self, image_path):
        prompt = """
        Extract receipt items into JSON:
        {
            "items": [{"name": str, "qty": int, "price": int}],
            "subtotal": int,
            "tax": int,
            "total": int
        }
        Output ONLY JSON.
        """

        try:
            sample_file = genai.upload_file(path=image_path)
            response = self.model.generate_content([prompt, sample_file])
            
            # Pembersihan format markdown agar json.loads tidak error
            raw_text = response.text.strip()
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].strip()
            return json.loads(raw_text)
        except Exception as e:
            print(f"Gemini Error: {e}")
            return None