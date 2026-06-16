# deneme_alani.py
import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

def calistir():
    st.header("📐 Mockup Baskı Yerleşimi")
    st.markdown("---")
    
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
        
        # Sağ sütun alt kısım: Değiştirilebilir Piksel Kutuları ve Çıktı
        with col_sag_bilgi:
            if box_coords:
                x_orj = int(box_coords['left'] / olcek_orani)
                y_orj = int(box_coords['top'] / olcek_orani)
                w_orj = int(box_coords['width'] / olcek_orani)
                h_orj = int(box_coords['height'] / olcek_orani)
                
                st.markdown("**Orijinal Çözünürlük Pikselleri:**")
                
                # Değerleri elle değiştirebilmen için input kutularına çevrildi
                m_col1, m_col2 = st.columns(2)
                x_son = m_col1.number_input("x_noktasi (X)", value=x_orj, step=1)
                y_son = m_col2.number_input("y_noktasi (Y)", value=y_orj, step=1)
                
                m_col3, m_col4 = st.columns(2)
                w_son = m_col3.number_input("genislik (G)", value=w_orj, step=1)
                h_son = m_col4.number_input("yukseklik (H)", value=h_orj, step=1)
                
                st.markdown("---")
                
                # E-tabloya kopyalanacak alan, üstteki kutulardan girilen son değerleri alır
                st.code(
                    f"x_noktasi: {x_son}\n"
                    f"y_noktasi: {y_son}\n"
                    f"genislik: {w_son}\n"
                    f"yukseklik: {h_son}"
                )
