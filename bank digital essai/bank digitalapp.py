
import streamlit as st

# Pengaturan halaman
st.set_page_config(
    page_title="Bank Pengalaman Mahasiswa",
    page_icon="📚",
    layout="wide"
)

# Judul utama
st.title("📚 BANK PENGALAMAN DIGITAL MAHASISWA")

st.write(
    "Platform berbagi pengalaman, pengetahuan, "
    "dan referensi pembelajaran antargenerasi mahasiswa."
)

st.divider()

# Menu navigasi
st.sidebar.title("MENU UTAMA")

menu = st.sidebar.radio(
    "Pilih Halaman:",
    [
        "Dashboard",
        "Pengalaman Praktikum",
        "Tambah Pengalaman",
        "Tips dan Trik",
        "Arsip Pembelajaran"
    ]
)

# HALAMAN DASHBOARD
if menu == "Dashboard":

    st.header("Dashboard Utama")
    st.write("Selamat datang di Bank Pengalaman Mahasiswa!")

    # Statistik
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Pengalaman", "45")
    col2.metric("Kontributor", "30")
    col3.metric("Materi Pembelajaran", "25")

    st.divider()

    st.subheader("Tujuan Platform")

    st.info(
        "Membantu mahasiswa memperoleh informasi, "
        "referensi, dan pengalaman praktikum dari "
        "mahasiswa angkatan sebelumnya."
    )

    st.subheader("Fitur Utama")

    a, b = st.columns(2)

    with a:
        st.success("📖 Berbagi pengalaman praktikum")
        st.success("💡 Tips dan solusi pembelajaran")

    with b:
        st.success("📁 Arsip materi pembelajaran")
        st.success("🔎 Pencarian informasi")

# HALAMAN PENGALAMAN
elif menu == "Pengalaman Praktikum":

    st.header("📖 Pengalaman Praktikum")

    st.write("Kumpulan pengalaman praktikum mahasiswa.")

    st.text_input(
        "Cari pengalaman berdasarkan mata kuliah:"
    )

    st.info(
        "Belum ada data pengalaman yang dimasukkan."
    )

# HALAMAN TAMBAH PENGALAMAN
elif menu == "Tambah Pengalaman":

    st.header("✍️ Bagikan Pengalaman")

    with st.form("form_pengalaman"):

        nama = st.text_input("Nama Mahasiswa")

        angkatan = st.text_input("Angkatan")

        mata_kuliah = st.text_input("Nama Mata Kuliah")

        judul = st.text_input("Judul Pengalaman")

        pengalaman = st.text_area(
            "Ceritakan pengalaman praktikum:"
        )

        tips = st.text_area(
            "Tips untuk mahasiswa berikutnya:"
        )

        kirim = st.form_submit_button(
            "Kirim Pengalaman"
        )

        if kirim:

            if nama and mata_kuliah and pengalaman:
                st.success(
                    "Data berhasil diterima sebagai contoh!"
                )
            else:
                st.warning(
                    "Mohon lengkapi nama, mata kuliah, "
                    "dan pengalaman."
                )

# HALAMAN TIPS
elif menu == "Tips dan Trik":

    st.header("💡 Tips dan Trik")

    st.write(
        "Berisi tips belajar dan solusi kendala praktikum."
    )

# HALAMAN ARSIP
elif menu == "Arsip Pembelajaran":

    st.header("📁 Arsip Pembelajaran")

    st.write(
        "Tempat menyimpan referensi dan dokumentasi "
        "pembelajaran mahasiswa."
    )

# Footer
st.divider()

st.caption(
    "Bank Pengalaman Digital Mahasiswa | "
    "Platform Pembelajaran Berkelanjutan"
)
