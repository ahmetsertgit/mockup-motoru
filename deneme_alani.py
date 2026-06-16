import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

def manual_update(olcek_orani, tetikleyen_kutu):
    """
    [MANUEL GİRİŞ TETİKLEYİCİSİ]
    Kullanıcı arayüzdeki (UI) sayı kutularına ELLE bir orijinal piksel değeri girdiğinde çalışır.
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
            
            # Girilen değere göre diğer boyutu en-boy oranına uygun şekilde hesapla
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
    
    # Orijinal pikselleri ekrandaki piksellere (küçültülmüş hale) dönüştür
    mw = guncel_w / olcek_orani
    mh = guncel_h / olcek_orani
    mx = orj_x / olcek_orani
    my = orj_y / olcek_orani
    
    mx_int = int(round(mx))
    my_int = int(round(my))
    mw_int = int(round(mw))
    mh_int = int(round(mh))
    
    # Yeni manuel değerleri referans olarak kaydet (Tolerans kontrolü için)
    st.session_state.cur_x_w_h = {"x": mx_int, "y": my_int, "w": mw_int, "h": mh_int}
    st.session_state.manual_coords = (mx_int, mx_int + mw_int, my_int, my_int + mh_int)
    
    # Bileşeni programatik olarak yenilemek için versiyonu artır
    st.session_state.cropper_version += 1

def calistir():
    st.header("📐 Mockup Baskı Yerleşimi")
    st.markdown("---")
    
    # --- [BAŞLANGIÇ AYARLARI VE STATE İLKLENDİRME] ---
    BASLANGIC_W = 150
    BASLANGIC_H = 170
    BASLANGIC_X = 50
    BASLANGIC_Y = 50
