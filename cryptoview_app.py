import streamlit as st
import requests
import plotly.graph_objects as go
import time

# Set judul
st.title("📊 Crypto Dashboard")

# API di sini
@st.cache_data
def get_top_cryptos():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 10, "page": 1}
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, params=params, headers=headers)

        # Memastikan keberhasilan api
        if response.status_code != 200:
            st.error(f"❌ Gagal mengambil data dari API CoinGecko (Status Code: {response.status_code})")
            return []

        data = response.json()

        # Memastikan respon yang diambil dalam bentuk list
        if not isinstance(data, list):
            st.error("⚠️ Data dari API tidak dalam format yang diharapkan.")
            return []

        return data

    except Exception as e:
        st.error(f"🚨 Terjadi error saat mengambil data: {e}")
        return []

cryptos = get_top_cryptos()
## Debugging respon api
# st.write("🔍 Debugging API Response:", cryptos)

# Memastikan data crypto pada api tersedia
if not cryptos:
    st.error("❌ Data crypto tidak tersedia. Coba periksa koneksi atau API limit.")
    crypto_options = {}
    st.stop()
else:
    crypto_options = {crypto["name"]: crypto["id"] for crypto in cryptos}

# Fungsi memilih crypto
selected_crypto = st.selectbox("Pilih Cryptocurrency:", list(crypto_options.keys()))
crypto_id = crypto_options[selected_crypto]

# Fungsi memilih rentang waktu pada chart
time_ranges = {
    "1 Hari": 1,
    "3 Hari": 3,
    "7 Hari": 7,
    "1 Bulan": 30,
    "3 Bulan": 90,
    "6 Bulan": 180,
    "1 Tahun": 365
}
selected_range = st.selectbox("Pilih Rentang Waktu:", list(time_ranges.keys()))
days = time_ranges[selected_range]

def get_crypto_data(crypto_id):
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            st.error(f"❌ Gagal mengambil data harga crypto (Status Code: {response.status_code})")
            return None
        return response.json()
    except Exception as e:
        st.error(f"🚨 Terjadi error saat mengambil data harga: {e}")
        return None

crypto_data = get_crypto_data(crypto_id)

# Menampilkan informasi crypto
st.subheader(f"💰 Informasi {selected_crypto}")
selected_crypto_info = next((c for c in cryptos if c["id"] == crypto_id), None)

if selected_crypto_info:
    st.write(f"**Harga Saat Ini:** ${selected_crypto_info['current_price']}")
    st.write(f"**Kapitalisasi Pasar:** ${selected_crypto_info['market_cap']:,}")
    st.write(f"**Volume 24 Jam:** ${selected_crypto_info['total_volume']:,}")

    image_url = selected_crypto_info["image"]
    st.image(image_url, width=80)

# Mengecek apakah data harga tersedia
if crypto_data:
    # Menampilkan grafik crypto
    st.subheader(f"📈 Grafik Harga {days} Terakhir")
    prices = [entry[1] for entry in crypto_data["prices"]]
    timestamps = [entry[0] for entry in crypto_data["prices"]]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=timestamps, y=prices, mode="lines", name="Harga"))
    st.plotly_chart(fig)

# Auto-refresh setiap beberapa detik
# refresh_time = st.sidebar.slider("Auto-refresh setiap (detik):", 10, 60, 30)
# st.sidebar.text(f"Refresh otomatis setiap {refresh_time} detik.")
refresh_time=30
time.sleep(refresh_time)
st.rerun()
