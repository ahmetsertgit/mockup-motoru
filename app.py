import streamlit as st
from streamlit_oauth import OAuth2Component
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import gspread
from PIL import Image
import io
import zipfile
from streamlit_cropper import st_cropper

# --- OAUTH VE SABİT AYARLAR ---
CLIENT_ID = st.secrets["oauth"]["client_id"]
CLIENT_SECRET = st.secrets["oauth"]["client_secret"]
REDIRECT_URI = "https://mockup-motoru-vxkujsyi98kigjm5yyov5h.streamlit.app/"

AUTHORIZE_ENDPOINT = 'https://accounts.google.com/o/oauth2/v2/auth'
TOKEN_ENDPOINT = 'https://oauth2.googleapis.com/token'
REVOKE_ENDPOINT = 'https://oauth2.googleapis.com/revoke'

TABLO_ID = "1KfloezbAz2saj3RKVoD6geVS9_wqefjjshWwMN0N-eY"
CIKTI_KLASOR_ID = "1u43nbgsfcXoMGkbWAYYxdd9Yw4bUsZOz"

oauth = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_ENDPOINT, TOKEN_ENDPOINT, REVOKE_ENDPOINT)

# --- GİRİŞ EKRANI ---
if 'token' not in st.session_state:
    st.set_page_config(page_title="Mockup Motoru", page_icon="👕", layout="wide")
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
    
    # Token verisini güvenli şekilde çek
    token_verisi = st.session_state.token
    gecerli_token = None
    
    if isinstance(token_verisi, dict):
        if "access_token" in token_verisi:
            gecerli_token = token_verisi["access_token"]
        elif "token" in token_verisi and isinstance(token_verisi["token"], dict):
            gecerli_token = token_verisi["token"].get("access_token")
        elif "token" in token_verisi and isinstance(token_verisi["token"], str):
            gecerli_token = token_verisi["token"]
            
    if not gecerli_token:
        st.error("Yetki verisi (Token) okunamadı. Lütfen aşağıdaki butona basarak önbelleği temizleyin ve yeniden giriş yapın.")
        if st.button("Sistemi Sıfırla ve Yeniden Başlat"):
            del st.session_state.token
            st.rerun()
        st.stop()
        
    # Güvenli token ile kullanıcı yetkilerini başlat
    user_creds = Credentials(token=gecerli_token)
    drive_service = build('drive', 'v3', credentials=user_creds)
    sheets_client = gspread.authorize(user_creds)
    
    st.sidebar.success("✅ Google Hesabınız Aktif")
    if st.sidebar.button("Çıkış Yap / Önbelleği Temizle"):
        del st.session_state.token
        st.rerun()

    # --- SEKMELİ YAPI (ANA KOD VE KOORDİNAT ARACI) ---
    tab1, tab2 = st.tabs(["👕 Üretim Hattı", "📐 Koordinat Bulucu"])

    # 1. SEKME: SENİN ORİJİNAL ÜRETİM HATTI KODUN
    with tab1:
        try:
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

                st.download_button(
                    label="📦 Tümünü ZIP Olarak İndir", 
                    data=zip_buffer.getvalue(), 
                    file_name="mockuplar_cikti.zip", 
                    mime="application/zip"
                )

    # 2. SEKME: YENİ KOORDİNAT BULUCU (Ana kodu etkilemez)
    with tab2:
        st.subheader("Mockup Üzerinde Tasarım Alanı Belirle")
        st.write("E-Tabloya gireceğiniz X, Y, Genişlik ve Yükseklik değerlerini buradan tespit edebilirsiniz.")
        
        referans_mockup = st.file_uploader("Boş Mockup Yükle", type=["png", "jpg"], key="cropper_upload")
        
        if referans_mockup:
            ref_img = Image.open(referans_mockup)
            
            # Kırpma aracını göster (Koordinatları alabilmek için return_type='box' kullanıyoruz)
            box_coords = st_cropper(ref_img, realtime_update=True, box_color='blue', return_type='box')
            
            if box_coords:
                st.info(f"**Tabloya Girilecek Değerler:**\n\n"
                        f"* **x_noktasi:** {box_coords['left']}\n"
                        f"* **y_noktasi:** {box_coords['top']}\n"
                        f"* **genislik:** {box_coords['width']}\n"
                        f"* **yukseklik:** {box_coords['height']}")
