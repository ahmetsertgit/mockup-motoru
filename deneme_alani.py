# deneme_alani.py
import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

def calistir():
    st.header("📐 Mockup Baskı Yerleşimi")
    st.markdown("---")
    
    # --- 1. HAFIZA BAŞLANGIÇ AYARLARI ---
    if 'coords' not in st.session_state:
        st.session_state.coords = {"x": 50, "y": 50, "w": 200, "h": 200}
        
    # Kırpıcının farenin hareketinden etkilenmeyen SAF İLK KOORDİNATI
    if 'cropper_initial_coords' not in st.session_state:
        st.session_state.cropper_initial_coords = (50, 250, 50, 250) # xl, xr, yt, yb
        
    # Sayı kutularının Streamlit iç hafıza kayıtları
    if 'input_x' not in st.session_state:
        st.session_state['input_x'] = 50
        st.session_state['input_y'] = 50
        st.session_state['input_w'] = 200
        st.session_state['input_h'] = 200
        
    if 'cropper_version' not in st.session_state:
        st.session_state.cropper_version = 0

    # --- 2. GÖRSEL YÜKLEME ---
    referans_mockup = st.file_uploader("Boş Mockup Yükle", type=["png", "jpg"], key="cropper_upload")
    
    if referans_mockup:
        ref_img = Image.open(referans_mockup)
        orj_genislik, orj_yukseklik = ref_img.size
        
        # --- DİNAMİK ÖLÇEKLENDİRME ---
        HEDEF_YUKSEKLIK = 500
        olcek_orani = orj_yukseklik / HEDEF_YUKSEKLIK
        
        yeni_w = int(round(orj_genislik / olcek_orani))
        yeni_h = HEDEF_YUKSEKLIK
        
        cropper_gorseli = ref_img.resize((yeni_w, yeni_h), Image.Resampling.LANCZOS)
        
        # --- YAN YANA DÜZEN ---
        col_sol_gorsel, col_sag_bilgi = st.columns([65, 35])
        
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
                    st.error("❌ Geçersiz format!")
            
            st.markdown("---")

        # Sol Sütun: Kırpıcı Alanı
        with col_sol_gorsel:
            # DÖNGÜYÜ KIRAN EN KRİTİK NOKTA: default_coords artık farenin hareketine göre DEĞİŞMİYOR, sabit kalıyor!
            box_coords = st_cropper(
                cropper_gorseli, 
                realtime_update=True, 
                box_color='blue', 
                aspect_ratio=aspect_ratio, 
                return_type='box',
                default_coords=st.session_state.cropper_initial_coords,
                key=f"cropper_{st.session_state.cropper_version}",
                should_resize_image=False
            )
        
        # --- FAREDEN GELEN DEĞİŞİKLİKLERİ YAKALA VE KUTULARA YANSIT ---
        if box_coords:
            b_x = int(round(box_coords['left']))
            b_y = int(round(box_coords['top']))
            b_w = int(round(box_coords['width']))
            b_h = int(round(box_coords['height']))
            
            # Eğer gerçekten tamsayı bazında bir hareket varsa hafızayı güncelle
            if (b_x != st.session_state.coords["x"] or 
                b_y != st.session_state.coords["y"] or 
                b_w != st.session_state.coords["w"] or 
                b_h != st.session_state.coords["h"]):
                
                st.session_state.coords["x"] = b_x
                st.session_state.coords["y"] = b_y
                st.session_state.coords["w"] = b_w
                st.session_state.coords["h"] = b_h                   
                
                # Sayı kutularının iç değerlerini farenin bıraktığı yere eşitle
                st.session_state["input_x"] = b_x
                st.session_state["input_y"] = b_y
                st.session_state["input_w"] = b_w
                st.session_state["input_h"] = b_h
        
        # Sağ Sütun Alt Kısım: Sayı Giriş Kutuları
        with col_sag_bilgi:
            st.markdown("**Ekran Önizleme Pikselleri (Kırpıcı Boyutu):**")
            
            m_col1, m_col2 = st.columns(2)
            # value= parametresini sildik, Streamlit doğrudan 'key' üzerinden hafızadan besleniyor
            x_son = m_col1.number_input("Kırpıcı X", step=1, key="input_x")
            y_son = m_col2.number_input("Kırpıcı Y", step=1, key="input_y")
            
            m_col3, m_col4 = st.columns(2)
            w_son = m_col3.number_input("Kırpıcı Genişlik", step=1, key="input_w")
            h_son = m_col4.number_input("Kırpıcı Yükseklik", step=1, key="input_h")
            
            # --- KLAVYEDEN ELLE BİR SAYI GİRİLİRSE TETİKLE ---
            if (x_son != st.session_state.coords["x"] or 
                y_son != st.session_state.coords["y"] or 
                w_son != st.session_state.coords["w"] or 
                h_son != st.session_state.coords["h"]):
                
                # Merkez hafızayı güncelle
                st.session_state.coords["x"] = x_son
                st.session_state.coords["y"] = y_son
                st.session_state.coords["w"] = w_son
                st.session_state.coords["h"] = h_son
                
                # Kırpıcının yeni başlangıç noktasını elinle girdiğin verilere ayarla
                xl = x_son
                xr = x_son + w_son
                yt = y_son
                yb = y_son + h_son
                st.session_state.cropper_initial_coords = (xl, xr, yt, yb)
                
                # Sadece klavyeyle müdahale edildiği için kırpıcıyı yeni konumuna ışınla
                st.session_state.cropper_version += 1
                st.rerun()
            
            st.markdown("---")
            
            # --- GERÇEK ÇÖZÜNÜRLÜK ÇIKTISI ---
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
