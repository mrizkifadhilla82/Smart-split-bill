import streamlit as st
import pandas as pd
from libs.extractor_groq import GroqExtractor
import os

# --- Konfigurasi Page ---
st.set_page_config(page_title="SmartSplit AI", page_icon="🧾", layout="wide")

# --- Custom CSS untuk UI yang Rapi ---
st.markdown("""
<style>
    .step-number {
        background-color: #007bff;
        color: white;
        padding: 5px 12px;
        border-radius: 50%;
        font-weight: bold;
        margin-right: 10px;
    }
    .success-badge {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        font-weight: bold;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- State Management ---
if "bill_data" not in st.session_state:
    st.session_state.bill_data = None
if "participants" not in st.session_state:
    st.session_state.participants = []
if "final_assignments" not in st.session_state:
    st.session_state.final_assignments = {}

# --- Sidebar / Header ---
st.title("🧾 SmartSplit Bill AI")
st.write("Ekstraksi nota otomatis dan pembagian porsi yang adil.")

if st.button("🔄 Reset Semua"):
    st.session_state.clear()
    st.rerun()

# ─── STEP 1: PARTICIPANTS ───
st.divider()
st.markdown(f'<div style="display: flex; align-items: center;">'
            f'<div class="step-number">1</div><b>Siapa saja yang ikut makan?</b></div>', unsafe_allow_html=True)
names_input = st.text_input("Masukkan nama (pisahkan dengan koma):", placeholder="Contoh: Andre, Budi, Cici")
if names_input:
    st.session_state.participants = [n.strip() for n in names_input.split(",") if n.strip()]

# ─── STEP 2: UPLOAD & EXTRACTION ───
st.divider()
st.markdown(f'<div style="display: flex; align-items: center;">'
            f'<div class="step-number">2</div><b>Upload Nota</b></div>', unsafe_allow_html=True)

col_up, col_prev = st.columns([2, 1])
with col_up:
    uploaded_file = st.file_uploader("Pilih gambar nota...", type=["jpg", "jpeg", "png"])
    if uploaded_file and st.button("⚡ Ekstrak Nota", type="primary"):
        with st.spinner("AI sedang membaca nota..."):
            # Simpan sementara untuk diproses
            with open("temp_nota.jpg", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            extractor = GroqExtractor()
            data = extractor.extract_nota("temp_nota.jpg")
            if data:
                st.session_state.bill_data = data
                # Inisialisasi assignment kosong untuk setiap item
                st.session_state.final_assignments = {idx: [] for idx in range(len(data.get('items', [])))}
                st.success("Nota berhasil dibaca!")
            else:
                st.error("Gagal mengekstrak data. Coba lagi.")

with col_prev:
    if uploaded_file:
        st.image(uploaded_file, caption="Preview Nota", use_container_width=True)

# ─── STEP 3: ASSIGNMENT (THE DYNAMIC UI) ───
if st.session_state.bill_data and st.session_state.participants:
    st.divider()
    st.markdown(f'<div style="display: flex; align-items: center; margin-bottom: 10px;">'
                f'<div class="step-number">3</div><b style="font-size: 1.2rem;">Alokasi Konsumsi</b></div>', unsafe_allow_html=True)
    
    items = st.session_state.bill_data.get('items', [])
    participants = st.session_state.participants

    for idx, item in enumerate(items):
        q_nota = int(item.get('qty', 1))
        u_price = float(item.get('price', 0))
        subtotal_row = u_price * q_nota
        
        with st.expander(f"🛒 {item.get('name')} ({q_nota}x)", expanded=True):
            c_info, c_assign = st.columns([1, 2])
            
            with c_info:
                st.write(f"Harga Satuan: **Rp {u_price:,.0f}**")
                st.write(f"Total Baris: **Rp {subtotal_row:,.0f}**")
                if st.button(f"➕ Tambah Orang", key=f"add_{idx}"):
                    # Default tambah orang pertama
                    st.session_state.final_assignments[idx].append({"name": participants[0], "portion": 1.0})

            with c_assign:
                current_assigns = st.session_state.final_assignments[idx]
                new_assigns = []
                
                # Validasi porsi agar tidak melebihi nota
                total_q_in = sum(float(a['portion']) for a in current_assigns)
                if total_q_in > q_nota:
                    st.error(f"Kelebihan porsi! (Nota: {q_nota}, Input: {total_q_in})")
                
                for r_idx, assign in enumerate(current_assigns):
                    row_name, row_qty, row_del = st.columns([2, 1, 0.5])
                    with row_name:
                        sel_n = st.selectbox("Nama", participants, 
                                           index=participants.index(assign['name']) if assign['name'] in participants else 0,
                                           key=f"n_{idx}_{r_idx}", label_visibility="collapsed")
                    with row_qty:
                        sel_q = st.number_input("Qty", min_value=0.1, max_value=float(q_nota),
                                              value=float(assign['portion']), step=0.5,
                                              key=f"q_{idx}_{r_idx}", label_visibility="collapsed")
                    with row_del:
                        if st.button("🗑️", key=f"d_{idx}_{r_idx}"):
                            continue
                    new_assigns.append({"name": sel_n, "portion": sel_q})
                
                st.session_state.final_assignments[idx] = new_assigns

    # ─── FINAL SUMMARY ───
    st.divider()
    st.markdown("### 📊 Ringkasan Pembayaran")
    
    tax = float(st.session_state.bill_data.get('tax') or 0)
    grand_total_nota = float(st.session_state.bill_data.get('total') or 0)
    
    indiv_costs = {p: 0.0 for p in participants}
    total_food_sum = 0.0

    for idx, item in enumerate(items):
        item_u_price = float(item.get('price') or 0)
        for a in st.session_state.final_assignments[idx]:
            share = a['portion'] * item_u_price
            indiv_costs[a['name']] += share
            total_food_sum += share

    # Susun Tabel
    summary_table = []
    for p in participants:
        # Pajak proporsional
        p_tax = (indiv_costs[p] / total_food_sum * tax) if total_food_sum > 0 else 0
        p_total = indiv_costs[p] + p_tax
        
        summary_table.append({
            "Nama": p,
            "Pesanan": indiv_costs[p],
            "Pajak & Service": p_tax,
            "Total Tagihan": round(p_total)
        })

    if summary_table:
        df_final = pd.DataFrame(summary_table)
        st.table(df_final.style.format({
            "Pesanan": "Rp {:,.0f}",
            "Pajak & Service": "Rp {:,.0f}",
            "Total Tagihan": "Rp {:,.0f}"
        }))

    # Footer Validasi
    final_sum_all = sum(indiv_costs.values()) + tax
    if abs(final_sum_all - grand_total_nota) < 500:
        st.markdown(f'<div class="success-badge">✅ Perhitungan Akurat: Rp {final_sum_all:,.0f}</div>', unsafe_allow_html=True)
    else:
        st.info(f"Total Terisi: Rp {final_sum_all:,.0f} | Target Nota: Rp {grand_total_nota:,.0f}")