import streamlit as st
import pandas as pd
import calendar

st.set_page_config(layout="wide")
st.title("📅 APLIKASI JADWAL KERJA")

# ========================
# PILIH BULAN & TAHUN
# ========================
bulan = st.selectbox("Pilih Bulan", list(range(1,13)), index=1)
tahun = st.number_input("Tahun", value=2026)

st.subheader(f"Jadwal Bulan {bulan} Tahun {tahun}")

# ========================
# LOAD FILE ASLI
# ========================
df = pd.read_csv("Jadwal_Februari_2026_Rapih.csv")

df.columns = df.columns.astype(str)

# Ambil kolom tetap
kolom_tetap = ["NO","NAMA","TITLE"]

# Ambil kolom tanggal dari file asli
kolom_tanggal = [col for col in df.columns if col not in kolom_tetap]

# Hitung jumlah hari bulan dipilih
jumlah_hari = calendar.monthrange(int(tahun), int(bulan))[1]

# ========================
# BUAT DATA BARU IKUT POLA ASLI
# ========================
data_baru = []

for index, row in df.iterrows():
    
    pola_asli = row[kolom_tanggal].tolist()
    
    row_baru = {
        "NO": row["NO"],
        "NAMA": row["NAMA"],
        "TITLE": row["TITLE"]
    }
    
    for h in range(jumlah_hari):
        row_baru[str(h+1)] = pola_asli[h % len(pola_asli)]
    
    data_baru.append(row_baru)

df_final = pd.DataFrame(data_baru)

# ========================
# WARNA SHIFT
# ========================
def highlight(val):
    if val == "OFF":
        return "background-color: red; color: white"
    elif val == 3 or val == "3":
        return "background-color: #9ecae1"
    elif val == 2 or val == "2":
        return "background-color: #ffff99"
    elif val == 1 or val == "1":
        return "background-color: #99ff99"
    return ""

st.dataframe(
    df_final.style.applymap(highlight),
    use_container_width=True
)
