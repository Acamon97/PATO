'''
Módulo ASR (Automatic Speech Recognition)
Implementación de reconocimiento de voz usando Whisper a través de faster_whisper.
'''


import speech_recognition as sr
import os
from faster_whisper import WhisperModel
import torch


device = "cuda" if torch.cuda.is_available() else "cpu"


# Inicialización de la fuente de audio y el reconocedor
source = sr.Microphone()
recognizer = sr.Recognizer()

# Selección del modelo (tiny, base, small)
selected_model = 'small'
whisper_model = WhisperModel(selected_model, device=device, compute_type="float32")

def listen_for_command():
    '''
    Escucha un comando a través del micrófono, graba el audio en un archivo temporal,
    lo transcribe utilizando Whisper y devuelve el texto transcrito.
    Retorna None si no se detecta un comando válido.
    '''
    with source as audio:
        print("\nASR -> Escuchando comandos...")
        recognizer.adjust_for_ambient_noise(audio)
        recorded_audio = recognizer.listen(audio)
    
    try:
        file_path = os.path.join("Resources", "command.wav")

        with open(file_path, "wb") as f:
            f.write(recorded_audio.get_wav_data())

        segments, info = whisper_model.transcribe(file_path, language="es")

        segments_list = list(segments)
        if segments_list:
            command = segments_list[0].text.strip()
            if command:
                print(f"\nASR -> Frase detectada: {command}")
                return command, file_path
        return None, None
    except sr.UnknownValueError:
        print("ERROR: No se pudo entender el audio. Intenta nuevamente.")
        return None, None
    except sr.RequestError:
        print("ERROR: No se puede acceder a la API de reconocimiento de voz.")
        return None, None
