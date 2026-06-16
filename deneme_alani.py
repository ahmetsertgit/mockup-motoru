# deneme_alani.py
import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

def manual_update(olcek_orani):
    """Kutulara doğrudan ORİJİNAL piksel değerleri girildiğinde tetiklenir."""
    # 1. Giriş kutularındaki orijinal çözünürlük değerlerini oku
    orj_x = st.session_state.val_x
    orj_y = st.session_state.val_y
    orj_w = st.session_state.val_w
    orj_h = st.session_state.val_h
    
    # 2. Kırpıcının boyutunu hesaplarken değerleri tekrar ölçek oranına BÖL
    mw = orj_w / olcek_orani
    mh = orj_h / olcek_orani
    mx = orj_x / olcek_orani
    my = orj_y / olcek_orani
    
    # En-boy oranı kilidi aktifse, hangi kutunun değiştiğine bakıp diğerini oranla hesapla
    ratio_str = st.session_state.get('ratio_str', '15:17')
    if ratio_str and ":" in ratio_str:
        try:
            parts = ratio_str.split(":")
            w_r, h_r = float(parts[0]), float(parts[1])
            
            # Genişlik mi değişti yoksa yükseklik mi? (Ekran pikselleri üzerinden kıyaslama)
            if abs(mw - st.session_state.cur_x_w_h["w"]) > 0.01:
                mh = mw * (h_r / w_r)
                # Karşı kutunun orijinal piksel değerini de güncelle ki kutu içi anında değişsin
                st.session_state.val_h = int(round(mh * olcek_orani))
            elif abs(mh - st.session_state.cur_x_w_h["h"]) > 0.01:
                mw = mh * (w_r / h_r)
                st.session_state.val_w = int(round(mw * olcek_orani))
        except ValueError:
            pass
    
    # Kırpıcının ihtiyaç duyduğu ekran koordinatlarını tam sayıya yuvarla
    mx_int = int(round(mx))
    my_int = int(round(my))
    mw_int = int(round(mw))
    mh_int = int(round(mh))
    
    # Hafızayı ve kırpıcıyı yeni konumuna ışınla
    st.session_state.cur_x_w_h = {"x": mx_int, "y": my_int, "w": mw_int, "h": mh_int}
    st.session_state.manual_coords = (mx_int, mx_int + mw_int, my_int, my_int + mh_int)
    st.session_state.cropper_version += 1

def calistir():
    st.header("📐 Mockup Baskı Yerleşimi")
    st.markdown("---")
    
    # --- HAFIZA BAŞLANGIÇ AYARLARI ---
    if 'manual_coords' not in st.session_state:
        st.session_state.manual_coords = (50, 250, 50, 250)
    if 'cropper_version' not in st.session_state:
        st.session_state.cropper_version = 0
    if 'cur_x_w_h' not in st.session_state:
        st.session_state.cur_x_w_h = {"x": 50, "y": 50, "w": 200, "h": 200}
    if 'ratio_str' not in st.session_state:
        st.session_state.ratio_str = "15:17"

    # --- GÖRSEL YÜKLEME ---
    referans_mockup = st.file_uploader("Boş Mockup Yükle", type=["png", "jpg"], key="cropper_upload")
    
    if referans_mockup:
        ref_img = Image.open(referans_mockup)
        orj_genislik, orj_yukseklik = ref_img.size
        
        # --- ÖLÇEKLENDİRME ESASLARI ---
        HEDEF_YUKSEKLIK = 500
        olcek_orani = orj_yukseklik / HEDEF_YUKSEKLIK
        yeni_w = int(round(orj_genislik / olcek_orani))
        yeni_h = HEDEF_YUKSEKLIK
        
        cropper_gorseli = ref_img.resize((yeni_w, yeni_h), Image.Resampling.LANCZOS)
        
        # Giriş kutularının ilk açılış değerlerini orijinal piksel cinsinden ata (Ekran Değeri * Ölçek Oranı)
        if 'val_x' not in st.session_state: st.session_state.val_x = int(round(50 * olcek_orani))
        if 'val_y' not in st.session_state: st.session_state.val_y = int(round(50 * olcek_orani))
        if 'val_w' not in st.session_state: st.session_state.val_w = int(round(200 * olcek_orani))
        if 'val_h' not in st.session_state: st.session_state.val_h = int(round(200 * olcek_orani))
        
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

        # Sol Sütun: Kırpıcı Alanı
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
        
        # --- FAREDEN GELEN VERİLERİ ORİJİNAL ÇÖZÜNÜRLÜĞE ÇEVİRİP KUTULARA YAZ ---
        if box_coords:
            bx = int(round(box_coords['left']))
            by = int(round(box_coords['top']))
            bw = int(round(box_coords['width']))
            bh = int(round(box_coords['height']))
            
            # Fare hareket ettiyse tetiklenir
            if (bx != st.session_state.cur_x_w_h["x"] or 
                by != st.session_state.cur_x_w_h["y"] or 
                bw != st.session_state.cur_x_w_h["w"] or 
                bh != st.session_state.cur_x_w_h["h"]):
                
                st.session_state.cur_x_w_h = {"x": bx, "y": by, "w": bw, "h": bh}
                
                # Sayı kutularının iç değerlerini ölçek oranıyla ÇARPARAK güncelle (Kullanıcının istediği mantık)
                st.session_state.val_x = int(round(bx * olcek_orani))
                st.session_state.val_y = int(round(by * olcek_orani))
                st.session_state.val_w = int(round(bw * olcek_orani))
                st.session_state.val_h = int(round(bh * olcek_orani))
        
        # Sağ Sütun: Sayı Giriş Kutuları (Artık Doğrudan Gerçek Çözünürlük Değerleri Gösterilir)
        with col_sag_bilgi:
            st.markdown("**Orijinal Çözünürlük Pikselleri (Doğrudan Düzenlenebilir):**")
            
            m_col1, m_col2 = st.columns(2)
            m_col1.number_input("Orijinal X", step=1, key="val_x", on_change=manual_update, args=(olcek_orani,))
            m_col2.number_input("Orijinal Y", step=1, key="val_y", on_change=manual_update, args=(olcek_orani,))
            
            m_col3, m_col4 = st.columns(2)
            m_col3.number_input("Orijinal Genişlik", step=1, key="val_w", on_change=manual_update, args=(olcek_orani,))
            m_col4.number_input("Orijinal Yükseklik", step=1, key="val_h", on_change=manual_update, args=(olcek_orani,))
            
            st.markdown("---")
            
            # Kod çıktısını doğrudan session_state.val_w'lardan besliyoruz çünkü onlar zaten nihai orijinal pikselleri tutuyor
            st.markdown("**Nihai Çıktı Değerleri:**")
            st.code(
                f"x_noktasi: {st.session_state.val_x}\n"
                f"y_noktasi: {st.session_state.val_y}\n"
                f"genislik: {st.session_state.val_w}\n"
                f"yukseklik: {st.session_state.val_h}"
            )
