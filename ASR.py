"""
ASR.py - Módulo de Reconocimiento Automático de Voz (ASR)

Este módulo implementa el reconocimiento de voz en español utilizando 
Whisper a través de la librería `faster_whisper`.

Funcionalidad:
- Captura de audio desde el micrófono.
- Almacenamiento temporal del audio grabado.
- Transcripción de voz a texto usando Whisper.
- Retorno del texto transcrito junto con la ubicación del archivo de audio.

Dependencias:
- `speech_recognition` para la captura de audio.
- `faster_whisper` para la transcripción eficiente.
- `torch` para detección de hardware y uso de CUDA si está disponible.

Métodos:
- `listen_for_command()`: Captura un comando por voz y lo transcribe.
"""

import speech_recognition as sr
import os
from faster_whisper import WhisperModel
import torch

# Determinar si se usará GPU o CPU
device = "cuda" if torch.cuda.is_available() else "cpu"

# Inicialización del micrófono y el reconocedor de voz
source = sr.Microphone()
recognizer = sr.Recognizer()

# Selección del modelo Whisper (opciones: tiny, base, small)
selected_model = 'small'
whisper_model = WhisperModel(selected_model, device=device, compute_type="float32")

def listen_for_command():
    """
    Escucha un comando a través del micrófono, graba el audio en un archivo temporal 
    y lo transcribe utilizando Whisper.

    Retorna:
    - command (str): Texto transcrito del comando.
    - file_path (str): Ruta del archivo de audio grabado.

    Si no se detecta un comando válido, devuelve (None, None).
    """
    with source as audio:
        print("\nASR -> Escuchando comandos...")
        recognizer.adjust_for_ambient_noise(audio)  # Ajustar ruido ambiente
        recorded_audio = recognizer.listen(audio)  # Capturar audio del micrófono

    try:
        file_path = os.path.join("Resources", "command.wav")

        # Guardar el audio grabado en un archivo temporal
        with open(file_path, "wb") as f:
            f.write(recorded_audio.get_wav_data())

        command = ""
        # Transcribir el audio con Whisper
        segments, info = whisper_model.transcribe(file_path, language="es")
        
        for segment in segments:
            command += segment.text
                
        if command and command != "":
            print(f"\nASR -> Frase detectada: {command}")
            return command, file_path

        return None, None

    except sr.UnknownValueError:
        print("ERROR: No se pudo entender el audio. Intenta nuevamente.")
        return None, None
    
    
def transcribe_audio_file(audio_path):
    """
    Transcribe un archivo de audio usando Faster Whisper.

    Parámetros:
    - audio_path (str): Ruta del archivo de audio.

    Retorna:
    - (str): Texto transcrito del archivo de audio.
    """
    if not os.path.exists(audio_path):
        print(f"ERROR: No se encontró el archivo {audio_path}.")
        return None

    try:
        transcription = ""
        segments, _ = whisper_model.transcribe(audio_path, language="es")
        for segment in segments:
            transcription += segment.text
        return transcription

    except Exception as e:
        print(f"ERROR al transcribir {audio_path}: {e}")
        return None

