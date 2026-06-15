import streamlit as st
from streamlit_oauth import OAuth2Component
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import gspread
from PIL import Image
import io
import zipfile

# 1. OAuth Ayarları (Secrets'tan güvenli çekim)
CLIENT_ID = st.secrets["oauth"]["client_id"]
CLIENT_SECRET = st.secrets["oauth"]["client_secret"]
AUTHORIZE_ENDPOINT = 'https://accounts.google.com/o/oauth2/v2/auth'
TOKEN_ENDPOINT = 'https://oauth2.googleapis.com/token'
REVOKE_ENDPOINT = 'https://oauth2.googleapis.com/revoke'

# DİKKAT: Buradaki link ile Google Cloud paneline yazdığınız link BİREBİR aynı olmalı
REDIRECT_URI = "https://mockup-motoru-vxkujsyi98kigjm5yyov5h.streamlit.app/"

oauth = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_ENDPOINT, TOKEN_ENDPOINT, REVOKE_ENDPOINT)

# 2. Giriş Kontrolü
if 'token' not in st.session_state:
    st.title("👕 Tam Bağımsız Mockup Motoru")
    st.write("Lütfen kendi Google Drive hesabınızla giriş yapın. Tablo ve görseller bu hesaptan çekilecektir.")
    
    result = oauth.authorize_button(
        name="Google ile Giriş Yap",
        icon="https://www.google.com/favicon.ico",
        redirect_uri=REDIRECT_URI,
        # Kapsama E-Tablolar (spreadsheets) yetkisi de eklendi
        scope="https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/spreadsheets",
    )
    if result:
        st.session_state.token = result
        st.rerun()
else:
    # Kullanıcı başarıyla giriş yaptı
    st.title("👕 Profesyonel Mockup Üretim Hattı")
    
    # Giriş yapan kullanıcının kimlik bilgileri (Token)
    user_creds = Credentials(token=st.session_state.token['access_token'])
    
    # Drive ve Sheets servislerini DOĞRUDAN GİRİŞ YAPAN KULLANICI İÇİN başlat
    user_drive_service = build('drive', 'v3', credentials=user_creds)
    sheets_client = gspread.authorize(user_creds)
    
    st.sidebar.success("Kendi Drive ve E-Tablo Hesabınız Aktif!")
    if st.sidebar.button("Çıkış Yap / Hesap Değiştir"):
        del st.session_state.token
        st.rerun()

    # KULLANICININ KENDİ E-TABLOSUNU ÇEK (Kişisel Drive'ında "Mockup_Veritabani" adlı tabloyu arar)
    try:
        tablo = sheets_client.open("Mockup_Veritabani").worksheet("Sayfa1")
        veriler = tablo.get_all_records()
        kategoriler = list(set([satir["kategori"] for satir in veriler]))
    except Exception as e:
        st.error(f"E-Tablo bulunamadı! Lütfen giriş yaptığınız hesapta 'Mockup_Veritabani' adında bir tablonuz olduğundan emin olun. (Hata Detayı: {e})")
        veriler = []
        kategoriler = []
        
    if veriler:
        yuklenen_tasarim = st.file_uploader("Tasarımınızı (PNG) Yükleyin", type=["png"])
        if yuklenen_tasarim:
            st.image(yuklenen_tasarim, caption="Yüklenen Tasarım", width=200)

        kategori = st.selectbox("Kategori Seçin", kategoriler)

        if yuklenen_tasarim and st.button("Üretime Başla"):
            tasarim = Image.open(yuklenen_tasarim).convert("RGBA")
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
                for satir in veriler:
                    if satir["kategori"] == kategori:
                        try:
                            # İndirme İşlemi
                            request = user_drive_service.files().get_media(fileId=satir["drive_file_id"])
                            mockup = Image.open(io.BytesIO(request.execute())).convert("RGBA")
                            
                            # Birleştirme İşlemi
                            tasarim_resized = tasarim.resize((satir["genislik"], satir["yukseklik"]), Image.Resampling.LANCZOS)
                            mockup.paste(tasarim_resized, (satir["x_noktasi"], satir["y_noktasi"]), tasarim_resized)
                            
                            # Geçici Belleğe Kaydet
                            img_byte_arr = io.BytesIO()
                            mockup.save(img_byte_arr, format="PNG")
                            
                            # ZIP paketine ekle
                            zip_file.writestr(f"{satir['mockup_id']}_cikti.png", img_byte_arr.getvalue())
                            
                            # KULLANICININ KENDİ DRIVE'INA YÜKLE
                            # Önemli: Eğer çıktıların belirli bir klasöre gitmesini istiyorsanız, 
                            # o klasörün ID'sini aşağıdaki '# parents' satırının başındaki '#' işaretini kaldırarak yazın.
                            # Klasör belirtmezseniz Drive ana dizinine (Ana Ekran) yükler.
                            media = MediaIoBaseUpload(io.BytesIO(img_byte_arr.getvalue()), mimetype='image/png')
                            user_drive_service.files().create(
                                body={
                                    'name': f"{satir['mockup_id']}_cikti.png", 
                                    # 'parents': ['KENDI_HESABINIZDAKI_KLASOR_ID'] 
                                },
                                media_body=media
                            ).execute()
                            
                            st.write(f"✅ {satir['mockup_id']} işlendi ve Drive'a yüklendi.")
                            st.image(mockup, caption=satir['mockup_id'], width=200)
                            
                        except Exception as e:
                            st.error(f"❌ {satir['mockup_id']} işlenirken hata oluştu. Drive ID'lerini kontrol edin: {e}")

            st.download_button("Tümünü ZIP Olarak İndir", zip_buffer.getvalue(), "mockuplar.zip", "application/zip")
