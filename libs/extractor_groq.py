import os
import base64
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqExtractor:
    def __init__(self):
        # Mengambil API Key dari .env
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"

    def encode_image(self, image_path):
        """Mengubah gambar menjadi format Base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def extract_nota(self, image_path):
        base64_image = self.encode_image(image_path)
        
        prompt = """
        Extract the following receipt items into a clean JSON format.
        
        CRITICAL RULES FOR CALCULATION:
        1. The "price" field MUST be the price for ONE (1) unit (Unit Price).
        2. If the receipt shows a total/subtotal for multiple items (e.g., '2 Es Teh ... 36.364'), 
           you MUST divide the total by the quantity (36.364 / 2 = 18.182).
        3. Put the result of that division (18.182) in the "price" field.
        4. Ensure "qty" is an integer.
        
        The JSON should have this structure:
        {
            "items": [
                {"name": "string", "qty": int, "price": int}
            ],
            "subtotal": int,
            "tax": int,
            "total": int
        }
        Only return the JSON object. No preamble or explanation.
        """

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                temperature=0, # Set ke 0 agar hasil lebih konsisten/tidak ngawur
                response_format={"type": "json_object"} # Menjamin output selalu JSON
            )

            # Mengambil string hasil dan mengubahnya jadi dictionary Python
            result_content = completion.choices[0].message.content
            return json.loads(result_content)

        except Exception as e:
            print(f"Error pada Groq Extractor: {e}")
            return None

# --- TESTING AREA ---
if __name__ == "__main__":
    extractor = GroqExtractor()
    # Ganti dengan path nota Anda untuk mencoba
    hasil = extractor.extract_nota("research/nota_1.jpeg") 
    if hasil:
        print(json.dumps(hasil, indent=4))
    else:
        print("Gagal ekstraksi.")