# deneme_alani.py
import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

def calistir():
    st.header("📐 Mockup Baskı Yerleşimi")
    st.markdown("---")
    
    # --- 1. KESİNTİSİZ SENKRONİZASYON HAFIZASI ---
    if 'coords' not in st.session_state:
        st.session_state.coords = {"x": 105, "y": 157, "w": 323, "h": 366}
    if 'cropper_version' not in st.session_state:
        st.session_state.cropper_version = 0

    # --- 2. GÖRSEL YÜKLEME ---
    referans_mockup = st.file_uploader("Boş Mockup Yükle", type=["png", "jpg"], key="cropper_upload")
    
    if referans_mockup:
        ref_img = Image.open(referans_mockup)
        orj_genislik, orj_yukseklik = ref_img.size
        
        # --- DİNAMİK ÖLÇEKLENDİRME MANTIĞI ---
        HEDEF_YUKSEKLIK = 500
        if orj_yukseklik > HEDEF_YUKSEKLIK:
            olcek_orani = HEDEF_YUKSEKLIK / orj_yukseklik
            yeni_w = int(orj_genislik * olcek_orani)
            yeni_h = HEDEF_YUKSEKLIK
            cropper_gorseli = ref_img.resize((yeni_w, yeni_h), Image.Resampling.LANCZOS)
        else:
            olcek_orani = 1.0
            cropper_gorseli = ref_img
        
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

        # Hafızadaki orijinal piksel durumunu ekrandaki önizleme ölçeğine çevir
        xl = int(st.session_state.coords["x"] * olcek_orani)
        xr = int((st.session_state.coords["x"] + st.session_state.coords["w"]) * olcek_orani)
        yt = int(st.session_state.coords["y"] * olcek_orani)
        yb = int((st.session_state.coords["y"] + st.session_state.coords["h"]) * olcek_orani)
        default_coords = (xl, xr, yt, yb)
        
        # Sol sütun: Görsel kırpma alanı
        with col_sol_gorsel:
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
        
        # [YUVARLAMA KORUMASI] Fareden gelen hareketi analiz et
        if box_coords:
            # Mevcut hafızadaki değerlerin ekrandaki teorik pikselleri
            current_xl = int(st.session_state.coords["x"] * olcek_orani)
            current_yt = int(st.session_state.coords["y"] * olcek_orani)
            current_wl = int(st.session_state.coords["w"] * olcek_orani)
            current_hl = int(st.session_state.coords["h"] * olcek_orani)
            
            # Eğer fareden gelen değer ekrandaki kareden GERÇEKTEN farklıysa (Fare taşındıysa)
            if (box_coords['left'] != current_xl or 
                box_coords['top'] != current_yt or 
                box_coords['width'] != current_wl or 
                box_coords['height'] != current_hl):
                
                # Sadece bu durumda fare koordinatını ana hafızaya kaydet
                st.session_state.coords["x"] = int(box_coords['left'] / olcek_orani)
                st.session_state.coords["y"] = int(box_coords['top'] / olcek_orani)
                st.session_state.coords["w"] = int(box_coords['width'] / olcek_orani)
                st.session_state.coords["h"] = int(box_coords['height'] / olcek_orani)
        
        # Sağ sütun alt kısım: Sayı Giriş Kutuları
        with col_sag_bilgi:
            st.markdown("**Orijinal Çözünürlük Pikselleri:**")
            
            m_col1, m_col2 = st.columns(2)
            x_son = m_col1.number_input("x_noktasi (X)", value=st.session_state.coords["x"], step=1, key="input_x")
            y_son = m_col2.number_input("y_noktasi (Y)", value=st.session_state.coords["y"], step=1, key="input_y")
            
            m_col3, m_col4 = st.columns(2)
            w_son = m_col3.number_input("genislik (G)", value=st.session_state.coords["w"], step=1, key="input_w")
            h_son = m_col4.number_input("yukseklik (H)", value=st.session_state.coords["h"], step=1, key="input_h")
            
            # Eğer kullanıcı kutulardan bir sayıyı ELLE değiştirdiyse tetikle
            if (x_son != st.session_state.coords["x"] or 
                y_son != st.session_state.coords["y"] or 
                w_son != st.session_state.coords["w"] or 
                h_son != st.session_state.coords["h"]):
                
                st.session_state.coords["x"] = x_son
                st.session_state.coords["y"] = y_son
                st.session_state.coords["w"] = w_son
                st.session_state.coords["h"] = h_son
                # Kırpıcıyı yeni konuma ışınlamak için sürüm değiştir ve sayfayı güvenli tetikle
                st.session_state.cropper_version += 1
                st.rerun()
            
            st.markdown("---")
            
            # Kopyalama alanı
            st.code(
                f"x_noktasi: {st.session_state.coords['x']}\n"
                f"y_noktasi: {st.session_state.coords['y']}\n"
                f"genislik: {st.session_state.coords['w']}\n"
                f"yukseklik: {st.session_state.coords['h']}"
            )
