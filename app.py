import streamlit as st
import pandas as pd
import calendar
import holidays

st.set_page_config(
    page_title="Shift App",
    page_icon="📅",
    layout="wide"
)

# =====================================================
# ANDROID APP STYLE
# =====================================================

BG = "https://images.unsplash.com/photo-1504384308090-c894fdcc538d"

st.markdown(f"""
<style>

/* ===== Full Mobile Look ===== */
.stApp {{
    background:
    linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)),
    url("{BG}");
    background-size: cover;
    background-attachment: fixed;
    font-family: "Segoe UI", sans-serif;
}}

/* ===== Hide Streamlit header ===== */
header, footer {{
    visibility: hidden;
}}

/* ===== App Bar ===== */
.appbar {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 60px;
    background: #0d6efd;
    color: white;
    display: flex;
    align-items: center;
    padding-left: 20px;
    font-size: 20px;
    font-weight: bold;
    z-index: 999;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}}

/* ===== Content padding ===== */
.block-container {{
    padding-top: 80px;
    padding-bottom: 40px;
}}

/* ===== Cards ===== */
.card {{
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(14px);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.4);
    color: white;
}}

/* ===== Buttons ===== */
.stButton>button {{
    width: 100%;
    height: 50px;
    border-radius: 14px;
    background: #0d6efd;
    color: white;
    font-size: 16px;
    font-weight: bold;
    border: none;
}}

/* ===== Inputs ===== */
.stTextInput input, .stSelectbox div {{
    border-radius: 12px !important;
}}

</style>

<div class="appbar">📅 Shift Management App</div>

""", unsafe_allow_html=True)

# =====================================================
# LOGIN
# =====================================================

if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.role = None

if not st.session_state.login:

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("🔐 Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):

        if u == "admin" and p == "admin123":
            st.session_state.login = True
            st.session_state.role = "Admin"
            st.rerun()

        elif u == "user" and p == "user123":
            st.session_state.login = True
            st.session_state.role = "User"
            st.rerun()

        else:
            st.error("Login salah")

    st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# =====================================================
# MAIN APP
# =====================================================

st.markdown('<div class="card">', unsafe_allow_html=True)

st.write(f"Login sebagai **{st.session_state.role}**")

bulan = st.selectbox("Bulan", list(range(1,13)))
tahun = st.number_input("Tahun", 2024, 2035, 2026)

st.markdown('</div>', unsafe_allow_html=True)

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
# INPUT JADWAL
# =====================================================

st.markdown('<div class="card">', unsafe_allow_html=True)

st.subheader("📝 Input Jadwal")

nama = st.text_input("Nama Karyawan")

shift = st.selectbox(
    "Pilih Shift",
    ["1 (Pagi)", "2 (Siang)", "3 (Malam)", "OFF"]
)

if st.button("Simpan"):
    st.success(f"{nama} → {shift} disimpan")

st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# PANEL LIBUR
# =====================================================

if libur_bulan_ini:

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("🇮🇩 Libur Nasional")

    df_libur = pd.DataFrame([
        {"Tanggal": f"{h}-{bulan}-{tahun}", "Keterangan": n}
        for h, n in libur_bulan_ini.items()
    ])

    st.dataframe(df_libur, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)
