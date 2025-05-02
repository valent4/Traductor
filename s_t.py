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

# Estilos visuales personalizados
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
            background-color: #f4f4f4;
            color: #222222;
        }

        h1, h2, h3, h4 {
            color: #1a1a1a;
        }

        .stButton>button {
            background-color: #007BFF;
            color: white;
            font-size: 18px;
            padding: 10px 24px;
            border-radius: 8px;
            border: none;
            transition: 0.3s;
        }

        .stButton>button:hover {
            background-color: #0056b3;
        }

        .stSelectbox>div>div>div {
            background-color: white;
            color: black;
        }

        .stMarkdown, .stText, .css-1cpxqw2 {
            color: #333333 !important;
        }

        .stSidebar {
            background-color: #ffffff;
        }

        .block-container {
            padding-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# Título e imagen
st.title("TRADUCTOR")
st.subheader("Escucho lo que quieres traducir.")
image = Image.open('traductor.jpg')
st.image(image, width=300)

# Sidebar
with st.sidebar:
    st.subheader("Traductor")
    st.write("Presiona el botón, cuando escuches la señal "
             "habla lo que quieres traducir, luego selecciona "
             "la configuración de lenguaje que necesites.")

st.write("Toca el botón y habla lo que quieres traducir:")

# Botón para activar el micrófono
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

# Capturar evento de voz
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
    st.markdown("### Texto capturado:")
    st.write(text)

    try:
        os.mkdir("temp")
    except:
        pass

    st.title("Texto a Audio")
    translator = Translator()

    # Selección de lenguajes
    in_lang = st.selectbox(
        "Selecciona el lenguaje de entrada",
        ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"),
    )
    lang_map = {
        "Inglés": "en", "Español": "es", "Bengali": "bn",
        "Coreano": "ko", "Mandarín": "zh-cn", "Japonés": "ja"
    }
    input_language = lang_map[in_lang]

    out_lang = st.selectbox(
        "Selecciona el lenguaje de salida",
        ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"),
    )
    output_language = lang_map[out_lang]

    english_accent = st.selectbox(
        "Selecciona el acento",
        (
            "Defecto", "Español", "Reino Unido", "Estados Unidos",
            "Canada", "Australia", "Irlanda", "Sudáfrica"
        ),
    )
    accent_map = {
        "Defecto": "com", "Español": "com.mx", "Reino Unido": "co.uk",
        "Estados Unidos": "com", "Canada": "ca", "Australia": "com.au",
        "Irlanda": "ie", "Sudáfrica": "co.za"
    }
    tld = accent_map[english_accent]

    # Función para traducir y convertir a audio
    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        try:
            my_file_name = text[0:20].strip().replace(" ", "_")
        except:
            my_file_name = "audio"
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text

    # Mostrar texto traducido
    display_output_text = st.checkbox("Mostrar el texto traducido")

    if st.button("Convertir"):
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown("## Tu audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        if display_output_text:
            st.markdown("## Texto de salida:")
            st.write(output_text)

    # Eliminar audios viejos
    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if len(mp3_files) != 0:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)
                    print("Deleted", f)

    remove_files(7)

        
    


