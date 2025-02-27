import sys
import os
import time

# Agregar el directorio padre al path para importar NLU.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pato import AsistenteVirtual
from DialogManager import DialogManager

import torch
print("CUDA disponible:", torch.cuda.is_available())
print("Número de GPUs:", torch.cuda.device_count())
print("Nombre de GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No hay GPU disponible")



# Inicializar el modelo
asistente = AsistenteVirtual()
dm = DialogManager(asistente)


# Lista de pruebas: frases de entrada y respuestas esperadas (opcional)
test_cases = [
    # 📌 Pruebas neutrales
    {"user_message": "Hola, ¿qué tal?", "emotion": "neutral"},
    {"user_message": "¿Qué puedes hacer?", "emotion": "neutral"},

    # 📌 Pruebas con felicidad
    {"user_message": "¡Hoy es un gran día! Me siento increíble.", "emotion": "happy"},
    {"user_message": "Acabo de lograr un objetivo importante, estoy muy contento.", "emotion": "happy"},

    # 📌 Pruebas con tristeza
    {"user_message": "Me siento muy mal hoy, nada me sale bien.", "emotion": "sad"},
    {"user_message": "Perdí algo importante para mí y estoy muy triste.", "emotion": "sad"},

    # 📌 Pruebas con enojo
    {"user_message": "Estoy harto de que las cosas siempre salgan mal.", "emotion": "angry"},
    {"user_message": "No soporto más esta situación, todo es un desastre.", "emotion": "angry"},

    # 📌 Pruebas con sorpresa
    {"user_message": "¡No puedo creer lo que acaba de pasar!", "emotion": "surprised"},
    {"user_message": "¡Wow, eso no me lo esperaba!", "emotion": "surprised"},

    # 📌 Pruebas con miedo
    {"user_message": "Tengo miedo de lo que pueda pasar mañana.", "emotion": "fearful"},
    {"user_message": "No sé qué hacer, todo esto me asusta.", "emotion": "fearful"},

    # 📌 Pruebas con asco
    {"user_message": "Eso es asqueroso, no puedo con esto.", "emotion": "disgusted"},
    {"user_message": "Qué horror, esto me da mucho asco.", "emotion": "disgusted"},

    # 📌 Pruebas con emociones desconocidas
    {"user_message": "No sé cómo me siento en este momento.", "emotion": "unknown"},
    {"user_message": "Estoy raro, no sé qué me pasa.", "emotion": "unknown"},

    # 📌 Pruebas con contexto específico (RAG)
    {"user_message": "¿Cuántas tareas tengo pendientes?", "emotion": "neutral"},
    {"user_message": "¿Ya completé todas mis tareas?", "emotion": "neutral"},
    {"user_message": "Dime qué tengo que hacer hoy.", "emotion": "neutral"},

    # 📌 Casos extremos
    {"user_message": "Siento que todo está perdido, no veo solución.", "emotion": "sad"},
    {"user_message": "Estoy muy molesto, no quiero hablar con nadie.", "emotion": "angry"},
    {"user_message": "No sé si confiar en nadie.", "emotion": "fearful"},

    #Pruebas sin carga emocional explícita
    {"user_message": "Tengo muchas cosas que hacer.", "emotion": "happy"},
    {"user_message": "Hoy es un día cualquiera.", "emotion": "sad"},
    {"user_message": "Voy a salir con mis amigos.", "emotion": "angry"},
    {"user_message": "Creo que haré algo diferente hoy.", "emotion": "fearful"},

    # Pruebas con emociones contradictorias
    {"user_message": "Estoy tan feliz... pero no sé por qué me siento así.", "emotion": "sad"},
    {"user_message": "Estoy muy enojado, pero no quiero que nadie se entere.", "emotion": "happy"},
    {"user_message": "Estoy tranquilo, pero mi corazón late muy rápido.", "emotion": "fearful"},
    {"user_message": "No pasa nada, todo está bien.", "emotion": "angry"},


    {"user_message": "Tengo que comprar pan y leche.", "emotion": "neutral"},
    {"user_message": "¿Qué cosas tenía que hacer?", "emotion": "neutral"},
    {"user_message": "Creo que ya hice todo lo importante.", "emotion": "neutral"},


    {"user_message": "¿Cómo estás?", "emotion": "neutral"},
    {"user_message": "¿Me puedes ayudar con algo?", "emotion": "neutral"},


    {"user_message": "Dime un dato curioso.", "emotion": "neutral"},
    {"user_message": "Cuéntame un chiste.", "emotion": "neutral"},

]


print("\n Iniciando pruebas del LLM...\n")

for test in test_cases:
    print(f"\n🔹 Probando: {test['user_message']} (Emoción: {test['emotion']})")
    
    dm.generar_respuesta(
        user_message=test["user_message"], 
        emotion_detected=test["emotion"]
    )

    #print(f"✅ Comportamiento esperado: {test['expected_behavior']}")
    print("-" * 80)
    time.sleep(1)