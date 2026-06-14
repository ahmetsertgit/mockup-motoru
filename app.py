import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from PIL import Image
import io

# Sayfa ayarları
st.set_page_config(page_title="Print On Demand Mockup Motoru", layout="wide")
st.title("👕 Otomatik Mockup Giydirme Sistemi")

# 1. Google E-Tablolara Bağlanma (Sırlar üzerinden)
@st.cache_resource
def google_baglantisi_kur():
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Google Bağlantı Hatası: Lütfen Secrets (Sırlar) ayarlarını kontrol edin. Hata: {e}")
        return None

client = google_baglantisi_kur()

if client:
    # Tabloyu çek
    try:
        tablo = client.open("Mockup_Veritabani").worksheet("Sayfa1")
        veriler = tablo.get_all_records()
        st.success("Google E-Tablolar bağlantısı başarılı!")
    except Exception as e:
        st.warning(f"Tablo bulunamadı! Lütfen tablonuzun adının 'Mockup_Veritabani' olduğundan ve hizmet hesabına yetki verdiğinizden emin olun.")
        veriler = []

    # 2. Ön Yüz (Kullanıcı Arayüzü)
    yuklenen_tasarim = st.file_uploader("Şeffaf Tasarımınızı (PNG) Yükleyin", type=["png"])
    kategori_secimi = st.selectbox("Hangi Kategoriye Uygulansın?", ["Kupa", "Tshirt", "Tablo"])

    if yuklenen_tasarim is not None:
        st.image(yuklenen_tasarim, caption="Yüklenen Tasarım", width=150)
        
        if st.button("Mockupları Üret"):
            with st.spinner("Sistem çalışıyor, tasarımlar giydiriliyor..."):
                # Kullanıcının yüklediği tasarımı aç
                tasarim_gorseli = Image.open(yuklenen_tasarim).convert("RGBA")
                
                # Tablodaki verileri döngüye sok (Seçilen kategoriye göre)
                islem_sayisi = 0
                for satir in veriler:
                    if satir.get("kategori") == kategori_secimi:
                        try:
                            # Not: Bu aşamada Drive'dan görsel indirme işlemi eklenecektir.
                            # Şimdilik simülasyon ve piksel hesaplama motoru çalışıyor:
                            
                            x = int(satir["x_noktasi"])
                            y = int(satir["y_noktasi"])
                            genislik = int(satir["genislik"])
                            yukseklik = int(satir["yukseklik"])
                            
                            # Tasarımı tablodaki ölçülere göre yeniden boyutlandır
                            yeniden_boyutlu_tasarim = tasarim_gorseli.resize((genislik, yukseklik), Image.Resampling.LANCZOS)
                            
                            st.write(f"✅ {satir['mockup_id']} için tasarım {x},{y} koordinatlarına, {genislik}x{yukseklik} boyutlarında ayarlandı.")
                            islem_sayisi += 1
                        except Exception as e:
                            st.error(f"{satir['mockup_id']} işlenirken bir hata oluştu: Değerlerin sadece sayı olduğundan emin olun.")
                
                if islem_sayisi > 0:
                    st.success("Tüm koordinat ve boyutlandırma işlemleri başarıyla simüle edildi! Bir sonraki adımda bu ölçüler Drive'daki görsellerin üzerine kalıcı olarak basılacaktır.")
                else:
                    st.warning("Bu kategoride E-Tablonuzda kayıtlı bir mockup bulunamadı.")