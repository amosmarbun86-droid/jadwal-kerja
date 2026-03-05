# app_final_admin.py

import streamlit as st
import pandas as pd
import calendar
import matplotlib.pyplot as plt
import holidays
from datetime import datetime

st.set_page_config(page_title="Jadwal Shift Team A", page_icon="📅", layout="wide")

# ================== STYLE FINAL ==================

BG = "https://images.unsplash.com/photo-1504384308090-c894fdcc538d"

st.markdown(f"""
<style>

h1 {{
font-size:20px !important;
}}

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

html, body, [class*="css"] {{
font-family: 'Poppins', sans-serif;
}}

.stApp {{
color:white;
background:
linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)),
url("{BG}");
background-size:cover;
background-position:center;
background-attachment:fixed;
}}

header, footer {{visibility:hidden;}}

.appbar {{
width:100%;
height:60px;
background:#0d6efd;
color:white;
display:flex;
align-items:center;
padding-left:20px;
font-size:20px;
font-weight:bold;
margin-bottom:20px;
}}

.block-container {{
padding-top:20px;
padding-bottom:40px;
}}

</style>

<div class="appbar">📅 Schedule By Amosrcp86</div>

""", unsafe_allow_html=True)

st.title("🏢 SCHEDULE MANAJEMEN TEAM A")

# ================== LOAD FILE ==================

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

# ================== ROTASI GLOBAL ==================

tanggal_awal_global = datetime(2026, 3, 1)
hari_libur = holidays.Indonesia(years=tahun)

# ================== DATA HARI LIBUR BULAN INI ==================

libur_bulan_ini = []

for tanggal, nama in hari_libur.items():

    if tanggal.month == bulan and tanggal.year == tahun:

        libur_bulan_ini.append({
            "Tanggal": tanggal.strftime("%d-%m-%Y"),
            "Hari": tanggal.strftime("%A"),
            "Keterangan": nama
        })

df_libur = pd.DataFrame(libur_bulan_ini)

# ================== GENERATE SHIFT ==================

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

# ================== HIGHLIGHT SHIFT ==================

def highlight(val):

    val = str(val)

    if "🇮🇩" in val:
        return "background-color:#b30000;color:white;font-weight:bold;"

    if val == "OFF":
        return "background-color:red;color:white;"

    return ""

# ================== TAB MENU ==================

tab_menu = st.tabs([
    "📅 Jadwal Shift",
    "📊 Dashboard",
    "⚙️ Admin Panel"
])

# ================== TAB 1 ==================

with tab_menu[0]:

    st.subheader("Jadwal Shift Team A")

    st.dataframe(
        df_baru.style.applymap(highlight),
        use_container_width=True
    )

# ================== TAB 2 DASHBOARD ==================

with tab_menu[1]:

    st.subheader("Dashboard Manager")

    total_karyawan = len(df_baru)

    total_off = 0
    total_kerja = 0

    for col in df_baru.columns[3:]:

        counts = df_baru[col].astype(str).value_counts()

        total_off += counts.get("OFF",0)

        total_kerja += len(df_baru) - counts.get("OFF",0)

    col1,col2,col3 = st.columns(3)

    col1.metric("Total Karyawan", total_karyawan)
    col2.metric("Total Hari Kerja", total_kerja)
    col3.metric("Total OFF", total_off)

    fig = plt.figure()

    plt.bar(["Kerja","OFF"], [total_kerja,total_off])

    st.pyplot(fig)

    # ================== DASHBOARD HARI LIBUR ==================

    st.divider()

    st.subheader("🇮🇩 Hari Libur Nasional")

    if df_libur.empty:

        st.success("Tidak ada hari libur nasional bulan ini")

    else:

        st.warning(f"Ada {len(df_libur)} hari libur nasional bulan ini")

        st.dataframe(
            df_libur,
            use_container_width=True
        )

# ================== TAB 3 ADMIN ==================

with tab_menu[2]:

    st.subheader("Admin Panel")

    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:

        user = st.text_input("Username Admin")
        pwd = st.text_input("Password Admin", type="password")

        if st.button("Login Admin"):

            if user == "admin" and pwd == "admin123":

                st.session_state.admin_logged_in = True
                st.success("Login Admin Berhasil")

            else:

                st.error("Hanya admin yang bisa mengakses")

        st.stop()

    st.subheader("Tambah Karyawan")

    nama = st.text_input("Nama")
    title = st.text_input("Title")

    if st.button("Tambah"):

        new_no = len(base_cols) + 1

        new_row = pd.DataFrame(
            [[new_no, nama, title]],
            columns=["NO","NAMA","TITLE"]
        )

        base_cols = pd.concat([base_cols, new_row])

        base_cols.to_csv(FILE_TETAP, index=False)

        st.success("Karyawan berhasil ditambahkan")

    st.subheader("Hapus Karyawan")

    hapus = st.selectbox("Pilih karyawan", base_cols["NAMA"])

    if st.button("Hapus"):

        base_cols = base_cols[base_cols["NAMA"] != hapus]

        base_cols.to_csv(FILE_TETAP, index=False)

        st.success("Karyawan dihapus")
