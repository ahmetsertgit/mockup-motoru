# deneme_alani.py
import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

def manual_update(olcek_orani):
    """
    [MANUEL GİRİŞ TETİKLEYİCİSİ]
    Kullanıcı arayüzdeki (UI) sayı kutularına ELLE bir orijinal piksel değeri girdiğinde çalışır.
    
    Buradaki temel mantık:
    1. Orijinal pikselleri al.
    2. Ekranda görünecek küçük piksellere (küçültülmüş görsel boyutuna) oranla.
    3. Eğer genişlik veya yükseklikten biri değiştiyse, en-boy oranını (aspect ratio) korumak için diğerini otomatik hesapla.
    4. Yeni koordinatları 'manual_coords' ve 'cur_x_w_h' içine yaz.
    5. 'cropper_version' değerini artırarak kırpıcı bileşenini (React) DOM'dan tamamen silip temiz bir state ile yeniden oluştur (Re-mount).
    """

    breakpoint()
    # 1. Session State üzerindeki güncel orijinal pikselleri oku
    orj_x = st.session_state.val_x
    orj_y = st.session_state.val_y
    orj_w = st.session_state.val_w
    orj_h = st.session_state.val_h
    
    # 2. Orijinal pikselleri, ekrandaki küçük görselin piksel karşılıklarına dönüştür (Float değerler)
    mw = orj_w / olcek_orani
    mh = orj_h / olcek_orani
    mx = orj_x / olcek_orani
    my = orj_y / olcek_orani
    
    # 3. En-Boy Oranı Kilidini kontrol et ve uyarla
    ratio_str = st.session_state.get('ratio_str', '15:17')
    if ratio_str and ":" in ratio_str:
        try:
            parts = ratio_str.split(":")
            w_r, h_r = float(parts[0]), float(parts[1])
            
            # Değişimin genişlik kutusundan mı yoksa yükseklik kutusundan mı geldiğini anlamak için 
            # eski ekran değerleri (cur_x_w_h) ile karşılaştırma yapılıyor (Hassasiyet: 0.01 piksel)
            if abs(mw - st.session_state.cur_x_w_h["w"]) > 0.01:
                # Genişlik değiştiyse, yüksekliği formüle göre yeniden hesapla
                mh = mw * (h_r / w_r)
                st.session_state.val_h = int(round(mh * olcek_orani))
            elif abs(mh - st.session_state.cur_x_w_h["h"]) > 0.01:
                # Yükseklik değiştiyse, genişliği formüle göre yeniden hesapla
                mw = mh * (w_r / h_r)
                st.session_state.val_w = int(round(mw * olcek_orani))
        except ValueError:
            pass # Geçersiz oran formatı girildiyse hesaplamayı atla
    breakpoint()
    # 4. Ekran piksellerini tam sayıya (Integer) yuvarla
    # DİKKAT: int(round()) esnasında yaşanan 0.5 piksellik sapmalar zincirleme büyümeye neden olabilir!
    mx_int = int(round(mx))
    my_int = int(round(my))
    mw_int = int(round(mw))
    mh_int = int(round(mh))
    breakpoint()
    # 5. Hesaplanan ekran koordinatlarını referans hafızalara kaydet
    st.session_state.cur_x_w_h = {"x": mx_int, "y": my_int, "w": mw_int, "h": mh_int}
    st.session_state.manual_coords = (mx_int, mx_int + mw_int, my_int, my_int + mh_int)
    
    # 6. Bileşenin key parametresini değiştirmek için versiyonu artır (Bileşeni hard-resetler)
    st.session_state.cropper_version += 1

def calistir():
    st.header("📐 Mockup Baskı Yerleşimi")
    st.markdown("---")
    
    # --- [BAŞLANGIÇ AYARLARI VE STATE İLKLENDİRME] ---
    # Uygulama ilk kez açıldığında ekranda duracak varsayılan kutu boyutları (Ekran Pikseli cinsinden)
    BASLANGIC_W = 150
    BASLANGIC_H = 170
    BASLANGIC_X = 50
    BASLANGIC_Y = 50
    
    # Kırpıcının (st_cropper) 'default_coords' parametresine beslenecek Tuple hafızası (Sol, Sağ, Üst, Alt)
    if 'manual_coords' not in st.session_state:
        st.session_state.manual_coords = (BASLANGIC_X, BASLANGIC_X + BASLANGIC_W, BASLANGIC_Y, BASLANGIC_Y + BASLANGIC_H)
        
    # Fare hareketleri ile Manuel girişlerin çakışmasını engellemek için kullanılan bileşen versiyon anahtarı
    if 'cropper_version' not in st.session_state:
        st.session_state.cropper_version = 0
        
    # Kırpıcıdan (JS tarafı) gelen anlık ekran koordinatlarını saklayan ve farenin hareketi bittiğinde 
    # sonsuz döngüye girilmesini engelleyen "Eski Değer" kontrol sözlüğü (Dictionary)
    if 'cur_x_w_h' not in st.session_state:
        st.session_state.cur_x_w_h = {"x": BASLANGIC_X, "y": BASLANGIC_Y, "w": BASLANGIC_W, "h": BASLANGIC_H}
        
    # Arayüzdeki metin kutusunda tutulan varsayılan kilitli oran string değeri
    if 'ratio_str' not in st.session_state:
        st.session_state.ratio_str = "15:17"

    # --- [GÖRSEL YÜKLEME VE CACHE/HAFIZA YÖNETİMİ] ---
    referans_mockup = st.file_uploader("Boş Mockup Yükle", type=["png", "jpg"], key="cropper_upload")
    
    if referans_mockup:
        # Streamlit her etkileşimde (fare hareketi dahil) tüm kodu yukarıdan aşağı yeniden çalıştırır (Rerun).
        # Görselin her rerun'da yeniden 'resize' edilmesi nesne kimliğini (ID) değiştireceğinden, 
        # React bileşeni görseli 'yeni bir dosya' sanıp kırpma kutusunu tetikleyebilir.
        # Bu yüzden dosya yüklemesini session_state içinde cache'liyoruz.
        if 'uploaded_file_id' not in st.session_state or st.session_state.uploaded_file_id != referans_mockup.file_id:
            ref_img = Image.open(referans_mockup)
            orj_genislik, orj_yukseklik = ref_img.size
            
            # Görseli ekrana sığdırmak için hedef yükseklik sabitleniyor
            HEDEF_YUKSEKLIK = 500
            olcek_orani = orj_yukseklik / HEDEF_YUKSEKLIK
            yeni_w = int(round(orj_genislik / olcek_orani))
            yeni_h = HEDEF_YUKSEKLIK
            
            # İşlenmiş verileri hafızaya alıyoruz (Yalnızca yeni dosya yüklenince 1 kez çalışır)
            st.session_state.cropper_gorseli = ref_img.resize((yeni_w, yeni_h), Image.Resampling.LANCZOS)
            st.session_state.olcek_orani = olcek_orani
            st.session_state.uploaded_file_id = referans_mockup.file_id
        
        # Döngü içinde sürekli kullanılacak sabitlenmiş görsel ve ölçek oranı
        cropper_gorseli = st.session_state.cropper_gorseli
        olcek_orani = st.session_state.olcek_orani
        
        # Sayı kutularının (st.number_input) başlangıç değerlerini orijinal piksel cinsinden atıyoruz
        if 'val_x' not in st.session_state: st.session_state.val_x = int(round(BASLANGIC_X * olcek_orani))
        if 'val_y' not in st.session_state: st.session_state.val_y = int(round(BASLANGIC_Y * olcek_orani))
        if 'val_w' not in st.session_state: st.session_state.val_w = int(round(BASLANGIC_W * olcek_orani))
        if 'val_h' not in st.session_state: st.session_state.val_h = int(round(BASLANGIC_H * olcek_orani))
        
        # Ekranı Sol (Kırpıcı) ve Sağ (Ayarlar) olarak iki sütuna bölüyoruz
        col_sol_gorsel, col_sag_bilgi = st.columns([65, 35])
        
        with col_sag_bilgi:
            def ratio_changed():
                # Kullanıcı oran metnini el ile değiştirirse kırpıcıyı sıfırla
                st.session_state.cropper_version += 1
            
            ratio_input = st.text_input("🔒 En : Boy Oranı Kilidi", key="ratio_str", on_change=ratio_changed)
            
            # Metin girdisinden (örn: "15:17") Float tuple elde etme mantığı
            aspect_ratio = None
            if ratio_input and ":" in ratio_input:
                try:
                    parts = ratio_input.split(":")
                    w_ratio, h_ratio = float(parts[0]), float(parts[1])
                    if w_ratio > 0 and h_ratio > 0:
                        aspect_ratio = (w_ratio, h_ratio) # st_cropper'a beslenecek nihai Tuple
                        st.caption(f"🎯 Oran **{ratio_input}** olarak kilitlendi.")
                except ValueError:
                    st.error("❌ Geçersiz format!")
            
            st.markdown("---")

        # --- [KIRPICI BİLEŞENİNİN ÇALIŞTIRILMASI] ---
        with col_sol_gorsel:
            # st_cropper bir sarmalayıcıdır (Wrapper). Fare ile kutu oynatıldığında 
            # 'realtime_update=True' olduğundan anında Python tarafına 'box_coords' sözlüğünü döndürür.
            box_coords = st_cropper(
                cropper_gorseli, 
                realtime_update=True, 
                box_color='blue', 
                aspect_ratio=aspect_ratio, 
                return_type='box',
                default_coords=st.session_state.manual_coords, # Manuel değişimlerde kutuyu zorla buraya taşır
                key=f"cropper_{st.session_state.cropper_version}", # Key değiştikçe bileşen tamamen sıfırlanır
                should_resize_image=False
            )
        
        # --- [FARE HAREKETİ VE GERİ BESLEME (FEEDBACK) DÖNGÜSÜ ANAlİZİ] ---
        if box_coords:
            breakpoint()
            # Tarayıcı ekranından (JavaScript) gelen anlık kutu konumları (Küçük piksel)
            bx = int(round(box_coords['left']))
            by = int(round(box_coords['top']))
            bw = int(round(box_coords['width']))
            bh = int(round(box_coords['height']))

            breakpoint()
            
            # KÜTÜPHANENİN OLASI SIKIŞMA NOKTASI BURASIDIR:
            # Fare ile sadece KONUM değiştirirken (sürüklerken), JS tarafı Python'a hafif yuvarlanmış değerler gönderir.
            # Eğer bu değerler bir önceki döngüdeki (cur_x_w_h) değerlerden farklıysa içeri girilir.
            if (bx != st.session_state.cur_x_w_h["x"] or 
                by != st.session_state.cur_x_w_h["y"] or 
                bw != st.session_state.cur_x_w_h["w"] or 
                bh != st.session_state.cur_x_w_h["h"]):
                
                # Mevcut durumu güncelle ki bir sonraki milisaniyede çalışan rerun'da sonsuz döngüye girmeyelim
                st.session_state.cur_x_w_h = {"x": bx, "y": by, "w": bw, "h": bh}
                
                # Ekranda okunan küçük değerleri tekrar fabrikasyon orijinal piksel değerlerine (büyük boyutlara) çarpıyoruz.
                # İPUCU: Fareyle taşırken bw ve bh aslında DEĞİŞMEMİŞTİR. Ancak çarpma işlemi 'olcek_orani' ile yapıldığında
                # ve int(round()) ile birleştiğinde, orijinal pikseller (val_w, val_h) her Rerun'da 1'er piksel kayabilir.
                st.session_state.val_x = int(round(bx * olcek_orani))
                st.session_state.val_y = int(round(by * olcek_orani))
                st.session_state.val_w = int(round(bw * olcek_orani))
                st.session_state.val_h = int(round(bh * olcek_orani))
                    
                breakpoint()
                # KRİTİK SORU: Fare ile sürükleme esnasında 'st.session_state.manual_coords' değerini de 
                # (bx, by) değerlerine göre anlık güncellemek gerekir mi, yoksa o değer sabit kaldığı için 
                # st_cropper her fare hareketinde eski manual_coords ile yeni fare konumu arasında kalıp 
                # kutuyu iki yönlü esnetiyor mu? İnceleme alanın burası olmalı.
        
        # --- [KULLANICI GİRİŞ ARAYÜZÜ (SAYI KUTULARI)] ---
        with col_sag_bilgi:
            st.markdown("**Orijinal Çözünürlük Pikselleri (Doğrudan Düzenlenebilir):**")
            
            # Sayı kutuları doğrudan session_state anahtarlarına ('val_x', 'val_w' vb.) bağlıdır (key parametresi).
            # Değer değiştiği an 'on_change=manual_update' fonksiyonu tetiklenir.
            m_col1, m_col2 = st.columns(2)
            m_col1.number_input("Orijinal X", step=1, key="val_x", on_change=manual_update, args=(olcek_orani,))
            m_col2.number_input("Orijinal Y", step=1, key="val_y", on_change=manual_update, args=(olcek_orani,))
            
            m_col3, m_col4 = st.columns(2)
            m_col3.number_input("Orijinal Genişlik", step=1, key="val_w", on_change=manual_update, args=(olcek_orani,))
            m_col4.number_input("Orijinal Yükseklik", step=1, key="val_h", on_change=manual_update, args=(olcek_orani,))
            breakpoint()
            
            st.markdown("---")
            
            # --- [ÇIKTI PANELİ] ---
            # Backend tarafına (baskı şablonu oluşturucuya) gönderilecek nihai temiz pikseller
            st.markdown("**Nihai Çıktı Değerleri:**")
            st.code(
                f"x_noktasi: {st.session_state.val_x}\n"
                f"y_noktasi: {st.session_state.val_y}\n"
                f"genislik: {st.session_state.val_w}\n"
                f"yukseklik: {st.session_state.val_h}"
            )
