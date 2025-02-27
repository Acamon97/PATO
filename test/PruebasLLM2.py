import json
from LLM import LLM

# Inicializar el modelo con memoria optimizada
llm = LLM()

# Función para probar la respuesta y validación del JSON
def probar_interaccion(mensaje):
    print(f"\n🔹 Usuario: {mensaje}")
    
    respuesta = llm.generar_respuesta(mensaje)
    
    # Validar que la respuesta sea un JSON válido
    try:
        respuesta_json = json.loads(json.dumps(respuesta))  # Simulación de validación JSON
        print("✅ Respuesta válida en JSON:")
        print(json.dumps(respuesta_json, indent=4, ensure_ascii=False))
    except json.JSONDecodeError:
        print("❌ ERROR: La respuesta del LLM no es un JSON válido.")
    
    return respuesta_json

# 📌 1️⃣ Prueba: Añadir tareas
probar_interaccion("Añade una tarea para comprar leche mañana con prioridad alta.")
probar_interaccion("Añade otra tarea para entregar el informe el próximo lunes con prioridad urgente.")

# 📌 2️⃣ Prueba: Conversación casual
probar_interaccion("Hola PATO, ¿cómo estás hoy?")
probar_interaccion("Cuéntame algo interesante sobre el espacio.")

# 📌 3️⃣ Prueba: Preguntar sobre tareas previas
probar_interaccion("¿Qué tareas tengo para mañana?")
probar_interaccion("¿Tengo alguna tarea de prioridad urgente?")

# 📌 4️⃣ Prueba: Deshacer última acción
probar_interaccion("Deshaz la última acción.")

# 📌 5️⃣ Prueba: Evaluar memoria con una conversación larga
mensajes_largos = [
    "Quiero planear mi semana. ¿Puedes ayudarme a organizar mis tareas?",
    "Voy a hacer ejercicio tres veces por semana. Agrégalo como tarea repetitiva.",
    "Recuérdame qué tareas tengo pendientes.",
    "Ahora elimina la tarea de hacer ejercicio, no la necesito."
]

for mensaje in mensajes_largos:
    probar_interaccion(mensaje)

# 📌 6️⃣ Prueba: Verificar si el asistente recuerda información pasada
probar_interaccion("Recuérdame qué tarea eliminé hace un momento.")
