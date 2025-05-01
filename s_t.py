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

# Configuración general
st.set_page_config(page_title="Traductor por Voz", page_icon="🗣️", layout="centered")

# Imagen decorativa
image = Image.open("OIG7.jpg")
st.image(image, caption="🎙️ Traductor Multilenguaje", use_column_width=True)

# Títulos
st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>🗣️ Traductor por Voz</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Presiona el botón, habla, selecciona los idiomas y escucha la traducción.</p>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📌 Instrucciones")
    st.write("1. Toca el botón 'Escuchar'.\n"
             "2. Espera la señal y habla.\n"
             "3. Selecciona el idioma de entrada y salida.\n"
             "4. Escoge el acento.\n"
             "5. ¡Convierte y escucha tu traducción!")

# Botón de escucha
st.markdown("### 🎤 Presiona para comenzar a hablar:")
stt_button = Button(label="🎙️ Escuchar", width=300, height=50)
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
    debounce_time=0,
)

# Si se obtuvo texto
if result and "GET_TEXT" in result:
    text = result.get("GET_TEXT")
    st.success("Texto capturado correctamente:")
    st.markdown(f"**📝 Lo que dijiste:** `{text}`")

    try:
        os.mkdir("temp")
    except:
        pass

    # Selección de idioma de entrada
    in_lang = st.selectbox("🌐 Lenguaje de Entrada", ["Español", "Inglés", "Bengali", "Coreano", "Mandarín", "Japonés"])
    out_lang = st.selectbox("🔄 Lenguaje de Salida", ["Español", "Inglés", "Bengali", "Coreano", "Mandarín", "Japonés"])
    accent = st.selectbox("🗣️ Acento del Audio", ["Defecto", "Español", "Reino Unido", "Estados Unidos", "Canada", "Australia", "Irlanda", "Sudáfrica"])

    lang_codes = {
        "Español": "es",
        "Inglés": "en",
        "Bengali": "bn",
        "Coreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja"
    }

    tld_codes = {
        "Defecto": "com",
        "Español": "com.mx",
        "Reino Unido": "co.uk",
        "Estados Unidos": "com",
        "Canada": "ca",
        "Australia": "com.au",
        "Irlanda": "ie",
        "Sudáfrica": "co.za"
    }

    input_language = lang_codes[in_lang]
    output_language = lang_codes[out_lang]
    tld = tld_codes[accent]

    translator = Translator()

    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        file_name = "audio_output"
        tts.save(f"temp/{file_name}.mp3")
        return file_name, trans_text

    # Checkbox para mostrar texto traducido
    display_output_text = st.checkbox("📄 Mostrar texto traducido")

    # Botón para convertir
    if st.button("🎧 Convertir y Reproducir"):
        result_name, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result_name}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown("### 🔊 Audio generado:")
        st.audio(audio_bytes, format="audio/mp3")

        if display_output_text:
            st.markdown("### 📘 Traducción:")
            st.info(output_text)

    # Limpieza de archivos viejos
    def remove_files(n):
        mp3_files = glob.glob("temp/*.mp3")
        now = time.time()
        limit = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - limit:
                os.remove(f)

    remove_files(7)

else:
    st.info("🕓 Esperando que hables para traducir.")



        
    


