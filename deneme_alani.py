# deneme_alani.py
import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

def manual_update(olcek_orani, tetikleyen_kutu):
    """
    Kullanıcı arayüzdeki sayı kutularına ELLE giriş yaptığında çalışır.
    """
    orj_x = st.session_state.val_x
    orj_y = st.session_state.val_y
    orj_w = st.session_state.val_w
    orj_h = st.session_state.val_h
    
    ratio_str = st.session_state.get('ratio_str', '15:17')
    if ratio_str and ":" in ratio_str:
        try:
            parts = ratio_str.split(":")
            w_r, h_r = float(parts[0]), float(parts[1])
            
            if tetikleyen_kutu == "w":
                orj_h = orj_w * (h_r / w_r)
                st.session_state.val_h = int(round(orj_h))
            elif tetikleyen_kutu == "h":
                orj_w = orj_h * (w_r / h_r)
                st.session_state.val_w = int(round(orj_w))
                
        except ValueError:
            pass
            
    guncel_w = st.session_state.val_w
    guncel_h = st.session_state.val_h
    
    mw = guncel_w / olcek_orani
    mh = guncel_h / olcek_orani
    mx = orj_x / olcek_orani
    my = orj_y / olcek_orani
    
    mx_int = int(round(mx))
    my_int = int(round(my))
    mw_int = int(round(mw))
    mh_int = int(round(mh))
    
    # Yeni manuel değerleri referans olarak kaydet
    st.session_state.cur_x_w_h = {"x": mx_int, "y": my_int, "w": mw_int, "h": mh_int}
    st.session_state.manual_coords = (mx_int, mx_int + mw_int, my_int, my_int + mh_int)
    st.session_state.cropper_version += 1

def calistir():
    st.header("📐 Mockup Baskı Yerleşimi")
    st.markdown("---")
    
    # --- [BAŞLANGIÇ AYARLARI VE STATE İLKLENDİRME] ---
    BASLANGIC_W = 150
    BASLANGIC_H = 170
    BASLANGIC_X = 50
    BASLANGIC_Y = 50
    
    if 'manual_coords' not in st.session_state:
        st.session_state.manual_coords = (BASLANGIC_X, BASLANGIC_X + BASLANGIC_W, BASLANGIC_Y, BASLANGIC_Y + BASLANGIC_H)
        
    if 'cropper_version' not in st.session_state:
        st.session_state.cropper_version = 0
        
    if 'cur_x_w_h' not in st.session_state:
        st.session_state.cur_x_w_h = {"x": BASLANGIC_X, "y": BASLANGIC_Y, "w": BASLANGIC_W, "h": BASLANGIC_H}
        
    if 'ratio_str' not in st.session_state:
        st.session_state.ratio_str = "15:17"

    # --- [GÖRSEL YÜKLEME] ---
    referans_mockup = st.file_uploader("Boş Mockup Yükle", type=["png", "jpg"], key="cropper_upload")
    
    if referans_mockup:
        if 'uploaded_file_id' not in st.session_state or st.session_state.uploaded_file_id != referans_mockup.file_id:
            ref_img = Image.open(referans_mockup)
            orj_genislik, orj_yukseklik = ref_img.size
            
            HEDEF_YUKSEKLIK = 500
            olcek_orani = orj_yukseklik / HEDEF_YUKSEKLIK
            yeni_w = int(round(orj_genislik / olcek_orani))
            yeni_h = HEDEF_YUKSEKLIK
            
            st.session_state.cropper_gorseli = ref_img.resize((yeni_w, yeni_h), Image.Resampling.LANCZOS)
            st.session_state.olcek_orani = olcek_orani
            st.session_state.uploaded_file_id = referans_mockup.file_id
        
        cropper_gorseli = st.session_state.cropper_gorseli
        olcek_orani = st.session_state.olcek_orani
        
        if 'val_x' not in st.session_state: st.session_state.val_x = int(round(BASLANGIC_X * olcek_orani))
        if 'val_y' not in st.session_state: st.session_state.val_y = int(round(BASLANGIC_Y * olcek_orani))
        if 'val_w' not in st.session_state: st.session_state.val_w = int(round(BASLANGIC_W * olcek_orani))
        if 'val_h' not in st.session_state: st.session_state.val_h = int(round(BASLANGIC_H * olcek_orani))
        
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
        
        # --- [TOLERANS (DEADZONE) MANTIĞI] ---
        if box_coords:
            bx = int(round(box_coords['left']))
            by = int(round(box_coords['top']))
            bw = int(
