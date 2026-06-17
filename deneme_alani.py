# deneme_alani.py
import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper
import io
from googleapiclient.http import MediaIoBaseDownload

def kaydet_veritabani(sheets_client, mockup_name, kategori, drive_file_id, x, y, w, h):
    """
    Belirtilen Google Sheet tablosunda drive_file_id kontrolü yapar.
    Varsa o satırı tamamen günceller, yoksa yeni satır olarak ekler.
    """
    try:
        TABLO_ID = "1KfloezbAz2saj3RKVoD6geVS9_wqefjjshWwMN0N-eY"
        sheet = sheets_client.open_by_key(TABLO_ID).sheet1
        tum_veriler = sheet.get_all_records()
        
        bulunan_satir = None
        mevcut_mockup_id = None
        
        for i, satir in enumerate(tum_veriler):
            if str(satir.get('drive_file_id')) == str(drive_file_id):
                bulunan_satir = i + 2
                mevcut_mockup_id = satir.get('mockup_id')
                break

        if bulunan_satir:
            guncel_satir_verisi = [[mevcut_mockup_id, mockup_name, kategori, drive_file_id, x, y, w, h]]
            sheet.update(f"A{bulunan_satir}:H{bulunan_satir}", guncel_satir_verisi)
            st.success(f"🔄 '{mockup_name}' güncellendi! (Satır: {bulunan_satir})")
        else:
            yeni_id = len(tum_veriler) + 1
            yeni_satir = [yeni_id, mockup_name, kategori, drive_file_id, x, y, w, h]
            sheet.append_row(yeni_satir)
            st.success(f"💾 Yeni mockup kaydedildi! (ID: {yeni_id})")
            
    except Exception as e:
        st.error(f"Veritabanı kayıt hatası: {e}")

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
    
    st.session_state.cur_x_w_h = {"x": int(round(mx)), "y": int(round(my)), "w": int(round(mw)), "h": int(round(mh))}
    st.session_state.manual_coords = (int(round(mx)), int(round(mx + mw)), int(round(my)), int(round(my + mh)))
    st.session_state.cropper_version += 1

def calistir(drive_service=None, sheets_client=None):
    st.subheader("📐 Mockup Baskı Yerleşimi")
    
    if drive_service is None or sheets_client is None:
        st.error("Bağlantı kurulamadı. Lütfen giriş yapın.")
        return

    BOS_MOCKUP_KLASOR_ID = "1SPParYqyzm1my2hldMacIOy2F-t9no81"

    try:
        klasor_sorgusu = f"'{BOS_MOCKUP_KLASOR_ID}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        klasor_sonuclari = drive_service.files().list(q=klasor_sorgusu, fields="files(id, name)").execute()
        model_klasorleri = klasor_sonuclari.get('files', [])
    except Exception as e:
        st.error(f"Drive hatası: {e}")
        model_klasorleri = []

    if not model_klasorleri:
        st.warning("Klasör bulunamadı.")
        return

    klasor_isimleri = {k['name']: k['id'] for k in model_klasorleri}
    
    # --- ÜST KONTROL PANELİ (Tek Satırda 4 Sütun) ---
    col_top1, col_top2, col_top3, col_top4 = st.columns([3, 3, 2, 2])
    
    with col_top1:
        secilen_klasor_adi = st.selectbox("Kategori (Model):", list(klasor_isimleri.keys()))
        secilen_klasor_id = klasor_isimleri[secilen_klasor_adi]

    try:
        gorsel_sorgusu = f"'{secilen_klasor_id}' in parents and mimeType contains 'image/' and trashed=false"
        gorsel_sonuclari = drive_service.files().list(q=gorsel_sorgusu, fields="files(id, name)").execute()
        gorseller = gorsel_sonuclari.get('files', [])
    except Exception as e:
        gorseller = []

    if not gorseller:
        st.info(f"Görsel bulunmuyor.")
        return

    gorsel_isimleri = {g['name']: g['id'] for g in gorseller}
    
    with col_top2:
        secilen_gorsel_adi = st.selectbox("Mockup Görseli:", list(gorsel_isimleri.keys()))
        secilen_gorsel_id = gorsel_isimleri[secilen_gorsel_adi]
        
    with col_top3:
        def ratio_changed():
            st.session_state.cropper_version += 1
        ratio_input = st.text_input("🔒 En : Boy Oranı:", key="ratio_str", on_change=ratio_changed)
        
        aspect_ratio = None
        if ratio_input and ":" in ratio_input:
            try:
                parts = ratio_input.split(":")
                w_ratio, h_ratio = float(parts[0]), float(parts[1])
                if w_ratio > 0 and h_ratio > 0:
                    aspect_ratio = (w_ratio, h_ratio)
            except ValueError:
                pass
                
    with col_top4:
        st.markdown("<div style='padding-top: 24px;'></div>", unsafe_allow_html=True)
        if st.button("💾 Veritabanına Kaydet", type="primary", use_container_width=True):
            kaydet_veritabani(
                sheets_client, 
                secilen_gorsel_adi,  
                secilen_klasor_adi,  
                secilen_gorsel_id,   
                st.session_state.get('val_x', 0), 
                st.session_state.get('val_y', 0), 
                st.session_state.get('val_w', 0), 
                st.session_state.get('val_h', 0)
            )

    st.markdown("---")

    # --- ALT PANEL (Görsel Alanı ve Koordinatlar) ---
    BASLANGIC_W, BASLANGIC_H = 150, 170
    BASLANGIC_X, BASLANGIC_Y = 50, 50
    
    if 'manual_coords' not in st.session_state:
        st.session_state.manual_coords = (BASLANGIC_X, BASLANGIC_X + BASLANGIC_W, BASLANGIC_Y, BASLANGIC_Y + BASLANGIC_H)
    if 'cropper_version' not in st.session_state:
        st.session_state.cropper_version = 0
    if 'cur_x_w_h' not in st.session_state:
        st.session_state.cur_x_w_h = {"x": BASLANGIC_X, "y": BASLANGIC_Y, "w": BASLANGIC_W, "h": BASLANGIC_H}

    if 'loaded_image_id' not in st.session_state or st.session_state.loaded_image_id != secilen_gorsel_id:
        with st.spinner('Görsel çekiliyor...'):
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
            st.session_state
