# deneme_alani.py
import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper
import io
from googleapiclient.http import MediaIoBaseDownload

def kaydet_veritabani(sheets_client, mockup_name, kategori, drive_file_id, x, y, w, h):
    """
    Belirtilen Google Sheet tablosunda drive_file_id kontrolü yapar.
    Sonucu arayüzde yan yana göstermek için (Durum, Mesaj) olarak döner.
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
            return True, f"🔄 Güncellendi! (Satır: {bulunan_satir})"
        else:
            yeni_id = len(tum_veriler) + 1
            yeni_satir = [yeni_id, mockup_name, kategori, drive_file_id, x, y, w, h]
            sheet.append_row(yeni_satir)
            return True, f"💾 Kaydedildi! (ID: {yeni_id})"
            
    except Exception as e:
        return False, f"Hata: {e}"

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
    # --- TEPE BOŞLUĞUNU SIFIRLAYAN CSS ---
    st.markdown(
        """
        <style>
            .block-container {
                padding-top: 1rem !important;
                padding-bottom: 0rem !important;
            }
            header[data-testid="stHeader"] {
                height: 1rem !important;
                background: transparent !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.header("📐 Mockup Baskı Yerleşimi (Drive Entegreli)")
    
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
    
    # --- YAN YANA İKİ ANA SÜTUN ---
    col_sol_gorsel, col_sag_bilgi = st.columns([58, 42])
    
    with col_sag_bilgi:
        secilen_klasor_adi = st.selectbox("T-Shirt Modelini Seçin (Kategori):", list(klasor_isimleri.keys()))
        secilen_klasor_id = klasor_isimleri[secilen_klasor_adi]

    # --- GOOGLE SHEETS'TEN MEVCUT DURUMU VE KOORDİNATLARI ÇEKME ---
    mevcut_gorsel_verileri = {}
    try:
        TABLO_ID = "1KfloezbAz2saj3RKVoD6geVS9_wqefjjshWwMN0N-eY"
        sheet = sheets_client.open_by_key(TABLO_ID).sheet1
        tum_veriler = sheet.get_all_records()
        for satir in tum_veriler:
            f_id = satir.get('drive_file_id')
            if f_id:
                try:
                    # Hata buradaydı: Sütun isimleri x_noktasi, y_noktasi, genislik, yukseklik olmalıydı!
                    w_val = int(satir.get('genislik', 0) or 0)
                    h_val = int(satir.get('yukseklik', 0) or 0)
                    
                    # Eğer w_val 0 ise tablo boş kabul edilir, varsayılan değerlerle açılır
                    if w_val > 0 and h_val > 0:
                        mevcut_gorsel_verileri[str(f_id)] = {
                            'x': int(satir.get('x_noktasi', 0) or 0),
                            'y': int(satir.get('y_noktasi', 0) or 0),
                            'w': w_val,
                            'h': h_val
                        }
                except Exception:
                    pass
    except Exception as e:
        st.error(f"Veritabanı kontrolü başarısız oldu: {e}")

    # --- GÖRSELLERİ DRIVEdan ÇEKME VE İŞARETLEME ---
    try:
        gorsel_sorgusu = f"'{secilen_klasor_id}' in parents and mimeType contains 'image/' and trashed=false"
        gorsel_sonuclari = drive_service.files().list(q=gorsel_sorgusu, fields="files(id, name)").execute()
        gorseller = gorsel_sonuclari.get('files', [])
    except Exception as e:
        gorseller = []

    if not gorseller:
        with col_sol_gorsel:
            st.info(f"Seçilen klasörde görsel bulunmuyor.")
        return

    selectbox_secenekleri = []
    gorsel_id_haritasi = {}       
    gorsel_orj_ad_haritasi = {}   

    for g in gorseller:
        f_id = str(g['id'])
        f_name = g['name']
        
        is_exist = f_id in mevcut_gorsel_verileri
        isaret = "✅ " if is_exist else "❌ "
        gosterim_adi = f"{isaret}{f_name}"
        
        selectbox_secenekleri.append(gosterim_adi)
        gorsel_id_haritasi[gosterim_adi] = f_id
        gorsel_orj_ad_haritasi[gosterim_adi] = f_name
    
    with col_sag_bilgi:
        secilen_gosterim_adi = st.selectbox("Mockup Görseli Seçin:", selectbox_secenekleri)
        secilen_gorsel_id = gorsel_id_haritasi[secilen_gosterim_adi]
        secilen_gorsel_adi = gorsel_orj_ad_haritasi[secilen_gosterim_adi]

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

    # --- GÖRSEL YÜKLENME VE İLK DÖRTGEN ÇİZİLME MANTIĞI ---
    if 'loaded_image_id' not in st.session_state or st.session_state.loaded_image_id != secilen_gorsel_id:
        with col_sol_gorsel:
            with st.spinner('Görsel çekiliyor...'):
