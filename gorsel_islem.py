# gorsel_islem.py
from PIL import Image
import io

def mockup_olustur(mockup_byte_verisi, tasarim_img, x, y, genislik, yukseklik, aci):
    """
    Drive'dan gelen ham mockup verisini ve tasarımı alıp belirtilen açıya göre 
    döndürerek birleştirir. Geriye PNG formatında byte dizisi döndürür.
    """
    # Alt katman (Boş Mockup)
    mockup = Image.open(io.BytesIO(mockup_byte_verisi)).convert("RGBA")
    
    # Üst katman (Tasarım - Önce hedef boyutlara getiriyoruz)
    tasarim_resized = tasarim_img.resize((genislik, yukseklik), Image.Resampling.LANCZOS)
    
    # Eğer bir döndürme açısı tanımlıysa rotasyonu uyguluyoruz
    if aci != 0:
        # Pillow saat yönünün tersine döndüğü için arayüzle eşitlemek adına -aci yapıyoruz.
        # expand=True köşelerin kesilmesini önler. BICUBIC ise netliği korur.
        tasarim_resized = tasarim_resized.rotate(
            -aci, 
            expand=True, 
            resample=Image.Resampling.BICUBIC
        )
    
    # --- MERKEZ ODAKLI HİZALAMA MATEMATİĞİ ---
    # Genişleyen görselin kaymasını engellemek için, yeni oluşan resmin merkezini
    # E-Tablo'daki orijinal hedef kutunun merkez noktasıyla çakıştırıyoruz.
    merkez_x = x + (genislik / 2)
    merkez_y = y + (yukseklik / 2)
    
    # Döndürme sonrası oluşan yeni resim boyutları
    yeni_w, yeni_h = tasarim_resized.size
    
    # Mockup üzerine yapıştırılacak yeni sol-üst koordinat hesaplaması
    sol_ust_x = int(round(merkez_x - (yeni_w / 2)))
    sol_ust_y = int(round(merkez_y - (yeni_h / 2)))
    
    # Tasarımı yeni hesaplanan koordinatlarla mockup üzerine maskesiyle yapıştır
    mockup.paste(tasarim_resized, (sol_ust_x, sol_ust_y), tasarim_resized)
    
    # Çıktıyı belleğe kaydet ve döndür
    img_byte_arr = io.BytesIO()
    mockup.save(img_byte_arr, format="PNG")
    
    return img_byte_arr.getvalue()
