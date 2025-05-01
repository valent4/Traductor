import os
import streamlit as st
from bokeh.models import Button, CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

# Estilo oscuro
st.markdown("""
    <style>
        body {
            background-color: #121212;
        }
        .main {
            background-color: #121212;
            color: #E0E0E0;
        }
        .stApp {
            background-color: #121212;
        }
        .stButton > button {
            background-color: #7B61FF;
            color: white;
            border-radius: 10px;
            font-size: 18px;
            padding: 0.75em 1em;
        }
        .custom-container {
            background-color: #1E1E1E;
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
            margin-bottom: 20px;
        }
        .title {
            font-size: 36px;
            font-weight: bold;
            color: #E0E0E0;
            text-align: center;
            margin-bottom: 0.2em;
        }
        .subtitle {
            font-size: 18px;
            color: #B0B0B0;
            text-align: center;
            margin-bottom: 1em;
        }
    </style>
""", unsafe_allow_html=True)

# Título
st.markdown('<div class="title">🎧 TRADUCTOR</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Escucho lo que dices y traduzco con voz.</div>', unsafe_allow_html=True)

# Imagen
image = Image.open('OIG7.jpg')
st.image(image, width=300)

# Sidebar
with st.sidebar:
    st.subheader("🎤 Traductor por voz")
    st.markdown("Presiona el botón para grabar tu voz. Luego elige el idioma de entrada y salida.")

# Sección del botón
st.markdown('<div class="custom-container">', unsafe_allow_html=True)
st.markdown("### 🎙️ Toca el botón para hablar")

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
    key="listen-dark",
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

    st.markdown('<div class="custom-container">', unsafe_allow_html=True)
    in_lang = st.selectbox("Lenguaje de entrada", ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"))
    out_lang = st.selectbox("Lenguaje de salida", ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"))
    accent = st.selectbox("Acento", ("Defecto", "Español", "Reino Unido", "Estados Unidos", "Canada", "Australia", "Irlanda", "Sudáfrica"))
    st.markdown('</div>', unsafe_allow_html=True)

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

    # Limpieza
    def remove_files(n_days=7):
        threshold = time.time() - n_days * 86400
        for f in glob.glob("temp/*.mp3"):
            if os.path.getmtime(f) < threshold:
                os.remove(f)

    remove_files()

        
    


