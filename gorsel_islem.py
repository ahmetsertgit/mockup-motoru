# gorsel_islem.py
from PIL import Image
import io

def mockup_olustur(mockup_byte_verisi, tasarim_img, x, y, genislik, yukseklik):
    """
    Drive'dan gelen ham mockup verisini ve tasarımı alıp birleştirir.
    Geriye PNG formatında byte dizisi döndürür.
    """
    # Alt katman (Boş Mockup)
    mockup = Image.open(io.BytesIO(mockup_byte_verisi)).convert("RGBA")
    
    # Üst katman (Tasarım - Boyutlandırılmış)
    tasarim_resized = tasarim_img.resize((genislik, yukseklik), Image.Resampling.LANCZOS)
    
    # Tasarımı mockup üzerine yapıştır
    mockup.paste(tasarim_resized, (x, y), tasarim_resized)
    
    # Çıktıyı belleğe kaydet ve döndür
    img_byte_arr = io.BytesIO()
    mockup.save(img_byte_arr, format="PNG")
    
    return img_byte_arr.getvalue()
