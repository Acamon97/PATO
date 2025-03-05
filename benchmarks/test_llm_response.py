import json
import sys
import os
import pandas as pd

# Agregar el directorio padre al path para importar LLM.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from LLM import LLM

# 📌 Inicializar LLM
llm = LLM()


# 📌 Casos de prueba con respuestas esperadas (50 frases únicas)
test_inputs = [
    # 🔹 Respuestas neutrales
    ("Añadir tarea comprar pan", "neutral"),
    ("Elimina la tarea de pagar la factura", "neutral"),
    ("Muéstrame mis tareas pendientes", "neutral"),
    ("¿Qué tareas tengo para mañana?", "neutral"),

    # 🔹 Respuestas con emoción (feliz)
    ("Añadir tarea estudiar para el examen", "feliz"),
    ("Agrega una tarea para recordar mi aniversario", "feliz"),
    ("Planifica una salida con amigos", "feliz"),

    # 🔹 Respuestas con emoción (triste)
    ("Añadir tarea ir al gimnasio", "triste"),
    ("Recuérdame llamar al médico", "triste"),
    ("Organizar documentos de impuestos", "triste"),

    # 🔹 Respuestas con emoción (molesto)
    ("Elimina la tarea de hacer la declaración de impuestos", "molesto"),
    ("Cancelar cita con el banco", "molesto"),
    ("Elimina la tarea de limpiar el garaje", "molesto"),

    # 🔹 Confirmaciones y preguntas
    ("¿Puedo cancelar mi última tarea?", "neutral"),
    ("¿Ya completaste mi última tarea?", "neutral"),
    ("¿Qué tareas tengo en prioridad alta?", "neutral"),
    ("Dime qué tareas completé recientemente", "neutral"),

    # 🔹 Consultas específicas
    ("Muéstrame las tareas urgentes", "neutral"),
    ("Consulta las tareas que tengo en casa", "neutral"),
    ("Recuérdame revisar mi correo a las 5 PM", "neutral"),

    # 🔹 Frases ambiguas o sin acción
    ("Pato, qué opinas de la inteligencia artificial?", "neutral"),
    ("Calcula cuánto es 25 x 8", "neutral"),
    ("Dame un consejo sobre productividad", "neutral"),
    ("¿Qué deberíamos hacer este fin de semana?", "neutral"),
    ("Pon esto en mi lista", "neutral"),

    # 🔹 Confirmaciones y negaciones
    ("No elimines la tarea de pagar la luz", "neutral"),
    ("No quiero completar la tarea de hacer ejercicio", "neutral"),
    ("No quiero ver mis tareas ahora", "neutral"),
    ("No hagas ningún cambio en mi lista", "neutral"),

    # 🔹 Planificación futura
    ("Planifica mis tareas para la próxima semana", "neutral"),
    ("Dame un resumen de mis pendientes", "neutral"),
    ("Configura un recordatorio para llamar a mi jefe", "neutral"),
    ("Añadir evento importante el próximo lunes", "neutral"),

    # 🔹 Estados de ánimo y personalización
    ("Hoy me siento desmotivado", "triste"),
    ("Estoy emocionado por mi nuevo proyecto", "feliz"),
    ("Hoy tengo un día muy ocupado", "neutral"),
    ("No tengo ganas de hacer nada", "triste"),
    ("Me siento agotado, tengo demasiadas cosas que hacer", "estresado"),
    ("Hoy estoy de mal humor, nada me sale bien", "molesto"),
    ("Estoy muy nervioso por una presentación importante", "nervioso"),
    ("Hoy me siento muy tranquilo, sin preocupaciones", "relajado"),
    ("No tengo ganas de hacer nada hoy", "triste"),
    ("Estoy muy emocionado porque voy a empezar un nuevo proyecto", "feliz"),
    ("Necesito motivación para terminar mis tareas", "triste"),
    ("Hoy ha sido un día muy difícil", "triste"),
    ("Estoy orgulloso de todo lo que he logrado esta semana", "feliz"),
    ("Siento que no estoy avanzando con mis proyectos", "frustrado"),
    ("No tengo ganas de hablar con nadie hoy", "triste"),
]
# 📌 Variables para almacenar los resultados
resultados_detallados = []

total_tests = len(test_inputs)

def test_llm_responses():
    """Ejecuta pruebas de LLM evaluando la calidad de las respuestas."""
    print("\n📌 INICIANDO TEST DE RESPUESTAS LLM")

    for entrada, emocion in test_inputs:
        print(f"\n🔍 Probando: \"{entrada}\" | Emoción: {emocion}")

        respuesta_json = llm.generar_respuesta(entrada, emotion_detected=emocion)

        try:
            respuesta = json.loads(respuesta_json)
            assert "response" in respuesta

            response_text = respuesta["response"]

            # 📂 Guardar resultados en CSV (sin evaluación automática)
            resultados_detallados.append([
                entrada, emocion, response_text, "", ""  # Columnas para evaluación manual y notas
            ])

        except (json.JSONDecodeError, AssertionError):
            print("❌ ERROR JSON: No se pudo procesar la respuesta correctamente.")
            resultados_detallados.append([
                entrada, emocion, "ERROR_JSON", "", ""
            ])

    # 📂 Guardar reporte en CSV con TODAS las respuestas
    df_resultados = pd.DataFrame(resultados_detallados, columns=["Frase", "Emoción", "Respuesta Generada", "Evaluación Manual", "Notas"])
    df_resultados.to_csv("test_llm_responses.csv", index=False, encoding="utf-8-sig", sep=";")

    print("\n📂 **Reporte completo guardado en 'test_llm_responses.csv'**")

if __name__ == "__main__":
    test_llm_responses()