import streamlit as st
import pandas as pd
import calendar
import matplotlib.pyplot as plt
import holidays
from datetime import datetime
import os
import re

st.set_page_config(
    page_title="Shift App",
    page_icon="📅",
    layout="wide"
)

# =====================================================
# STYLE LAMA (TIDAK DIUBAH)
# =====================================================

BG = "https://images.unsplash.com/photo-1504384308090-c894fdcc538d"

st.markdown(f"""
<style>
.stApp {{
    background:
    linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)),
    url("{BG}");
    background-size: cover;
    background-attachment: fixed;
}}

header, footer {{visibility:hidden;}}

.appbar {{
    position: fixed;
    top:0; left:0;
    width:100%;
    height:60px;
    background:#0d6efd;
    color:white;
    display:flex;
    align-items:center;
    padding-left:20px;
    font-size:20px;
    font-weight:bold;
    z-index:999;
}}

.block-container {{
    padding-top:80px;
    padding-bottom:40px;
}}
</style>

<div class="appbar">📅 Sistem Manajemen Shift</div>
""", unsafe_allow_html=True)

st.title("🏢 SISTEM MANAJEMEN SHIFT")

# =====================================================
# LOGIN (SAMA)
# =====================================================

if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.role = None

if not st.session_state.login:
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "admin" and pwd == "admin123":
            st.session_state.login = True
            st.session_state.role = "Admin"
        elif user == "spx" and pwd == "spx123":
            st.session_state.login = True
            st.session_state.role = "User"
        else:
            st.error("Login salah")
    st.stop()

st.success(f"Login sebagai {st.session_state.role}")

# =====================================================
# AUTO SAVE FILE PERMANEN (1 FILE UTAMA)
# =====================================================

DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)

uploaded_file = st.file_uploader(
    "Upload File Jadwal (Excel / CSV) - Upload Sekali Saja",
    type=["xlsx", "csv"]
)

if uploaded_file is not None:
    for f in os.listdir(DATA_FOLDER):
        os.remove(os.path.join(DATA_FOLDER, f))

    save_path = os.path.join(DATA_FOLDER, uploaded_file.name)

    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("File utama berhasil disimpan")

files = os.listdir(DATA_FOLDER)

if not files:
    st.warning("Silakan upload file jadwal terlebih dahulu")
    st.stop()

file_path = os.path.join(DATA_FOLDER, files[0])

# =====================================================
# BACA FILE
# =====================================================

if file_path.endswith(".xlsx"):
    df = pd.read_excel(file_path)
else:
    df = pd.read_csv(file_path)

df.columns = df.columns.str.strip().str.upper()

base_cols = df.iloc[:, :3]
base_cols.columns = ["NO", "NAMA", "TITLE"]

# =====================================================
# AMBIL BULAN DASAR OTOMATIS DARI NAMA FILE
# =====================================================

filename = os.path.basename(file_path)

bulan_map = {
    "JANUARI":1,"FEBRUARI":2,"MARET":3,"APRIL":4,
    "MEI":5,"JUNI":6,"JULI":7,"AGUSTUS":8,
    "SEPTEMBER":9,"OKTOBER":10,"NOVEMBER":11,"DESEMBER":12
}

bulan_dasar = None
tahun_dasar = None

for nama_bulan in bulan_map:
    if nama_bulan in filename.upper():
        bulan_dasar = bulan_map[nama_bulan]
        break

match_tahun = re.search(r"20\d{2}", filename)
if match_tahun:
    tahun_dasar = int(match_tahun.group())

if bulan_dasar is None:
    bulan_dasar = datetime.now().month
if tahun_dasar is None:
    tahun_dasar = datetime.now().year

# =====================================================
# PILIH BULAN
# =====================================================

bulan = st.selectbox("Pilih Bulan", list(range(1, 13)), index=datetime.now().month-1)
tahun = st.number_input("Tahun", 2024, 2035, datetime.now().year)

jumlah_hari = calendar.monthrange(int(tahun), bulan)[1]

# =====================================================
# HITUNG OFFSET OTOMATIS
# =====================================================

def hitung_selisih_hari(b1, t1, b2, t2):
    total = 0
    if (t2, b2) > (t1, b1):
        t, b = t1, b1
        while (t, b) != (t2, b2):
            total += calendar.monthrange(t, b)[1]
            b += 1
            if b > 12:
                b = 1
                t += 1
    elif (t2, b2) < (t1, b1):
        t, b = t2, b2
        while (t, b) != (t1, b1):
            total -= calendar.monthrange(t, b)[1]
            b += 1
            if b > 12:
                b = 1
                t += 1
    return total

total_offset = hitung_selisih_hari(
    bulan_dasar, tahun_dasar,
    bulan, tahun
)

# =====================================================
# LIBUR NASIONAL
# =====================================================

hari_libur = holidays.Indonesia(years=tahun)

libur_bulan_ini = {
    tgl.day: nama
    for tgl, nama in hari_libur.items()
    if tgl.month == bulan
}

# =====================================================
# POLA SHIFT
# =====================================================

default_pola = [
    "OFF","2","2","2",
    "OFF","1","1","1",
    "OFF","3","3","3",
]

if st.session_state.role == "Admin":
    pola_input = st.text_input(
        "Edit Pola Shift (pisahkan koma)",
        value="OFF,2,2,2,OFF,1,1,1,OFF,3,3,3"
    )
    pola = pola_input.split(",")
else:
    pola = default_pola

# =====================================================
# GENERATE JADWAL (BERKELANJUTAN)
# =====================================================

data_baru = []

for _, row in base_cols.iterrows():

    baris = {
        "NO": row["NO"],
        "NAMA": row["NAMA"],
        "TITLE": row["TITLE"],
    }

    for i in range(jumlah_hari):
        hari_ke = i + 1
        posisi = (total_offset + i) % len(pola)
        shift_val = pola[posisi]

        if hari_ke in libur_bulan_ini:
            shift_val = f"{shift_val} 🇮🇩"

        baris[str(hari_ke)] = shift_val

    data_baru.append(baris)

df_baru = pd.DataFrame(data_baru)

# =====================================================
# HIGHLIGHT (SAMA)
# =====================================================

def highlight(val):
    val = str(val)
    if "🇮🇩" in val:
        return "background-color:#b30000;color:white;font-weight:bold;"
    if val == "OFF":
        return "background-color:red;color:white;"
    return ""

st.dataframe(
    df_baru.style.applymap(highlight),
    use_container_width=True
)

# =====================================================
# DOWNLOAD
# =====================================================

csv = df_baru.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇ Download Jadwal CSV",
    csv,
    f"Jadwal_{bulan}_{tahun}.csv",
    "text/csv"
)
