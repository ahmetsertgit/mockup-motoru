# app.py
import streamlit as st
from streamlit_oauth import OAuth2Component
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import gspread

# Alt modülleri içe aktarıyoruz
import uretim_hatti
import deneme_alani

st.set_page_config(page_title="Mockup Motoru", page_icon="👕", layout="wide")

CLIENT_ID = st.secrets["oauth"]["client_id"]
CLIENT_SECRET = st.secrets["oauth"]["client_secret"]
REDIRECT_URI = "https://mockup-motoru-vxkujsyi98kigjm5yyov5h.streamlit.app/"
AUTHORIZE_ENDPOINT = 'https://accounts.google.com/o/oauth2/v2/auth'
TOKEN_ENDPOINT = 'https://oauth2.googleapis.com/token'
REVOKE_ENDPOINT = 'https://oauth2.googleapis.com/revoke'

oauth = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_ENDPOINT, TOKEN_ENDPOINT, REVOKE_ENDPOINT)

if 'token' not in st.session_state:
    st.title("👕 Otomatik Mockup Üretim Hattı")
    st.warning("Sisteme erişmek için Google ile giriş yapın.")
    result = oauth.authorize_button(
        name="Google ile Giriş Yap",
        icon="https://www.google.com/favicon.ico",
        redirect_uri=REDIRECT_URI,
        scope="https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/spreadsheets",
    )
    if result:
        st.session_state.token = result
        st.rerun()
else:
    # Token işleme
    token_verisi = st.session_state.token
    gecerli_token = None
    if isinstance(token_verisi, dict):
        gecerli_token = token_verisi.get("access_token", token_verisi.get("token", {}).get("access_token") if isinstance(token_verisi.get("token"), dict) else token_verisi.get("token"))
            
    if not gecerli_token:
        st.error("Oturum süresi doldu veya token geçersiz.")
        if st.button("Yeniden Giriş Yap"):
            del st.session_state.token
            st.rerun()
        st.stop()
        
    # Servisleri Başlat
    user_creds = Credentials(token=gecerli_token)
    drive_service = build('drive', 'v3', credentials=user_creds)
    sheets_client = gspread.authorize(user_creds)
    
    # YAN MENÜ (SIDEBAR) - Modül Seçimi
    st.sidebar.success("✅ Google Hesabı Bağlı")
    
    secim = st.sidebar.radio("Çalışma Alanı Seçin:", ["Üretim Hattı", "Deneme Alanı"])
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Güvenli Çıkış"):
        del st.session_state.token
        st.rerun()

    # SEÇİME GÖRE İLGİLİ DOSYAYI ÇALIŞTIR
    if secim == "Üretim Hattı":
        uretim_hatti.calistir(drive_service, sheets_client)
    elif secim == "Deneme Alanı":
        deneme_alani.calistir()
