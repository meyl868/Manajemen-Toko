# app.py - Aplikasi Manajemen Toko
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Manajemen Toko", layout="wide")
st.title("🏪 Manajemen Toko")

# Inisialisasi session state
if "produk" not in st.session_state:
    st.session_state.produk = []
if "transaksi" not in st.session_state:
    st.session_state.transaksi = []
if "id_counter" not in st.session_state:
    st.session_state.id_counter = 1

# ── Sidebar: Statistik ─────────────────────────────────────────────────────────
st.sidebar.header("📊 Statistik")
total_produk = len(st.session_state.produk)
total_stok = sum(p["stok"] for p in st.session_state.produk)
total_pendapatan = sum(t["total"] for t in st.session_state.transaksi)
total_transaksi = len(st.session_state.transaksi)

st.sidebar.metric("Total Produk", total_produk)
st.sidebar.metric("Total Stok", total_stok)
st.sidebar.metric("Pendapatan", f"Rp {total_pendapatan:,.0f}")
st.sidebar.metric("Jumlah Transaksi", total_transaksi)

stok_tipis = [p for p in st.session_state.produk if p["stok"] <= 5]
if stok_tipis:
    st.sidebar.warning(f"⚠️ {len(stok_tipis)} produk stok menipis!")
    for p in stok_tipis:
        st.sidebar.write(f"- {p['nama']} (stok: {p['stok']})")

# ── Tab utama ──────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📦 Produk", "💰 Transaksi", "📋 Riwayat"])

# ── TAB 1: Produk ──────────────────────────────────────────────────────────────
with tab1:
    st.subheader("Tambah Produk Baru")
    with st.form("form_produk"):
        col1, col2 = st.columns(2)
        with col1:
            nama = st.text_input("Nama Produk")
            kategori = st.selectbox("Kategori", ["Pakaian", "Makanan", "Elektronik", "Lainnya"])
        with col2:
            harga = st.number_input("Harga (Rp)", min_value=0, step=500)
            stok = st.number_input("Stok", min_value=0, step=1)
        submitted = st.form_submit_button("➕ Tambah Produk")
        if submitted:
            if not nama:
                st.error("Nama produk tidak boleh kosong!")
            else:
                st.session_state.produk.append({
                    "id": st.session_state.id_counter,
                    "nama": nama,
                    "kategori": kategori,
                    "harga": harga,
                    "stok": stok,
                })
                st.session_state.id_counter += 1
                st.success(f"✅ Produk '{nama}' berhasil ditambahkan!")
                st.rerun()

    st.divider()
    st.subheader("🗂️ Daftar Produk")

    if not st.session_state.produk:
        st.info("Belum ada produk. Tambahkan produk di atas.")
    else:
        for i, p in enumerate(st.session_state.produk):
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
            with col1:
                st.write(f"**{p['nama']}**")
                st.caption(p["kategori"])
            with col2:
                st.write(f"Rp {p['harga']:,.0f}")
            with col3:
                if p["stok"] > 10:
                    st.success(f"Stok: {p['stok']}")
                elif p["stok"] > 3:
                    st.warning(f"Stok: {p['stok']}")
                else:
                    st.error(f"Stok: {p['stok']}")
            with col4:
                new_stok = st.number_input(
                    "Update stok", value=p["stok"], min_value=0,
                    key=f"stok_{p['id']}", label_visibility="collapsed"
                )
                if new_stok != p["stok"]:
                    st.session_state.produk[i]["stok"] = new_stok
                    st.rerun()
            with col5:
                if st.button("🗑️", key=f"del_{p['id']}"):
                    st.session_state.produk.pop(i)
                    st.rerun()

# ── TAB 2: Transaksi ───────────────────────────────────────────────────────────
with tab2:
    st.subheader("Catat Penjualan")

    produk_tersedia = [p for p in st.session_state.produk if p["stok"] > 0]

    if not produk_tersedia:
        st.warning("Tidak ada produk tersedia. Tambahkan produk di tab Produk.")
    else:
        with st.form("form_transaksi"):
            col1, col2 = st.columns([3, 1])
            with col1:
                pilihan = st.selectbox(
                    "Pilih Produk",
                    options=produk_tersedia,
                    format_func=lambda p: f"{p['nama']} — Rp {p['harga']:,.0f} (stok: {p['stok']})"
                )
            with col2:
                qty = st.number_input("Jumlah", min_value=1, max_value=pilihan["stok"], step=1)

            total = pilihan["harga"] * qty
            st.info(f"💵 Total: **Rp {total:,.0f}**")

            jual = st.form_submit_button("💰 Catat Penjualan")
            if jual:
                # Kurangi stok
                for p in st.session_state.produk:
                    if p["id"] == pilihan["id"]:
                        p["stok"] -= qty
                        break
                # Simpan transaksi
                st.session_state.transaksi.append({
                    "nama": pilihan["nama"],
                    "qty": qty,
                    "harga_satuan": pilihan["harga"],
                    "total": total,
                    "waktu": datetime.now().strftime("%d/%m/%Y %H:%M"),
                })
                st.success(f"✅ Terjual {qty}x {pilihan['nama']} — Rp {total:,.0f}")
                st.rerun()

# ── TAB 3: Riwayat ─────────────────────────────────────────────────────────────
with tab3:
    st.subheader("📋 Riwayat Transaksi")

    if not st.session_state.transaksi:
        st.info("Belum ada transaksi.")
    else:
        # Tampilkan terbaru di atas
        for t in reversed(st.session_state.transaksi):
            col1, col2, col3 = st.columns([4, 2, 2])
            with col1:
                st.write(f"**{t['nama']}**")
                st.caption(f"{t['waktu']} · {t['qty']} pcs @ Rp {t['harga_satuan']:,.0f}")
            with col2:
                st.write(f"Rp {t['total']:,.0f}")
            with col3:
                st.caption("✅ Selesai")

        st.divider()
        st.write(f"**Total Pendapatan: Rp {total_pendapatan:,.0f}**")

        if st.button("🗑️ Hapus Semua Riwayat"):
            st.session_state.transaksi = []
            st.rerun()
