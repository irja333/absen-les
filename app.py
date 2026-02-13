import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Konfigurasi Halaman
st.set_page_config(page_title="AbsenLesBna", layout="wide")

# Inisialisasi Database (Menggunakan Session State untuk demo, bisa diganti Database asli)
if 'db_absensi' not in st.session_state:
    st.session_state.db_absensi = pd.DataFrame(columns=[
        'Tanggal', 'Tentor', 'Siswa', 'Jumlah Siswa', 'Tingkatan', 'Alamat', 'Durasi', 'Status'
    ])

# --- SIDEBAR NAVIGASI ---
st.sidebar.title("AbsenLesBna")
menu = st.sidebar.radio("Pilih Menu", ["Input Absensi (Tentor)", "Dashboard Admin"])

# --- HALAMAN TENTOR ---
if menu == "Input Absensi (Tentor)":
    st.header("📝 Absensi Tentor")
    
    with st.form("form_absen", clear_on_submit=True):
        tentor = st.text_input("Nama Tentor")
        siswa = st.text_input("Nama Siswa")
        jumlah_siswa = st.number_input("Jumlah Siswa", min_value=1, value=1)
        tingkatan = st.selectbox("Pilih Tingkatan", ["Preschool", "PAUD", "TK", "SD", "SMP", "SMA", "UMUM"])
        alamat = st.text_area("Alamat")
        durasi = st.number_input("Durasi Belajar (menit)", min_value=1, value=90)
        status = st.selectbox("Status Kehadiran", ["Hadir", "Izin (Tentor)", "Izin (Siswa)"])
        
        submit = st.form_submit_button("Simpan Absensi")
        
        if submit:
            if tentor and siswa:
                new_data = {
                    'Tanggal': datetime.now().strftime("%d/%m/%Y"),
                    'Tentor': tentor,
                    'Siswa': siswa,
                    'Jumlah Siswa': jumlah_siswa,
                    'Tingkatan': tingkatan,
                    'Alamat': alamat,
                    'Durasi': durasi,
                    'Status': status
                }
                # Menambahkan data ke session state
                st.session_state.db_absensi = pd.concat([st.session_state.db_absensi, pd.DataFrame([new_data])], ignore_index=True)
                st.success("✅ Absensi berhasil disimpan!")
            else:
                st.error("Nama Tentor dan Siswa wajib diisi!")

# --- HALAMAN ADMIN ---
elif menu == "Dashboard Admin":
    st.header("📊 Dashboard Admin")
    
    # Login Sederhana
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        
    if not st.session_state.logged_in:
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "admin" and pw == "admin123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Salah password!")
    else:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

        # Tampilkan Data Tabular
        st.subheader("Data Absensi Keseluruhan")
        df = st.session_state.db_absensi
        st.dataframe(df, use_container_width=True)

        # Fitur Hapus Data
        if not df.empty:
            index_to_delete = st.number_input("Masukkan Index baris untuk dihapus", min_value=0, max_value=len(df)-1, step=1)
            if st.button("Hapus Baris"):
                st.session_state.db_absensi = df.drop(df.index[index_to_delete]).reset_index(drop=True)
                st.rerun()

        # Rekap Bulanan
        st.divider()
        st.subheader("📅 Rekap Bulanan")
        col1, col2 = st.columns(2)
        with col1:
            bulan_pilih = st.selectbox("Pilih Bulan", list(range(1, 13)), format_func=lambda x: datetime(2024, x, 1).strftime('%B'))
        with col2:
            tahun_pilih = st.number_input("Tahun", value=datetime.now().year)

        if st.button("Tampilkan Rekap"):
            # Filter data berdasarkan bulan/tahun (asumsi kolom Tanggal format DD/MM/YYYY)
            df['dt'] = pd.to_datetime(df['Tanggal'], format="%d/%m/%Y")
            mask = (df['dt'].dt.month == bulan_pilih) & (df['dt'].dt.year == tahun_pilih) & (df['Status'] == "Hadir")
            rekap_df = df[mask]
            
            if not rekap_df.empty:
                # Grouping seperti di JavaScript
                summary = rekap_df.groupby(['Tentor', 'Siswa', 'Tingkatan']).agg({
                    'Tanggal': 'count',
                    'Durasi': 'sum'
                }).rename(columns={'Tanggal': 'Pertemuan', 'Durasi': 'Total Durasi (menit)'}).reset_index()
                
                st.table(summary)
                
                # Export ke CSV
                output = io.StringIO()
                summary.to_csv(output, index=False)
                st.download_button(
                    label="📥 Download Rekap (CSV)",
                    data=output.getvalue(),
                    file_name=f"Rekap_{bulan_pilih}_{tahun_pilih}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("Tidak ada data hadir untuk periode ini.")
