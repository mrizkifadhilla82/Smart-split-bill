import os
import time
import json
import base64
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Konfigurasi Google
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Konfigurasi Groq
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def validate_data(data):
    if not data:
        return "N/A (No Data)"
    
    try:
        items = data.get("items", [])
        # 1. Hitung Subtotal Murni (Harga Makanan Saja)
        calc_subtotal = sum(item.get("price", 0) * item.get("qty", 1) for item in items)
        
        # 2. Ambil data dari AI
        declared_total = data.get("total", 0)
        tax = data.get("tax", 0)  # Kita coba ambil field tax jika AI mengekstraknya
        
        # 3. Logika Validasi Baru:
        # Jika Subtotal + Pajak == Total, maka SEMPURNA
        if (calc_subtotal + tax) == declared_total:
            return "✅ PASSED (Match with Tax)"
        
        # Jika ada selisih, cek apakah selisihnya wajar (misal 10% untuk pajak)
        diff = declared_total - calc_subtotal
        if diff > 0 and (0.09 <= diff/calc_subtotal <= 0.11): # Range pajak 10%
            return f"✅ PASSED (Detected ~10% Tax/Service: {diff})"
            
        return f"⚠️ CHECK (Items Sum: {calc_subtotal}, Final Total: {declared_total})"
    except Exception:
        return "❌ ERROR"

def clean_json_output(text):
    """Membersihkan tag markdown ```json agar bisa di-parse"""
    text = text.strip()
    if text.startswith("```json"):
        text = text.replace("```json", "", 1).replace("```", "", 1).strip()
    elif text.startswith("```"):
        text = text.replace("```", "", 2).strip()
    return text

def test_gemini_flash(image_path):
    print(f"\n[1] Mengetes Gemini 2.5 Flash pada {image_path}...")
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = "Extract receipt items into JSON. Crucial: Identify if the price shown is the price per unit or the total price for that row. If it's the total price for multiple units, divide it first to get the unit price for the 'price' field. Format: {'items': [{'name': str, 'qty': int, 'price': int}], 'total': int}."
    
    start_time = time.time()
    try:
        sample_file = genai.upload_file(path=image_path)
        response = model.generate_content([prompt, sample_file])
        duration = time.time() - start_time
        
        # Parse ke JSON untuk divalidasi
        clean_text = clean_json_output(response.text)
        data = json.loads(clean_text)
        
        return {"status": "Success", "time": round(duration, 2), "data": data}
    except Exception as e:
        return {"status": f"Error: {str(e)}", "time": round(time.time() - start_time, 2), "data": None}

def test_llama_groq(image_path):
    print(f"[2] Mengetes Llama 4 Scout (Groq) pada {image_path}...")
    base64_image = encode_image(image_path)
    
    start_time = time.time()
    try:
        completion = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract receipt items into JSON. IMPORTANT: If the receipt shows a total price for multiple quantities (e.g., 2 items for 18.182), treat the 18.182 as the total for that row and calculate the unit price accordingly. Format: {'items': [{'name': str, 'qty': int, 'price': int}], 'total': int}. Output JSON only."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        duration = time.time() - start_time
        
        # Parse hasil dari Groq
        data = json.loads(completion.choices[0].message.content)
        
        return {"status": "Success", "time": round(duration, 2), "data": data}
    except Exception as e:
        return {"status": f"Error: {str(e)}", "time": round(time.time() - start_time, 2), "data": None}

# --- EKSEKUSI UTAMA ---
DAFTAR_NOTA = ["research/nota_1.jpeg", "research/nota_2.jpeg"]

print("=== MEMULAI COMPARISON TEST (SPEED & ACCURACY) ===")

for nota in DAFTAR_NOTA:
    print(f"\n" + "="*50)
    print(f"FILE: {nota}")
    print("="*50)
    
    # --- TEST GEMINI ---
    res_flash = test_gemini_flash(nota)
    val_flash = validate_data(res_flash['data'])
    print(f"   >> Hasil: {res_flash['status']}")
    print(f"   >> Waktu: {res_flash['time']} detik")
    print(f"   >> Validasi: {val_flash}")
    
    # --- TEST GROQ ---
    res_llama = test_llama_groq(nota)
    val_llama = validate_data(res_llama['data'])
    print(f"   >> Hasil: {res_llama['status']}")
    print(f"   >> Waktu: {res_llama['time']} detik")
    print(f"   >> Validasi: {val_llama}")

print("\n" + "="*50)
print("--- ANALISIS SELESAI ---")
print("="*50)