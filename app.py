import streamlit as st
from streamlit_oauth import OAuth2Component
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import gspread
from PIL import Image
import io
import zipfile

# --- AYARLAR ---
# GitHub'a şifre sızmaması için st.secrets kullanıyoruz
CLIENT_ID = st.secrets["oauth"]["client_id"]
CLIENT_SECRET = st.secrets["oauth"]["client_secret"]
REDIRECT_URI = "https://mockup-motoru-vxkujsyi98kigjm5yyov5h.streamlit.app/"

AUTHORIZE_ENDPOINT = 'https://accounts.google.com/o/oauth2/v2/auth'
TOKEN_ENDPOINT = 'https://oauth2.googleapis.com/token'
REVOKE_ENDPOINT = 'https://oauth2.googleapis.com/revoke'

TABLO_ID = "1KfloezbAz2saj3RKVoD6geVS9_wqefjjshWwMN0N-eY"
CIKTI_KLASOR_ID = "1u43nbgsfcXoMGkbWAYYxdd9Yw4bUsZOz"

st.set_page_config(page_title="Mockup Motoru", layout="wide")

oauth = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_ENDPOINT, TOKEN_ENDPOINT, REVOKE_ENDPOINT)

# --- GİRİŞ KONTROLÜ ---
if 'token' not in st.session_state:
    st.title("👕 Otomatik Mockup Üretim Hattı")
    st.warning("Devam etmek için Google ile giriş yapın.")
    result = oauth.authorize_button(
        name="Google ile Giriş Yap", 
        icon="https://www.google.com/favicon.ico", 
        redirect_uri=REDIRECT_URI, 
        scope="https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/spreadsheets"
    )
    if result:
        st.session_state.token = result
        st.rerun()
else:
    # --- YETKİLENDİRME VE ANA UYGULAMA ---
    token_verisi = st.session_state.token
    gecerli_token = token_verisi.get("access_token") if isinstance(token_verisi, dict) else token_verisi
    
    try:
        user_creds = Credentials(token=gecerli_token)
        drive_service = build('drive', 'v3', credentials=user_creds)
        sheets_client = gspread.authorize(user_creds)
        
        st.title("👕 Otomatik Mockup Üretim Hattı")
        st.success("Sisteme başarıyla giriş yapıldı! Bağlantılar aktif.")
        
        # Ana üretim hattı kodların ve arayüzün buraya eklenecek
        st.write("Sistem şu an stabil ve ana üretim işlemleri için hazır.")
        
        if st.button("Sistemi Yenile"):
            st.rerun()
            
    except Exception as e:
        st.error(f"Google servislerine bağlanırken bir hata oluştu: {e}")

    # Çıkış Butonu
    st.sidebar.button("Çıkış Yap", on_click=lambda: st.session_state.pop('token', None))
