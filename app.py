import os
import glob
import time
from datetime import datetime

import streamlit as st
from gtts import gTTS
from PIL import Image

# ─────────────────────────── Config ─────────────────────────── #
st.set_page_config(page_title="Interfases Multimodales: Texto → Audio", page_icon="🎧", layout="wide")

# Estilos ligeros
st.markdown("""
<style>
/* ancho centrado y consistente */
.block-container { max-width: 1100px; margin: 0 auto; }

/* botones: misma altura/padding/borde */
.stButton > button {
  height: 44px !important;
  padding: 0 16px !important;
  border-radius: 10px !important;
}

/* textarea más limpio */
.stTextArea textarea { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────── Header ─────────────────────────── #
c1, c2 = st.columns([1, 2])
with c1:
    if os.path.exists("imagen.jpg"):
        st.image(Image.open("imagen.jpg"), width=220, caption="Interfases Multimodales")
with c2:
    st.title("Interfases Multimodales · Texto → Audio")
    st.markdown('<span class="badge">Accesible</span> <span class="badge">Rápido</span> <span class="badge">Offline TTS (gTTS)</span>', unsafe_allow_html=True)

st.markdown("""
Las interfaces **texto a audio** favorecen accesibilidad (p. ej., usuarios con baja visión), manos libres y casos
donde leer no es posible. Aquí puedes escribir un texto, elegir idioma/acento y obtener un **MP3**.
""")

# ─────────────────────────── Sidebar ─────────────────────────── #
with st.sidebar:
    st.header("Ajustes")

    LANG_MAP = {
        "Español": "es",
        "Inglés": "en",
        "Portugués": "pt",
        "Francés": "fr",
        "Italiano": "it",
        "Alemán": "de",
        "Japonés": "ja",
    }
    lang_label = st.selectbox("Idioma del audio (TTS)", list(LANG_MAP.keys()), index=0)
    lang_code = LANG_MAP[lang_label]

    TLD_MAP = {
        "Default": "com",
        "Estados Unidos": "com",
        "Reino Unido": "co.uk",
        "India": "co.in",
        "Canadá": "ca",
        "Australia": "com.au",
        "Irlanda": "ie",
        "Sudáfrica": "co.za",
    }
    tld_label = st.selectbox("Acento (TLD)", list(TLD_MAP.keys()), index=0)
    tld = TLD_MAP[tld_label]

    slow = st.toggle("Voz lenta", value=False)

# ─────────────────────────── Utilidades ─────────────────────────── #
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

def remove_old_files(days: int = 7):
    now = time.time()
    for f in glob.glob(os.path.join(TEMP_DIR, "*.mp3")):
        try:
            if os.stat(f).st_mtime < now - days * 86400:
                os.remove(f)
        except Exception:
            pass

remove_old_files()

def safe_stub(text: str, max_len: int = 36) -> str:
    if not text.strip():
        return "audio"
    stub = "".join(c for c in text.strip().split("\n")[0] if c.isalnum() or c in (" ", "-", "_")).strip()
    if not stub:
        stub = "audio"
    return stub[:max_len].replace(" ", "_")

def text_to_speech(text: str, lang: str, tld: str, slow: bool) -> str:
    tts = gTTS(text=text, lang=lang, tld=tld, slow=slow)
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_stub(text)}.mp3"
    path = os.path.join(TEMP_DIR, filename)
    tts.save(path)
    return path

# ─────────────────────────── Form principal ─────────────────────────── #
st.subheader("Texto a audio")
with st.container():
    default = "Hola, este es un ejemplo de síntesis de voz con gTTS en Streamlit."
    colA, colB = st.columns([3, 1])
    with colA:
        text = st.text_area("Ingresa el texto", value="", height=180, placeholder=default)
        st.caption(f"Caracteres: {len(text)}")
    with colB:
        if st.button("Usar texto de ejemplo"):
            text = default
            st.session_state["__tmp_text"] = default
        # si el usuario pulsó ejemplo, refrescamos el textarea
        if "__tmp_text" in st.session_state:
            if st.session_state["__tmp_text"] and not text:
                text = st.session_state["__tmp_text"]

    convert = st.button("Convertir a MP3", type="primary", use_container_width=True)

    if convert:
        if not text or not text.strip():
            st.error("Escribe algún texto antes de convertir.")
        elif len(text) > 5000:
            st.error("El texto es muy largo (máx. 5000 caracteres para gTTS).")
        else:
            with st.spinner("Generando audio..."):
                try:
                    mp3_path = text_to_speech(text.strip(), lang_code, tld, slow)
                except Exception as e:
                    st.error(f"Error al generar el audio: {e}")
                else:
                    st.success("¡Listo! Tu audio está abajo.")
                    with open(mp3_path, "rb") as f:
                        audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/mp3")
                    st.download_button(
                        "Descargar MP3",
                        data=audio_bytes,
                        file_name=os.path.basename(mp3_path),
                        mime="audio/mpeg",
                        use_container_width=True,
                    )
                    with st.expander("Texto utilizado"):
                        st.write(text)
