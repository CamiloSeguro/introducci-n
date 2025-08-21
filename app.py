import streamlit as st
from PIL import Image

st.title("App")

st.header("Hola")
st.write("Mundo")
image = Image.open('imagen.jpg')
st.image(image, caption='mundo')
