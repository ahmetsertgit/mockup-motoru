# deneme_alani.py
import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

def manual_update(olcek_orani, tetikleyen_kutu):
    """
    [MANUEL GİRİŞ TETİKLEYİCİSİ]
    Kullanıcı arayüzdeki (UI) sayı kutularına ELLE bir orijinal piksel değeri girdiğinde çalışır.
    'tetikleyen_kutu' parametresi değişimin hangi kutudan (x, y, w, h) geldiğini doğrudan söyler.
    """
    # 1. Session State üzerindeki güncel orijinal pikselleri oku
    orj_x = st.session_state.val_x
    orj_y = st.session_state.val_y
    orj_w = st.session_state.val_w
    orj_h = st.session_state.val_h
    
    # 2. En-Boy Oranı Kilidini kontrol et ve uyarla
    ratio_str = st.session_state.get('ratio_str', '15:17')
    if ratio_str and ":" in ratio_str:
        try:
            parts = ratio_str.split(":")
            w_r, h_r = float(parts[0]), float(parts[1])
            
            # Değişimi doğrudan tetikleyen kutuya göre hesapla
            if tetikleyen_kutu == "w":
                # Genişlik elle değiştiyse, yüksekliği orijinal pikseller üzerinden hesapla
                orj_h = orj_w * (h_r / w_r)
                st.session_state.val_h = int(round(orj_h))
            elif tetikleyen_kutu == "h":
                # Yükseklik elle değiştiyse, genişliği orijinal pikseller üzerinden hesapla
                orj_w = orj_h * (w_r / h_r)
                st.session_state.val_w = int(round(orj_w))
                
        except ValueError:
            pass # Geçersiz oran formatı girildiyse hesaplamayı atla
            
    # Session state'den en güncel (belki az önce üstte değişmiş) değerleri tekrar çekelim
    guncel_w = st.session_state.val_w
    guncel_h = st.session_state.val_h
    
    # 3. Orijinal pikselleri, ekrandaki küçük görselin piksel karşılıklarına dönüştür
    mw = guncel_w / olcek_orani
    mh = guncel_h / olcek_orani
    mx = orj_x / olcek_orani
    my = orj_y / olcek_orani
    
    # 4. Ekran piksellerini tam sayıya (Integer) yuvarla
    mx_int = int(round(mx))
    my_int = int(round(my))
    mw_int = int(round(mw))
    mh_int = int(round(mh))
    
    # 5. Hesaplanan ekran koordinatlarını referans hafızalara kaydet
    st.session_state.cur_x_w_h = {"x": mx_int, "y": my_int, "w": mw_int, "h": mh_int}
    st.session_state.manual_coords = (mx_int, mx_int + mw_int, my_int, my_int + mh_int)
    
    # 6. Bileşenin key parametresini değiştirmek için versiyonu artır (Bileşeni hard-resetler)
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

    # --- [GÖRSEL YÜKLEME VE CACHE/HAFIZA YÖNETİMİ] ---
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

        # --- [KIRPICI BİLEŞENİNİN ÇALIŞTIRILMASI] ---
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
        
        # --- [FARE HAREKETİ VE GERİ BESLEME (FEEDBACK) DÖNGÜSÜ ANAlİZİ] ---
        if box_coords:
            bx = int(round(box_coords['left']))
            by = int(round(box_coords['top']))
            bw = int(round(box_coords['width']))
            bh = int(round(box_coords['height']))
            
            if (bx != st.session_state.cur_x_w_h["x"] or 
                by != st.session_state.cur_x_w_h["y"] or 
                bw != st.session_state.cur_x_w_h["w"] or 
                bh != st.session_state.cur_x_w_h["h"]):
                
                st.session_state.cur_x_w_h = {"x": bx, "y": by, "w": bw, "h": bh}
                
                st.session_state.val_x = int(round(bx * olcek_orani))
                st.session_state.val_y = int(round(by * olcek_orani))
                st.session_state.val_w = int(round(bw * olcek_orani))
                st.session_state.val_h = int(round(bh * olcek_orani))
        
        # --- [KULLANICI GİRİŞ ARAYÜZÜ (SAYI KUTULARI)] ---
        with col_sag_bilgi:
            st.markdown("**Orijinal Çözünürlük Pikselleri (Doğrudan Düzenlenebilir):**")
            
            m_col1, m_col2 = st.columns(2)
            # Args kısmına tetikleyen kutunun kimliğini ("x", "y", "w", "h") gönderiyoruz
            m_col1.number_input("Orijinal X", step=1, key="val_x", on_change=manual_update, args=(olcek_orani, "x"))
            m_col2.number_input("Orijinal Y", step=1, key="val_y", on_change=manual_update, args=(olcek_orani, "y"))
            
            m_col3, m_col4 = st.columns(2)
            m_col3.number_input("Orijinal Genişlik", step=1, key="val_w", on_change=manual_update, args=(olcek_orani, "w"))
            m_col4.number_input("Orijinal Yükseklik", step=1, key="val_h", on_change=manual_update, args=(olcek_orani, "h"))
            
            st.markdown("---")
            
            # --- [ÇIKTI PANELİ] ---
            st.markdown("**Nihai Çıktı Değerleri:**")
            st.code(
                f"x_noktasi: {st.session_state.val_x}\n"
                f"y_noktasi: {st.session_state.val_y}\n"
                f"genislik: {st.session_state.val_w}\n"
                f"yukseklik: {st.session_state.val_h}"
            )
