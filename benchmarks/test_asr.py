import sys
import os
import jiwer
import pandas as pd
import re


# Agregar el directorio padre al path para importar ASR.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import ASR

import os
import jiwer
import pandas as pd
import ASR
import re

# 📌 Cargar las transcripciones del dataset TEDx Spanish
transcription_file = "test_audios/transcriptions.csv"

# Verificar que el archivo de transcripciones existe
if not os.path.exists(transcription_file):
    raise FileNotFoundError(f"⚠ No se encontró `{transcription_file}`. Asegúrate de ejecutar `download_tedx.py` primero.")

# 📌 Cargar transcripciones en un diccionario {archivo_audio: "transcripción esperada"}
df = pd.read_csv(transcription_file, encoding="utf-8")

# Convertir a diccionario
test_audios = dict(zip(df["path"], df["sentence"]))

# Variables para métricas globales
total_wer = 0
total_cer = 0
errores = 0
total_pruebas = len(test_audios)

def normalizar_texto(texto):
    """Convierte a minúsculas y elimina puntuación para mejorar la comparación."""
    texto = texto.lower()  # 🔹 Convertir a minúsculas
    texto = re.sub(r"[^\w\s]", "", texto)  # 🔹 Eliminar puntuación (comas, puntos, etc.)
    return texto

def calcular_wer_cer(referencia, transcripcion):
    """Calcula métricas de Word Error Rate (WER) y Character Error Rate (CER)."""
    referencia_norm = normalizar_texto(referencia)  # 🔹 Normalizar transcripción original
    transcripcion_norm = normalizar_texto(transcripcion)  # 🔹 Normalizar salida de ASR

    wer = jiwer.wer(referencia_norm, transcripcion_norm)
    cer = jiwer.cer(referencia_norm, transcripcion_norm)
    return wer, cer

def test_asr():
    """Ejecuta pruebas de ASR en los audios del dataset TEDx Spanish."""
    global total_wer, total_cer, errores

    print("\n📌 INICIANDO TEST ASR con TEDx Spanish")
    
    numero = 1

    for audio, referencia in test_audios.items():
        audio_path = os.path.join("test_audios", os.path.basename(audio))  # 🔹 Asegurar que la ruta es correcta
        print(f"\n🔍 {numero}/100 Probando ASR con: {audio_path}")
        numero = numero +1
        transcripcion = ASR.transcribe_audio_file(audio_path)  # Usar método de transcripción de PATO
        
        if transcripcion:
            wer, cer = calcular_wer_cer(referencia, transcripcion)
            total_wer += wer
            total_cer += cer

            # 📌 Mostrar la transcripción esperada junto a la generada
            print(f"🔹 Original: {normalizar_texto(referencia)}")
            print(f"✅ Transcripción: {normalizar_texto(transcripcion)}")
            print(f"📊 WER: {wer:.2f}, CER: {cer:.2f}")
        else:
            print("❌ No se obtuvo transcripción")
            errores += 1

    # Cálculo de métricas globales
    print("\n📊 RESULTADOS GLOBALES:")
    print(f"🔹 WER Promedio: {total_wer / total_pruebas:.2f}")
    print(f"🔹 CER Promedio: {total_cer / total_pruebas:.2f}")
    print(f"❌ Errores de transcripción: {errores}/{total_pruebas}")

if __name__ == "__main__":
    test_asr()
