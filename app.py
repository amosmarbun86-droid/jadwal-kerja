import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import matplotlib.pyplot as plt

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="Manajemen Shift Pro",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS (MODERN UI)
# =====================================================
st.markdown("""
<style>
.main-title {
    font-size:30px;
    font-weight:700;
    color:#1f77b4;
}
.metric-box {
    padding:15px;
    border-radius:15px;
    background-color:#f8f9fa;
    box-shadow:0 4px 8px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏢 SISTEM MANAJEMEN SHIFT - PRO</div>', unsafe_allow_html=True)
st.markdown("---")

# =====================================================
# LOGIN SYSTEM
# =====================================================
if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.role = None

if not st.session_state.login:
    st.subheader("🔐 Login Sistem")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.login = True
            st.session_state.role = "Admin"
            st.rerun()
        elif username == "user" and password == "user123":
            st.session_state.login = True
            st.session_state.role = "User"
            st.rerun()
        else:
            st.error("Username atau Password salah")

    st.stop()

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.header("⚙ Pengaturan")

    bulan = st.selectbox("Pilih Bulan", list(range(1, 13)), index=1)
    tahun = st.number_input("Tahun", 2024, 2035, 2026)

    st.markdown("---")
    st.success(f"Login sebagai {st.session_state.role}")

    if st.button("Logout"):
        st.session_state.login = False
        st.rerun()

# =====================================================
# LOAD DATA
# =====================================================
df = pd.read_csv("Jadwal_Februari_2026_Rapih.csv")
df.columns = df.columns.str.upper()

jumlah_hari = calendar.monthrange(int(tahun), bulan)[1]

# =====================================================
# POLA SHIFT
# =====================================================
default_pola = [
    "OFF","3","3","3",
    "OFF","2","2","2",
    "OFF","1","1","1"
]

if st.session_state.role == "Admin":
    pola_input = st.text_input(
        "Edit Pola Shift (pisahkan koma)",
        value="OFF,3,3,3,OFF,2,2,2,OFF,1,1,1"
    )
    pola = pola_input.split(",")
else:
    pola = default_pola

# =====================================================
# OFFSET ROTASI DARI FEB 2026
# =====================================================
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

# =====================================================
# GENERATE JADWAL BARU
# =====================================================
data_baru = []

for _, row in df.iterrows():
    baris = {
        "NO": row["NO"],
        "NAMA": row["NAMA"],
        "TITLE": row["TITLE"],
    }

    for i in range(jumlah_hari):
        posisi = (total_offset + i) % len(pola)
        baris[str(i+1)] = pola[posisi]

    data_baru.append(baris)

df_baru = pd.DataFrame(data_baru)

# =====================================================
# HIGHLIGHT SHIFT
# =====================================================
def highlight(val):
    if val == "1":
        return "background-color:#d4edda"
    elif val == "2":
        return "background-color:#fff3cd"
    elif val == "3":
        return "background-color:#cce5ff"
    elif val == "OFF":
        return "background-color:#dc3545;color:white;"
    return ""

# =====================================================
# DASHBOARD METRIC
# =====================================================
shift_counts = {"1":0,"2":0,"3":0,"OFF":0}

for col in df_baru.columns[3:]:
    counts = df_baru[col].value_counts()
    for key in shift_counts:
        shift_counts[key] += counts.get(key,0)

st.subheader("📊 Dashboard Statistik")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Shift 1", shift_counts["1"])
col2.metric("Shift 2", shift_counts["2"])
col3.metric("Shift 3", shift_counts["3"])
col4.metric("OFF", shift_counts["OFF"])

# =====================================================
# TABEL JADWAL
# =====================================================
st.subheader("📅 Jadwal Shift")

st.dataframe(
    df_baru.style.applymap(highlight),
    use_container_width=True
)

# =====================================================
# GRAFIK
# =====================================================
st.subheader("📈 Grafik Distribusi Shift")

chart_data = pd.DataFrame({
    "Shift": shift_counts.keys(),
    "Jumlah": shift_counts.values()
}).set_index("Shift")

st.bar_chart(chart_data)

# =====================================================
# TOTAL KERJA PER ORANG
# =====================================================
st.subheader("📋 Total Hari Kerja per Karyawan")

rekap = []

for _, row in df_baru.iterrows():
    kerja = sum(1 for col in df_baru.columns[3:] if row[col] != "OFF")
    rekap.append({"NAMA": row["NAMA"], "TOTAL KERJA": kerja})

df_rekap = pd.DataFrame(rekap)

st.dataframe(df_rekap, use_container_width=True)

# =====================================================
# NOTIFIKASI SHIFT BESOK
# =====================================================
today = datetime.today().day

if today < jumlah_hari:
    besok = str(today + 1)

    st.subheader("🔔 Shift Besok")

    notif = df_baru[["NAMA", besok]]
    notif.columns = ["NAMA", "SHIFT BESOK"]

    st.dataframe(notif, use_container_width=True)

# =====================================================
# DOWNLOAD CSV
# =====================================================
csv = df_baru.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇ Download Jadwal CSV",
    csv,
    f"Jadwal_{bulan}_{tahun}.csv",
    "text/csv"
)
