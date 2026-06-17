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
    st.session_state.just_loaded = True  # Yeniden çizimde sıfırlama korumasını aktif et
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
                mevcut_gorsel_verileri[str(f_id)] = {
                    'x': satir.get('x', 0),
                    'y': satir.get('y', 0),
                    'w': satir.get('w', 0),
                    'h': satir.get('h', 0)
                }
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
                
                # Güncelleme Kontrolü: Görsel veritabanında var mı?
                if secilen_gorsel_id in mevcut_gorsel_verileri:
                    v = mevcut_gorsel_verileri[secilen_gorsel_id]
                    st.session_state.val_x = int(v['x'])
                    st.session_state.val_y = int(v['y'])
                    st.session_state.val_w = int(v['w'])
                    st.session_state.val_h = int(v['h'])
                    
                    mx = st.session_state.val_x / olcek_orani
                    my = st.session_state.val_y / olcek_orani
                    mw = st.session_state.val_w / olcek_orani
                    mh = st.session_state.val_h / olcek_orani
                else:
                    st.session_state.val_x = int(round(BASLANGIC_X * olcek_orani))
                    st.session_state.val_y = int(round(BASLANGIC_Y * olcek_orani))
                    st.session_state.val_w = int(round(BASLANGIC_W * olcek_orani))
                    st.session_state.val_h = int(round(BASLANGIC_H * olcek_orani))
                    
                    mx, my, mw, mh = BASLANGIC_X, BASLANGIC_Y, BASLANGIC_W, BASLANGIC_H

                st.session_state.manual_coords = (int(round(mx)), int(round(mx + mw)), int(round(my)), int(round(my + mh)))
                st.session_state.cur_x_w_h = {"x": int(round(mx)), "y": int(round(my)), "w": int(round(mw)), "h": int(round(mh))}
                st.session_state.just_loaded = True  # İlk yüklemede sıfırlama korumasını aktif et
                st.session_state.cropper_version += 1

    ratio_input = st.session_state.get('ratio_str', '15:17')
    aspect_ratio = None
    if ratio_input and ":" in ratio_input:
        try:
            parts = ratio_input.split(":")
            w_ratio, h_ratio = float(parts[0]), float(parts[1])
            if w_ratio > 0 and h_ratio > 0:
                aspect_ratio = (w_ratio, h_ratio)
        except ValueError:
            pass

    # --- SOL SÜTUN ---
    with col_sol_gorsel:
        box_coords = st_cropper(
            st.session_state.cropper_gorseli, 
            realtime_update=True, 
            box_color='blue', 
            aspect_ratio=aspect_ratio, 
            return_type='box',
            default_coords=st.session_state.manual_coords,
            key=f"cropper_{st.session_state.cropper_version}",
            should_resize_image=False
        )
    
    # --- AKILLI SENKRONİZASYON VE KORUMA KALKANI ---
    if box_coords:
        if st.session_state.get('just_loaded', False):
            # İlk yükleme karesinde cropper'ın sıfır veya bozuk dönmesini engelle, kalkanı indir
            st.session_state.just_loaded = False
        else:
            bx = int(round(box_coords['left']))
            by = int(round(box_coords['top']))
            bw = int(round(box_coords['width']))
            bh = int(round(box_coords['height']))
            
            # Sadece geçerli ve canlı bir dörtgen varsa koordinat güncellemesi yap
            if bw > 0 and bh > 0:
                olcek_orani = st.session_state.olcek_orani
                son_w = st.session_state.cur_x_w_h["w"]
                son_h = st.session_state.cur_x_w_h["h"]
                son_x = st.session_state.cur_x_w_h["x"]
                son_y = st.session_state.cur_x_w_h["y"]
                
                if bx != son_x or by != son_y or bw != son_w or bh != son_h:
                    size_changed = abs(bw - son_w) > 5 or abs(bh - son_h) > 5
                    
                    st.session_state.val_x = int(round(bx * olcek_orani))
                    st.session_state.val_y = int(round(by * olcek_orani))
                    st.session_state.cur_x_w_h["x"] = bx
                    st.session_state.cur_x_w_h["y"] = by
                    
                    if size_changed:
                        st.session_state.val_w = int(round(bw * olcek_orani))
                        st.session_state.val_h = int(round(bh * olcek_orani))
                        st.session_state.cur_x_w_h["w"] = bw
                        st.session_state.cur_x_w_h["h"] = bh

    # --- SAĞ SÜTUN ---
    with col_sag_bilgi:
        col_btn, col_msg = st.columns([62, 38])
        
        with col_btn:
            kaydet_butonu = st.button("💾 Konumu Veritabanına Kaydet", type="primary", use_container_width=True)
            
        if kaydet_butonu:
            basarili, sonuc_mesaji = kaydet_veritabani(
                sheets_client, 
                secilen_gorsel_adi,  
                secilen_klasor_adi,  
                secilen_gorsel_id,   
                st.session_state.val_x, 
                st.session_state.val_y, 
                st.session_state.val_w, 
                st.session_state.val_h
            )
            with col_msg:
                if basarili:
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; justify-content: center; 
                                    height: 38px; color: #155724; background-color: #d4edda; 
                                    border: 1px solid #c3e6cb; border-radius: 0.25rem; 
                                    font-size: 0.85rem; font-weight: 500; padding: 0 4px; text-align: center;">
                            {sonuc_mesaji}
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                    st.rerun()
                else:
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; justify-content: center; 
                                    height: 38px; color: #721c24; background-color: #f8d7da; 
                                    border: 1px solid #f5c6cb; border-radius: 0.25rem; 
                                    font-size: 0.85rem; font-weight: 500; padding: 0 4px; text-align: center;">
                            {sonuc_mesaji}
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
            
        st.markdown("**Orijinal Çözünürlük Pikselleri:**")
        
        olcek = st.session_state.get('olcek_orani', 1.0)
        m_col1, m_col2 = st.columns(2)
        m_col1.number_input("Orijinal X", step=1, key="val_x", on_change=manual_update, args=(olcek, "x"))
        m_col2.number_input("Orijinal Y", step=1, key="val_y", on_change=manual_update, args=(olcek, "y"))
        
        m_col3, m_col4 = st.columns(2)
        m_col3.number_input("Orijinal Genişlik", step=1, key="val_w", on_change=manual_update, args=(olcek, "w"))
        m_col4.number_input("Orijinal Yükseklik", step=1, key="val_h", on_change=manual_update, args=(olcek, "h"))
        
        def ratio_changed():
            st.session_state.just_loaded = True  # Oran değiştiğinde de sıfırlama korumasını aç
            st.session_state.cropper_version += 1
        st.text_input("🔒 En : Boy Oranı Kilidi", key="ratio_str", on_change=ratio_changed)

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    st.error("Lütfen uygulamayı app.py üzerinden çalıştırın.")
