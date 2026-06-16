# deneme_alani.py
import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

def manual_update():
    """Bu fonksiyon SADECE sağdaki kutulara elle sayı girildiğinde tetiklenir."""
    mx = st.session_state.val_x
    my = st.session_state.val_y
    mw = st.session_state.val_w
    mh = st.session_state.val_h
    
    # Eğer oran kilidi aktifse, genişlik veya yükseklik değişimine göre diğerini otomatik hesapla
    ratio_str = st.session_state.get('ratio_str', '15:17')
    if ratio_str and ":" in ratio_str:
        try:
            parts = ratio_str.split(":")
            w_r, h_r = float(parts[0]), float(parts[1])
            if mw != st.session_state.cur_x_w_h["w"]:
                mh = int(round(mw * (h_r / w_r)))
                st.session_state.val_h = mh
            elif mh != st.session_state.cur_x_w_h["h"]:
                mw = int(round(mh * (w_r / h_r)))
                st.session_state.val_w = mw
        except ValueError:
            pass

    # Mevcut pozisyon hafızasını güncelle
    st.session_state.cur_x_w_h = {"x": mx, "y": my, "w": mw, "h": mh}
    
    # Kırpıcıyı yeni değerlerle sıfırdan başlatmak için ilk koordinatları ayarla ve versiyonu uçur
    st.session_state.manual_coords = (mx, mx + mw, my, my + mh)
    st.session_state.cropper_version += 1

def calistir():
    st.header("📐 Mockup Baskı Yerleşimi")
    st.markdown("---")
    
    # --- 1. SAF HAFIZA AYARLARI ---
    if 'manual_coords' not in st.session_state:
        st.session_state.manual_coords = (50, 250, 50, 250)
    if 'cropper_version' not in st.session_state:
        st.session_state.cropper_version = 0
    if 'cur_x_w_h' not in st.session_state:
        st.session_state.cur_x_w_h = {"x": 50, "y": 50, "w": 200, "h": 200}

    # Kutuların iç değerleri (Widget hafızası)
    if 'val_x' not in st.session_state: st.session_state.val_x = 50
    if 'val_y' not in st.session_state: st.session_state.val_y = 50
    if 'val_w' not in st.session_state: st.session_state.val_w = 200
    if 'val_h' not in st.session_state: st.session_state.val_h = 200
    if 'ratio_str' not in st.session_state: st.session_state.ratio_str = "15:17"

    # --- 2. GÖRSEL YÜKLEME ---
    referans_mockup = st.file_uploader("Boş Mockup Yükle", type=["png", "jpg"], key="cropper_upload")
    
    if referans_mockup:
        ref_img = Image.open(referans_mockup)
        orj_genislik, orj_yukseklik = ref_img.size
        
        # --- ÖLÇEKLENDİRME ---
        HEDEF_YUKSEKLIK = 500
        olcek_orani = orj_yukseklik / HEDEF_YUKSEKLIK
        yeni_w = int(round(orj_genislik / olcek_orani))
        yeni_h = HEDEF_YUKSEKLIK
        
        cropper_gorseli = ref_img.resize((yeni_w, yeni_h), Image.Resampling.LANCZOS)
        
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

        # Sol Sütun: Kırpıcı Alanı
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
        
        # --- FAREDEN GELEN VERİLERİ YAKALA VE SADECE EKRANA YANSIT ---
        if box_coords:
            bx = int(round(box_coords['left']))
            by = int(round(box_coords['top']))
            bw = int(round(box_coords['width']))
            bh = int(round(box_coords['height']))
            
            # Eğer kullanıcı fareyle kutuyu hareket ettirdiyse, sayı kutularını güncelle
            if (bx != st.session_state.cur_x_w_h["x"] or 
                by != st.session_state.cur_x_w_h["y"] or 
                bw != st.session_state.cur_x_w_h["w"] or 
                bh != st.session_state.cur_x_w_h["h"]):
                
                st.session_state.cur_x_w_h = {"x": bx, "y": by, "w": bw, "h": bh}
                
                # Sayı kutularının içini fare konumuna eşitle (Ama manual_coords'a dokunmuyoruz!)
                st.session_state.val_x = bx
                st.session_state.val_y = by
                st.session_state.val_w = bw
                st.session_state.val_h = bh
        
        # Sağ Sütun: Sayı Giriş Kutuları
        with col_sag_bilgi:
            st.markdown("**Ekran Önizleme Pikselleri (Kırpıcı Boyutu):**")
            
            m_col1, m_col2 = st.columns(2)
            m_col1.number_input("Kırpıcı X", step=1, key="val_x", on_change=manual_update)
            m_col2.number_input("Kırpıcı Y", step=1, key="val_y", on_change=manual_update)
            
            m_col3, m_col4 = st.columns(2)
            m_col3.number_input("Kırpıcı Genişlik", step=1, key="val_w", on_change=manual_update)
            m_col4.number_input("Kırpıcı Yükseklik", step=1, key="val_h", on_change=manual_update)
            
            st.markdown("---")
            
            # Orijinal Boyut Çıktısı
            orj_x = int(round(st.session_state.cur_x_w_h["x"] * olcek_orani))
            orj_y = int(round(st.session_state.cur_x_w_h["y"] * olcek_orani))
            orj_w = int(round(st.session_state.cur_x_w_h["w"] * olcek_orani))
            orj_h = int(round(st.session_state.cur_x_w_h["h"] * olcek_orani))
            
            st.markdown("**Orijinal Çözünürlük Çıktısı:**")
            st.code(
                f"x_noktasi: {orj_x}\n"
                f"y_noktasi: {orj_y}\n"
                f"genislik: {orj_w}\n"
                f"yukseklik: {orj_h}"
            )
            
