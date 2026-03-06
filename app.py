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

/* APPBAR DI ATAS */
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

th:first-child, td:first-child{{
min-width:120px;
}}

th:nth-child(2), td:nth-child(2){{
min-width:80px;
}}

@media (max-width:768px){{
.block-container{{
padding-top:20px;
padding-left:10px;
padding-right:10px;
padding-bottom:40px;
}}

.appbar{{
height:40px;
font-size:14px;
}}

table{{
font-size:12px;
width:100%;
}}

[data-testid="stDataFrame"]{{
overflow-x:auto;
}}

th, td{{
white-space:nowrap;
}}
}}
</style>

<div class="appbar">📅 Schedule Powered By Amosrcp86</div>

""", unsafe_allow_html=True)

st.title("🏢 SCHEDULE MANAJEMEN TEAM A")

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

# ================== ROTASI GLOBAL ==================

tanggal_awal_global = datetime(2026, 3, 1)
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

# ================== TAB 1: Jadwal Shift ==================

with tab_menu[0]:
    st.subheader("Jadwal Shift Team A")
    st.dataframe(df_baru.style.applymap(highlight), use_container_width=True)

# ================== TAB 2: Dashboard ==================

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

# ================== TAB 3: Admin Panel ==================

with tab_menu[2]:
    st.subheader("Admin Panel")

    # Cek login admin
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

    # Jika sudah login, tampilkan panel admin
    st.subheader("Tambah Karyawan")
    nama = st.text_input("Nama")
    title = st.text_input("Title")
    if st.button("Tambah"):
        new_no = len(base_cols) + 1
        new_row = pd.DataFrame([[new_no, nama, title]], columns=["NO","NAMA","TITLE"])
        base_cols = pd.concat([base_cols, new_row])
        base_cols.to_csv(FILE_TETAP, index=False)
        st.success("Karyawan berhasil ditambahkan")

    st.subheader("Hapus Karyawan")
    hapus = st.selectbox("Pilih karyawan", base_cols["NAMA"])
    if st.button("Hapus"):
        base_cols = base_cols[base_cols["NAMA"] != hapus]
        base_cols.to_csv(FILE_TETAP, index=False)
        st.success("Karyawan dihapus")

# =================================================
# DASHBOARD TAMBAHAN (AMAN - TIDAK MERUBAH SISTEM)
# =================================================

with tab_menu[1]:

    st.divider()
    st.subheader("🇮🇩 Hari Libur Nasional")

    libur_bulan_ini = []

    for tanggal, nama in hari_libur.items():

        if tanggal.month == bulan and tanggal.year == tahun:

            libur_bulan_ini.append({
                "Tanggal": tanggal.strftime("%d-%m-%Y"),
                "Hari": tanggal.strftime("%A"),
                "Keterangan": nama
            })

    if len(libur_bulan_ini) == 0:

        st.success("Tidak ada hari libur nasional bulan ini")

    else:

        st.warning(f"Ada {len(libur_bulan_ini)} hari libur nasional")

        st.dataframe(libur_bulan_ini, use_container_width=True)


    # ===============================================
    # KALENDER SHIFT WARNA OTOMATIS
    # ===============================================

    st.divider()
    st.subheader("📅 Kalender Shift Visual")

    warna_shift = {
        "1": "#3498db",
        "2": "#2ecc71",
        "3": "#f1c40f",
        "OFF": "#e74c3c"
    }

    kal = calendar.monthcalendar(tahun, bulan)

    kal_display = []

    for minggu in kal:

        row = []

        for hari in minggu:

            if hari == 0:

                row.append("")

            else:

                shift = str(df_baru[str(hari)].iloc[0]).replace(" 🇮🇩","")

                warna = warna_shift.get(shift,"#888")

                html = f"""
                <div style="
                background:{warna};
                padding:8px;
                border-radius:8px;
                text-align:center;
                color:white;
                ">
                {hari}<br>{shift}
                </div>
                """

                row.append(html)

        kal_display.append(row)

    df_kalender = pd.DataFrame(
        kal_display,
        columns=["Sen","Sel","Rab","Kam","Jum","Sab","Min"]
    )

    st.markdown(
        df_kalender.to_html(escape=False,index=False),
        unsafe_allow_html=True
)


# =========================================================
# 🚀 EXTRA FEATURES (ADDED WITHOUT MODIFYING ORIGINAL LOGIC)
# By Amosrcp86 Assistant Upgrade
# =========================================================

from io import BytesIO
from fpdf import FPDF

st.divider()
st.subheader("🚀 Upgrade Dashboard Tambahan")

# ================== DASHBOARD LIBUR NASIONAL ==================
st.markdown("### 🇮🇩 Peringatan Hari Libur Nasional")

libur_list = []
for tgl, nama in hari_libur.items():
    if tgl.month == bulan and tgl.year == tahun:
        libur_list.append({
            "Tanggal": tgl.strftime("%d-%m-%Y"),
            "Hari": tgl.strftime("%A"),
            "Keterangan": nama
        })

if len(libur_list) == 0:
    st.success("Tidak ada hari libur nasional bulan ini")
else:
    st.warning(f"Terdapat {len(libur_list)} hari libur nasional bulan ini")
    st.dataframe(libur_list, use_container_width=True)


# ================== DISTRIBUSI SHIFT ==================
st.markdown("### 📊 Distribusi Shift")

shift1 = 0
shift2 = 0
shift3 = 0

for col in df_baru.columns[3:]:
    for val in df_baru[col]:
        val = str(val)
        if "1" in val:
            shift1 += 1
        if "2" in val:
            shift2 += 1
        if "3" in val:
            shift3 += 1

import matplotlib.pyplot as plt
fig_shift = plt.figure()
plt.bar(["Shift 1","Shift 2","Shift 3"],[shift1,shift2,shift3])
st.pyplot(fig_shift)


# ================== KALENDER BULAN ==================
st.markdown("### 📅 Kalender Bulan Ini")

import calendar
kal = calendar.monthcalendar(tahun, bulan)

import pandas as pd
df_kal = pd.DataFrame(
    kal,
    columns=["Sen","Sel","Rab","Kam","Jum","Sab","Min"]
)

st.dataframe(df_kal, use_container_width=True)


# ================== DOWNLOAD JADWAL ==================
st.markdown("### ⬇️ Export Jadwal")

buffer = BytesIO()
df_baru.to_excel(buffer, index=False)

st.download_button(
    label="Download Jadwal Excel",
    data=buffer.getvalue(),
    file_name="jadwal_shift_teamA.xlsx",
    mime="application/vnd.ms-excel"
)


if st.button("Generate PDF Jadwal"):

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=8)

    for i in range(len(df_baru)):
        row = " | ".join(str(x) for x in df_baru.iloc[i])
        pdf.cell(200,8,txt=row,ln=True)

    pdf_path = "jadwal_shift_teamA.pdf"
    pdf.output(pdf_path)

    with open(pdf_path,"rb") as f:
        st.download_button(
            "Download PDF",
            f,
            file_name="jadwal_shift_teamA.pdf"
)
