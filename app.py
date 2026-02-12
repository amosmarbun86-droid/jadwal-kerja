import streamlit as st
import pandas as pd
import calendar

st.set_page_config(layout="wide")
st.title("📅 APLIKASI JADWAL KERJA")

# =========================
# PILIH BULAN & TAHUN
# =========================
bulan = st.selectbox("Pilih Bulan", list(range(1,13)), index=1)
tahun = st.number_input("Tahun", value=2026)

st.subheader(f"Jadwal Bulan {bulan} Tahun {tahun}")

# =========================
# LOAD CSV ANDA
# =========================
df = pd.read_csv("Jadwal_Februari_2026_Rapih.csv")

# Bersihkan header
df.columns = df.columns.str.strip()

# Kolom tetap sesuai file Anda
nama_col = "Nama"
jabatan_col = "Jabatan"

# Kolom tanggal
kolom_tanggal = [col for col in df.columns if col not in [nama_col, jabatan_col]]

# Hitung jumlah hari bulan
jumlah_hari = calendar.monthrange(int(tahun), int(bulan))[1]

data_baru = []

for index, row in df.iterrows():
    
    pola_asli = row[kolom_tanggal].tolist()
    
    row_baru = {
        "NO": index + 1,
        "Nama": row[nama_col],
        "Jabatan": row[jabatan_col]
    }
    
    for h in range(jumlah_hari):
        row_baru[str(h+1)] = pola_asli[h % len(pola_asli)]
    
    data_baru.append(row_baru)

df_final = pd.DataFrame(data_baru)

# =========================
# WARNAKAN SHIFT
# =========================
def highlight(val):
    if val == "OFF":
        return "background-color: red; color: white"
    elif str(val) == "3":
        return "background-color: #9ecae1"
    elif str(val) == "2":
        return "background-color: #ffff99"
    elif str(val) == "1":
        return "background-color: #99ff99"
    return ""

st.dataframe(
    df_final.style.applymap(highlight),
    use_container_width=True
)
