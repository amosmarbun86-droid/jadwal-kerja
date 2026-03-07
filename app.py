import streamlit as st
import pandas as pd
import calendar
import matplotlib.pyplot as plt
import holidays
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
from streamlit_calendar import calendar as st_calendar

st.set_page_config(page_title="Jadwal Shift Team A", page_icon="📅", layout="wide")

# ================== STYLE ==================

BG = "https://images.unsplash.com/photo-1504384308090-c894fdcc538d"

st.markdown(f"""
<style>
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
</style>

<div class="appbar">📅 Schedule Powered By Amosrcp86</div>
""", unsafe_allow_html=True)

st.title("🏢 SCHEDULE MANAJEMEN TEAM A")

# ================== LOAD DATA ==================

FILE_TETAP = "karyawan_bersih.csv"

if FILE_TETAP.endswith(".csv"):
    df = pd.read_csv(FILE_TETAP)
else:
    df = pd.read_excel(FILE_TETAP)

df.columns = df.columns.str.strip().str.upper()
base_cols = df.iloc[:, :3]
base_cols.columns = ["NO", "NAMA", "TITLE"]

# ================== PILIH BULAN ==================

bulan = st.selectbox("Pilih Bulan", list(range(1,13)), index=datetime.now().month-1)
tahun = st.number_input("Tahun",2024,2035,datetime.now().year)

@st.cache_data
def generate_schedule(base_cols, bulan, tahun):

    jumlah_hari = calendar.monthrange(int(tahun), bulan)[1]

    pola = ["OFF","2","2","2","OFF","1","1","1","OFF","3","3","3"]

    tanggal_awal_global = datetime(2026,3,1)

    hari_libur = holidays.Indonesia(years=tahun)

    data_baru=[]

    for _, row in base_cols.iterrows():

        baris={
            "NO":row["NO"],
            "NAMA":row["NAMA"],
            "TITLE":row["TITLE"]
        }

        for i in range(jumlah_hari):

            tanggal=datetime(tahun,bulan,i+1)

            selisih=(tanggal-tanggal_awal_global).days
            posisi=selisih%len(pola)

            shift=pola[posisi]

            if tanggal in hari_libur:
                shift=f"{shift} LIBUR"

            baris[str(i+1)]=shift

        data_baru.append(baris)

    return pd.DataFrame(data_baru)
    df_baru = generate_schedule(base_cols, bulan, tahun)
# ================== TAB ==================

tab1,tab2,tab3 = st.tabs([
"📅 Jadwal Shift",
"📊 Dashboard",
"⚙️ Admin Panel"
])

# ================== TAB 1 ==================

with tab1:

    st.subheader("Jadwal Shift")

    def highlight(val):

        val=str(val)

        if "LIBUR" in val:
            return "background-color:#b30000;color:white"

        if val=="OFF":
            return "background-color:red;color:white"

        return ""

    st.dataframe(df_baru, use_container_width=True)

# ================== TAB 2 ==================

with tab2:

    st.subheader("Dashboard Manager")

    total_karyawan=len(df_baru)
    total_off=0
    total_kerja=0

    for col in df_baru.columns[3:]:

        counts=df_baru[col].astype(str).value_counts()

        total_off+=counts.get("OFF",0)
        total_kerja+=len(df_baru)-counts.get("OFF",0)

    c1,c2,c3=st.columns(3)

    c1.metric("Total Karyawan",total_karyawan)
    c2.metric("Total Hari Kerja",total_kerja)
    c3.metric("Total OFF",total_off)

    fig=plt.figure()
    plt.bar(["Kerja","OFF"],[total_kerja,total_off])
    st.pyplot(fig)

# ================== LIBUR NASIONAL ==================

    st.divider()
    st.subheader("🇮🇩 Peringatan Hari Libur Nasional")

    libur_list=[]

    for tgl,nama in hari_libur.items():

        if tgl.month==bulan and tgl.year==tahun:

            libur_list.append({
            "Tanggal":tgl.strftime("%d-%m-%Y"),
            "Hari":tgl.strftime("%A"),
            "Keterangan":nama
            })

    if len(libur_list)==0:

        st.success("Tidak ada hari libur nasional bulan ini")

    else:

        st.warning(f"Ada {len(libur_list)} hari libur nasional")

        st.dataframe(libur_list,use_container_width=True)

# ================== KALENDER VISUAL ==================

    st.divider()
    st.subheader("📅 Kalender Shift Visual")

    warna_shift={
    "1":"#3498db",
    "2":"#2ecc71",
    "3":"#f1c40f",
    "OFF":"#e74c3c"
    }

    events=[]

    for hari in range(1,jumlah_hari+1):

        shift=str(df_baru[str(hari)].iloc[0]).replace(" LIBUR","")

        warna=warna_shift.get(shift,"#888")

        tanggal=f"{tahun}-{bulan:02d}-{hari:02d}"

        events.append({
        "title":f"Shift {shift}",
        "start":tanggal,
        "backgroundColor":warna,
        "borderColor":warna
        })

    calendar_options={
    "initialView":"dayGridMonth",
    "height":600
    }

    st_calendar(events=events,options=calendar_options)

# ================== EXPORT ==================

    st.divider()
    st.subheader("⬇️ Export Jadwal")

    buffer=BytesIO()
    df_baru.to_excel(buffer,index=False)

    st.download_button(
    "Download Excel",
    buffer.getvalue(),
    "jadwal_shift.xlsx"
    )

    if st.button("Generate PDF"):

        pdf=FPDF()
        pdf.add_page()
        pdf.set_font("Arial",size=8)

        for i in range(len(df_baru)):

            row=" | ".join(str(x) for x in df_baru.iloc[i])
            row=row.encode("latin-1","ignore").decode("latin-1")

            pdf.cell(200,8,txt=row,ln=True)

        pdf.output("jadwal.pdf")

        with open("jadwal.pdf","rb") as f:

            st.download_button(
            "Download PDF",
            f,
            "jadwal_shift.pdf"
            )

# ================== ADMIN ==================

with tab3:

    st.subheader("Admin Panel")

    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in=False

    if not st.session_state.admin_logged_in:

        user=st.text_input("Username")
        pwd=st.text_input("Password",type="password")

        if st.button("Login"):

            if user=="admin" and pwd=="admin123":

                st.session_state.admin_logged_in=True
                st.success("Login berhasil")

            else:

                st.error("Login gagal")

        st.stop()

    st.subheader("Tambah Karyawan")

    nama=st.text_input("Nama")
    title=st.text_input("Title")

    if st.button("Tambah"):

        new_no=len(base_cols)+1

        new_row=pd.DataFrame(
        [[new_no,nama,title]],
        columns=["NO","NAMA","TITLE"]
        )

        base_cols=pd.concat([base_cols,new_row])

        base_cols.to_csv(FILE_TETAP,index=False)

        st.success("Karyawan ditambahkan")

    st.subheader("Hapus Karyawan")

    hapus=st.selectbox("Pilih karyawan",base_cols["NAMA"])

    if st.button("Hapus"):

        base_cols=base_cols[base_cols["NAMA"]!=hapus]

        base_cols.to_csv(FILE_TETAP,index=False)

        st.success("Karyawan dihapus")
