# deneme_alani.py
import streamlit as st
from PIL import Image, ImageDraw
from streamlit_cropper import st_cropper

def calistir():
    st.header("🧪 Alan Belirleme ve Koordinat Aracı")
    st.write("E-Tabloya gireceğiniz değerleri ister fareyle çizerek ister elle sayı girerek tespit edebilirsiniz.")
    
    referans_mockup = st.file_uploader("Boş Mockup Yükle", type=["png", "jpg"], key="cropper_upload")
    
    if referans_mockup:
        ref_img = Image.open(referans_mockup)
        orj_genislik, orj_yukseklik = ref_img.size
        
        st.info(f"📋 Yüklenen Görselin Orijinal Boyutu: {orj_genislik} x {orj_yukseklik} piksel")
        
        # Giriş Yöntemi Seçimi
        yontem = st.radio(
            "Koordinat Giriş Yöntemi Seçin:",
            ["🖱️ Fare ile Çizerek Belirle", "⌨️ Elle Sayı Girerek İnce Ayar Yap"],
            horizontal=True
        )
        
        st.markdown("---")
        
        # --- 1. YÖNTEM: FARE İLE ÇİZİM ---
        if yontem == "🖱️ Fare ile Çizerek Belirle":
            st.subheader("Görsel Üzerinde Kutuyu Sürükleyip Boyutlandırın")
            
            box_coords = st_cropper(ref_img, realtime_update=True, box_color='blue', return_type='box')
            
            if box_coords:
                st.success("🎉 Fare ile Seçilen Koordinatlar Hazır!")
                
                # Değerleri yan yana kutularda göster
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("x_noktasi (X)", box_coords['left'])
                col2.metric("y_noktasi (Y)", box_coords['top'])
                col3.metric("genislik (G)", box_coords['width'])
                col4.metric("yukseklik (Y)", box_coords['height'])
                
                # Tabloya kopyalamak için hazır kod bloğu
                st.markdown("**E-Tabloya Kopyalamak İçin Değerler:**")
                st.code(f"x_noktasi: {box_coords['left']}\ny_noktasi: {box_coords['top']}\ngenislik: {box_coords['width']}\nyukseklik: {box_coords['height']}")

        # --- 2. YÖNTEM: ELLE SAYI GİRİŞİ ---
        elif yontem == "⌨️ Elle Sayı Girerek İnce Ayar Yap":
            st.subheader("Milimetrik Ayar İçin Piksel Değerlerini Girin")
            
            # Giriş kutularını yan yana konumlandır
            col1, col2, col3, col4 = st.columns(4)
            
            x_input = col1.number_input("x_noktasi (Sol Uzaklık)", min_value=0, max_value=orj_genislik, value=100, step=1)
            y_input = col2.number_input("y_noktasi (Üst Uzaklık)", min_value=0, max_value=orj_yukseklik, value=100, step=1)
            w_input = col3.number_input("genislik (Genişlik)", min_value=1, max_value=orj_genislik, value=300, step=1)
            h_input = col4.number_input("yukseklik (Yükseklik)", min_value=1, max_value=orj_yukseklik, value=400, step=1)
            
            # Girilen sayılara göre görsel üzerine dinamik kutu çizme
            onizleme_gorseli = ref_img.copy().convert("RGBA")
            cizim = ImageDraw.Draw(onizleme_gorseli)
            
            # Kutunun sağ ve alt sınırlarını hesapla (Görsel dışına taşmasın)
            sag_sinir = min(x_input + w_input, orj_genislik)
            alt_sinir = min(y_input + h_input, orj_yukseklik)
            
            # Belirgin olması için kırmızı renkli kalın bir çerçeve çiziyoruz
            cizim.rectangle([x_input, y_input, sag_sinir, alt_sinir], outline="red", width=6)
            
            # Çizilen resmi ekranda göster
            st.image(onizleme_gorseli, caption="Elle Girilen Koordinatların Önizlemesi (Kırmızı Kutu)", use_container_width=True)
            
            st.success("🎉 Elle Girilen Koordinatlar Hazır!")
            st.markdown("**E-Tabloya Kopyalamak İçin Değerler:**")
            st.code(f"x_noktasi: {x_input}\ny_noktasi: {y_input}\ngenislik: {w_input}\nyukseklik: {h_input}")
