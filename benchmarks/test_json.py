import json
import sys
import os
import pandas as pd
from collections import defaultdict

# Agregar el directorio padre al path para importar LLM.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from LLM import LLM

# 📌 Inicializar LLM
llm = LLM()

# 📌 Campos esperados en tool_calls
VALORES_VALIDOS_PRIORIDAD = {"baja", "normal", "alta", "urgente"}

# 📌 Casos de prueba con el número exacto de acciones esperadas, fechas y prioridades
test_inputs = [
    # 🔹 Añadir tareas simples
    ("Añadir tarea comprar pan", {"añadir": 1}, None, "normal"),
    ("Agregar 'llamar al dentista'", {"añadir": 1}, None, "normal"),
    ("Crea una nueva tarea: revisar informe mensual", {"añadir": 1}, None, "normal"),
    ("Anota 'comprar billetes de tren'", {"añadir": 1}, None, "normal"),
    ("Registra 'recoger paquete en la oficina de correos'", {"añadir": 1}, None, "normal"),

    # 🔹 Añadir tareas con fechas
    ("Añadir tarea 'pagar alquiler' para el próximo viernes", {"añadir": 1}, "2025-03-07", "normal"),
    ("Agrega 'revisión médica' el 10 de marzo", {"añadir": 1}, "2025-03-10", "normal"),
    ("Anota 'preparar presentación' para el lunes", {"añadir": 1}, "2025-03-03", "normal"),

    # 🔹 Añadir tareas con prioridad
    ("Añadir 'enviar informe final' con prioridad alta", {"añadir": 1}, None, "alta"),
    ("Registra 'pagar facturas' como urgente", {"añadir": 1}, None, "urgente"),

    # 🔹 Eliminar tareas simples
    ("Eliminar la tarea de comprar pan", {"eliminar": 1}, None, None),
    ("Borra 'llamar al dentista' de mi lista", {"eliminar": 1}, None, None),
    ("Quita la tarea de revisar informe mensual", {"eliminar": 1}, None, None),

    # 🔹 Completar tareas
    ("Marca como completada la tarea de comprar pan", {"completar": 1}, None, None),
    ("Ya hice 'llamar al dentista', márcala como completada", {"completar": 1}, None, None),

    # 🔹 Modificar tareas
    ("Cambia la tarea de comprar pan por comprar leche", {"modificar": 1}, None, None),
    ("Modifica 'llamar al dentista' para que sea el martes en vez del lunes", {"modificar": 1}, "2025-03-04", None),

    # 🔹 Deshacer acciones
    ("Deshacer la última acción", {"deshacer": 1}, None, None),
    ("Anula el último cambio que hice", {"deshacer": 1}, None, None),

    # 🔹 Consultar tareas
    ("Muéstrame mis tareas pendientes", {"consultar": 2}, None, None),  
    ("Dime qué tareas tengo programadas para mañana", {"consultar": 3}, "2025-03-03", None),

    # 🔹 Combinaciones de añadir y eliminar
    ("Añadir 'hacer ejercicio' y eliminar 'revisar documentos'", {"añadir": 1, "eliminar": 1}, None, "normal"),
    ("Agregar 'comprar entradas' y eliminar 'cancelar suscripción'", {"añadir": 1, "eliminar": 1}, None, "normal"),
    ("Añadir 'cita con el médico' y borrar 'revisión anual'", {"añadir": 1, "eliminar": 1}, None, "normal"),

    # 🔹 Múltiples acciones del mismo tipo
    ("Añadir 'leer un libro', 'hacer ejercicio' y 'revisar correo'", {"añadir": 3}, None, "normal"),
    ("Eliminar 'pagar la luz', 'sacar la basura' y 'organizar documentos'", {"eliminar": 3}, None, None),
    ("Modificar 'hacer ejercicio' a 'yoga' y 'leer un libro' a 'escuchar audiolibro'", {"modificar": 2}, None, None),

    # 🔹 Casos límite
    ("Añadir tarea", {}, None, None),  
    ("Eliminar tarea", {}, None, None),  
    ("Modificar tarea", {}, None, None),  
    ("Deshacer", {"deshacer": 1}, None, None),

    # 🔹 Consultas con filtros
    ("Muéstrame solo las tareas urgentes", {"consultar": 1}, None, "urgente"),  
    ("Consulta las tareas que tengo para este fin de semana", {"consultar": 2}, "2025-03-08", None),
    ("Filtra mis tareas por prioridad alta", {"consultar": 2}, None, "alta"),

    # 🔹 Más combinaciones
    ("Añadir 'revisar informe' y 'asistir a reunión' y eliminar 'hacer ejercicio'", {"añadir": 2, "eliminar": 1}, None, "normal"),
    ("Completa 'sacar la basura' y 'lavar el coche'", {"completar": 2}, None, None),
    ("Añadir 'preparar comida', modificar 'hacer ejercicio' a 'yoga' y eliminar 'leer libro'", {"añadir": 1, "modificar": 1, "eliminar": 1}, None, "normal"),

    # 🔹 Frases ambiguas
    ("Pon esto en mi lista", {}, None, None),  
    ("Quiero que registres algo", {}, None, None),  
    ("Creo que necesito recordar algo", {}, None, None),

    # 🔹 Frases con negaciones
    ("No elimines la tarea de pagar la luz", {}, None, None),  
    ("No quiero completar la tarea de hacer ejercicio", {}, None, None),  
    ("No borres nada todavía", {}, None, None),

    # 🔹 Consultas avanzadas
    ("Muéstrame las tareas de la próxima semana", {"consultar": 3}, "2025-03-10", None),
    ("Dime qué tareas ya completé este mes", {"consultar": 2}, None, None),
    ("Consulta mis tareas de trabajo y personales por separado", {"consultar": 4}, None, None),

    # 🔹 Fechas relativas
    ("Añadir 'comprar un regalo' para mañana", {"añadir": 1}, "2025-03-04", "normal"),
    ("Eliminar la tarea programada para la próxima semana", {"eliminar": 1}, "2025-03-10", None),
    ("Consulta mis tareas dentro de dos semanas", {"consultar": 2}, "2025-03-17", None),

    # 🔹 Casos de muchas tareas
    ("Añadir 5 tareas: 'hacer la cama', 'sacar la basura', 'regar plantas', 'ordenar el armario' y 'enviar correo'", {"añadir": 5}, None, "normal"),
    ("Eliminar 4 tareas: 'pagar suscripción', 'borrar archivos', 'devolver libro' y 'hacer ejercicio'", {"eliminar": 4}, None, None),
    ("Modificar 3 tareas: 'trabajar en proyecto' a 'terminar informe', 'leer libro' a 'escuchar audiolibro', 'hacer ejercicio' a 'caminar'", {"modificar": 3}, None, None),
]


# 📌 Acciones válidas en `tool_calls`
ACCIONES_VALIDAS = {"añadir", "eliminar", "completar", "modificar", "deshacer", "consultar"}
VALORES_VALIDOS_PRIORIDAD = {"baja", "normal", "alta", "urgente"}

# 📌 Variables para estadísticas y errores
errores_por_accion = defaultdict(int)
aciertos_por_accion = defaultdict(int)
errores_fecha = 0
errores_prioridad = 0
errores_combinaciones = 0
errores_json = 0
errores_totales = 0

errores_detallados = []
total_tests = len(test_inputs)

def validar_estructura_tool_calls(tool_calls, acciones_esperadas, fecha_esperada, prioridad_esperada):
    """Verifica que la estructura de tool_calls sea correcta"""
    errores = []
    found_actions = defaultdict(int)

    if not tool_calls:
        errores.append("tool_calls está vacío.")
        return errores

    for idx, tool_call in enumerate(tool_calls):
        tool_idx = f"ToolCall {idx + 1}"

        # Verificar que la acción es válida
        if tool_call["action"] not in ACCIONES_VALIDAS:
            errores.append(f"{tool_idx}: Acción desconocida '{tool_call['action']}'.")

        # Validar la fecha esperada (`due_date`)
        if fecha_esperada is not None and tool_call["due_date"] != fecha_esperada:
            errores.append(f"{tool_idx}: La fecha esperada era '{fecha_esperada}', pero se generó '{tool_call['due_date']}'.")
            global errores_fecha
            errores_fecha += 1

        # Validar la prioridad esperada (`priority`)
        if prioridad_esperada is not None and tool_call["priority"] != prioridad_esperada:
            errores.append(f"{tool_idx}: La prioridad esperada era '{prioridad_esperada}', pero se generó '{tool_call['priority']}'.")
            global errores_prioridad
            errores_prioridad += 1

        found_actions[tool_call["action"]] += 1

    # **Validar que cada tipo de acción detectado en `tool_calls` coincida con lo esperado**
    for accion, cantidad_esperada in acciones_esperadas.items():
        cantidad_detectada = found_actions.get(accion, 0)
        if cantidad_detectada != cantidad_esperada:
            errores.append(f"Se esperaban {cantidad_esperada} acciones '{accion}', pero se detectaron {cantidad_detectada}.")
            global errores_combinaciones
            errores_combinaciones += 1

    return errores

def test_llm_json_structure():
    """Ejecuta pruebas de LLM validando la estructura del JSON"""
    print("\n📌 INICIANDO TEST DE ESTRUCTURA JSON")

    for entrada, acciones_esperadas, fecha_esperada, prioridad_esperada in test_inputs:
        acciones_str = ", ".join(f"{accion} ({cantidad})" for accion, cantidad in acciones_esperadas.items())
        print(f"\n🔍 Probando: \"{entrada}\" | Esperado: {acciones_str}, Fecha: {fecha_esperada}, Prioridad: {prioridad_esperada}")

        respuesta_json = llm.generar_respuesta(entrada)

        try:
            respuesta = json.loads(respuesta_json)
            assert "response" in respuesta and "tool_calls" in respuesta

            tool_calls = respuesta["tool_calls"]

            # 📌 Validar estructura de tool_calls
            errores = validar_estructura_tool_calls(tool_calls, acciones_esperadas, fecha_esperada, prioridad_esperada)
            es_correcto = len(errores) == 0

            if es_correcto:
                for accion in acciones_esperadas:
                    aciertos_por_accion[accion] += 1
                print("✅ JSON ESTRUCTURA CORRECTA")
            else:
                global errores_totales
                errores_totales += 1
                for accion in acciones_esperadas:
                    errores_por_accion[accion] += 1
                print(f"❌ ERROR en estructura JSON: {', '.join(errores)}")

            resultados = [entrada, acciones_str, fecha_esperada, prioridad_esperada, respuesta_json, "CORRECTO" if es_correcto else "INCORRECTO"]
            errores_detallados.append(resultados)

        except (json.JSONDecodeError, AssertionError):
            global errores_json
            errores_totales += 1
            errores_json += 1
            print("❌ ERROR JSON: No se pudo procesar la respuesta correctamente.")
            errores_detallados.append([entrada, acciones_str, fecha_esperada, prioridad_esperada, "ERROR_JSON", "INCORRECTO"])

    # 📂 Guardar reporte en CSV con TODAS las respuestas
    df_resultados = pd.DataFrame(errores_detallados, columns=["Frase", "Acciones Esperadas", "Fecha Esperada", "Prioridad Esperada", "JSON Generado", "Estado"])
    df_resultados.to_csv("test_llm_json_structure.csv", index=False, encoding="utf-8-sig", sep=";")

    # 📊 Resumen Final de Resultados
    print("\n📊 📌 **RESUMEN FINAL DE RESULTADOS** 📌")
    print("──────────────────────────────────────────────")
    print(f"🔹 **TOTAL DE TESTS:** {total_tests}")
    print(f"✅ **RESPUESTAS CORRECTAS:** {total_tests - errores_totales} ({((total_tests - errores_totales) / total_tests) * 100:.2f}%)")
    print(f"❌ **ERRORES DETECTADOS:** {errores_totales} ({(errores_totales / total_tests) * 100:.2f}%)")
    print(f"🔄 **Errores en JSON estructural:** {errores_json}")
    print(f"📅 **Errores en fechas (`due_date`)**: {errores_fecha}")
    print(f"🔥 **Errores en prioridad (`priority`)**: {errores_prioridad}")
    print(f"⚠ **Errores en combinación de acciones:** {errores_combinaciones}")

    # 📊 Errores por tipo de acción
    print("\n📊 **ERRORES POR TIPO DE ACCIÓN:**")
    for accion, count in errores_por_accion.items():
        total_tests_accion = errores_por_accion[accion] + aciertos_por_accion[accion]
        precision = (aciertos_por_accion[accion] / total_tests_accion) * 100 if total_tests_accion > 0 else 0
        print(f"❌ {accion}: {count} errores | 📌 Precisión: {precision:.2f}%")

    print("\n📂 **Reporte completo guardado en 'test_llm_json_structure.csv'**")

if __name__ == "__main__":
    test_llm_json_structure()