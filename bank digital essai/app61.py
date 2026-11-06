
import streamlit as st
import sqlite3
import pandas as pd
import os
import uuid
from datetime import datetime

# ==========================================
# KONFIGURASI APLIKASI
# ==========================================

st.set_page_config(
    page_title="Bank Pengalaman Mahasiswa | PNM",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_NAME = "bank_pengalaman.db"

# Daftar jurusan dan program studi berdasarkan informasi yang diberikan pengguna.
PROGRAM_STUDI = {
    "Jurusan Administrasi Bisnis": [
        "D3 - Administrasi Bisnis", "D3 - Bahasa Inggris", "D4 - Pemasaran Digital"
    ],
    "Jurusan Akuntansi": [
        "D3 - Akuntansi", "D4 - Akuntansi Perpajakan",
        "D4 - Akuntansi Sektor Publik", "D4 - Akuntansi Bisnis Digital"
    ],
    "Jurusan Teknik": [
        "D2 - Teknik Pembentukan Logam", "D3 - Teknik Komputer Kontrol",
        "D3 - Teknik Listrik", "D3 - Teknologi Informasi",
        "D4 - Teknologi Rekayasa Otomotif", "D4 - Perkeretaapian (Rollingstock)",
        "D4 - Teknologi Rekayasa Perangkat Lunak", "D4 - Teknologi Rekayasa Otomasi",
        "D4 - Teknologi Rekayasa Elektronika",
        "D4 - Teknologi Rekayasa Konstruksi Jalan dan Jembatan"
    ]
}


# ==========================================
# DATABASE SQLITE
# ==========================================

def koneksi_database():
    return sqlite3.connect(DB_NAME)


def buat_tabel():
    with koneksi_database() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pengalaman (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                jurusan TEXT DEFAULT 'Belum dipilih',
                program_studi TEXT DEFAULT 'Belum dipilih',
                angkatan TEXT NOT NULL,
                mata_kuliah TEXT NOT NULL,
                judul TEXT NOT NULL,
                pengalaman TEXT NOT NULL,
                kendala TEXT,
                solusi TEXT,
                tips TEXT,
                kategori TEXT DEFAULT 'Umum',
                tanggal TEXT NOT NULL
            )
        """)


def simpan_pengalaman(
    nama, jurusan, program_studi, angkatan, mata_kuliah,
    judul, pengalaman, kendala,
    solusi, tips, kategori
):
    with koneksi_database() as conn:
        conn.execute("""
            INSERT INTO pengalaman (
                nama, jurusan, program_studi, angkatan, mata_kuliah,
                judul, pengalaman, kendala,
                solusi, tips, kategori, tanggal
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            nama, jurusan, program_studi, angkatan, mata_kuliah,
            judul, pengalaman, kendala,
            solusi, tips, kategori,
            datetime.now().strftime("%Y-%m-%d")
        ))


def ambil_data():
    with koneksi_database() as conn:
        return pd.read_sql_query("""
            SELECT * FROM pengalaman
            ORDER BY id DESC
        """, conn)


def buat_tabel_komentar():
    """Membuat tabel diskusi yang terhubung ke setiap pengalaman."""
    with koneksi_database() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS komentar_pengalaman (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pengalaman_id INTEGER NOT NULL,
                nama TEXT NOT NULL,
                isi_komentar TEXT NOT NULL,
                tanggal TEXT NOT NULL,
                FOREIGN KEY (pengalaman_id) REFERENCES pengalaman(id)
            )
        """)


def simpan_komentar(pengalaman_id, nama, isi_komentar):
    with koneksi_database() as conn:
        conn.execute("""
            INSERT INTO komentar_pengalaman
                (pengalaman_id, nama, isi_komentar, tanggal)
            VALUES (?, ?, ?, ?)
        """, (
            int(pengalaman_id), nama.strip(), isi_komentar.strip(),
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))


def ambil_komentar(pengalaman_id):
    with koneksi_database() as conn:
        return conn.execute("""
            SELECT nama, isi_komentar, tanggal
            FROM komentar_pengalaman
            WHERE pengalaman_id = ?
            ORDER BY id DESC
        """, (int(pengalaman_id),)).fetchall()


def buat_tabel_rating():
    """Membuat tabel rating dan ulasan untuk setiap pengalaman."""
    with koneksi_database() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rating_pengalaman (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pengalaman_id INTEGER NOT NULL,
                nim TEXT NOT NULL,
                nama TEXT NOT NULL,
                nilai INTEGER NOT NULL CHECK (nilai BETWEEN 1 AND 5),
                ulasan TEXT DEFAULT '',
                tanggal TEXT NOT NULL,
                UNIQUE (pengalaman_id, nim),
                FOREIGN KEY (pengalaman_id) REFERENCES pengalaman(id)
            )
        """)


def simpan_rating(pengalaman_id, nim, nama, nilai, ulasan):
    with koneksi_database() as conn:
        conn.execute("""
            INSERT INTO rating_pengalaman
                (pengalaman_id, nim, nama, nilai, ulasan, tanggal)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(pengalaman_id, nim) DO UPDATE SET
                nama = excluded.nama,
                nilai = excluded.nilai,
                ulasan = excluded.ulasan,
                tanggal = excluded.tanggal
        """, (
            int(pengalaman_id), nim.strip(), nama.strip(), int(nilai),
            ulasan.strip(), datetime.now().strftime("%Y-%m-%d %H:%M")
        ))


def ambil_ringkasan_rating(pengalaman_id):
    with koneksi_database() as conn:
        return conn.execute("""
            SELECT AVG(nilai), COUNT(*)
            FROM rating_pengalaman
            WHERE pengalaman_id = ?
        """, (int(pengalaman_id),)).fetchone()


def ambil_ulasan_rating(pengalaman_id):
    with koneksi_database() as conn:
        return conn.execute("""
            SELECT nama, nilai, ulasan, tanggal
            FROM rating_pengalaman
            WHERE pengalaman_id = ? AND TRIM(ulasan) != ''
            ORDER BY id DESC
        """, (int(pengalaman_id),)).fetchall()


buat_tabel()
buat_tabel_komentar()
buat_tabel_rating()


def buat_tabel_dokumen():
    with koneksi_database() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dokumen_tugas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                nim TEXT NOT NULL,
                jurusan TEXT DEFAULT 'Belum dipilih',
                program_studi TEXT DEFAULT 'Belum dipilih',
                angkatan TEXT DEFAULT '',
                mata_kuliah TEXT NOT NULL,
                jenis_tugas TEXT DEFAULT 'Lainnya',
                nama_tugas TEXT NOT NULL,
                keterangan TEXT,
                nama_file_kriteria TEXT NOT NULL,
                lokasi_file_kriteria TEXT NOT NULL,
                nama_file_tugas TEXT NOT NULL,
                lokasi_file_tugas TEXT NOT NULL,
                tanggal TEXT NOT NULL
            )
        """)


buat_tabel_dokumen()


def perbarui_struktur_tabel_dokumen():
    """Menambahkan kolom baru tanpa menghapus data lama."""
    with koneksi_database() as conn:
        kolom = [
            baris[1]
            for baris in conn.execute("PRAGMA table_info(dokumen_tugas)").fetchall()
        ]
        if "jurusan" not in kolom:
            conn.execute("ALTER TABLE dokumen_tugas ADD COLUMN jurusan TEXT DEFAULT 'Belum dipilih'")
        if "program_studi" not in kolom:
            conn.execute("ALTER TABLE dokumen_tugas ADD COLUMN program_studi TEXT DEFAULT 'Belum dipilih'")
        if "angkatan" not in kolom:
            conn.execute(
                "ALTER TABLE dokumen_tugas ADD COLUMN angkatan TEXT DEFAULT ''"
            )
        if "jenis_tugas" not in kolom:
            conn.execute(
                "ALTER TABLE dokumen_tugas ADD COLUMN jenis_tugas TEXT DEFAULT 'Lainnya'"
            )

    # Migrasi tabel pengalaman: menambah kategori tanpa menghapus data lama.
    with koneksi_database() as conn:
        kolom_pengalaman = [b[1] for b in conn.execute("PRAGMA table_info(pengalaman)").fetchall()]
        if "kategori" not in kolom_pengalaman:
            conn.execute("ALTER TABLE pengalaman ADD COLUMN kategori TEXT DEFAULT 'Umum'")
        if "jurusan" not in kolom_pengalaman:
            conn.execute("ALTER TABLE pengalaman ADD COLUMN jurusan TEXT DEFAULT 'Belum dipilih'")
        if "program_studi" not in kolom_pengalaman:
            conn.execute("ALTER TABLE pengalaman ADD COLUMN program_studi TEXT DEFAULT 'Belum dipilih'")


perbarui_struktur_tabel_dokumen()


# ==========================================
# DESAIN CSS
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #F5F7FA;
    color: #243447;
}

header[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background-color: #142D4E;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    font-size: 14px;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1250px;
}

.main-header {
    background-color: #FFFFFF;
    border-left: 5px solid #234B76;
    padding: 25px 30px;
    border-radius: 5px;
    margin-bottom: 25px;
    border-top: 1px solid #E1E7EF;
    border-right: 1px solid #E1E7EF;
    border-bottom: 1px solid #E1E7EF;
}

.main-header h1 {
    color: #142D4E;
    font-size: 27px;
    margin-bottom: 8px;
}

.main-header p {
    color: #68778A;
    font-size: 14px;
    margin-bottom: 0;
}

.campus-label {
    color: #42678E;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.3px;
    margin-bottom: 8px;
}

.section-heading {
    color: #142D4E;
    font-size: 20px;
    font-weight: 650;
    margin-top: 25px;
    margin-bottom: 15px;
}

.metric-box {
    background-color: #FFFFFF;
    border: 1px solid #E0E6ED;
    border-radius: 7px;
    padding: 18px;
}

.metric-label {
    color: #718096;
    font-size: 13px;
}

.metric-value {
    color: #142D4E;
    font-size: 27px;
    font-weight: 700;
    margin-top: 8px;
}

.content-box {
    background-color: #FFFFFF;
    border: 1px solid #E0E6ED;
    border-radius: 7px;
    padding: 20px;
    margin-bottom: 12px;
}

.content-box h4 {
    color: #142D4E;
    font-size: 16px;
}

.content-box p {
    color: #68778A;
    font-size: 14px;
}

.stButton button,
.stFormSubmitButton button {
    background-color: #234B76;
    color: white;
    border-radius: 5px;
    border: none;
}

.stButton button:hover,
.stFormSubmitButton button:hover {
    background-color: #142D4E;
    color: white;
}

.footer {
    text-align: center;
    color: #8793A2;
    font-size: 12px;
    border-top: 1px solid #E0E6ED;
    margin-top: 40px;
    padding-top: 20px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# IDENTITAS MAHASISWA
# ==========================================

def halaman_identitas():
    st.markdown(
        '<div class="main-header"><div class="campus-label">POLITEKNIK NEGERI MADIUN</div>'
        '<h1>Bank Pengalaman Digital Mahasiswa</h1>'
        '<p>Masukkan identitas untuk melanjutkan ke platform.</p></div>',
        unsafe_allow_html=True
    )

    st.subheader("Identitas Mahasiswa")
    st.caption("Ini merupakan identitas awal pada prototipe, bukan proses verifikasi akun resmi.")

    # Kontrol identitas diletakkan di luar st.form agar Streamlit langsung
    # menjalankan ulang halaman saat jurusan berubah dan memperbarui pilihan prodi.
    nama_masuk = st.text_input("Nama mahasiswa", key="input_nama_masuk")
    nim_masuk = st.text_input("NIM", key="input_nim_masuk")
    jurusan_masuk = st.selectbox(
        "Jurusan",
        list(PROGRAM_STUDI.keys()),
        key="pilih_jurusan_masuk"
    )
    prodi_masuk = st.selectbox(
        "Program studi",
        PROGRAM_STUDI[jurusan_masuk],
        key=f"pilih_prodi_{jurusan_masuk}"
    )
    lanjut = st.button("Lanjutkan", use_container_width=True, type="primary")

    if lanjut:
        if not nama_masuk.strip() or not nim_masuk.strip():
            st.warning("Nama dan NIM harus diisi terlebih dahulu.")
        else:
            st.session_state["identitas_aktif"] = True
            st.session_state["nama_mahasiswa"] = nama_masuk.strip()
            st.session_state["nim_mahasiswa"] = nim_masuk.strip()
            st.session_state["jurusan_mahasiswa"] = jurusan_masuk
            st.session_state["prodi_mahasiswa"] = prodi_masuk
            st.rerun()


if not st.session_state.get("identitas_aktif", False):
    halaman_identitas()
    st.stop()


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown("""
    <div style="padding:20px 5px 15px 5px;">
        <div style="font-size:30px;">🎓</div>
        <div style="font-size:18px;font-weight:700;">
            BANK PENGALAMAN
        </div>
        <div style="font-size:12px;color:#C7D6E7;">
            DIGITAL MAHASISWA
        </div>
        <hr style="border-color:#49617D;">
        <div style="font-size:11px;font-weight:600;">
            SELURUH JURUSAN DAN PROGRAM STUDI
        </div>
        <div style="font-size:10px;color:#C7D6E7;">
            POLITEKNIK NEGERI MADIUN
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Navigasi")

    menu = st.radio(
        "Pilih halaman",
        [
            "Beranda",
            "Jelajahi Pengalaman",
            "Bagikan Pengalaman",
            "Upload Tugas",
            "Tips Praktikum",
            "Tentang Platform"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.markdown("### Identitas")
    st.write(st.session_state.get("nama_mahasiswa", ""))
    st.caption("NIM: " + st.session_state.get("nim_mahasiswa", ""))
    st.caption(st.session_state.get("jurusan_mahasiswa", ""))
    st.caption(st.session_state.get("prodi_mahasiswa", ""))

    if st.button("Keluar", use_container_width=True):
        st.session_state["identitas_aktif"] = False
        st.session_state.pop("nama_mahasiswa", None)
        st.session_state.pop("nim_mahasiswa", None)
        st.session_state.pop("jurusan_mahasiswa", None)
        st.session_state.pop("prodi_mahasiswa", None)
        st.rerun()

    st.markdown("---")

    st.caption("PROTOTIPE PLATFORM MAHASISWA")
    st.caption("Berbagi pengalaman, menyimpan pengetahuan.")


# ==========================================
# HEADER
# ==========================================

st.markdown("""
<div class="main-header">
    <div class="campus-label">
        POLITEKNIK NEGERI MADIUN
    </div>
    <h1>Bank Pengalaman Digital Mahasiswa</h1>
    <p>
        Seluruh Jurusan dan Program Studi |
        Ruang berbagi pengalaman dan referensi pembelajaran mahasiswa PNM.
    </p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# MENGAMBIL DATA
# ==========================================

data = ambil_data()

total_pengalaman = len(data)

if total_pengalaman > 0:
    total_kontributor = data["nama"].nunique()
    total_matkul = data["mata_kuliah"].nunique()
else:
    total_kontributor = 0
    total_matkul = 0


# ==========================================
# HALAMAN BERANDA
# ==========================================

if menu == "Beranda":

    st.markdown(
        '<div class="section-heading">Ringkasan Platform</div>',
        unsafe_allow_html=True
    )

    with koneksi_database() as conn:
        total_dokumen = conn.execute("SELECT COUNT(*) FROM dokumen_tugas").fetchone()[0]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">
                Total Pengalaman
            </div>
            <div class="metric-value">
                {total_pengalaman}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">
                Total Kontributor
            </div>
            <div class="metric-value">
                {total_kontributor}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Mata Kuliah</div>
            <div class="metric-value">{total_matkul}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Dokumen Tugas</div>
            <div class="metric-value">{total_dokumen}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-heading">Informasi Platform</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="content-box">
        <h4>Selamat Datang</h4>
        <p>
            Platform ini dikembangkan sebagai tempat
            penyimpanan pengalaman pembelajaran dan praktikum
            mahasiswa dari seluruh jurusan dan program studi PNM.
        </p>
        <p>
            Mahasiswa dapat memanfaatkan pengalaman
            dari angkatan sebelumnya sebagai referensi
            sebelum mengikuti kegiatan praktikum.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-heading">Pengalaman Terbaru</div>',
        unsafe_allow_html=True
    )

    if data.empty:
        st.info(
            "Belum ada pengalaman yang dibagikan. "
            "Jadilah kontributor pertama."
        )
    else:
        for _, item in data.head(3).iterrows():

            with st.container(border=True):
                st.subheader(item["judul"])
                st.caption(
                    f'{item["mata_kuliah"]} | '
                    f'Angkatan {item["angkatan"]} | '
                    f'{item["tanggal"]}'
                )
                st.write(item["pengalaman"][:250])

    st.markdown('<div class="section-heading">Dokumen Tugas Terbaru</div>', unsafe_allow_html=True)
    with koneksi_database() as conn:
        dokumen_terbaru = pd.read_sql_query("SELECT nama_tugas, mata_kuliah, jenis_tugas, tanggal FROM dokumen_tugas ORDER BY id DESC LIMIT 3", conn)
    if dokumen_terbaru.empty:
        st.caption("Belum ada dokumen tugas yang diunggah.")
    else:
        for _, doc in dokumen_terbaru.iterrows():
            with st.container(border=True):
                st.write(f"**{doc['nama_tugas']}**")
                st.caption(f"{doc['mata_kuliah']} | {doc['jenis_tugas']} | {doc['tanggal']}")


# ==========================================
# JELAJAHI PENGALAMAN
# ==========================================

elif menu == "Jelajahi Pengalaman":

    st.header("Jelajahi Pengalaman")

    st.write(
        "Cari pengalaman mahasiswa dari berbagai jurusan dan program studi "
        "berdasarkan jurusan, program studi, mata kuliah, atau topik."
    )

    pencarian = st.text_input(
        "Cari pengalaman",
        placeholder="Contoh: elektronika, praktikum..."
    )

    if not data.empty:
        hasil = data.copy()
        c0, c1, c2 = st.columns(3)
        with c0:
            opsi_jurusan = ["Semua jurusan"] + sorted(hasil["jurusan"].dropna().unique().tolist())
            pilih_jurusan = st.selectbox("Filter jurusan", opsi_jurusan)
        with c1:
            opsi_prodi = ["Semua program studi"] + sorted(hasil["program_studi"].dropna().unique().tolist())
            pilih_prodi = st.selectbox("Filter program studi", opsi_prodi)
        if pilih_jurusan != "Semua jurusan":
            hasil = hasil[hasil["jurusan"] == pilih_jurusan]
        if pilih_prodi != "Semua program studi":
            hasil = hasil[hasil["program_studi"] == pilih_prodi]
        with c2:
            opsi_matkul = ["Semua mata kuliah"] + sorted(hasil["mata_kuliah"].dropna().unique().tolist())
            pilih_matkul = st.selectbox("Filter mata kuliah", opsi_matkul)
        with c2:
            opsi_angkatan = ["Semua angkatan"] + sorted(hasil["angkatan"].dropna().astype(str).unique().tolist(), reverse=True)
            pilih_angkatan = st.selectbox("Filter angkatan", opsi_angkatan)
        if pilih_matkul != "Semua mata kuliah":
            hasil = hasil[hasil["mata_kuliah"] == pilih_matkul]
        if pilih_angkatan != "Semua angkatan":
            hasil = hasil[hasil["angkatan"].astype(str) == pilih_angkatan]

        if pencarian:
            kolom_cari = [
                "judul", "mata_kuliah",
                "pengalaman", "kendala",
                "solusi", "tips", "kategori"
            ]

            kondisi = pd.Series(
                False, index=hasil.index
            )

            for kolom in kolom_cari:
                kondisi |= hasil[kolom].fillna(
                    ""
                ).str.contains(
                    pencarian,
                    case=False,
                    regex=False
                )

            hasil = hasil[kondisi]

        st.caption(
            f"Ditemukan {len(hasil)} pengalaman."
        )

        if hasil.empty:
            st.warning("Pengalaman tidak ditemukan.")

        for _, item in hasil.iterrows():

            with st.container(border=True):

                st.subheader(item["judul"])

                st.caption(
                    f'{item["mata_kuliah"]} | '
                    f'{item["nama"]} | {item.get("program_studi", "Belum dipilih")} | '
                    f'Angkatan {item["angkatan"]} | '
                    f'Kategori: {item.get("kategori", "Umum")}'
                )

                st.write("**Pengalaman:**")
                st.write(item["pengalaman"])

                if item["kendala"]:
                    st.write("**Kendala:**")
                    st.write(item["kendala"])

                if item["solusi"]:
                    st.write("**Solusi:**")
                    st.write(item["solusi"])

                if item["tips"]:
                    st.info("Tips: " + item["tips"])

                # Diskusi dan komentar untuk pengalaman ini.
                daftar_komentar = ambil_komentar(item["id"])
                with st.expander(f"💬 Diskusi dan komentar ({len(daftar_komentar)})"):
                    if daftar_komentar:
                        for nama_komentar, isi_komentar, tanggal_komentar in daftar_komentar:
                            st.markdown(f"**{nama_komentar}** · {tanggal_komentar}")
                            st.write(isi_komentar)
                            st.divider()
                    else:
                        st.caption("Belum ada komentar. Jadilah yang pertama berdiskusi.")

                    with st.form(f"form_komentar_{int(item['id'])}", clear_on_submit=True):
                        isi_baru = st.text_area(
                            "Tulis komentar atau pertanyaan",
                            placeholder="Bagikan tanggapan, pertanyaan, atau tambahan informasi...",
                            key=f"isi_komentar_{int(item['id'])}",
                            max_chars=1000
                        )
                        kirim_komentar = st.form_submit_button(
                            "Kirim komentar", use_container_width=True
                        )
                        if kirim_komentar:
                            nama_aktif = st.session_state.get("nama_mahasiswa", "").strip()
                            if not nama_aktif:
                                st.warning("Silakan masuk kembali menggunakan identitas mahasiswa.")
                            elif not isi_baru.strip():
                                st.warning("Komentar tidak boleh kosong.")
                            else:
                                simpan_komentar(item["id"], nama_aktif, isi_baru)
                                st.success("Komentar berhasil ditambahkan.")
                                st.rerun()

                # Rating dan ulasan manfaat pengalaman.
                rata_rata, jumlah_rating = ambil_ringkasan_rating(item["id"])
                if jumlah_rating:
                    st.markdown(
                        f"**Penilaian mahasiswa:** ⭐ {rata_rata:.1f}/5 "
                        f"({jumlah_rating} penilaian)"
                    )
                else:
                    st.caption("Belum ada penilaian untuk pengalaman ini.")

                with st.expander("⭐ Beri rating dan ulasan"):
                    nim_aktif = st.session_state.get("nim_mahasiswa", "").strip()
                    with st.form(f"form_rating_{int(item['id'])}", clear_on_submit=True):
                        nilai_rating = st.select_slider(
                            "Seberapa bermanfaat pengalaman ini?",
                            options=[1, 2, 3, 4, 5],
                            value=5,
                            format_func=lambda x: f"{'⭐' * x} ({x}/5)"
                        )
                        ulasan_baru = st.text_area(
                            "Ulasan (opsional)",
                            placeholder="Ceritakan manfaat pengalaman ini bagi pembelajaran...",
                            max_chars=1000,
                            key=f"ulasan_rating_{int(item['id'])}"
                        )
                        kirim_rating = st.form_submit_button(
                            "Simpan penilaian", use_container_width=True
                        )
                        if kirim_rating:
                            if not nim_aktif:
                                st.warning("Silakan masuk kembali menggunakan identitas mahasiswa.")
                            elif str(item["nama"]).strip().lower() == st.session_state.get("nama_mahasiswa", "").strip().lower():
                                st.warning("Kamu tidak dapat menilai pengalaman yang kamu bagikan sendiri.")
                            else:
                                simpan_rating(
                                    item["id"], nim_aktif,
                                    st.session_state.get("nama_mahasiswa", ""),
                                    nilai_rating, ulasan_baru
                                )
                                st.success("Penilaian berhasil disimpan. Penilaian berikutnya akan memperbarui penilaianmu sebelumnya.")
                                st.rerun()

                    daftar_ulasan = ambil_ulasan_rating(item["id"])
                    if daftar_ulasan:
                        st.markdown("**Ulasan mahasiswa**")
                        for nama_penilai, nilai, isi_ulasan, tanggal_ulasan in daftar_ulasan:
                            st.markdown(f"**{nama_penilai}** · {'⭐' * nilai} · {tanggal_ulasan}")
                            st.write(isi_ulasan)
                            st.divider()

    else:
        st.info(
            "Belum ada data pengalaman yang tersedia."
        )


# ==========================================
# BAGIKAN PENGALAMAN
# ==========================================

elif menu == "Bagikan Pengalaman":

    st.header("Bagikan Pengalaman")

    st.write(
        "Bagikan pengalaman perkuliahan, praktikum, tugas, "
        "proyek, atau kegiatan akademik untuk mahasiswa PNM lainnya."
    )

    with st.form("form_pengalaman", clear_on_submit=True):

        st.text_input("Nama mahasiswa", value=st.session_state.get("nama_mahasiswa", ""), disabled=True)
        nama = st.session_state.get("nama_mahasiswa", "")

        angkatan = st.text_input(
            "Tahun angkatan",
            placeholder="Contoh: 2025"
        )

        mata_kuliah = st.text_input(
            "Nama mata kuliah"
        )

        kategori = st.selectbox(
            "Kategori pembelajaran",
            [
                "Administrasi Bisnis dan Pemasaran",
                "Akuntansi dan Perpajakan",
                "Bahasa Inggris",
                "Komputer dan Teknologi Informasi",
                "Elektronika dan Kelistrikan",
                "Otomotif dan Perkeretaapian",
                "Konstruksi dan Gambar Teknik",
                "Pemrograman dan Perangkat Lunak",
                "Keselamatan Kerja (K3)",
                "Umum/Lainnya"
            ]
        )

        judul = st.text_input(
            "Judul pengalaman"
        )

        pengalaman = st.text_area(
            "Ceritakan pengalaman praktikum",
            height=130
        )

        kendala = st.text_area(
            "Kendala yang pernah dihadapi",
            height=90
        )

        solusi = st.text_area(
            "Solusi atau cara mengatasi kendala",
            height=90
        )

        tips = st.text_area(
            "Pesan atau tips untuk angkatan berikutnya",
            height=90
        )

        kirim = st.form_submit_button(
            "Simpan Pengalaman",
            use_container_width=True
        )

        if kirim:

            if not all([
                nama.strip(),
                angkatan.strip(),
                mata_kuliah.strip(),
                judul.strip(),
                pengalaman.strip()
            ]):

                st.warning(
                    "Mohon lengkapi nama, angkatan, "
                    "mata kuliah, judul, dan pengalaman."
                )

            elif not angkatan.strip().isdigit():

                st.warning(
                    "Angkatan harus berupa angka tahun."
                )

            else:

                simpan_pengalaman(
                    nama.strip(),
                    st.session_state.get("jurusan_mahasiswa", "Belum dipilih"),
                    st.session_state.get("prodi_mahasiswa", "Belum dipilih"),
                    angkatan.strip(),
                    mata_kuliah.strip(),
                    judul.strip(),
                    pengalaman.strip(),
                    kendala.strip(),
                    solusi.strip(),
                    tips.strip(),
                    kategori
                )

                st.success(
                    "Pengalaman berhasil disimpan."
                )

                st.rerun()


# ==========================================
# UPLOAD KRITERIA DAN DOKUMEN TUGAS
# ==========================================

elif menu == "Upload Tugas":

    st.header("Upload Kriteria dan Dokumen Tugas")
    st.write(
        "Unggah dokumen tugas dan kelompokkan berdasarkan mata kuliah, "
        "angkatan, serta jenis tugas agar mudah ditemukan kembali."
    )

    with st.form("form_upload_tugas", clear_on_submit=True):
        st.text_input(
            "Nama mahasiswa",
            value=st.session_state.get("nama_mahasiswa", ""),
            disabled=True
        )
        st.text_input(
            "NIM",
            value=st.session_state.get("nim_mahasiswa", ""),
            disabled=True
        )
        st.text_input("Jurusan", value=st.session_state.get("jurusan_mahasiswa", ""), disabled=True)
        st.text_input("Program studi", value=st.session_state.get("prodi_mahasiswa", ""), disabled=True)
        angkatan_upload = st.text_input("Tahun angkatan", placeholder="Contoh: 2025")
        mata_kuliah_upload = st.text_input("Mata kuliah")
        jenis_tugas_upload = st.selectbox(
            "Jenis tugas",
            ["Tugas individu", "Tugas kelompok", "Laporan praktikum",
             "Proyek", "Presentasi", "Lainnya"]
        )
        nama_tugas = st.text_input("Nama/judul tugas")
        keterangan = st.text_area(
            "Keterangan tambahan (opsional)",
            placeholder="Contoh: tugas individu, dikumpulkan minggu ke-5..."
        )
        file_kriteria = st.file_uploader(
            "Upload file kriteria/instruksi tugas",
            type=["pdf", "doc", "docx"]
        )
        file_tugas = st.file_uploader(
            "Upload dokumen tugas",
            type=["pdf", "doc", "docx"]
        )
        simpan_upload = st.form_submit_button(
            "Simpan Dokumen", use_container_width=True
        )

    if simpan_upload:
        if (
            not angkatan_upload.strip()
            or not angkatan_upload.strip().isdigit()
            or not mata_kuliah_upload.strip()
            or not nama_tugas.strip()
        ):
            st.warning("Isi tahun angkatan dengan angka serta lengkapi mata kuliah dan nama tugas.")
        elif file_kriteria is None or file_tugas is None:
            st.warning("Silakan unggah file kriteria dan dokumen tugas.")
        else:
            folder_upload = "uploads"
            os.makedirs(folder_upload, exist_ok=True)

            ekstensi_kriteria = os.path.splitext(file_kriteria.name)[1].lower()
            ekstensi_tugas = os.path.splitext(file_tugas.name)[1].lower()
            nama_simpan_kriteria = str(uuid.uuid4()) + ekstensi_kriteria
            nama_simpan_tugas = str(uuid.uuid4()) + ekstensi_tugas
            lokasi_kriteria = os.path.join(folder_upload, nama_simpan_kriteria)
            lokasi_tugas = os.path.join(folder_upload, nama_simpan_tugas)

            with open(lokasi_kriteria, "wb") as file_simpan:
                file_simpan.write(file_kriteria.getbuffer())
            with open(lokasi_tugas, "wb") as file_simpan:
                file_simpan.write(file_tugas.getbuffer())

            with koneksi_database() as conn:
                conn.execute("""
                    INSERT INTO dokumen_tugas (
                        username, nim, jurusan, program_studi, angkatan, mata_kuliah, jenis_tugas,
                        nama_tugas, keterangan,
                        nama_file_kriteria, lokasi_file_kriteria,
                        nama_file_tugas, lokasi_file_tugas, tanggal
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    st.session_state.get("nama_mahasiswa", ""),
                    st.session_state.get("nim_mahasiswa", ""),
                    st.session_state.get("jurusan_mahasiswa", "Belum dipilih"),
                    st.session_state.get("prodi_mahasiswa", "Belum dipilih"),
                    angkatan_upload.strip(),
                    mata_kuliah_upload.strip(),
                    jenis_tugas_upload,
                    nama_tugas.strip(),
                    keterangan.strip(),
                    file_kriteria.name,
                    lokasi_kriteria,
                    file_tugas.name,
                    lokasi_tugas,
                    datetime.now().strftime("%Y-%m-%d")
                ))

            st.success("Kriteria dan dokumen tugas berhasil disimpan.")
            st.rerun()

    st.markdown("---")
    st.subheader("Arsip Dokumen Tugas")
    st.caption("Cari dokumen dan gunakan filter untuk menemukan referensi.")

    with koneksi_database() as conn:
        daftar_dokumen = pd.read_sql_query(
            "SELECT * FROM dokumen_tugas ORDER BY id DESC", conn
        )

    if daftar_dokumen.empty:
        st.info("Belum ada dokumen tugas yang diunggah.")
    else:
        for kolom, default in [("angkatan", ""), ("jenis_tugas", "Lainnya")]:
            if kolom not in daftar_dokumen.columns:
                daftar_dokumen[kolom] = default
            daftar_dokumen[kolom] = daftar_dokumen[kolom].fillna(default)

        metrik1, metrik2, metrik3 = st.columns(3)
        metrik1.metric("Total dokumen", len(daftar_dokumen))
        metrik2.metric("Mata kuliah", daftar_dokumen["mata_kuliah"].nunique())
        angkatan_terisi = daftar_dokumen["angkatan"].astype(str).str.strip() != ""
        metrik3.metric("Angkatan terdata", daftar_dokumen.loc[angkatan_terisi, "angkatan"].nunique())

        kata_kunci = st.text_input(
            "Cari dokumen",
            placeholder="Judul tugas, mata kuliah, atau nama pengunggah..."
        )
        daftar_matkul = ["Semua mata kuliah"] + sorted(
            daftar_dokumen["mata_kuliah"].dropna().unique().tolist()
        )
        daftar_angkatan = ["Semua angkatan"] + sorted(
            [str(x) for x in daftar_dokumen["angkatan"].unique() if str(x).strip()],
            reverse=True
        )
        daftar_jenis = ["Semua jenis tugas"] + sorted(
            daftar_dokumen["jenis_tugas"].dropna().unique().tolist()
        )

        f1, f2, f3 = st.columns(3)
        with f1:
            filter_matkul = st.selectbox("Filter mata kuliah", daftar_matkul)
        with f2:
            filter_angkatan = st.selectbox("Filter angkatan", daftar_angkatan)
        with f3:
            filter_jenis = st.selectbox("Filter jenis tugas", daftar_jenis)

        hasil = daftar_dokumen.copy()
        if kata_kunci.strip():
            cocok = pd.Series(False, index=hasil.index)
            for kolom in ["nama_tugas", "mata_kuliah", "username", "keterangan"]:
                cocok |= hasil[kolom].fillna("").astype(str).str.contains(
                    kata_kunci.strip(), case=False, regex=False
                )
            hasil = hasil[cocok]
        if filter_matkul != "Semua mata kuliah":
            hasil = hasil[hasil["mata_kuliah"] == filter_matkul]
        if filter_angkatan != "Semua angkatan":
            hasil = hasil[hasil["angkatan"].astype(str) == filter_angkatan]
        if filter_jenis != "Semua jenis tugas":
            hasil = hasil[hasil["jenis_tugas"] == filter_jenis]

        st.caption(f"Menampilkan {len(hasil)} dari {len(daftar_dokumen)} dokumen.")
        if hasil.empty:
            st.warning("Dokumen tidak ditemukan. Coba ubah kata kunci atau filter.")
        else:
            for _, dokumen in hasil.iterrows():
                with st.container(border=True):
                    st.subheader(dokumen["nama_tugas"])
                    st.caption(
                        f'{dokumen["mata_kuliah"]} | {dokumen["jenis_tugas"]} | '
                        f'Angkatan {dokumen["angkatan"] or "Belum diisi"}'
                    )
                    st.write(
                        f'**Pengunggah:** {dokumen["username"]} | '
                        f'**Tanggal:** {dokumen["tanggal"]}'
                    )
                    if dokumen["keterangan"]:
                        st.write(dokumen["keterangan"])

                    kolom_kriteria, kolom_tugas = st.columns(2)
                    with kolom_kriteria:
                        if os.path.exists(dokumen["lokasi_file_kriteria"]):
                            with open(dokumen["lokasi_file_kriteria"], "rb") as f:
                                st.download_button(
                                    "Unduh Kriteria", data=f.read(),
                                    file_name=dokumen["nama_file_kriteria"],
                                    key=f'kriteria_{dokumen["id"]}',
                                    use_container_width=True
                                )
                        else:
                            st.caption("File kriteria tidak ditemukan.")
                    with kolom_tugas:
                        if os.path.exists(dokumen["lokasi_file_tugas"]):
                            with open(dokumen["lokasi_file_tugas"], "rb") as f:
                                st.download_button(
                                    "Unduh Dokumen Tugas", data=f.read(),
                                    file_name=dokumen["nama_file_tugas"],
                                    key=f'tugas_{dokumen["id"]}',
                                    use_container_width=True
                                )
                        else:
                            st.caption("File tugas tidak ditemukan.")


# ==========================================
# TIPS PRAKTIKUM
# ==========================================

elif menu == "Tips Praktikum":

    st.header("Tips Praktikum")

    st.write(
        "Kumpulan solusi dan saran berdasarkan "
        "pengalaman mahasiswa."
    )

    if not data.empty:

        tips_data = data[
            data["tips"].fillna("").str.strip() != ""
        ]

        if tips_data.empty:
            st.info(
                "Belum ada tips praktikum yang dibagikan."
            )

        else:

            for _, item in tips_data.iterrows():

                with st.container(border=True):

                    st.subheader(item["mata_kuliah"])

                    st.write(item["tips"])

                    st.caption(
                        f'Sumber: {item["nama"]} | '
                        f'Angkatan {item["angkatan"]}'
                    )

    else:
        st.info(
            "Belum ada tips praktikum yang tersedia."
        )


# ==========================================
# TENTANG PLATFORM
# ==========================================

elif menu == "Tentang Platform":

    st.header("Tentang Platform")

    st.write(
        "Bank Pengalaman Digital Mahasiswa merupakan "
        "gagasan platform berbagi pengetahuan "
        "antargenerasi mahasiswa."
    )

    st.subheader("Latar Belakang")

    st.write(
        "Informasi mengenai praktikum, kendala "
        "pembelajaran, dan pengalaman mahasiswa "
        "sering kali hanya disampaikan secara lisan. "
        "Akibatnya, mahasiswa angkatan berikutnya "
        "dapat mengalami kesulitan memperoleh "
        "referensi dari pengalaman sebelumnya."
    )

    st.subheader("Tujuan")

    st.write(
        "Mendokumentasikan pengalaman mahasiswa "
        "agar dapat dimanfaatkan sebagai sumber "
        "informasi dan pembelajaran berkelanjutan."
    )

    st.info(
        "Platform ini merupakan prototipe pengembangan "
        "mahasiswa, bukan portal resmi Politeknik Negeri Madiun. "
        "Jangan mengunggah data pribadi atau dokumen yang bersifat rahasia."
    )


# ==========================================
# FOOTER
# ==========================================

st.markdown("""
<div class="footer">
    Bank Pengalaman Digital Mahasiswa<br>
    Seluruh Jurusan dan Program Studi<br>
    Politeknik Negeri Madiun<br><br>
    Prototipe pengembangan platform pembelajaran mahasiswa
</div>
""", unsafe_allow_html=True)
