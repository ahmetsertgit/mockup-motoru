# deneme_alani.py
import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

def calistir():
    st.header("📐 Mockup Baskı Yerleşimi")
    st.markdown("---")
    
    # --- 1. KIRPICI TABANLI SAF HAFIZA (Değerler doğrudan kırpıcı pikselidir) ---
    if 'coords' not in st.session_state:
        st.session_state.coords = {"x": 50, "y": 50, "w": 200, "h": 200}
    if 'cropper_version' not in st.session_state:
        st.session_state.cropper_version = 0

    # --- 2. GÖRSEL YÜKLEME ---
    referans_mockup = st.file_uploader("Boş Mockup Yükle", type=["png", "jpg"], key="cropper_upload")
    
    if referans_mockup:
        ref_img = Image.open(referans_mockup)
        orj_genislik, orj_yukseklik = ref_img.size
        
        # --- DİNAMİK ÖLÇEKLENDİRME VE YUVARLAMA ---
        HEDEF_YUKSEKLIK = 500
        
        # Ölçek oranını orijinal boyuta dönmek için çarpan olarak kurguluyoruz
        olcek_orani = orj_yukseklik / HEDEF_YUKSEKLIK
        
        # yeni_w değerini kesin olarak tamsayıya yuvarlıyoruz
        yeni_w = int(round(orj_genislik / olcek_orani))
        yeni_h = HEDEF_YUKSEKLIK
        
        # Görseli kırpıcı boyutuna tam oturtup arka plan katmanı yapıyoruz
        cropper_gorseli = ref_img.resize((yeni_w, yeni_h), Image.Resampling.LANCZOS)
        
        # --- YAN YANA DÜZEN ---
        col_sol_gorsel, col_sag_bilgi = st.columns([65, 35])
        
        # Sağ sütun üst kısım: En/Boy kilit girişi
        with col_sag_bilgi:
            ratio_input = st.text_input("🔒 En : Boy Oranı Kilidi (Örn: 15:17 veya serbest çizim için boş bırakın)", value="15:17")
            
            aspect_ratio = None
            if ratio_input and ":" in ratio_input:
                try:
                    parts = ratio_input.split(":")
                    w_ratio = float(parts[0])
                    h_ratio = float(parts[1])
                    if w_ratio > 0 and h_ratio > 0:
                        aspect_ratio = (w_ratio, h_ratio)
                        st.caption(f"🎯 Oran **{ratio_input}** olarak kilitlendi.")
                except ValueError:
                    st.error("❌ Geçersiz format! Lütfen '15:17' şeklinde girin.")
            
            st.markdown("---")

        # Hafızadaki kırpıcı piksellerini doğrudan çizime gönderiyoruz (Hesaplama yok)
        xl = st.session_state.coords["x"]
        xr = st.session_state.coords["x"] + st.session_state.coords["w"]
        yt = st.session_state.coords["y"]
        yb = st.session_state.coords["y"] + st.session_state.coords["h"]
        default_coords = (xl, xr, yt, yb)
        
        # Sol sütun: Görsel kırpma alanı
        with col_sol_gorsel:
            # should_resize_image=False ile görseli ve şeffaf kırpıcı tuvalini üst üste eşitliyoruz
            box_coords = st_cropper(
                cropper_gorseli, 
                realtime_update=True, 
                box_color='blue', 
                aspect_ratio=aspect_ratio, 
                return_type='box',
                default_coords=default_coords,
                key=f"cropper_{st.session_state.cropper_version}",
                should_resize_image=False
            )
        
        # Fareden gelen ham kırpıcı piksellerini doğrudan hafızaya eşitliyoruz
        if box_coords:
            if (box_coords['left'] != st.session_state.coords["x"] or 
                box_coords['top'] != st.session_state.coords["y"] or 
                box_coords['width'] != st.session_state.coords["w"] or 
                box_coords['height'] != st.session_state.coords["h"]):
                
                st.session_state.coords["x"] = box_coords['left']
                st.session_state.coords["y"] = box_coords['top']
                st.session_state.coords["w"] = box_coords['width']
                st.session_state.coords["h"] = box_coords['height']                   
                st.session_state.cropper_version += 1
                st.rerun()
        
        # Sağ sütun alt kısım: Kırpıcı Boyutundaki Sayı Giriş Kutuları
        with col_sag_bilgi:
            st.markdown("**Ekran Önizleme Pikselleri (Kırpıcı Boyutu):**")
            
            m_col1, m_col2 = st.columns(2)
            x_son = m_col1.number_input("Kırpıcı X", value=box_coords['left'], step=1, key="input_x")
            y_son = m_col2.number_input("Kırpıcı Y", value=box_coords['top'], step=1, key="input_y")
            
            m_col3, m_col4 = st.columns(2)
            w_son = m_col3.number_input("Kırpıcı Genişlik", value=box_coords['width'], step=1, key="input_w")
            h_son = m_col4.number_input("Kırpıcı Yükseklik", value=box_coords['height'], step=1, key="input_h")
            
            # Kutulardan elle müdahale edilirse hafızayı güncelle ve çizimi zorla
            if (x_son != st.session_state.coords["x"] or 
                y_son != st.session_state.coords["y"] or 
                w_son != st.session_state.coords["w"] or 
                h_son != st.session_state.coords["h"]):
                
                st.session_state.coords["x"] = x_son
                st.session_state.coords["y"] = y_son
                st.session_state.coords["w"] = w_son
                st.session_state.coords["h"] = h_son
                st.session_state.cropper_version += 1
                st.rerun()
            
            st.markdown("---")
            
            # --- 3. SON ADIM: GERÇEK BOYUTLARA ÖLÇEKLENDİRME VE YUVARLAMA ---
            orj_x = int(round(st.session_state.coords["x"] * olcek_orani))
            orj_y = int(round(st.session_state.coords["y"] * olcek_orani))
            orj_w = int(round(st.session_state.coords["w"] * olcek_orani))
            orj_h = int(round(st.session_state.coords["h"] * olcek_orani))
            
            st.markdown("**Orijinal Çözünürlük Çıktısı:**")
            st.code(
                f"x_noktasi: {orj_x}\n"
                f"y_noktasi: {orj_y}\n"
                f"genislik: {orj_w}\n"
                f"yukseklik: {orj_h}"
            )
