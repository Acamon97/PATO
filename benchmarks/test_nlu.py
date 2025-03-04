import sys
import os

# Agregar el directorio padre al path para importar NLU.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from NLU import NLU

nlu = NLU()

test_intents = {
    "Apagar PATO": "detener_conversacion",
    "Muéstrame los comandos": "mostrar_comandos",
    "Pausa la conversación": "pausar_conversacion",
    "No entiendo qué hacer": "nlu_fallback",
}

def test_nlu():
    for frase, intent_esperado in test_intents.items():
        print(f"\n🔍 Probando NLU con: {frase}")
        intent_detectado = nlu.detectar_intent(frase)
        print(f"✅ Intent detectado: {intent_detectado} | Esperado: {intent_esperado}")
        assert intent_detectado == intent_esperado, f"❌ Error en {frase}"

if __name__ == "__main__":
    test_nlu()
