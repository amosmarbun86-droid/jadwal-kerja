import streamlit as st
import pandas as pd
import calendar

st.set_page_config(layout="wide")

st.title("JADWAL KERJA")

# =============================
# LOAD DATA DASAR (FEBRUARI)
# =============================
file_name = "Jadwal_Februari_2026_Rapih.csv"
df = pd.read_csv(file_name)

# Paksa semua header jadi huruf besar (ANTI ERROR)
df.columns = df.columns.str.upper()

# =============================
# PILIH BULAN & TAHUN
# =============================
bulan = st.selectbox("Pilih Bulan", list(range(1, 13)), index=1)
tahun = st.number_input("Tahun", min_value=2024, max_value=2035, value=2026)

st.subheader(f"Jadwal Bulan {bulan} Tahun {tahun}")

# =============================
# POLA DASAR
# =============================
pola = [
    "OFF","3","3","3",
    "OFF","2","2","2",
    "OFF","1","1","1",
]

# Total hari bulan dipilih
jumlah_hari = calendar.monthrange(int(tahun), bulan)[1]

# Hitung selisih hari dari Februari 2026
bulan_dasar = 2
tahun_dasar = 2026

total_offset = 0

if tahun == tahun_dasar and bulan >= bulan_dasar:
    for b in range(bulan_dasar, bulan):
        total_offset += calendar.monthrange(tahun, b)[1]
elif tahun > tahun_dasar:
    # sisa bulan di 2026
    for b in range(bulan_dasar, 13):
        total_offset += calendar.monthrange(tahun_dasar, b)[1]
    # tahun berikutnya
    for t in range(tahun_dasar + 1, tahun):
        for b in range(1, 13):
            total_offset += calendar.monthrange(t, b)[1]
    # bulan di tahun sekarang
    for b in range(1, bulan):
        total_offset += calendar.monthrange(tahun, b)[1]

# =============================
# GENERATE JADWAL BARU
# =============================
data_baru = []

for index, row in df.iterrows():
    baris = {
        "NO": row["NO"],
        "NAMA": row["NAMA"],
        "TITLE": row["TITLE"],
    }

    for i in range(jumlah_hari):
        posisi = (total_offset + i) % len(pola)
        baris[str(i+1)] = pola[posisi]

    data_baru.append(baris)

df_baru = pd.DataFrame(data_baru)

st.dataframe(df_baru, use_container_width=True)
