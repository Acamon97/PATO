import json

import sys
import os

# Agregar el directorio padre al path para importar LLM.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from LLM import LLM

llm = LLM()

test_inputs = [
    "Añadir tarea comprar pan",
    "Elimina la tarea de pagar la factura",
    "Muéstrame mis tareas pendientes",
]

def test_llm():
    for entrada in test_inputs:
        print(f"\n🔍 Probando LLM con: {entrada}")
        respuesta_json = llm.generar_respuesta(entrada)
        
        try:
            respuesta = json.loads(respuesta_json)
            assert "response" in respuesta and "tool_calls" in respuesta
            print(f"✅ JSON válido generado: {respuesta_json}")
        except json.JSONDecodeError:
            print("❌ Respuesta no es un JSON válido")

if __name__ == "__main__":
    test_llm()
