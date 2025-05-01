import os
import streamlit as st
from bokeh.models import Button, CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

# Estilo global
st.markdown("""
    <style>
        .stButton > button {
            background-color: #4A90E2;
            color: white;
            border-radius: 8px;
            height: 3em;
            width: 100%;
            font-size: 18px;
        }
        .custom-section {
            background-color: #F0F2F6;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .title-text {
            text-align: center;
            font-size: 32px;
            font-weight: bold;
        }
        .sub-text {
            text-align: center;
            font-size: 18px;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Título y descripción
st.markdown('<div class="title-text">🎧 TRADUCTOR</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Escucho lo que quieres traducir.</div>', unsafe_allow_html=True)

# Imagen decorativa
image = Image.open('OIG7.jpg')
st.image(image, width=300)

# Sidebar
with st.sidebar:
    st.subheader("Traductor por voz")
    st.write("Presiona el botón, cuando escuches la señal habla lo que quieres traducir. Luego selecciona la configuración de idioma.")

# Sección del botón de escucha
st.markdown('<div class="custom-section">', unsafe_allow_html=True)
st.markdown("### 🎙️ Toca el botón y habla lo que quieres traducir")

stt_button = Button(label="🎤 Escuchar", width=300)
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
        if (value !== "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    };
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
st.markdown('</div>', unsafe_allow_html=True)

# Procesamiento
if result and "GET_TEXT" in result:
    st.success("Texto reconocido:")
    st.write(result.get("GET_TEXT"))

    try:
        os.mkdir("temp")
    except:
        pass

    translator = Translator()
    text = str(result.get("GET_TEXT"))

    in_lang = st.selectbox("Selecciona el lenguaje de Entrada", ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"))
    out_lang = st.selectbox("Selecciona el lenguaje de salida", ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"))
    accent = st.selectbox("Selecciona el acento", ("Defecto", "Español", "Reino Unido", "Estados Unidos", "Canada", "Australia", "Irlanda", "Sudáfrica"))

    lang_map = {"Inglés": "en", "Español": "es", "Bengali": "bn", "Coreano": "ko", "Mandarín": "zh-cn", "Japonés": "ja"}
    tld_map = {"Defecto": "com", "Español": "com.mx", "Reino Unido": "co.uk", "Estados Unidos": "com", "Canada": "ca", "Australia": "com.au", "Irlanda": "ie", "Sudáfrica": "co.za"}

    input_language = lang_map[in_lang]
    output_language = lang_map[out_lang]
    tld = tld_map[accent]

    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        file_name = text[:20] if text else "audio"
        tts.save(f"temp/{file_name}.mp3")
        return file_name, trans_text

    show_text = st.checkbox("Mostrar texto traducido")

    if st.button("🔊 Convertir a audio"):
        result_name, translated = text_to_speech(input_language, output_language, text, tld)
        with open(f"temp/{result_name}.mp3", "rb") as audio_file:
            st.audio(audio_file.read(), format="audio/mp3")
        if show_text:
            st.markdown("### Texto traducido:")
            st.write(translated)

    # Limpieza de audios antiguos
    def remove_files(n_days=7):
        threshold = time.time() - n_days * 86400
        for f in glob.glob("temp/*.mp3"):
            if os.path.getmtime(f) < threshold:
                os.remove(f)

    remove_files()


        
    


