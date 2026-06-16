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
        
        # --- DİNAMİK ÖLÇEKLENDİRME MANTIĞI ---
        # Görsel yüksekliği 500px'den büyükse, taşmayı önlemek için geçici olarak küçültüyoruz
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
        
        with col_sol_gorsel:
            # Hata veren max_height kaldırıldı, doğrudan optimize edilmiş görsele çalışıyor
            box_coords = st_cropper(
                cropper_gorseli, 
                realtime_update=True, 
                box_color='blue', 
                aspect_ratio=aspect_ratio, 
                return_type='box'
            )
        
        with col_sag_bilgi:
            if box_coords:
                st.success("🎉 Koordinatlar Hesaplandı")
                
                # Ekrandaki küçük görsel koordinatlarını, orijinal büyük görsele oranlıyoruz
                x_orj = int(box_coords['left'] / olcek_orani)
                y_orj = int(box_coords['top'] / olcek_orani)
                w_orj = int(box_coords['width'] / olcek_orani)
                h_orj = int(box_coords['height'] / olcek_orani)
                
                # Doğrudan kopyalayıp tabloya yapıştıracağın temiz kod bloğu
                st.markdown("**E-Tabloya Kopyalamak İçin Değerler:**")
                st.code(
                    f"x_noktasi: {x_orj}\n"
                    f"y_noktasi: {y_orj}\n"
                    f"genislik: {w_orj}\n"
                    f"yukseklik: {h_orj}"
                )
                
                st.markdown("---")
                st.markdown("**Orijinal Çözünürlük Pikselleri:**")
                
                # Sağ panel metrik gösterimi (Gerçek yüksek çözünürlük değerleri)
                m_col1, m_col2 = st.columns(2)
                m_col1.metric("x_noktasi (X)", x_orj)
                m_col2.metric("y_noktasi (Y)", y_orj)
                
                m_col3, m_col4 = st.columns(2)
                m_col3.metric("genislik (G)", w_orj)
                m_col4.metric("yukseklik (H)", h_orj)
