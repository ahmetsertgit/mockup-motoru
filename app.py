import streamlit as st
from streamlit_oauth import OAuth2Component
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import gspread
from PIL import Image
import io
import zipfile
from streamlit_drawable_canvas import st_canvas
import base64
import io


# --- AYARLAR ---
CLIENT_ID = st.secrets["oauth"]["client_id"]
CLIENT_SECRET = st.secrets["oauth"]["client_secret"]
REDIRECT_URI = "https://mockup-motoru-vxkujsyi98kigjm5yyov5h.streamlit.app/"

AUTHORIZE_ENDPOINT = 'https://accounts.google.com/o/oauth2/v2/auth'
TOKEN_ENDPOINT = 'https://oauth2.googleapis.com/token'
REVOKE_ENDPOINT = 'https://oauth2.googleapis.com/revoke'

TABLO_ID = "1KfloezbAz2saj3RKVoD6geVS9_wqefjjshWwMN0N-eY"
CIKTI_KLASOR_ID = "1u43nbgsfcXoMGkbWAYYxdd9Yw4bUsZOz"

oauth = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_ENDPOINT, TOKEN_ENDPOINT, REVOKE_ENDPOINT)

st.set_page_config(page_title="Mockup Motoru", layout="wide")

# --- GİRİŞ KONTROLÜ ---
if 'token' not in st.session_state:
    st.title("👕 Otomatik Mockup Üretim Hattı")
    st.warning("Devam etmek için giriş yapın.")
    result = oauth.authorize_button(name="Google ile Giriş Yap", icon="https://www.google.com/favicon.ico", redirect_uri=REDIRECT_URI, scope="https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/spreadsheets")
    if result:
        st.session_state.token = result
        st.rerun()
else:
    # --- YETKİLENDİRME ---
    token_verisi = st.session_state.token
    gecerli_token = token_verisi.get("access_token") if isinstance(token_verisi, dict) else token_verisi
    user_creds = Credentials(token=gecerli_token)
    drive_service = build('drive', 'v3', credentials=user_creds)
    sheets_client = gspread.authorize(user_creds)

    # --- SEKMELER ---
    tab1, tab2 = st.tabs(["👕 Çalışan İşlevler", "🧪 Demo Alanı"])

    # 1. TAB: ÇALIŞAN İŞLEVLER
    with tab1:
        st.header("Üretim Hattı")
        # Eski çalışan kodlarınız burada (üretim hattı)
        if st.button("Sistemi Yenile"):
            st.rerun()
   
    # 2. TAB: DEMO ALANI
    with tab2:
        st.header("Yeni Özellik Denemeleri")
        demo_secim = st.radio("Hangi demoyu deniyorsun?", ["Canvas ile Koordinat Belirleme", "Henüz Yok"])
        
        if demo_secim == "Canvas ile Koordinat Belirleme":
            yuklenen_mockup = st.file_uploader("Mockup Yükle", type=["png", "jpg"], key="canvas_upload")
            # --- Demo Alanı İçinde ---




# ... (Kodun en üstüne ekleyebilirsin veya demo alanı içine)
def image_to_base64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

# --- Demo Alanı İçinde ---
if yuklenen_mockup:
    img = Image.open(yuklenen_mockup)
    
    # Görseli base64 formatına çeviriyoruz
    b64_img = image_to_base64(img)
    
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)", 
        stroke_width=2, 
        stroke_color="#E9967A",
        background_image=b64_img, # Artık objeyi değil, string'i gönderiyoruz
        height=img.height, 
        width=img.width,
        drawing_mode="rect", 
        key="canvas_demo",
    )





                if canvas_result.json_data is not None and len(canvas_result.json_data["objects"]) > 0:
                    rect = canvas_result.json_data["objects"][-1]
                    st.write(f"Koordinatlar: X={int(rect['left'])}, Y={int(rect['top'])}, G={int(rect['width'])}, Y={int(rect['height'])}")
                    
                    if st.button("Tabloya Kaydet"):
                        tablo = sheets_client.open_by_key(TABLO_ID).get_worksheet(0)
                        tablo.append_row(["Yeni_ID", "Kategori", int(rect['left']), int(rect['top']), int(rect['width']), int(rect['height'])])
                        st.success("Tabloya eklendi!")

    st.sidebar.button("Çıkış Yap", on_click=lambda: st.session_state.pop('token', None))
