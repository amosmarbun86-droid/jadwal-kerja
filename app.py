import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date
import matplotlib.pyplot as plt
import holidays

st.set_page_config(layout="wide")

# ==========================================
# BACKGROUND GAMBAR
# ==========================================
def set_bg():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("background.png");
            background-size: cover;
            background-attachment: fixed;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg()

# ==========================================
# LOGIN SYSTEM
# ==========================================
st.title("🏢 SISTEM MANAJEMEN SHIFT - PRO")

if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.role = None

if not st.session_state.login:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.login = True
            st.session_state.role = "Admin"
        elif username == "user" and password == "user123":
            st.session_state.login = True
            st.session_state.role = "User"
        else:
            st.error("Login salah")

    st.stop()

st.success(f"Login sebagai {st.session_state.role}")

# ==========================================
# LOAD DATA
# ==========================================
df = pd.read_csv("Jadwal_Februari_2026_Rapih.csv")
df.columns = df.columns.str.upper()

# ==========================================
# PILIH BULAN & TAHUN
# ==========================================
bulan = st.selectbox("Pilih Bulan", list(range(1, 13)), index=1)
tahun = st.number_input("Tahun", 2024, 2035, 2026)

jumlah_hari = calendar.monthrange(int(tahun), bulan)[1]

# ==========================================
# LIBUR NASIONAL INDONESIA 🇮🇩
# ==========================================
hari_libur = holidays.Indonesia(years=tahun)
libur_bulan_ini = {}

for tanggal, nama in hari_libur.items():
    if tanggal.month == bulan:
        libur_bulan_ini[tanggal.day] = nama

# ==========================================
# POLA SHIFT
# ==========================================
default_pola = [
    "OFF","3","3","3",
    "OFF","2","2","2",
    "OFF","1","1","1",
]

if st.session_state.role == "Admin":
    pola_input = st.text_input(
        "Edit Pola Shift (pisahkan koma)",
        value="OFF,3,3,3,OFF,2,2,2,OFF,1,1,1"
    )
    pola = pola_input.split(",")
else:
    pola = default_pola

# ==========================================
# OFFSET DARI FEB 2026
# ==========================================
bulan_dasar = 2
tahun_dasar = 2026
total_offset = 0

if tahun == tahun_dasar and bulan >= bulan_dasar:
    for b in range(bulan_dasar, bulan):
        total_offset += calendar.monthrange(tahun, b)[1]
elif tahun > tahun_dasar:
    for b in range(bulan_dasar, 13):
        total_offset += calendar.monthrange(tahun_dasar, b)[1]
    for t in range(tahun_dasar + 1, tahun):
        for b in range(1, 13):
            total_offset += calendar.monthrange(t, b)[1]
    for b in range(1, bulan):
        total_offset += calendar.monthrange(tahun, b)[1]

# ==========================================
# GENERATE JADWAL
# ==========================================
data_baru = []

for _, row in df.iterrows():
    baris = {
        "NO": row["NO"],
        "NAMA": row["NAMA"],
        "TITLE": row["TITLE"],
    }

    for i in range(jumlah_hari):
        posisi = (total_offset + i) % len(pola)
        hari_ke = i + 1
        shift = pola[posisi]

        # Tambah tanda libur nasional 🇮🇩
        if hari_ke in libur_bulan_ini:
            shift = f"{shift} 🇮🇩"

        baris[str(hari_ke)] = shift

    data_baru.append(baris)

df_baru = pd.DataFrame(data_baru)

# ==========================================
# HIGHLIGHT OFF + LIBUR
# ==========================================
def highlight(val):
    val = str(val)

    if "🇮🇩" in val:
        return "background-color:#b30000;color:white;font-weight:bold;"
    if val == "OFF":
        return "background-color:red;color:white;"
    return ""

st.dataframe(df_baru.style.applymap(highlight), use_container_width=True)

# ==========================================
# PANEL LIBUR NASIONAL
# ==========================================
if libur_bulan_ini:
    st.subheader("🇮🇩 Libur Nasional")

    df_libur = pd.DataFrame([
        {"Tanggal": f"{hari}-{bulan}-{tahun}", "Keterangan": nama}
        for hari, nama in libur_bulan_ini.items()
    ])

    st.dataframe(df_libur, use_container_width=True)

# ==========================================
# STATISTIK
# ==========================================
st.subheader("📊 Statistik Shift Bulan Ini")

shift_counts = {"1":0,"2":0,"3":0,"OFF":0}

for col in df_baru.columns[3:]:
    counts = df_baru[col].astype(str).value_counts()
    for key in shift_counts:
        shift_counts[key] += sum(counts.get(k,0) for k in counts.index if key in k)

fig = plt.figure()
plt.bar(shift_counts.keys(), shift_counts.values())
plt.title("Total Shift")
plt.xlabel("Jenis Shift")
plt.ylabel("Jumlah")
st.pyplot(fig)

# ==========================================
# TOTAL HARI KERJA
# ==========================================
st.subheader("📋 Total Hari Kerja per Karyawan")

rekap = []

for _, row in df_baru.iterrows():
    kerja = 0
    for col in df_baru.columns[3:]:
        if "OFF" not in str(row[col]):
            kerja += 1
    rekap.append({"NAMA": row["NAMA"], "TOTAL KERJA": kerja})

df_rekap = pd.DataFrame(rekap)
st.dataframe(df_rekap, use_container_width=True)

# ==========================================
# DOWNLOAD
# ==========================================
csv = df_baru.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇ Download CSV",
    csv,
    f"Jadwal_{bulan}_{tahun}.csv",
    "text/csv"
)
