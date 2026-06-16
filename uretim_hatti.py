# uretim_hatti.py
import streamlit as st
from PIL import Image
import io
import zipfile
from googleapiclient.http import MediaIoBaseUpload
import gorsel_islem # Kendi yazdığımız modülü içe aktarıyoruz

TABLO_ID = "1KfloezbAz2saj3RKVoD6geVS9_wqefjjshWwMN0N-eY"
CIKTI_KLASOR_ID = "1u43nbgsfcXoMGkbWAYYxdd9Yw4bUsZOz"

def calistir(drive_service, sheets_client):
    st.header("👕 Ana Üretim Hattı")
    
    # E-Tablo Verilerini Çekme
    try:
        tablo = sheets_client.open_by_key(TABLO_ID).get_worksheet(0)
        veriler = tablo.get_all_records()
        kategoriler = list(set([satir["kategori"] for satir in veriler if "kategori" in satir]))
    except Exception as e:
        st.error(f"E-Tablo okunamadı! Hata: {e}")
        return

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
                            mockup_bytes = request.execute()
                            
                            # 2. AYRI DOSYADAKİ FONKSİYONU KULLANARAK BİRLEŞTİR
                            islenmis_gorsel_bytes = gorsel_islem.mockup_olustur(
                                mockup_bytes, 
                                tasarim, 
                                satir["x_noktasi"], 
                                satir["y_noktasi"], 
                                satir["genislik"], 
                                satir["yukseklik"]
                            )
                            
                            # 3. ZIP dosyasına ekle
                            dosya_adi = f"{satir['mockup_id']}_cikti.png"
                            zip_file.writestr(dosya_adi, islenmis_gorsel_bytes)
                            
                            # 4. Dolu Mockup Klasörüne (Drive) Yükle
                            media = MediaIoBaseUpload(io.BytesIO(islenmis_gorsel_bytes), mimetype='image/png')
                            drive_service.files().create(
                                body={'name': dosya_adi, 'parents': [CIKTI_KLASOR_ID]},
                                media_body=media
                            ).execute()
                            
                            st.success(f"✅ {satir['mockup_id']} işlendi ve Drive'a kaydedildi.")
                            
                        except Exception as e:
                            st.error(f"❌ {satir['mockup_id']} işlenirken hata: {e}")

            st.download_button(label="📦 Tümünü ZIP Olarak İndir", data=zip_buffer.getvalue(), file_name="mockuplar_cikti.zip", mime="application/zip")
