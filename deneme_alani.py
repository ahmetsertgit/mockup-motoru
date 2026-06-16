# deneme_alani.py
import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

def calistir():
    st.header("📐 Mockup Baskı Yerleşimi")
    st.markdown("---")
    
    # --- 1. ÇİFT YÖNLÜ SENKRONİZASYON HAFIZA YÖNETİMİ ---
    if 'coords' not in st.session_state:
        st.session_state.coords = {"x": 105, "y": 157, "w": 323, "h": 366}
    if 'cropper_version' not in st.session_state:
        st.session_state.cropper_version = 0

    # Sayı kutularının başlangıç değerlerini hafıza ile eşleme
    if 'num_x' not in st.session_state: st.session_state.num_x = st.session_state.coords["x"]
    if 'num_y' not in st.session_state: st.session_state.num_y = st.session_state.coords["y"]
    if 'num_w' not in st.session_state: st.session_state.num_w = st.session_state.coords["w"]
    if 'num_h' not in st.session_state: st.session_state.num_h = st.session_state.coords["h"]

    # Kullanıcı kutulardan birine elle sayı girdiğinde çalışacak fonksiyon (Callback)
    def on_input_change():
        st.session_state.coords["x"] = st.session_state.num_x
        st.session_state.coords["y"] = st.session_state.num_y
        st.session_state.coords["w"] = st.session_state.num_w
        st.session_state.coords["h"] = st.session_state.num_h
        # Elle sayı girildiğinde cropper bileşenini tarayıcıda yeniden çizilmeye (re-mount) zorlar
        st.session_state.cropper_version += 1

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

        # Hafızadaki orijinal piksel koordinatlarını ekran ölçeğine çevirip cropper'a besliyoruz
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
                default_coords=default_coords, # Kutulardan girilen değeri ekrana basar
                key=f"cropper_{st.session_state.cropper_version}", # Sürüm değiştikçe görseli tetikler
                should_resize_image=False
            )
        
        # Eğer kullanıcı fareyle sürükleme yaptıysa kutuları sessizce güncelle
        if box_coords:
            x_orj = int(box_coords['left'] / olcek_orani)
            y_orj = int(box_coords['top'] / olcek_orani)
            w_orj = int(box_coords['width'] / olcek_orani)
            h_orj = int(box_coords['height'] / olcek_orani)
            
            # Fare hareketi hafızadan farklıysa, son durumu güncelle
            if (x_orj != st.session_state.coords["x"] or 
                y_orj != st.session_state.coords["y"] or 
                w_orj != st.session_state.coords["w"] or 
                h_orj != st.session_state.coords["h"]):
                
                st.session_state.coords["x"] = x_orj
                st.session_state.coords["y"] = y_orj
                st.session_state.coords["w"] = w_orj
                st.session_state.coords["h"] = h_orj
                
                # Sayı girdi kutularının içindeki rakamları da farenin yerine eşitle
                st.session_state.num_x = x_orj
                st.session_state.num_y = y_orj
                st.session_state.num_w = w_orj
                st.session_state.num_h = h_orj
        
        # Sağ sütun alt kısım: Değiştirilebilir Piksel Kutuları ve Çıktı
        with col_sag_bilgi:
            st.markdown("**Orijinal Çözünürlük Pikselleri:**")
            
            # Girdi kutuları artık tetikleyici (on_change) fonksiyonumuza bağlı
            m_col1, m_col2 = st.columns(2)
            m_col1.number_input("x_noktasi (X)", key="num_x", on_change=on_input_change, step=1)
            m_col2.number_input("y_noktasi (Y)", key="num_y", on_change=on_input_change, step=1)
            
            m_col3, m_col4 = st.columns(2)
            m_col3.number_input("genislik (G)", key="num_w", on_change=on_input_change, step=1)
            m_col4.number_input("yukseklik (H)", key="num_h", on_change=on_input_change, step=1)
            
            st.markdown("---")
            
            # Kopyalanacak alan, her iki kaynaktan (Klavye veya Fare) süzülen en net güncel halini gösterir
            st.code(
                f"x_noktasi: {st.session_state.coords['x']}\n"
                f"y_noktasi: {st.session_state.coords['y']}\n"
                f"genislik: {st.session_state.coords['w']}\n"
                f"yukseklik: {st.session_state.coords['h']}"
            )
