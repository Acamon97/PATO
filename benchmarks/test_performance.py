import json
import sys
import os
import time
import pandas as pd

# Agregar el directorio padre al path para importar los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import ASR  # Reconocimiento de voz
from SER import SER # Reconocimiento de emocion
from NLU import NLU  # Procesamiento de lenguaje natural
from LLM import LLM  # Generación de respuesta
import TTS  # Síntesis de voz

# 📌 Inicializar módulos
nlu = NLU(models_path="D:\MASTER\PATO\models")
llm = LLM()
ser = SER()


# 📌 Carpeta con los audios de prueba
AUDIO_FOLDER = "test_audios/"

# 📌 Obtener lista de archivos de audio
test_audios = [os.path.join(AUDIO_FOLDER, f) for f in os.listdir(AUDIO_FOLDER) if f.endswith(".wav")]

# 📌 Verificar si hay audios en la carpeta
if not test_audios:
    print(f"❌ ERROR: No se encontraron archivos de audio en '{AUDIO_FOLDER}'.")
    sys.exit(1)

# 📌 Variables para medición de tiempos
tiempos_respuesta = []
errores = 0

def test_full_system():
    """Ejecuta pruebas de rendimiento midiendo el tiempo del sistema completo"""
    print("\n📌 INICIANDO TEST DE SISTEMA COMPLETO")

    for audio in test_audios:
        print(f"\n🔍 Procesando: \"{audio}\"")

        try:
            # ⏱️ Medir tiempo de transcripción (ASR)
            inicio_ASR = time.time()
            transcripcion = ASR.transcribe_audio_file(audio)
            fin_ASR = time.time()
            tiempo_ASR = fin_ASR - inicio_ASR
            print(f"🎙️ ASR completado en {tiempo_ASR:.3f} segundos | Transcripción: \"{transcripcion}\"")
            
            # ⏱️ Medir tiempo de detección de emociones (SER)
            inicio_SER = time.time()
            emocion = ser.detect_emotion(audio)
            fin_SER = time.time()
            tiempo_SER = fin_SER - inicio_SER
            print(f"🎙️ SER completado en {tiempo_SER:.3f} segundos | Emoción: \"{emocion}\"")

            # ⏱️ Medir tiempo de procesamiento (NLU + LLM)
            inicio_nlp = time.time()
            intent = nlu.detectar_intent(transcripcion)
            respuesta_json = llm.generar_respuesta(transcripcion)
            respuesta_json = json.loads(respuesta_json)
            fin_nlp = time.time()
            tiempo_nlp = fin_nlp - inicio_nlp
            print(f"🧠 NLP + LLM completado en {tiempo_nlp:.3f} segundos | Intent detectado: \"{intent}\"")

            # ⏱️ Medir tiempo de síntesis de voz (TTS)
            inicio_TTS = time.time()
            TTS.speak(respuesta_json.get("response"))
            fin_TTS = time.time()
            tiempo_TTS = fin_TTS - inicio_TTS
            print(f"🔊 TTS completado en {tiempo_TTS:.3f} segundos")

            # 📌 Calcular tiempo total
            tiempo_total = tiempo_ASR + tiempo_SER + tiempo_nlp + tiempo_TTS
            print(f"⏳ Tiempo TOTAL: {tiempo_total:.3f} segundos")

            # 📌 Guardar resultado
            tiempos_respuesta.append([audio, tiempo_ASR, tiempo_SER, tiempo_nlp, tiempo_TTS, tiempo_total, respuesta_json])

        except Exception as e:
            tiempos_respuesta.append([audio, "ERROR", "ERROR", "ERROR", "ERROR", str(e)])
            print(f"❌ ERROR procesando el audio: {e}")
            global errores
            errores += 1

    # 📂 Guardar reporte en CSV
    df_tiempos = pd.DataFrame(tiempos_respuesta, columns=["Audio", "Tiempo ASR (s)", "Tiempo SER (s)", "Tiempo NLP+LLM (s)", "Tiempo TTS (s)", "Tiempo Total (s)", "Respuesta JSON"])
    df_tiempos.to_csv("test_full_system.csv", index=False, encoding="utf-8-sig", sep=";")

    # 📊 Resumen Final de Resultados
    tiempos_totales = [t[4] for t in tiempos_respuesta if isinstance(t[4], float)]

    if tiempos_totales:
        tiempo_promedio = sum(tiempos_totales) / len(tiempos_totales)
        tiempo_minimo = min(tiempos_totales)
        tiempo_maximo = max(tiempos_totales)
    else:
        tiempo_promedio = tiempo_minimo = tiempo_maximo = None

    print("\n📊 📌 **RESUMEN FINAL DE RENDIMIENTO DEL SISTEMA** 📌")
    print("──────────────────────────────────────────────")
    print(f"🔹 **TOTAL DE PRUEBAS:** {len(test_audios)}")
    print(f"✅ **PRUEBAS EXITOSAS:** {len(test_audios) - errores} ({((len(test_audios) - errores) / len(test_audios)) * 100:.2f}%)")
    print(f"❌ **ERRORES DETECTADOS:** {errores} ({(errores / len(test_audios)) * 100:.2f}%)")
    
    if tiempos_totales:
        print(f"⏱ **Tiempo Promedio del Sistema:** {tiempo_promedio:.3f} segundos")
        print(f"⚡ **Tiempo Mínimo:** {tiempo_minimo:.3f} segundos")
        print(f"🐢 **Tiempo Máximo:** {tiempo_maximo:.3f} segundos")

    print("\n📂 **Reporte de tiempos guardado en 'test_full_system.csv'**")

if __name__ == "__main__":
    test_full_system()
