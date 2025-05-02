import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

# ---------- CSS PERSONALIZADO ----------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        background-color: #f6f9fc;
        color: #333333;
    }

    .stButton>button {
        background-color: #4a90e2;
        color: white;
        border-radius: 10px;
        height: 50px;
        font-size: 18px;
        font-weight: 500;
    }

    .stButton>button:hover {
        background-color: #357ABD;
    }

    .stSidebar {
        background-color: #f0f2f6;
    }

    .main h1 {
        color: #1f3b73;
        font-weight: 700;
    }

    .main h3 {
        color: #2e5caa;
        font-weight: 500;
    }

    .block-container {
        padding-top: 2rem;
    }

    .stAudio {
        margin-top: 1rem;
    }

    </style>
""", unsafe_allow_html=True)

# ---------- CONTENIDO ----------
st.title("🌍 Traductor por Voz")
st.subheader("🎧 Escucho lo que quieres traducir")

image = Image.open('traductor.jpg')
st.image(image, width=300)

with st.sidebar:
    st.subheader("ℹ️ Instrucciones")
    st.write("""
        1. Presiona el botón "Escuchar".
        2. Habla lo que deseas traducir.
        3. Elige el idioma de entrada y salida.
        4. ¡Escucha tu traducción en voz!
    """)

st.markdown("## 🎙️ Toca el botón y habla lo que quieres traducir")

# Botón de reconocimiento de voz
stt_button = Button(label="🎤 Escuchar", width=300, height=50)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

if result and "GET_TEXT" in result:
    text = str(result.get("GET_TEXT"))
    st.markdown("### 📝 Texto detectado:")
    st.write(text)

    try:
        os.mkdir("temp")
    except:
        pass

    translator = Translator()

    in_lang = st.selectbox("🈸 Selecciona el lenguaje de **entrada**", 
        ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"))
    out_lang = st.selectbox("🌐 Selecciona el lenguaje de **salida**", 
        ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"))

    lang_map = {
        "Inglés": "en",
        "Español": "es",
        "Bengali": "bn",
        "Coreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja"
    }

    input_language = lang_map[in_lang]
    output_language = lang_map[out_lang]

    accent = st.selectbox("🎧 Acento del audio de salida", 
        ["Defecto", "Español", "Reino Unido", "Estados Unidos", "Canada", "Australia", "Irlanda", "Sudáfrica"])
    
    tld_map = {
        "Defecto": "com",
        "Español": "com.mx",
        "Reino Unido": "co.uk",
        "Estados Unidos": "com",
        "Canada": "ca",
        "Australia": "com.au",
        "Irlanda": "ie",
        "Sudáfrica": "co.za"
    }
    tld = tld_map[accent]

    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        filename = text[:20] if text else "audio"
        tts.save(f"temp/{filename}.mp3")
        return filename, trans_text

    if st.button("🔄 Convertir texto a audio"):
        filename, translated = text_to_speech(input_language, output_language, text, tld)
        with open(f"temp/{filename}.mp3", "rb") as audio_file:
            audio_bytes = audio_file.read()
            st.markdown("## 🔊 Tu audio:")
            st.audio(audio_bytes, format="audio/mp3", start_time=0)

        if st.checkbox("Mostrar texto traducido"):
            st.markdown("## ✏️ Traducción:")
            st.write(translated)

    def remove_files(days):
        mp3_files = glob.glob("temp/*.mp3")
        now = time.time()
        for f in mp3_files:
            if os.stat(f).st_mtime < now - days * 86400:
                os.remove(f)

    remove_files(7)

        
    


