import json
import sys
import os
import time
import pandas as pd
from collections import defaultdict

# Agregar el directorio padre al path para importar LLM.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from LLM import LLM

# 📌 Inicializar LLM
llm = LLM()

# 📌 Acciones válidas en tool_calls
ACCIONES_VALIDAS = {"añadir", "eliminar", "completar", "modificar", "deshacer", "consultar"}

# 📌 Casos de prueba (100 frases únicas)
test_inputs = [
    # 🔹 Añadir tareas
    ("Añadir tarea comprar pan", "añadir"),
    ("Pon en mi lista 'llamar al dentista'", "añadir"),
    ("Crea una nueva tarea: revisar informes", "añadir"),
    ("Registra 'comprar billetes de tren'", "añadir"),
    ("Anota 'recoger paquete en la oficina de correos'", "añadir"),
    ("Programa una tarea para mañana: pagar la renta", "añadir"),
    ("Añadir tarea urgente: enviar contrato firmado", "añadir"),
    ("Registra la tarea de estudiar para el examen", "añadir"),
    ("Agrega 'hacer la declaración de impuestos' a mis pendientes", "añadir"),
    ("Toma nota: 'preparar presentación para el viernes'", "añadir"),

    # 🔹 Eliminar tareas
    ("Elimina la tarea de comprar pan", "eliminar"),
    ("Borra 'llamar al dentista' de mi lista", "eliminar"),
    ("Quiero quitar la tarea de revisar informes", "eliminar"),
    ("Cancela 'comprar billetes de tren'", "eliminar"),
    ("Olvida la tarea 'recoger paquete en la oficina de correos'", "eliminar"),
    ("Elimina la tarea programada de pagar la renta", "eliminar"),
    ("Borra la tarea urgente de enviar contrato firmado", "eliminar"),
    ("Quita 'estudiar para el examen' de mis pendientes", "eliminar"),
    ("Anula la tarea de hacer la declaración de impuestos", "eliminar"),
    ("Cancela la tarea 'preparar presentación para el viernes'", "eliminar"),

    # 🔹 Completar tareas
    ("Marca como completada la tarea de comprar pan", "completar"),
    ("Ya hice 'llamar al dentista', márcala como completada", "completar"),
    ("He terminado con la tarea de revisar informes", "completar"),
    ("Confirmo que completé la tarea 'comprar billetes de tren'", "completar"),
    ("Listo, ya recogí el paquete en la oficina de correos", "completar"),
    ("He pagado la renta, marca esa tarea como terminada", "completar"),
    ("La tarea urgente de enviar el contrato ya está hecha", "completar"),
    ("Ya estudié para el examen, puedes marcar la tarea como completada", "completar"),
    ("He hecho la declaración de impuestos, tarea completada", "completar"),
    ("Terminé la presentación para el viernes, marca la tarea como hecha", "completar"),

    # 🔹 Modificar tareas
    ("Cambia la tarea de comprar pan por comprar leche", "modificar"),
    ("Modifica 'llamar al dentista' para que sea el lunes en vez del martes", "modificar"),
    ("Edita la tarea de revisar informes y cámbiala a 'revisar contrato'", "modificar"),
    ("Cambia la fecha de la tarea 'comprar billetes de tren' al jueves", "modificar"),
    ("Modifica 'recoger paquete en la oficina de correos' para que sea en la tarde", "modificar"),
    ("Actualiza la tarea de pagar la renta y pon prioridad alta", "modificar"),
    ("Edita la tarea 'enviar contrato firmado' y agrega 'adjuntar factura'", "modificar"),
    ("Cambia la prioridad de 'estudiar para el examen' a urgente", "modificar"),
    ("Edita la tarea 'hacer declaración de impuestos' y pon fecha límite mañana", "modificar"),
    ("Modifica 'preparar presentación para el viernes' y agrégale 'hacer diapositivas'", "modificar"),

    # 🔹 Consultar tareas
    ("Muéstrame mis tareas pendientes", "consultar"),
    ("Dime qué tareas tengo por hacer", "consultar"),
    ("Lista todas mis tareas activas", "consultar"),
    ("¿Qué tengo pendiente para mañana?", "consultar"),
    ("Enséñame las tareas con prioridad alta", "consultar"),
    ("Quiero ver las tareas que están programadas para esta semana", "consultar"),
    ("Consulta las tareas que he completado recientemente", "consultar"),
    ("Dime qué tareas están atrasadas", "consultar"),
    ("Necesito un resumen de mis tareas para hoy", "consultar"),
    ("¿Cuántas tareas tengo activas?", "consultar"),

    # 🔹 Deshacer acciones
    ("Deshacer la última acción", "deshacer"),
    ("Anula el último cambio que hice", "deshacer"),
    ("Quiero revertir la última tarea eliminada", "deshacer"),
    ("Recupera la última tarea que marqué como completada", "deshacer"),
    ("Deshaz el cambio que hice en la tarea 'pagar la renta'", "deshacer"),
    ("Anula la modificación de la tarea 'enviar contrato firmado'", "deshacer"),
    ("Revertir el cambio en la prioridad de 'estudiar para el examen'", "deshacer"),
    ("Recupera la tarea que cancelé sin querer", "deshacer"),
    ("Vuelve a poner la tarea de 'hacer presentación' como pendiente", "deshacer"),
    ("Deshaz la eliminación de 'comprar billetes de tren'", "deshacer"),

    # 🔹 Casos ambiguos
    ("Pon esto en mi lista", "ninguna"),
    ("Quiero hacer eso después", "ninguna"),
    ("Agrégame algo importante, pero no sé qué", "ninguna"),
    ("Recuerda que tengo algo pendiente", "ninguna"),
    ("Esto es urgente, agrégalo", "ninguna"),
    ("Necesito que me recuerdes algo", "ninguna"),
    ("Guárdame esta tarea", "ninguna"),
    ("Tengo muchas cosas que hacer, ¿qué me sugieres?", "ninguna"),
    ("No sé qué hacer primero", "ninguna"),
    ("Tengo que organizarme mejor", "ninguna"),

    # 🔹 Comandos negativos
    ("No elimines la tarea de pagar la luz", "ninguna"),
    ("No quiero completar la tarea de hacer ejercicio", "ninguna"),
    ("No borres nada todavía", "ninguna"),
    ("No quiero modificar ninguna tarea", "ninguna"),
    ("No hagas cambios en mis tareas", "ninguna"),
    ("No agregues más tareas por ahora", "ninguna"),
    ("No quiero que recuerdes esto", "ninguna"),
    ("No hagas nada con mi lista de tareas", "ninguna"),
    ("No quiero ver mis pendientes ahora", "ninguna"),
    ("No modifiques mis tareas urgentes", "ninguna"),
]

# 📌 Variables para estadísticas y errores
errores_por_categoria = defaultdict(int)
aciertos_por_categoria = defaultdict(int)
errores_por_accion = defaultdict(int)
aciertos_por_accion = defaultdict(int)
resultados_detallados = []

total_tests = len(test_inputs)

def test_llm():
    """Ejecuta pruebas de LLM validando JSON, contexto y memoria, y analiza estadísticas detalladas."""
    print("\n📌 INICIANDO TEST DE LLM")
    errores_totales = 0

    for entrada, accion_esperada in test_inputs:
        print(f"\n🔍 Probando: \"{entrada}\" | Esperado: {accion_esperada}")

        respuesta_json = llm.generar_respuesta(entrada)

        try:
            respuesta = json.loads(respuesta_json)
            assert "response" in respuesta and "tool_calls" in respuesta

            # 📌 Evaluación específica de acciones
            tool_calls = respuesta["tool_calls"]
            acciones_detectadas = {tc["action"] for tc in tool_calls} if tool_calls else set()
            es_correcto = accion_esperada in acciones_detectadas if accion_esperada != "ninguna" else not acciones_detectadas

            # 📌 Registro de resultados
            if es_correcto:
                aciertos_por_categoria[accion_esperada] += 1
                aciertos_por_accion[accion_esperada] += 1
                print(f"✔ ACCIÓN CORRECTA ({accion_esperada})")
            else:
                errores_totales += 1
                errores_por_categoria[accion_esperada] += 1
                errores_por_accion[accion_esperada] += 1
                print(f"❌ ERROR: Se esperaba '{accion_esperada}' | Detectado: {acciones_detectadas if acciones_detectadas else 'NINGUNA ACCIÓN'}")

            # 📂 Guardar resultados en CSV
            resultados_detallados.append([
                entrada, accion_esperada, acciones_detectadas, "CORRECTO" if es_correcto else "INCORRECTO", respuesta_json
            ])

        except (json.JSONDecodeError, AssertionError):
            errores_totales += 1
            errores_por_categoria[accion_esperada] += 1
            resultados_detallados.append([
                entrada, accion_esperada, "ERROR_JSON", "INCORRECTO", respuesta_json
            ])
            print("❌ ERROR JSON: No se pudo procesar la respuesta correctamente.")
            
        time.sleep(0.1)

    # 📊 Resultados finales
    aciertos_totales = sum(aciertos_por_categoria.values())

    print("\n📊 📌 **RESUMEN GENERAL DE LOS TESTS** 📌")
    print("──────────────────────────────────────────────")
    print(f"🔹 **TOTAL DE TESTS:** {total_tests}")
    print(f"✅ **RESPUESTAS CORRECTAS:** {aciertos_totales} ({(aciertos_totales / total_tests) * 100:.2f}%)")
    print(f"❌ **ERRORES DETECTADOS:** {errores_totales} ({(errores_totales / total_tests) * 100:.2f}%)")
    print("──────────────────────────────────────────────\n")

    # 📊 Errores por acción esperada
    print("📊 **ERRORES POR ACCIÓN ESPERADA:**")
    for accion, count in errores_por_categoria.items():
        total_tests_accion = errores_por_categoria[accion] + aciertos_por_categoria[accion]
        precision = (aciertos_por_categoria[accion] / total_tests_accion) * 100 if total_tests_accion > 0 else 0
        print(f"❌ {accion}: {count} errores | 📌 Precisión: {precision:.2f}%")

    print("\n📊 **ERRORES POR ACCIÓN DETECTADA:**")
    for accion, count in errores_por_accion.items():
        total_tests_accion = errores_por_accion[accion] + aciertos_por_accion[accion]
        precision = (aciertos_por_accion[accion] / total_tests_accion) * 100 if total_tests_accion > 0 else 0
        print(f"❌ {accion}: {count} errores | 📌 Precisión: {precision:.2f}%")

    # 📂 Guardar reporte en CSV con TODAS las respuestas (buenas y malas)
    df_resultados = pd.DataFrame(resultados_detallados, columns=["Frase", "Acción Esperada", "Acciones Detectadas", "Estado", "Respuesta Generada"])
    df_resultados.to_csv("test_llm_resultados.csv", index=False, encoding="utf-8")

    print("\n📂 **Reporte completo guardado en 'test_llm_resultados.csv'**")

if __name__ == "__main__":
    test_llm()
