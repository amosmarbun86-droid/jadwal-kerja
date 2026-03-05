import streamlit as st
import pandas as pd
import calendar
import matplotlib.pyplot as plt
import holidays
from datetime import datetime

st.set_page_config(page_title="Jadwal Shift Team A", page_icon="📅", layout="wide")

# ================= BACKGROUND =================

BG = "https://images.unsplash.com/photo-1504384308090-c894fdcc538d"

st.markdown(f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

html, body, [class*="css"] {{
font-family: 'Poppins', sans-serif;
}}

h1 {{
font-size:20px !important;
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
position: fixed;
top:0;
left:0;
width:100%;
height:60px;
background:#0d6efd;
color:white;
display:flex;
align-items:center;
padding-left:20px;
font-size:18px;
font-weight:bold;
z-index:999;
}}

.block-container {{
padding-top:80px;
padding-bottom:40px;
}}

@media (max-width:768px){{

.block-container{{
padding-top:90px;
padding-left:10px;
padding-right:10px;
}}

.appbar{{
height:50px;
font-size:16px;
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

th:first-child, td:first-child{{
min-width:120px;
}}

th:nth-child(2), td:nth-child(2){{
min-width:80px;
}}

}}

</style>

<div class="appbar">📅 Schedule By Amosrcp86</div>

""", unsafe_allow_html=True)

st.title("🏢 SCHEDULE MANAJEMEN TEAM A")

# ================= FILE DATA =================

FILE_TETAP = "karyawan_bersih.csv"

df = pd.read_csv(FILE_TETAP)

df.columns = df.columns.str.strip().str.upper()

base_cols = df.iloc[:, :3]
base_cols.columns = ["NO", "NAMA", "TITLE"]

# ================= MENU =================

menu = st.sidebar.selectbox(
"MENU",
["📅 Lihat Jadwal","🔐 Admin Panel"]
)

# ================= PILIH BULAN =================

bulan = st.selectbox("Pilih Bulan", list(range(1,13)), index=datetime.now().month-1)

tahun = st.number_input("Tahun",2024,2035,datetime.now().year)

jumlah_hari = calendar.monthrange(int(tahun),bulan)[1]

# ================= POLA SHIFT =================

pola = ["OFF","2","2","2","OFF","1","1","1","OFF","3","3","3"]

tanggal_awal_global = datetime(2026,3,1)

hari_libur = holidays.Indonesia(years=tahun)

data_baru = []

for _, row in base_cols.iterrows():

    baris = {
    "NO":row["NO"],
    "NAMA":row["NAMA"],
    "TITLE":row["TITLE"]
    }

    for i in range(jumlah_hari):

        tanggal_sekarang = datetime(tahun,bulan,i+1)

        selisih_hari = (tanggal_sekarang - tanggal_awal_global).days

        posisi = selisih_hari % len(pola)

        shift_val = pola[posisi]

        if tanggal_sekarang in hari_libur:
            shift_val = f"{shift_val} 🇮🇩"

        baris[str(i+1)] = shift_val

    data_baru.append(baris)

df_baru = pd.DataFrame(data_baru)

# ================= WARNA SHIFT =================

def highlight(val):

    val = str(val)

    if "🇮🇩" in val:
        return "background-color:#b30000;color:white;font-weight:bold;"

    if val == "OFF":
        return "background-color:red;color:white;"

    return ""

# ================= USER VIEW =================

if menu == "📅 Lihat Jadwal":

    st.dataframe(
        df_baru.style.applymap(highlight),
        use_container_width=True
    )

# ================= ADMIN PANEL =================

if menu == "🔐 Admin Panel":

    st.subheader("Login Admin")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if user == "admin" and pwd == "admin123":

        st.success("Login berhasil")

        st.markdown("---")

        # DASHBOARD

        st.subheader("📊 Dashboard")

        total_karyawan = len(base_cols)

        total_off = 0
        total_kerja = 0

        for col in df_baru.columns[3:]:

            counts = df_baru[col].astype(str).value_counts()

            total_off += counts.get("OFF",0)

            total_kerja += len(df_baru) - counts.get("OFF",0)

        c1,c2,c3 = st.columns(3)

        c1.metric("Total Karyawan",total_karyawan)
        c2.metric("Total Hari Kerja",total_kerja)
        c3.metric("Total OFF",total_off)

        fig = plt.figure()

        plt.bar(["Kerja","OFF"],[total_kerja,total_off])

        st.pyplot(fig)

        st.markdown("---")

        # TAMBAH KARYAWAN

        st.subheader("➕ Tambah Karyawan")

        nama = st.text_input("Nama Karyawan")
        title = st.text_input("Title")

        if st.button("Tambah"):

            new_no = len(base_cols)+1

            new_row = pd.DataFrame(
                [[new_no,nama,title]],
                columns=["NO","NAMA","TITLE"]
            )

            df_new = pd.concat([base_cols,new_row])

            df_new.to_csv(FILE_TETAP,index=False)

            st.success("Karyawan berhasil ditambahkan")

        # HAPUS KARYAWAN

        st.subheader("❌ Hapus Karyawan")

        nama_hapus = st.selectbox(
        "Pilih Nama",
        base_cols["NAMA"]
        )

        if st.button("Hapus"):

            df_hapus = base_cols[base_cols["NAMA"] != nama_hapus]

            df_hapus.to_csv(FILE_TETAP,index=False)

            st.success("Karyawan berhasil dihapus")

        # UPLOAD DATA

        st.subheader("⬆ Upload File Baru")

        upload = st.file_uploader("Upload CSV",type=["csv"])

        if upload:

            df_upload = pd.read_csv(upload)

            df_upload.to_csv(FILE_TETAP,index=False)

            st.success("Data berhasil diganti")

        st.markdown("---")

        # LINK SHARE

        st.subheader("🔗 Link Aplikasi")

        st.code("https://jadwal-kerja-eqhfsftfwps6axdunrghan.streamlit.app")

    else:
        st.warning("Masukkan username dan password admin")
