import streamlit as st

# Sayfa ayarları
st.set_page_config(page_title="Mockup Motoru", layout="wide")

st.title("👕 Otomatik Mockup Giydirme Sistemi")
st.write("Tebrikler! Sistem başarıyla kuruldu ve yayında.")
st.write("Google Drive ve E-Tablolar entegrasyonu için arka plan hazır.")

# Geçici bir tasarım yükleme alanı (Önizleme amaçlı)
yuklenen_tasarim = st.file_uploader("Tasarımınızı (PNG) Yükleyin", type=["png"])

if yuklenen_tasarim is not None:
    st.success("Görsel başarıyla sisteme alındı! (Birleştirme motoru eklenecek)")