"""
TTS.py - Módulo de síntesis de voz (Text-to-Speech)

Este módulo implementa la conversión de texto a voz utilizando:
- `Kokoro`: Para la síntesis de voz principal.
- `eSpeak NG`: Para la conversión fonética.
- `sounddevice` y `soundfile`: Para la reproducción y almacenamiento del audio.

Funcionalidad:
- `speak(text)`: Convierte texto en audio y lo reproduce en tiempo real.
- `quack(times)`: Reproduce un sonido predefinido de "quack" un número determinado de veces.

Dependencias:
- `kokoro.KPipeline`: Para la síntesis de voz.
- `espeak-ng`: Para la fonetización del texto.
- `sounddevice`: Para la reproducción del audio generado.
- `soundfile`: Para almacenar los audios generados.

Clases y funciones:
- `speak(text)`: Convierte y reproduce texto en voz.
- `quack(times)`: Reproduce el sonido de un pato "quack".
"""

import os
from kokoro import KPipeline
import soundfile as sf
from playsound import playsound
import sounddevice as sd
from phonemizer.backend.espeak.wrapper import EspeakWrapper


# Configuración de la librería eSpeak (ajustar ruta según instalación)
_ESPEAK_LIBRARY = r'C:\Program Files\eSpeak NG\libespeak-ng.dll'
EspeakWrapper.set_library(_ESPEAK_LIBRARY)


# Inicialización del pipeline de Kokoro para TTS
pipeline = KPipeline(lang_code='e')

def speak(text):
    """
    Convierte el texto en audio y lo reproduce en tiempo real.

    Parámetros:
    - text (str): Texto a convertir en audio.

    Funcionalidad:
    - Divide el texto en fragmentos para mejorar la pronunciación.
    - Utiliza Kokoro para la síntesis de voz con la voz `ef_dora`.
    - Reproduce el audio generado y lo guarda en un archivo WAV.

    El audio generado se guarda en `Resources/response.wav`.
    """
    print(f"\nTTS -> {text}\n")
    print("-" * 50)

    # Dividir el texto en oraciones cortas para mejorar la generación de audio
    text_chunks = text.split('. ')

    for chunk in text_chunks:
        generator = pipeline(
            chunk,  
            voice='ef_dora',
            speed=1.1,
            split_pattern=r'\n+'  # Asegura una correcta segmentación del texto
        )
    
        for i, (_, _, audio) in enumerate(generator):
            # Reproduce el audio generado
            sd.play(audio, samplerate=25000)
            sd.wait()

            # Guardar el fragmento en un archivo
            filename = os.path.join("Resources", "response.wav")
            sf.write(filename, audio, 25000)

def quack(times):
    """
    Reproduce el sonido de "quack" un número determinado de veces.

    Parámetros:
    - times (int): Número de veces que se reproducirá el sonido.

    El archivo de sonido debe estar en `Resources/QUACK.wav`.
    """
    quack_path = os.path.abspath(os.path.join("Resources", "QUACK.wav"))

    if not os.path.exists(quack_path):
        print(f"ERROR: No se encontró el archivo {quack_path}.")
        return

    for _ in range(times):
        playsound(quack_path)
