# deneme_alani.py
import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper
import io
from googleapiclient.http import MediaIoBaseDownload

def kaydet_veritabani(sheets_client, kategori, drive_file_id, x, y, w, h):
    """
    Belirtilen Google Sheet tablosunda drive_file_id kontrolü yapar.
    Varsa satırı günceller, yoksa yeni satır ekler.
    """
    try:
        TABLO_ID = "1KfloezbAz2saj3RKVoD6geVS9_wqefjjshWwMN0N-eY"
        sheet = sheets_client.open_by_key(TABLO_ID).sheet1
        tum_veriler = sheet.get_all_records() # Başlıkları otomatik okur
        
        bulunan_satir = None
        mevcut_mockup_id = None
        
        # Tabloda bu görselin daha önce kaydedilip kaydedilmediğini kontrol et
        for i, satir in enumerate(tum_veriler):
            if str(satir.get('drive_file_id')) == str(drive_file_id):
                bulunan_satir = i + 2 # 1. satır başlık olduğu için index'e 2 ekliyoruz
                mevcut_mockup_id = satir.get('mockup_id')
                break

        if bulunan_satir:
            # Görsel zaten var, eski veriyi yenisiyle DEĞİŞTİR (Overwrite)
            # Sıralama: mockup_id, kategori, drive_file_id, x_noktasi, y_noktasi, genislik, yukseklik
            guncel_satir_verisi = [[mevcut_mockup_id, kategori, drive_file_id, x, y, w, h]]
            sheet.update(f"A{bulunan_satir}:G{bulunan_satir}", guncel_satir_verisi)
            st.success(f"🔄 '{kategori}' kategorisindeki görsel güncellendi! (Satır: {bulunan_satir})")
        else:
            # Görsel ilk defa ekleniyor, YENİ SATIR oluştur
            yeni_id = len(tum_veriler) + 1 # Basit sıralı ID üretimi
            yeni_satir = [yeni_id, kategori, drive_file_id, x, y, w, h]
            sheet.append_row(yeni_satir)
            st.success(f"💾 Yeni mockup başarıyla veritabanına kaydedildi! (ID: {yeni_id})")
            
    except Exception as e:
        st.error(f"Veritabanı kayıt işlemi sırasında hata oluştu: {e}")

def manual_update(olcek_orani, tetikleyen_kutu):
    """Kullanıcı arayüzdeki sayı kutularına ELLE giriş yaptığında çalışır."""
    orj_x = st.session_state.val_x
    orj_y = st.session_state.val_y
    orj_w = st.session_state.val_w
    orj_h = st.session_state.val_h
    
    ratio_str = st.session_state.get('ratio_str', '15:17')
    if ratio_str and ":" in ratio_str:
        try:
            parts = ratio_str.split(":")
            w_r, h_r = float(parts[0]), float(parts[1])
            if tetikleyen_kutu == "w":
                orj_h = orj_w * (h_r / w_r)
                st.session_state.val_h = int(round(orj_h))
            elif tetikleyen_kutu == "h":
                orj_w = orj_h * (w_r / h_r)
                st.session_state.val_w = int(round(orj_w))
        except ValueError:
            pass
            
    guncel_w = st.session_state.val_w
    guncel_h = st.session_state.val_h
    
    mw = guncel_w / olcek_orani
    mh = guncel_h / olcek_orani
    mx = orj_x / olcek_orani
    my = orj_y / olcek_orani
    
    mx_int = int(round(mx))
    my_int = int(round(my))
    mw_int = int(round(mw))
    mh_int = int(round(mh))
    
    st.session_state.cur_x_w_h = {"x": mx_int, "y": my_int, "w": mw_int, "h": mh_int}
    st.session_state.manual_coords = (mx_int, mx_int + mw_int, my_int, my_int + mh_int)
    st.session_state.cropper_version += 1

def calistir(drive_service=None, sheets_client=None):
    st.header("📐 Mockup Baskı Yerleşimi (Drive Entegreli)")
    st.markdown("---")
    
    if drive_service is None or sheets_client is None:
        st.error("Google Drive veya Sheets bağlantısı kurulamadı. Lütfen giriş yapın.")
        return

    BOS_MOCKUP_KLASOR_ID = "1SPParYqyzm1my2hldMacIOy2F-t9no81"

    # Drive'dan T-Shirt Model Klasörlerini Çek
    try:
        klasor_sorgusu = f"'{BOS_MOCKUP_KLASOR_ID}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        klasor_sonuclari = drive_service.files().list(q=klasor_sorgusu, fields="files(id, name)").execute()
        model_klasorleri = klasor_sonuclari.get('files', [])
    except Exception as e:
        st.error(f"Drive klasörleri okunurken hata oluştu: {e}")
        model_klasorleri = []

    if not model_klasorleri:
        st.warning("Boş Mockup ana klasöründe alt klasör bulunamadı.")
        return

    klasor_isimleri = {k['name']: k['id'] for k in model_klasorleri}
    secilen_klasor_adi = st.selectbox("T-Shirt Modelini Seçin (Kategori):", list(klasor_isimleri.keys()))
    secilen_klasor_id = klasor_isimleri[secilen_klasor_adi]

    # Seçilen Klasördeki Görselleri Çek
    try:
        gorsel_sorgusu = f"'{secilen_klasor_id}' in parents and mimeType contains 'image/' and trashed=false"
        gorsel_sonuclari = drive_service.files().list(q=gorsel_sorgusu, fields="files(id, name)").execute()
        gorseller = gorsel_sonuclari.get('files', [])
    except Exception as e:
        st.error(f"Görseller okunurken hata oluştu: {e}")
        gorseller = []

    if not gorseller:
        st.info(f"{secilen_klasor_adi} klasöründe görsel bulunmuyor.")
        return

    gorsel_isimleri = {g['name']: g['id'] for g in gorseller}
    secilen_gorsel_adi = st.selectbox("Mockup Görseli Seçin:", list(gorsel_isimleri.keys()))
    secilen_gorsel_id = gorsel_isimleri[secilen_gorsel_adi]

    BASLANGIC_W, BASLANGIC_H = 150, 170
    BASLANGIC_X, BASLANGIC_Y = 50, 50
    
    if 'manual_coords' not in st.session_state:
        st.session_state.manual_coords = (BASLANGIC_X, BASLANGIC_X + BASLANGIC_W, BASLANGIC_Y, BASLANGIC_Y + BASLANGIC_H)
    if 'cropper_version' not in st.session_state:
        st.session_state.cropper_version = 0
    if 'cur_x_w_h' not in st.session_state:
        st.session_state.cur_x_w_h = {"x": BASLANGIC_X, "y": BASLANGIC_Y, "w": BASLANGIC_W, "h": BASLANGIC_H}
    if 'ratio_str' not in st.session_state:
        st.session_state.ratio_str = "15:17"

    # Görseli Drive'dan İndir ve İşle
    if 'loaded_image_id' not in st.session_state or st.session_state.loaded_image_id != secilen_gorsel_id:
        with st.spinner('Görsel Drive\'dan çekiliyor...'):
            request = drive_service.files().get_media(fileId=secilen_gorsel_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            fh.seek(0)
            
            ref_img = Image.open(fh)
            orj_genislik, orj_yukseklik = ref_img.size
            
            HEDEF_YUKSEKLIK = 500
            olcek_orani = orj_yukseklik / HEDEF_YUKSEKLIK
            yeni_w = int(round(orj_genislik / olcek_orani))
            yeni_h = HEDEF_YUKSEKLIK
            
            st.session_state.cropper_gorseli = ref_img.resize((yeni_w, yeni_h), Image.Resampling.LANCZOS)
            st.session_state.olcek_orani = olcek_orani
            st.session_state.loaded_image_id = secilen_gorsel_id
            
            st.session_state.val_x = int(round(BASLANGIC_X * olcek_orani))
            st.session_state.val_y = int(round(BASLANGIC_Y * olcek_orani))
            st.session_state.val_w = int(round(BASLANGIC_W * olcek_orani))
            st.session_state.val_h = int(round(BASLANGIC_H * olcek_orani))
            st.session_state.manual_coords = (BASLANGIC_X, BASLANGIC_X + BASLANGIC_W, BASLANGIC_Y, BASLANGIC_Y + BASLANGIC_H)
            st.session_state.cur_x_w_h = {"x": BASLANGIC_X, "y": BASLANGIC_Y, "w": BASLANGIC_W, "h": BASLANGIC_H}
            st.session_state.cropper_version += 1

    cropper_gorseli = st.session_state.cropper_gorseli
    olcek_orani = st.session_state.olcek_orani
    
    col_sol_gorsel, col_sag_bilgi = st.columns([65, 35])
    
    with col_sag_bilgi:
        def ratio_changed():
            st.session_state.cropper_version += 1
        
        ratio_input = st.text_input("🔒 En : Boy Oranı Kilidi", key="ratio_str", on_change=ratio_changed)
        
        aspect_ratio = None
        if ratio_input and ":" in ratio_input:
            try:
                parts = ratio_input.split(":")
                w_ratio, h_ratio = float(parts[0]), float(parts[1])
                if w_ratio > 0 and h_ratio > 0:
                    aspect_ratio = (w_ratio, h_ratio)
                    st.caption(f"🎯 Oran **{ratio_input}** olarak kilitlendi.")
            except ValueError:
                st.error("❌ Geçersiz format!")
        
        st.markdown("---")

    with col_sol_gorsel:
        box_coords = st_cropper(
            cropper_gorseli, 
            realtime_update=True, 
            box_color='blue', 
            aspect_ratio=aspect_ratio, 
            return_type='box',
            default_coords=st.session_state.manual_coords,
            key=f"cropper_{st.session_state.cropper_version}",
            should_resize_image=False
        )
    
    if box_coords:
        bx = int(round(box_coords['left']))
        by = int(round(box_coords['top']))
        bw = int(round(box_coords['width']))
        bh = int(round(box_coords['height']))
        
        son_w = st.session_state.cur_x_w_h["w"]
        son_h = st.session_state.cur_x_w_h["h"]
        son_x = st.session_state.cur_x_w_h["x"]
        son_y = st.session_state.cur_x_w_h["y"]
        
        if bx != son_x or by != son_y or bw != son_w or bh != son_h:
            size_changed = abs(bw - son_w) > 10 or abs(bh - son_h) > 10
            
            st.session_state.val_x = int(round(bx * olcek_orani))
            st.session_state.val_y = int(round(by * olcek_orani))
            st.session_state.cur_x_w_h["x"] = bx
            st.session_state.cur_x_w_h["y"] = by
            
            if size_changed:
                st.session_state.val_w = int(round(bw * olcek_orani))
                st.session_state.val_h = int(round(bh * olcek_orani))
                st.session_state.cur_x_w_h["w"] = bw
                st.session_state.cur_x_w_h["h"] = bh
    
    with col_sag_bilgi:
        st.markdown("**Orijinal Çözünürlük Pikselleri:**")
        m_col1, m_col2 = st.columns(2)
        m_col1.number_input("Orijinal X", step=1, key="val_x", on_change=manual_update, args=(olcek_orani, "x"))
        m_col2.number_input("Orijinal Y", step=1, key="val_y", on_change=manual_update, args=(olcek_orani, "y"))
        
        m_col3, m_col4 = st.columns(2)
        m_col3.number_input("Orijinal Genişlik", step=1, key="val_w", on_change=manual_update, args=(olcek_orani, "w"))
        m_col4.number_input("Orijinal Yükseklik", step=1, key="val_h", on_change=manual_update, args=(olcek_orani, "h"))
        
        st.markdown("---")
        st.markdown("**Veritabanı İşlemleri**")
        
        if st.button("💾 Konumu Veritabanına Kaydet", type="primary", use_container_width=True):
            # Değişken eşleşmeleri:
            # secilen_klasor_adi -> kategori
            # secilen_gorsel_id  -> drive_file_id
            kaydet_veritabani(
                sheets_client, 
                secilen_klasor_adi, 
                secilen_gorsel_id, 
                st.session_state.val_x, 
                st.session_state.val_y, 
                st.session_state.val_w, 
                st.session_state.val_h
            )

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    st.error("Lütfen uygulamayı app.py üzerinden çalıştırın.")
