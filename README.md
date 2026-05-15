# 🧾 SmartSplit AI: Receipt Parser & Bill Splitter

Aplikasi prototype berbasis web yang menggunakan Multimodal AI (**Llama-4-Scout via Groq**) untuk mengekstraksi data nota pembelian secara otomatis dan melakukan pembagian tagihan (*split bill*) secara akurat dan proporsional.

---

## 🚀 1. Cara Instalasi dan Menjalankan Code

### Langkah-langkah Menjalankan Lokal:

1.  **Persiapan Lingkungan:**
    Pastikan Anda telah menginstal Python 3.9 atau versi di atasnya.
2.  **Install Dependencies:**
    Buka terminal di folder proyek dan jalankan:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Konfigurasi API Key:**
    Buat file bernama `.env` di direktori utama dan masukkan API Key Groq Anda:
    ```env
    GROQ_API_KEY=isi_api_key_groq_anda_disini
    ```
4.  **Jalankan Aplikasi:**
    Jalankan perintah berikut:
    ```bash
    streamlit run app.py
    ```
5.  **Akses aplikasi** melalui browser di: [http://localhost:8501](http://localhost:8501)

---

## 🧪 2. Riset Model AI (Step 1)

Eksperimen dilakukan untuk membandingkan dua model Multimodal guna memenuhi **Requirement D**:

| Kriteria | Model 1: Gemini 2.5 Flash | Model 2: Llama-4-Scout (Groq) |
| :--- | :--- | :--- |
| **Status** | Tidak Dipilih | **DIPILIH (Selected)** |
| **Kecepatan** | Lambat (> 10 detik) | Sangat Cepat (< 2 detik) |
| **Akurasi** | Sangat Detail | Sangat Baik & Responsif |

**Alasan Pemilihan Model:**
Dipilih **Llama-4-Scout (Groq)** karena kecepatan inference yang sangat tinggi (< 2 detik). Meskipun Gemini 2.5 Flash memiliki OCR yang kuat, latensi di atas 10 detik merusak pengalaman pengguna (UX). Llama-4-Scout melalui infrastruktur Groq memberikan hasil hampir instan dengan akurasi format JSON yang sangat stabil.

---

## 🔍 3. Evaluasi dan Analisis (Step 3)

### A. Evaluasi Model Pembaca Bill
*   **Kelemahan Logika:** Pada riset awal, model sempat kesulitan membedakan antara Harga Satuan dan Total Harga Item ketika kuantitas (Qty) lebih dari satu. AI cenderung menganggap harga total sebagai harga satuannya.
*   **Solusi Improvisasi:** Kami menggunakan *Prompt Engineering* yang memaksa AI melakukan kalkulasi pembagian (Total Item / Qty) untuk mendapatkan harga satuan yang benar secara otomatis.

### B. Evaluasi Produk Web (Streamlit)
*   **Kelemahan UX (Manual Fatigue):** Aplikasi ini terasa kurang efisien ketika menangani nota dengan jumlah item yang sangat banyak dan jumlah peserta yang banyak. Proses memilih nama pembayar satu per satu untuk setiap baris item memakan waktu dan melelahkan bagi pengguna.
*   **Bug/Kelemahan:** Data akan hilang jika halaman browser di-refresh secara tidak sengaja karena sistem hanya mengandalkan *session state*.
*   **Ide Improvisasi:**
    *   **Fitur "Split to All":** Tombol otomatis untuk membagi harga satu item ke seluruh peserta yang ada tanpa perlu memilih satu per satu.
    *   **Integrasi Database:** Menggunakan SQLite agar data tetap tersimpan meskipun koneksi terputus atau halaman di-refresh.
    *   **Export Result:** Fitur untuk menyalin ringkasan tagihan langsung ke format teks WhatsApp untuk mempercepat proses penagihan.

---

## 📁 4. Struktur Folder Proyek
- `app.py`: Entry point aplikasi menggunakan Streamlit (Menangani UI dan Logic Alur Requirement A-G).
- `prompts.py`: Berisi instruksi sistem (System Message) untuk LLM guna menangani logika ekstraksi JSON dan perbaikan perhitungan item (kasus "Es Teh").
- `libs/`:
    - `extractor_groq.py`: Modul untuk komunikasi dengan API Groq (Llama-4-Scout).
    - `extractor_gemini.py`: Modul alternatif untuk komunikasi dengan API Gemini (digunakan saat riset/komparasi).
    - `calculator.py`: **Logika pembagian biaya (Split Bill), menghitung proporsi pajak dan servis untuk setiap orang secara otomatis.**
    - `validator.py`: **Fungsi validasi untuk memastikan total penjumlahan per orang sama dengan total Grand Total di nota (Requirement G).**
- `research/`:
    - `comparison_test2.py`: Skrip pengujian untuk membandingkan kecepatan dan akurasi antar model.
    - `nota_1.jpeg` & `nota_2.jpeg`: Sampel gambar nota yang digunakan dalam tahap riset.
- `requirements.txt`: Daftar library Python yang diperlukan.
- `.env`: Berisi API Key (Secret).
