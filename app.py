import streamlit as st
from streamlit_oauth import OAuth2Component
import os

# Google OAuth Bilgileri
st.secrets["oauth"]["client_id"]
AUTHORIZE_ENDPOINT = 'https://accounts.google.com/o/oauth2/v2/auth'
TOKEN_ENDPOINT = 'https://oauth2.googleapis.com/token'
REVOKE_ENDPOINT = 'https://oauth2.googleapis.com/revoke'

# OAuth Bileşenini Oluştur
oauth = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_ENDPOINT, TOKEN_ENDPOINT, REVOKE_ENDPOINT)

if 'token' not in st.session_state:
    # Giriş yapılmamışsa butonu göster
    result = oauth.authorize_button(
        name="Google ile Giriş Yap",
        icon="https://www.google.com/favicon.ico",
        redirect_uri="https://mockup-motoru.streamlit.app/",
        scope="https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/spreadsheets",
    )
    if result:
        st.session_state.token = result
        st.rerun()
else:
    # Giriş yapılmışsa uygulama içeriği
    st.title("👕 Profesyonel Mockup Üretim Hattı")
    st.success("Google hesabınızla başarıyla bağlandınız!")
    
    # Artık 'st.session_state.token' kullanarak Drive servislerine erişebilirsiniz.
    # Burada daha önceki mockup birleştirme kodlarınızı çalıştıracağız.
    if st.button("Çıkış Yap"):
        del st.session_state.token
        st.rerun()
