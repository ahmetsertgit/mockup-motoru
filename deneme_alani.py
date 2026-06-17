# deneme_alani.py
import streamlit as st
from PIL import Image, ImageDraw
import io
import math
from googleapiclient.http import MediaIoBaseDownload

def draw_rotated_rect(image, bx, by, bw, bh, angle_deg):
    """
    Ekrandaki mavi cropper kutusunun koordinatlarını ve açı değerini alarak,
    görselin üzerine anlık olarak DÖNDÜRÜLMÜŞ kırmızı gerçek baskı çerçevesini çizer.
    """
    if bw <= 0 or bh <= 0:
        return image
        
    # Kutunun merkez noktası
    cx = bx + bw / 2.0
    cy = by + bh / 2.0
    
    # Orijinal (dönmemiş) 4 köşe noktası
    corners = [
        (bx, by),
        (bx + bw, by),
        (bx + bw, by + bh),
        (bx, by + bh)
    ]
    
    angle_rad = math.radians(angle_deg)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    
    # Köşeleri merkez etrafında döndürme formülü
    rotated_corners = []
    for x, y in corners:
        nx = x - cx
        ny = y - cy
        rx = nx * cos_a - ny * sin_a + cx
        ry = nx * sin_a + ny * cos_a + cy
        rotated_corners.append((int(round(rx)), int(round(ry))))
        
    # Çizim katmanını oluştur
    draw = ImageDraw.Draw(image)
    
    # Gerçek baskı sınırını temsil eden kırmızı poligonu çiz
    draw.polygon(rotated_corners, outline="#FF3333", width=3)
    
    # Merkez hizalama hedefi (küçük artı işareti)
    r = 6
    draw.line([(int(round(cx))-r, int(round(cy))), (int(round(cx))+r, int(round(cy)))], fill="#FF3333", width=2)
    draw.line([(int(round(cx)), int(round(cy))-r), (int(round(cx)), int(round(cy))+r)], fill="#FF3333", width=2)
    
    return image

def kaydet_veritabani(sheets_client, mockup_name, kategori, drive_file_id, x, y, w, h, aci):
    """Google Sheet tablosunda drive_file_id kontrolü yapıp I sütununa kadar kaydeder."""
    try:
        TABLO_ID = "1KfloezbAz2saj3RKVoD6geVS9_wqefjjshWwMN0N-eY"
        sheet = sheets_client.open_by_key(TABLO_ID).sheet1
        tum_veriler = sheet.get_all_records()
        
        bulunan_satir = None
        mevcut_mockup_id = None
        
        for i, satir in enumerate(tum_veriler):
            if str(satir.get('drive_file_id')) == str(drive_file_id):
                bulunan_satir = i + 2
                mevcut_mockup_id = satir.get('mockup_id')
                break

        if bulunan_satir:
            guncel_satir_verisi = [[mevcut_mockup_id, mockup_name, kategori, drive_file_id, x, y, w, h, aci]]
            sheet.update(f"A{bulunan_satir}:I{bulunan_satir}", guncel_satir_verisi)
            return True, f"🔄 Güncellendi! (Satır: {bulunan_satir})"
        else:
            yeni_id = len(tum_veriler) + 1
            yeni_satir = [yeni_id, mockup_name, kategori, drive_file_id, x, y, w, h, aci]
            sheet.append_row(yeni_satir)
            return True, f"💾 Kaydedildi! (ID: {yeni_id})"
            
    except Exception as e:
        return False, f"Hata: {e}"

def manual_update(olcek_orani, tetikleyen_kutu):
    """Kullanıcı arayüzdeki sayı kutularına ELLE giriş yaptığında çalışır."""
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
    
    st.
