# deneme_alani.py
import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

def calistir():
    st.header("📐 Mockup Baskı Yerleşimi")
    st.markdown("---")
    
    # Hafıza (Session State) Tanımlamaları - Sayıların fare tarafından ezilmesini önler
    if 'prev_mouse_coords' not in st.session_state:
        st.session_state.prev_mouse_coords = None
    if 'coords' not in st.session_state:
        st.session_state.coords = {"x": 0, "y": 0, "w": 100, "h": 100}
    
    # 1. GÖRSEL YÜKLEME
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
        
        # Sol sütun: Görsel kırpma alanı
        with col_sol_gorsel:
            box_coords = st_cropper(
                cropper_gorseli, 
                realtime_update=True, 
                box_color='blue', 
                aspect_ratio=aspect_ratio, 
                return_type='box'
            )
        
        # Akıllı Senkronizasyon Bloğu
        if box_coords:
            current_mouse = (box_coords['left'], box_coords['top'], box_coords['width'], box_coords['height'])
            
            # Eğer kullanıcı fareyle yeni bir yer seçtiyse hafızayı fareye göre güncelle
            if current_mouse != st.session_state.prev_mouse_coords:
                st.session_state.coords["x"] = int(box_coords['left'] / olcek_orani)
                st.session_state.coords["y"] = int(box_coords['top'] / olcek_orani)
                st.session_state.coords["w"] = int(box_coords['width'] / olcek_orani)
                st.session_state.coords["h"] = int(box_coords['height'] / olcek_orani)
                st.session_state.prev_mouse_coords = current_mouse
        
        # Sağ sütun alt kısım: Değiştirilebilir Piksel Kutuları ve Çıktı
        with col_sag_bilgi:
            st.markdown("**Orijinal Çözünürlük Pikselleri:**")
            
            # Girdi kutuları değerleri artık bağımsız hafıza hücresinden okuyor
            m_col1, m_col2 = st.columns(2)
            x_son = m_col1.number_input("x_noktasi (X)", value=st.session_state.coords["x"], step=1)
            y_son = m_col2.number_input("y_noktasi (Y)", value=st.session_state.coords["y"], step=1)
            
            m_col3, m_col4 = st.columns(2)
            w_son = m_col3.number_input("genislik (G)", value=st.session_state.coords["w"], step=1)
            h_son = m_col4.number_input("yukseklik (H)", value=st.session_state.coords["h"], step=1)
            
            # Kutularda elinle yaptığın değişiklikleri hafızaya geri işle
            st.session_state.coords["x"] = x_son
            st.session_state.coords["y"] = y_son
            st.session_state.coords["w"] = w_son
            st.session_state.coords["h"] = h_son
            
            st.markdown("---")
            
            # Kopyalanacak alan, üstteki kutulara yazdığın en son nihai pikselleri basar
            st.code(
                f"x_noktasi: {x_son}\n"
                f"y_noktasi: {y_son}\n"
                f"genislik: {w_son}\n"
                f"yukseklik: {h_son}"
            )
