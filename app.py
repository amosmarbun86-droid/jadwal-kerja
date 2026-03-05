import streamlit as st
import pandas as pd
import calendar
import matplotlib.pyplot as plt
import holidays
from datetime import datetime

st.set_page_config(page_title="Shift App", page_icon="📅", layout="wide")

# ================== STYLE LAMA (TIDAK DIUBAH) ==================

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

# ================== LOGIN ==================

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

# ================== LOAD FILE TETAP ==================

FILE_TETAP = "karyawan_bersih.csv"

if FILE_TETAP.endswith(".csv"):
    df = pd.read_csv(FILE_TETAP)
else:
    df = pd.read_excel(FILE_TETAP)

df.columns = df.columns.str.strip().str.upper()
base_cols = df.iloc[:, :3]
base_cols.columns = ["NO", "NAMA", "TITLE"]

# ================== PILIH BULAN ==================

bulan = st.selectbox("Pilih Bulan", list(range(1, 13)), index=datetime.now().month-1)
tahun = st.number_input("Tahun", 2024, 2035, datetime.now().year)

jumlah_hari = calendar.monthrange(int(tahun), bulan)[1]

# ================== POLA SHIFT ==================

pola = ["OFF","2","2","2","OFF","1","1","1","OFF","3","3","3"]

# ================== ROTASI GLOBAL (TIDAK PERNAH RESET) ==================

tanggal_awal_global = datetime(2024, 1, 1)
hari_libur = holidays.Indonesia(years=tahun)

data_baru = []

for _, row in base_cols.iterrows():

    baris = {
        "NO": row["NO"],
        "NAMA": row["NAMA"],
        "TITLE": row["TITLE"]
    }

    for i in range(jumlah_hari):

        tanggal_sekarang = datetime(tahun, bulan, i+1)
        selisih_hari = (tanggal_sekarang - tanggal_awal_global).days

        posisi = selisih_hari % len(pola)
        shift_val = pola[posisi]

        if tanggal_sekarang in hari_libur:
            shift_val = f"{shift_val} 🇮🇩"

        baris[str(i+1)] = shift_val

    data_baru.append(baris)

df_baru = pd.DataFrame(data_baru)

# ================== TAMPILAN ==================

def highlight(val):
    val = str(val)
    if "🇮🇩" in val:
        return "background-color:#b30000;color:white;font-weight:bold;"
    if val == "OFF":
        return "background-color:red;color:white;"
    return ""

st.dataframe(df_baru.style.applymap(highlight), use_container_width=True)

# ================== DASHBOARD ADMIN ==================

if st.session_state.role == "Admin":

    st.markdown("---")
    st.subheader("📊 Dashboard Manajer")

    total_karyawan = len(df_baru)
    total_off = 0
    total_kerja = 0

    for col in df_baru.columns[3:]:
        counts = df_baru[col].astype(str).value_counts()
        total_off += counts.get("OFF", 0)
        total_kerja += len(df_baru) - counts.get("OFF", 0)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Karyawan", total_karyawan)
    col2.metric("Total Hari Kerja", total_kerja)
    col3.metric("Total OFF", total_off)

    fig = plt.figure()
    plt.bar(["Kerja","OFF"], [total_kerja,total_off])
    st.pyplot(fig)
