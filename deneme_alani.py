# deneme_alani.py
import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

def calistir():
    st.header("📐 En/Boy Kilitli Koordinat Aracı")
    st.write("Fareyle alanı belirleyebilir, sağ taraftaki panelden pikselleri anlık olarak takip edebilirsiniz.")
    
    # 1. EN/BOY ORANI GİRİŞİ
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
    
    # 2. GÖRSEL YÜKLEME
    referans_mockup = st.file_uploader("Boş Mockup Yükle", type=["png", "jpg"], key="cropper_upload")
    
    if referans_mockup:
        ref_img = Image.open(referans_mockup)
        orj_genislik, orj_yukseklik = ref_img.size
        st.info(f"📋 Yüklenen Görselin Orijinal Boyutu: {orj_genislik} x {orj_yukseklik} piksel")
        
        # --- YAN YANA DÜZEN (LİKİT KOLONLAR) ---
        # Sol kolon görsel için (%65 genişlik), Sağ kolon bilgiler için (%35 genişlik)
        col_sol_gorsel, col_sag_bilgi = st.columns([65, 35])
        
        with col_sol_gorsel:
            # max_height=500 parametresi ile dikeyde taşmayı tamamen engelledik
            box_coords = st_cropper(
                ref_img, 
                realtime_update=True, 
                box_color='blue', 
                aspect_ratio=aspect_ratio, 
                return_type='box',
                max_height=500 
            )
        
        with col_sag_bilgi:
            if box_coords:
                st.success("🎉 Koordinatlar Hesaplandı")
                
                # Doğrudan kopyalayıp tabloya yapıştıracağın temiz kod bloğu
                st.markdown("**E-Tabloya Kopyalamak İçin Değerler:**")
                st.code(
                    f"x_noktasi: {int(box_coords['left'])}\n"
                    f"y_noktasi: {int(box_coords['top'])}\n"
                    f"genislik: {int(box_coords['width'])}\n"
                    f"yukseklik: {int(box_coords['height'])}"
                )
                
                st.markdown("---")
                st.markdown("**Anlık Piksel Takibi:**")
                
                # Sağ panelde metrikleri 2x2 düzeninde şık bir şekilde listeleme
                m_col1, m_col2 = st.columns(2)
                m_col1.metric("x_noktasi (X)", int(box_coords['left']))
                m_col2.metric("y_noktasi (Y)", int(box_coords['top']))
                
                m_col3, m_col4 = st.columns(2)
                m_col3.metric("genislik (G)", int(box_coords['width']))
                m_col4.metric("yukseklik (H)", int(box_coords['height']))
