import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
from io import StringIO

st.set_page_config(page_title="Jadwal Kerja Otomatis", layout="centered")

st.title("📅 APLIKASI JADWAL KERJA")

# =============================
# PILIH BULAN & TAHUN
# =============================

col1, col2 = st.columns(2)

with col1:
    bulan = st.selectbox(
        "Pilih Bulan",
        list(range(1, 13)),
        index=datetime.now().month - 1
    )

with col2:
    tahun = st.number_input("Tahun", value=2026)

jumlah_hari = calendar.monthrange(int(tahun), int(bulan))[1]

st.subheader(f"Jadwal Bulan {bulan} Tahun {tahun}")

# =============================
# LOAD NAMA DARI CSV
# =============================

base_df = pd.read_csv("Jadwal_Februari_2026_Rapih.csv")

# Ubah semua header jadi huruf besar
base_df.columns = base_df.columns.str.upper().str.strip()

nama_list = base_df.iloc[:, 1]   # kolom kedua (Nama)
title_list = base_df.iloc[:, 2]  # kolom ketiga (Title)

# =============================
# POLA SHIFT 3-3-3-OFF
# =============================

pola = [
    "OFF", "3", "3", "3",
    "OFF", "2", "2", "2",
    "OFF", "1", "1", "1"
]

data = []

for idx in range(len(nama_list)):
    row = {
        "NO": idx + 1,
        "NAMA": nama_list.iloc[idx],
        "TITLE": title_list.iloc[idx]
    }

    for i in range(jumlah_hari):
        shift = pola[(i + idx) % len(pola)]
        row[str(i + 1)] = shift

    data.append(row)

df = pd.DataFrame(data)

# =============================
# WARNA SHIFT
# =============================

def warna_shift(val):
    if str(val) == "OFF":
        return "background-color: red; color: white"
    elif str(val) == "1":
        return "background-color: #90EE90"
    elif str(val) == "2":
        return "background-color: #FFFF99"
    elif str(val) == "3":
        return "background-color: #ADD8E6"
    return ""

styled_df = df.style.applymap(warna_shift)

st.dataframe(styled_df, use_container_width=True, height=500)

# =============================
# DOWNLOAD CSV
# =============================

csv_buffer = StringIO()
df.to_csv(csv_buffer, index=False)

st.download_button(
    label="📥 Download CSV",
    data=csv_buffer.getvalue(),
    file_name=f"Jadwal_{bulan}_{tahun}.csv",
    mime="text/csv",
    use_container_width=True
)
