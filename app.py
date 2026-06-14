import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from PIL import Image
import io

# Sayfa ayarları
st.set_page_config(page_title="Print On Demand Mockup Motoru", layout="wide")
st.title("👕 Otomatik Mockup Giydirme Sistemi")

# Google Bağlantıları
@st.cache_resource
def get_services():
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], 
                                                 scopes=['https://www.googleapis.com/auth/spreadsheets', 
                                                         'https://www.googleapis.com/auth/drive.readonly'])
    sheets_client = gspread.authorize(creds)
    drive_service = build('drive', 'v3', credentials=creds)
    return sheets_client, drive_service

sheets_client, drive_service = get_services()

# Google Drive'dan görseli indirme fonksiyonu
def drive_gorsel_indir(file_id):
    request = drive_service.files().get_media(fileId=file_id)
    file_content = io.BytesIO(request.execute())
    return Image.open(file_content).convert("RGBA")

# Arayüz
tablo = sheets_client.open("Mockup_Veritabani").worksheet("Sayfa1")
veriler = tablo.get_all_records()
kategoriler = list(set([satir["kategori"] for satir in veriler]))

kategori_secimi = st.selectbox("Kategori Seçin", kategoriler)
yuklenen_tasarim = st.file_uploader("Tasarım (PNG)", type=["png"])

if yuklenen_tasarim and st.button("Üretime Başla"):
    tasarim = Image.open(yuklenen_tasarim).convert("RGBA")
    
    for satir in veriler:
        if satir["kategori"] == kategori_secimi:
            with st.spinner(f"{satir['mockup_id']} işleniyor..."):
                # Mockup'ı Drive'dan çek
                mockup = drive_gorsel_indir(satir["drive_file_id"])
                
                # Tasarımı boyutlandır ve yapıştır
                tasarim_resized = tasarim.resize((satir["genislik"], satir["yukseklik"]), Image.Resampling.LANCZOS)
                mockup.paste(tasarim_resized, (satir["x_noktasi"], satir["y_noktasi"]), tasarim_resized)
                
                # Sonucu göster
                st.image(mockup, caption=f"Sonuç: {satir['mockup_id']}", use_container_width=True)
                
                # İndirme butonu
                buf = io.BytesIO()
                mockup.save(buf, format="PNG")
                st.download_button(f"{satir['mockup_id']} İndir", buf.getvalue(), f"{satir['mockup_id']}.png", "image/png")
