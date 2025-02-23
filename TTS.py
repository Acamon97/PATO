"""
Módulo TTS (Text-to-Speech)
Implementación de síntesis de voz usando el pipeline de Kokoro y eSpeak.
"""

import os
import logging
import time
from kokoro import KPipeline
import soundfile as sf
from playsound import playsound
import sounddevice as sd
from phonemizer.backend.espeak.wrapper import EspeakWrapper

# Configuración de logging
logging.basicConfig(level=logging.INFO)

# Configuración de la librería eSpeak (usa cadenas raw para rutas)
_ESPEAK_LIBRARY = r'C:\Program Files\eSpeak NG\libespeak-ng.dll'
EspeakWrapper.set_library(_ESPEAK_LIBRARY)

# Inicialización del pipeline de Kokoro para TTS
pipeline = KPipeline(lang_code='e')

def hola(text):
    """
    Sintetiza y reproduce el texto dado utilizando el pipeline de Kokoro.
    Guarda cada fragmento de audio generado en la carpeta Resources con un nombre único.
    """
    generator = pipeline(
        text, 
        voice='ef_dora',  # Puedes cambiar la voz según tus preferencias
        speed=1, 
        split_pattern=r'\n+'
    )
    
    for i, (gs, ps, audio) in enumerate(generator):
        # Reproduce el audio y espera a que termine la reproducción
        sd.play(audio, 24000)
        sd.wait()
        
        # Guarda cada fragmento en un archivo separado para evitar sobrescrituras
        filename = os.path.join("Resources", f"response_{i}.wav")
        sf.write(filename, audio, 24000)
        logging.info(f"Fragmento de respuesta guardado en: {filename}")

def quack(times):
    """
    Reproduce el sonido de 'quack' el número de veces especificado.
    """
    quack_path = os.path.join("Resources", "QUACK.wav")
    for _ in range(times):
        playsound(quack_path)
