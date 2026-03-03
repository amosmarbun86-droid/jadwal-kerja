import streamlit as st
import pandas as pd
import calendar
import matplotlib.pyplot as plt
import holidays
from datetime import datetime
import os
import re
import sqlite3

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

# ================== DATABASE ==================

conn = sqlite3.connect("shift_database.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS jadwal (
    bulan INTEGER,
    tahun INTEGER,
    nama TEXT,
    hari INTEGER,
    shift TEXT
)
""")
conn.commit()

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

# ================== FILE PERMANEN ==================

DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)

uploaded_file = st.file_uploader("Upload File Jadwal (Sekali Saja)", type=["xlsx","csv"])

if uploaded_file:
    for f in os.listdir(DATA_FOLDER):
        os.remove(os.path.join(DATA_FOLDER,f))

    path = os.path.join(DATA_FOLDER, uploaded_file.name)
    with open(path,"wb") as f:
        f.write(uploaded_file.getbuffer())

files = os.listdir(DATA_FOLDER)

if not files:
    st.warning("Upload file jadwal terlebih dahulu")
    st.stop()

file_path = os.path.join(DATA_FOLDER, files[0])

if file_path.endswith(".xlsx"):
    df = pd.read_excel(file_path)
else:
    df = pd.read_csv(file_path)

df.columns = df.columns.str.strip().str.upper()
base_cols = df.iloc[:, :3]
base_cols.columns = ["NO","NAMA","TITLE"]

# ================== BULAN ==================

bulan = st.selectbox("Pilih Bulan", list(range(1,13)), index=datetime.now().month-1)
tahun = st.number_input("Tahun", 2024, 2035, datetime.now().year)

jumlah_hari = calendar.monthrange(int(tahun), bulan)[1]

pola = ["OFF","2","2","2","OFF","1","1","1","OFF","3","3","3"]

# ================== AUTO GENERATE / LOAD ==================

c.execute("SELECT COUNT(*) FROM jadwal WHERE bulan=? AND tahun=?", (bulan,tahun))
cek = c.fetchone()[0]

if cek == 0:

    hari_libur = holidays.Indonesia(years=tahun)

    # Titik awal rotasi global (jangan diubah lagi)
    tanggal_awal_global = datetime(2024, 1, 1)

    for _, row in base_cols.iterrows():

        for i in range(jumlah_hari):

            tanggal_sekarang = datetime(tahun, bulan, i+1)

            # Hitung selisih hari dari tanggal awal global
            selisih_hari = (tanggal_sekarang - tanggal_awal_global).days

            posisi = selisih_hari % len(pola)
            shift_val = pola[posisi]

            if tanggal_sekarang in hari_libur:
                shift_val = f"{shift_val} 🇮🇩"

            c.execute("""
                INSERT INTO jadwal (bulan,tahun,nama,hari,shift)
                VALUES (?,?,?,?,?)
            """, (
                bulan,
                tahun,
                row["NAMA"],
                i+1,
                shift_val
            ))

    conn.commit()

# ================== LOAD DATABASE ==================

c.execute("SELECT * FROM jadwal WHERE bulan=? AND tahun=?", (bulan,tahun))
rows = c.fetchall()

data_dict = {}

for _,_,nama,hari,shift in rows:
    if nama not in data_dict:
        data_dict[nama] = {"NAMA":nama}
    data_dict[nama][str(hari)] = shift

df_baru = pd.DataFrame(data_dict.values())

# ================== TAMPILAN ==================

def highlight(val):
    val=str(val)
    if "🇮🇩" in val:
        return "background-color:#b30000;color:white;font-weight:bold;"
    if val=="OFF":
        return "background-color:red;color:white;"
    return ""

st.dataframe(df_baru.style.applymap(highlight), use_container_width=True)

# ================== DASHBOARD ADMIN ==================

if st.session_state.role=="Admin":

    st.markdown("---")
    st.subheader("📊 Dashboard Manajer")

    total_karyawan=len(df_baru)
    total_off=0
    total_kerja=0

    for col in df_baru.columns[1:]:
        counts=df_baru[col].astype(str).value_counts()
        total_off+=counts.get("OFF",0)
        total_kerja+=len(df_baru)-counts.get("OFF",0)

    col1,col2,col3=st.columns(3)
    col1.metric("Total Karyawan",total_karyawan)
    col2.metric("Total Hari Kerja",total_kerja)
    col3.metric("Total OFF",total_off)

    fig=plt.figure()
    plt.bar(["Kerja","OFF"],[total_kerja,total_off])
    st.pyplot(fig)
