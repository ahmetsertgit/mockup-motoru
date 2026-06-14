import streamlit as st
from googleapiclient.http import MediaIoBaseUpload
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from PIL import Image
import io
import zipfile

# Google Servis Yetkilendirme
@st.cache_resource
def get_services():
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], 
                                                 scopes=['https://www.googleapis.com/auth/spreadsheets', 
                                                         'https://www.googleapis.com/auth/drive'])
    return gspread.authorize(creds), build('drive', 'v3', credentials=creds)

sheets_client, drive_service = get_services()

st.title("👕 Profesyonel Mockup Üretim Hattı")

# Verileri çek
tablo = sheets_client.open("Mockup_Veritabani").worksheet("Sayfa1")
veriler = tablo.get_all_records()

# 1. Arayüz: Tasarım Yükleme ve Önizleme
yuklenen_tasarim = st.file_uploader("Tasarımınızı (PNG) Yükleyin", type=["png"])
if yuklenen_tasarim:
    st.image(yuklenen_tasarim, caption="Yüklenen Tasarım", width=200) # Küçük boyutlu önizleme

kategori = st.selectbox("Kategori Seçin", list(set([s["kategori"] for s in veriler])))

if yuklenen_tasarim and st.button("Üretime Başla"):
    tasarim = Image.open(yuklenen_tasarim).convert("RGBA")
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
        for satir in veriler:
            if satir["kategori"] == kategori:
                # Mockup indir
                request = drive_service.files().get_media(fileId=satir["drive_file_id"])
                mockup = Image.open(io.BytesIO(request.execute())).convert("RGBA")
                
                # Birleştirme
                tasarim_resized = tasarim.resize((satir["genislik"], satir["yukseklik"]), Image.Resampling.LANCZOS)
                mockup.paste(tasarim_resized, (satir["x_noktasi"], satir["y_noktasi"]), tasarim_resized)
                
                # Kaydet (Buffer'a)
                img_byte_arr = io.BytesIO()
                mockup.save(img_byte_arr, format="PNG")
                
                # Zip'e ekle
                zip_file.writestr(f"{satir['mockup_id']}_cikti.png", img_byte_arr.getvalue())

                # Bellekteki görseli Drive'a uygun formata çevir
                media = MediaIoBaseUpload(io.BytesIO(img_byte_arr.getvalue()), mimetype='image/png')
                
                # Dosyayı yükle
                drive_service.files().create(
                    body={
                        'name': f"{satir['mockup_id']}_cikti.png", 
                        'parents': ['1u43nbgsfcXoMGkbWAYYxdd9Yw4bUsZOz']
                    },
                    media_body=media
                ).execute()
                

                
                st.write(f"✅ {satir['mockup_id']} hazırlandı.")
                st.image(mockup, caption=satir['mockup_id'], width=300) # Daha küçük görseller

    # 3 & 4. Toplu İndirme
    st.download_button("Tümünü ZIP Olarak İndir", zip_buffer.getvalue(), "mockuplar.zip", "application/zip")
