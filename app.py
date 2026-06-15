import streamlit as st
from streamlit_oauth import OAuth2Component
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import gspread
from PIL import Image
import io
import zipfile

# --- OAUTH VE SABİT AYARLAR ---
CLIENT_ID = st.secrets["oauth"]["client_id"]
CLIENT_SECRET = st.secrets["oauth"]["client_secret"]
REDIRECT_URI = "https://mockup-motoru-vxkujsyi98kigjm5yyov5h.streamlit.app/"

AUTHORIZE_ENDPOINT = 'https://accounts.google.com/o/oauth2/v2/auth'
TOKEN_ENDPOINT = 'https://oauth2.googleapis.com/token'
REVOKE_ENDPOINT = 'https://oauth2.googleapis.com/revoke'

# Sizin ilettiğiniz sabit ID'ler
TABLO_ID = "1KfloezbAz2saj3RKVoD6geVS9_wqefjjshWwMN0N-eY"
CIKTI_KLASOR_ID = "1u43nbgsfcXoMGkbWAYYxdd9Yw4bUsZOz"

oauth = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_ENDPOINT, TOKEN_ENDPOINT, REVOKE_ENDPOINT)

# --- GİRİŞ EKRANI ---
if 'token' not in st.session_state:
    st.set_page_config(page_title="Mockup Motoru", page_icon="👕")
    st.title("👕 Otomatik Mockup Üretim Hattı")
    st.warning("Devam etmek için Drive hesabınızla giriş yapın.")
    
    result = oauth.authorize_button(
        name="Google ile Giriş Yap",
        icon="https://www.google.com/favicon.ico",
        redirect_uri=REDIRECT_URI,
        scope="https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/spreadsheets",
    )
    if result:
        st.session_state.token = result
        st.rerun()

# --- ANA UYGULAMA ---
else:
    st.title("👕 Otomatik Mockup Üretim Hattı")
    
    # Kullanıcı yetkilerini başlat
    user_creds = Credentials(token=st.session_state.token['access_token'])
    drive_service = build('drive', 'v3', credentials=user_creds)
    sheets_client = gspread.authorize(user_creds)
    
    st.sidebar.success("✅ Google Hesabınız Aktif")
    if st.sidebar.button("Çıkış Yap"):
        del st.session_state.token
        st.rerun()

    # E-Tablo'dan verileri çek
    try:
        # İsme göre değil, doğrudan sizin verdiğiniz ID'ye göre tabloyu açar
        tablo = sheets_client.open_by_key(TABLO_ID).get_worksheet(0)
        veriler = tablo.get_all_records()
        kategoriler = list(set([satir["kategori"] for satir in veriler if "kategori" in satir]))
    except Exception as e:
        st.error(f"E-Tablo okunamadı! Hata: {e}")
        veriler = []
        kategoriler = []
        
    if veriler:
        yuklenen_tasarim = st.file_uploader("Tasarımınızı (PNG) Yükleyin", type=["png"])
        if yuklenen_tasarim:
            st.image(yuklenen_tasarim, caption="Yüklenen Tasarım", width=250)

        kategori = st.selectbox("Mockup Kategorisi Seçin", kategoriler)

        if yuklenen_tasarim and st.button("Üretime Başla"):
            tasarim = Image.open(yuklenen_tasarim).convert("RGBA")
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
                for satir in veriler:
                    if satir.get("kategori") == kategori:
                        try:
                            # 1. Drive'dan boş mockup'ı indir
                            request = drive_service.files().get_media(fileId=satir["drive_file_id"])
                            mockup = Image.open(io.BytesIO(request.execute())).convert("RGBA")
                            
                            # 2. Tasarımı boyutlandır ve yerleştir
                            tasarim_resized = tasarim.resize((satir["genislik"], satir["yukseklik"]), Image.Resampling.LANCZOS)
                            mockup.paste(tasarim_resized, (satir["x_noktasi"], satir["y_noktasi"]), tasarim_resized)
                            
                            # 3. Geçici belleğe kaydet
                            img_byte_arr = io.BytesIO()
                            mockup.save(img_byte_arr, format="PNG")
                            
                            # 4. ZIP dosyasına ekle
                            zip_file.writestr(f"{satir['mockup_id']}_cikti.png", img_byte_arr.getvalue())
                            
                            # 5. Dolu Mockup Klasörüne (Drive) Yükle
                            media = MediaIoBaseUpload(io.BytesIO(img_byte_arr.getvalue()), mimetype='image/png')
                            drive_service.files().create(
                                body={
                                    'name': f"{satir['mockup_id']}_cikti.png", 
                                    'parents': [CIKTI_KLASOR_ID] 
                                },
                                media_body=media
                            ).execute()
                            
                            st.success(f"✅ {satir['mockup_id']} işlendi ve Drive'a kaydedildi.")
                            
                        except Exception as e:
                            st.error(f"❌ {satir['mockup_id']} işlenirken hata: {e}")

            # Tüm işlemler bitince toplu indirme butonu
            st.download_button(
                label="📦 Tümünü ZIP Olarak İndir", 
                data=zip_buffer.getvalue(), 
                file_name="mockuplar_cikti.zip", 
                mime="application/zip"
            )
