"""
Módulo ASR (Automatic Speech Recognition)
Implementación de reconocimiento de voz usando Whisper a través de faster_whisper.
"""

import speech_recognition as sr
import os
import logging
import tempfile
from faster_whisper import WhisperModel

# Configuración de logging
logging.basicConfig(level=logging.INFO)

# Inicialización de la fuente de audio y el reconocedor
source = sr.Microphone()
recognizer = sr.Recognizer()

# Selección del modelo (tiny, base, small)
selected_model = 'small'
whisper_model = WhisperModel(selected_model, device="cpu", compute_type="float32")

def listen_for_command():
    """
    Escucha un comando a través del micrófono, graba el audio en un archivo temporal,
    lo transcribe utilizando Whisper y devuelve el texto transcrito.
    Retorna None si no se detecta un comando válido.
    """
    with source as audio:
        logging.info("Escuchando comandos...")
        recognizer.adjust_for_ambient_noise(audio)
        recorded_audio = recognizer.listen(audio, phrase_time_limit=2.5)
    
    try:
        # Uso de un archivo temporal para almacenar el audio grabado
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(recorded_audio.get_wav_data())
            tmp_file_path = tmp_file.name

        segments, info = whisper_model.transcribe(tmp_file_path, language="es")
        # Eliminamos el archivo temporal después de la transcripción
        #os.remove(tmp_file_path)

        segments_list = list(segments)
        if segments_list:
            command = segments_list[0].text.strip()
            if command:
                return command
        return None
    except sr.UnknownValueError:
        logging.error("No se pudo entender el audio. Intenta nuevamente.")
        return None
    except sr.RequestError:
        logging.error("No se puede acceder a la API de reconocimiento de voz.")
        return None
