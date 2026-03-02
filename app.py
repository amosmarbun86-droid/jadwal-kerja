fig = plt.figure()
plt.bar(shift_counts.keys(), shift_counts.values())
plt.title("Total Shift")
plt.xlabel("Jenis Shift")
plt.ylabel("Jumlah")
st.pyplot(fig)

# =====================================================
# TOTAL HARI KERJA PER ORANG (ASLI)
# =====================================================

st.subheader("ðŸ“‹ Total Hari Kerja per Karyawan")

rekap = []

for _, row in df_baru.iterrows():
    kerja = 0
    for col in df_baru.columns[3:]:
        if "OFF" not in str(row[col]):
            kerja += 1
    rekap.append({"NAMA": row["NAMA"], "TOTAL KERJA": kerja})

df_rekap = pd.DataFrame(rekap)
st.dataframe(df_rekap, use_container_width=True)

# =====================================================
# DOWNLOAD CSV (ASLI)
# =====================================================

csv = df_baru.to_csv(index=False).encode("utf-8")

st.download_button(
    "â¬‡ Download CSV",
    csv,
    f"Jadwal_{bulan}_{tahun}.csv",
    "text/csv")
