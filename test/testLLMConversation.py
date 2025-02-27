from LLM import LLM

llm = LLM()

# Simulación de prueba de conversación para evaluar si el modelo mantiene el contexto
test_conversation = [
    {"user_message": "Oye PATO, quiero organizar mis tareas para la semana.", "expected_behavior": "Reconocer que el usuario quiere gestionar sus tareas y preguntar detalles como días, prioridades, etc."},

    {"user_message": "Añade 'Revisar el informe' para el martes.", "expected_behavior": "Registrar la tarea correctamente para el martes."},

    {"user_message": "También pon 'Comprar regalos' el viernes.", "expected_behavior": "Añadir la nueva tarea sin perder la del martes."},

    {"user_message": "Cuáles son mis tareas?", "expected_behavior": "Devolver la lista de tareas pendientes con los días asignados."},

    {"user_message": "Cámbialo al jueves mejor.", "expected_behavior": "Inferir que el usuario quiere mover la última tarea mencionada ('Comprar regalos') al jueves."},

    {"user_message": "Y elimina la otra.", "expected_behavior": "Entender que 'la otra' se refiere a 'Revisar el informe' y eliminarla."},

    {"user_message": "Perfecto, qué me queda pendiente?", "expected_behavior": "Responder solo con la tarea restante."},
]

# Inicializar contexto acumulativo
contexto = ""

# Ejecutar la prueba con el LLM y mostrar resultados en formato de bloques
for i, test in enumerate(test_conversation, 1):
    response = llm.generar_respuesta(
        mensaje_usuario=test["user_message"],
        contexto=contexto  # Se pasa el contexto acumulado
    )
    
    # Agregar la respuesta del asistente al contexto para la siguiente iteración
    contexto += f"\nUsuario: {test['user_message']}\nPATO: {response}"

    # Imprimir resultados de forma clara en bloques de texto
    print("\n" + "=" * 80)
    print(f"🔹 **Interacción {i}**")
    print(f"🗣️ **Usuario:**\n{test['user_message']}\n")
    print(f"🎯 **Comportamiento esperado:**\n{test['expected_behavior']}\n")
    print(f"🤖 **Respuesta del LLM:**\n{response}\n")
    print("=" * 80)

print("\n✅ **Prueba finalizada.** Revisa si las respuestas son coherentes con el contexto.")
