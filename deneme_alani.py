# deneme_alani.py
import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

def calistir():
    st.header("🧪 Test ve Deneme Alanı")
    st.write("Ana sistemi bozmadan burada yeni kodlar test edilebilir.")
    
    referans_mockup = st.file_uploader("Test için Boş Mockup Yükle", type=["png", "jpg"], key="test_upload")
    
    if referans_mockup:
        ref_img = Image.open(referans_mockup)
        box_coords = st_cropper(ref_img, realtime_update=True, box_color='blue', return_type='box')
        
        if box_coords:
            st.info(f"Test Koordinatları:\n\nX: {box_coords['left']} | Y: {box_coords['top']} | G: {box_coords['width']} | Y: {box_coords['height']}")
