import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
from supabase import create_client

st.set_page_config(page_title="Shift System PRO", layout="wide")

# =============================
# KONEKSI DATABASE (Secrets)
# =============================
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)

# =============================
# LOGIN SYSTEM DATABASE
# =============================
st.title("🏢 SHIFT MANAGEMENT SYSTEM PRO")

if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.user = None

if not st.session_state.login:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        result = supabase.table("users") \
            .select("*") \
            .eq("username", username) \
            .eq("password", password) \
            .execute()

        if result.data:
            st.session_state.login = True
            st.session_state.user = result.data[0]
            st.success("Login berhasil")
            st.rerun()
        else:
            st.error("Login gagal")

    st.stop()

st.success(f"Login sebagai {st.session_state.user['role']}")

# =============================
# LOAD DATA DARI DATABASE
# =============================
data = supabase.table("karyawan").select("*").execute()
df = pd.DataFrame(data.data)

# =============================
# PILIH BULAN
# =============================
bulan = st.selectbox("Bulan", list(range(1, 13)))
tahun = st.number_input("Tahun", 2024, 2035, 2026)

jumlah_hari = calendar.monthrange(int(tahun), bulan)[1]

# =============================
# POLA SHIFT
# =============================
pola = [
    "OFF","3","3","3",
    "OFF","2","2","2",
    "OFF","1","1","1",
]

# =============================
# GENERATE JADWAL
# =============================
jadwal = []

for _, row in df.iterrows():
    data_row = {
        "NAMA": row["nama"],
        "TITLE": row["title"]
    }

    for i in range(jumlah_hari):
        data_row[str(i+1)] = pola[i % len(pola)]

    jadwal.append(data_row)

df_jadwal = pd.DataFrame(jadwal)

# =============================
# TAMPILKAN
# =============================
def highlight(val):
    if val == "OFF":
        return "background-color:red;color:white;"
    return ""

st.dataframe(df_jadwal.style.applymap(highlight), use_container_width=True)

# =============================
# STATISTIK
# =============================
st.subheader("📊 Statistik Shift")

counts = {"1":0,"2":0,"3":0,"OFF":0}

for col in df_jadwal.columns[2:]:
    c = df_jadwal[col].value_counts()
    for k in counts:
        counts[k] += c.get(k, 0)

st.bar_chart(counts)

# =============================
# DOWNLOAD
# =============================
csv = df_jadwal.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇ Download CSV",
    csv,
    f"jadwal_{bulan}_{tahun}.csv",
    "text/csv"
)
