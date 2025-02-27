import sys
import os
from time import sleep

# Agregar el directorio padre al path para importar NLU.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from NLU import NLU  # Importar la clase NLU

# Inicializar el modelo de detección de intenciones
nlu_model = NLU()

# Casos de prueba
test_cases = {
    "despedir": ["Hasta luego", "Nos vemos", "Chao", "Adiós PATO"],
    "detener_conversacion": ["Apaga PATO", "Detén la conversación", "Ya está, termina"],
    "reiniciar_conversacion": ["Vamos a empezar de nuevo", "Reinicia todo"],
    "mostrar_comandos": ["¿Qué puedes hacer?", "Dime los comandos", "Lista de comandos"],
    "pausar_conversacion": ["Espera un momento", "Detente un rato", "Pausa"],
    "continuar_conversacion": ["Sigamos", "Reanuda la conversación", "Continúa"],
    "unknown": ["Cuéntame un chiste", "¿Qué hora es?", "Me gusta el helado de fresa"]
}

# Ejecutar pruebas
print("🧪 **Ejecutando pruebas de detección de intenciones...**\n")

for intent_esperado, mensajes in test_cases.items():
    for mensaje in mensajes:
        intent_detectado = nlu_model.detectar_intent(mensaje)
        print(f"🗣️ Entrada: \"{mensaje}\"")
        print(f"🎯 Intent detectado: {intent_detectado} (esperado: {intent_esperado})")
        print("-" * 50)
        sleep(1)

print("\n✅ **Pruebas finalizadas.**")
