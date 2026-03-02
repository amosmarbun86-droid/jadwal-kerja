import streamlit as st
import pandas as pd
import calendar
import matplotlib.pyplot as plt
import holidays
from datetime import datetime
import os

st.set_page_config(
    page_title="Shift App",
    page_icon="📅",
    layout="wide"
)

# =====================================================
# STYLE LAMA (ANDROID LOOK)
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
# LOGIN
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
        elif user == "user" and pwd == "user123":
            st.session_state.login = True
            st.session_state.role = "User"
        else:
            st.error("Login salah")
    st.stop()

st.success(f"Login sebagai {st.session_state.role}")

# =====================================================
# AUTO LOAD FILE PERMANEN
# =====================================================

DATA_FOLDER = "data"
MAIN_FILE = os.path.join(DATA_FOLDER, "jadwal_utama")

os.makedirs(DATA_FOLDER, exist_ok=True)

uploaded_file = st.file_uploader(
    "Upload File Jadwal (Excel / CSV) - Upload Sekali Saja",
    type=["xlsx", "csv"]
)

# Jika upload baru → overwrite file utama
if uploaded_file is not None:
    ext = uploaded_file.name.split(".")[-1]
    MAIN_FILE_WITH_EXT = MAIN_FILE + "." + ext

    # Hapus file lama
    for f in os.listdir(DATA_FOLDER):
        os.remove(os.path.join(DATA_FOLDER, f))

    with open(MAIN_FILE_WITH_EXT, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("File tersimpan sebagai file utama")

# Cari file utama otomatis
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
# BULAN OTOMATIS
# =====================================================

bulan_sekarang = datetime.now().month
tahun_sekarang = datetime.now().year

bulan = st.selectbox("Pilih Bulan", list(range(1, 13)), index=bulan_sekarang-1)
tahun = st.number_input("Tahun", 2024, 2035, tahun_sekarang)

jumlah_hari = calendar.monthrange(int(tahun), bulan)[1]

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
# GENERATE JADWAL
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
        posisi = i % len(pola)
        shift_val = pola[posisi]

        if hari_ke in libur_bulan_ini:
            shift_val = f"{shift_val} 🇮🇩"

        baris[str(hari_ke)] = shift_val

    data_baru.append(baris)

df_baru = pd.DataFrame(data_baru)

# =====================================================
# TAMPILKAN
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
