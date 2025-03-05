import sys
import os
import pandas as pd
from collections import defaultdict

# Agregar el directorio padre al path para importar NLU.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from NLU import NLU

nlu = NLU(models_path="D:\MASTER\PATO\models")

test_intents = {
    "Adiós" : "despedir",
    "Hasta pronto, pato" : "despedir",
    "Ya me voy, hablamos luego" : "despedir",
    "Muchas gracias por todo, nos vemos más tarde" : "despedir",
    "Gracias por la ayuda, hasta otra" : "despedir",
    "Pato, ya puedes descansar" : "despedir",
    "Ciao, amigo pato" : "despedir",
    "Hablamos otro día, cuídate" : "despedir",
    "Pato, apágate y descansa" : "despedir",
    "Nos vemos en la próxima conversación" : "despedir",
    "Ya es tarde, mejor dejo esto por ahora, hasta luego" : "despedir",
    "Terminé por hoy, gracias y adiós" : "despedir",
    "Me despido, seguimos otro día" : "despedir",

    "Termina esta conversación" : "terminar_conversacion",
    "Pato, para la conversación" : "terminar_conversacion",
    "Apaga el chat, ya no quiero seguir" : "terminar_conversacion",
    "Detén el diálogo, no quiero más respuestas" : "terminar_conversacion",
    "Cierra esto, ya no es necesario" : "terminar_conversacion",
    "Fin del tema, no más interacción" : "terminar_conversacion",
    "Pato, ya puedes detenerte" : "terminar_conversacion",
    "Corta la comunicación, no sigas hablando" : "terminar_conversacion",
    "Pato, para ya, necesito silencio" : "terminar_conversacion",
    "Ya acabamos, deja de responder" : "terminar_conversacion",
    "Finaliza esta charla, hemos terminado" : "terminar_conversacion",
    "Quiero cerrar este tema y seguir otro día" : "terminar_conversacion",
    "No hables más, termina aquí" : "terminar_conversacion",

    "Quiero empezar de nuevo" : "reiniciar_conversacion",
    "Pato, olvida todo lo que hemos hablado" : "reiniciar_conversacion",
    "Reinicia el contexto de la conversación" : "reiniciar_conversacion",
    "Borra todo y volvamos a empezar" : "reiniciar_conversacion",
    "Resetea la charla y empecemos otra vez" : "reiniciar_conversacion",
    "Borrón y cuenta nueva, empecemos desde cero" : "reiniciar_conversacion",
    "Vamos a intentarlo otra vez, pero desde el principio" : "reiniciar_conversacion",
    "Pato, necesito empezar otra vez, sin recordar lo anterior" : "reiniciar_conversacion",
    "Necesito un nuevo comienzo en esta charla" : "reiniciar_conversacion",
    "Elimina el historial y dime que puedo hacer ahora" : "reiniciar_conversacion",
    "Reinicia tus datos de conversación y dime algo nuevo" : "reiniciar_conversacion",
    "Quiero que empieces de cero, sin contexto previo" : "reiniciar_conversacion",

    "Muéstrame todos los comandos posibles" : "mostrar_comandos",
    "Qué funciones puedo activar contigo?" : "mostrar_comandos",
    "Dame una lista de órdenes válidas" : "mostrar_comandos",
    "Pato, dime cómo puedo controlarte" : "mostrar_comandos",
    "¿Cómo interactúo contigo con comandos?" : "mostrar_comandos",
    "Dame un resumen de los comandos que entiendes" : "mostrar_comandos",
    "Explícame qué puedo hacer con comandos" : "mostrar_comandos",
    "Necesito saber qué órdenes puedes ejecutar" : "mostrar_comandos",
    "Quiero saber las instrucciones para manejar la conversación" : "mostrar_comandos",
    "Qué comandos tengo disponibles para manejar la charla?" : "mostrar_comandos",
    "Pato, dime todas las funciones que puedo usar contigo" : "mostrar_comandos",

    "Pausa esto por un momento" : "pausar_conversacion",
    "Pato, quédate en silencio unos minutos" : "pausar_conversacion",
    "Pon en espera la charla" : "pausar_conversacion",
    "Necesito hacer algo, detente un momento" : "pausar_conversacion",
    "Haz una pausa en la conversación y espera" : "pausar_conversacion",
    "Guarda silencio hasta que te diga que sigas" : "pausar_conversacion",
    "No respondas por ahora, solo espera" : "pausar_conversacion",
    "Déjame concentrarme, no hables por un rato" : "pausar_conversacion",
    "Necesito un respiro, pon esto en pausa" : "pausar_conversacion",
    "Luego seguimos, mantén esto pausado" : "pausar_conversacion",

    "Sigamos donde lo dejamos" : "continuar_conversacion",
    "Continúa con la conversación" : "continuar_conversacion",
    "Retoma lo último que me estabas diciendo" : "continuar_conversacion",
    "Puedes seguir con el tema anterior" : "continuar_conversacion",
    "Perdón, tuve que irme, dime qué decías" : "continuar_conversacion",
    "Estoy de vuelta, seguimos?" : "continuar_conversacion",
    "No recuerdo qué decías antes, puedes repetir?" : "continuar_conversacion",
    "Quiero continuar con lo que hablábamos antes" : "continuar_conversacion",
    "Retomemos esto desde el punto en que lo dejamos" : "continuar_conversacion",
    "Dime en qué habíamos quedado" : "continuar_conversacion",

    "Pato, qué opinas de la inteligencia artificial?" : "nlu_fallback",
    "Me recomiendas comprar un coche eléctrico?" : "nlu_fallback",
    "Oye, qué piensas sobre la filosofía del estoicismo?" : "nlu_fallback",
    "Dime algo interesante sobre el universo" : "nlu_fallback",
    "Cómo preparo una pizza en casa?" : "nlu_fallback",
    "Qué temperatura hará mañana en Madrid?" : "nlu_fallback",
    "Pato, cuál es la mejor película de ciencia ficción?" : "nlu_fallback",
    "Cuéntame un chiste, quiero reírme un poco" : "nlu_fallback",
    "Quiero hablar sobre política, qué opinas?" : "nlu_fallback",
    "Necesito ayuda con matemáticas, cuánto es 25 x 8?" : "nlu_fallback",
    "Hola PATO buenos dias, ¿cómo estas?" : "nlu_fallback",

    "Añadir tarea comprar pan" : "nlu_fallback",
    "Agrega una nueva tarea: llamar al médico" : "nlu_fallback",
    "Quiero que registres la tarea de revisar correos" : "nlu_fallback",
    "Anota la tarea de pagar la factura de la luz" : "nlu_fallback",
    "Pato, apunta 'revisar informe mensual' en la lista de tareas" : "nlu_fallback",
    "Agrégame 'llevar el coche al taller' como una tarea pendiente" : "nlu_fallback",
    "Crea una tarea para hacer ejercicio a las 6pm" : "nlu_fallback",
    "Toma nota: 'terminar presentación para el viernes'" : "nlu_fallback",
    "Pon en mi lista de tareas: 'comprar regalo para mamá'" : "nlu_fallback",
    "Apunta esto: 'estudiar para el examen de matemáticas'" : "nlu_fallback",

    "¿Qué tareas tengo pendientes?" : "nlu_fallback",
    "Muéstrame mi lista de tareas" : "nlu_fallback",
    "¿Cuáles son mis próximas tareas?" : "nlu_fallback",
    "Dime qué cosas tengo por hacer hoy" : "nlu_fallback",
    "Enséñame la lista de tareas activas" : "nlu_fallback",
    "Pato, dime qué pendientes tengo" : "nlu_fallback",
    "¿Cuántas tareas sin completar tengo?" : "nlu_fallback",
    "Quiero ver las tareas que aún no he hecho" : "nlu_fallback",
    "Recuérdame qué cosas tenía anotadas para hoy" : "nlu_fallback",
    "Lista todas mis tareas, por favor" : "nlu_fallback",

    "Borra la tarea de comprar pan" : "nlu_fallback",
    "Elimina la tarea que dice 'revisar informe mensual'" : "nlu_fallback",
    "Pato, quiero borrar 'llamar al médico' de mi lista" : "nlu_fallback",
    "Quiero quitar la tarea de hacer ejercicio" : "nlu_fallback",
    "Borra todas las tareas que ya no sean importantes" : "nlu_fallback",
    "Elimina la última tarea que agregué" : "nlu_fallback",
    "¿Puedes eliminar la tarea de pagar la luz?" : "nlu_fallback",
    "Ya no necesito la tarea de 'comprar regalo', bórrala" : "nlu_fallback",
    "Pato, elimina la tarea con el nombre 'estudiar para examen'" : "nlu_fallback",

    "Borra las tareas completadas" : "nlu_fallback",
    "Marca como completada la tarea de comprar pan" : "nlu_fallback",
    "Ya terminé 'llamar al médico', márcala como hecha" : "nlu_fallback",
    "Tarea 'hacer ejercicio' completada, actualiza mi lista" : "nlu_fallback",
    "Pato, marca la tarea de revisar correos como hecha" : "nlu_fallback",
    "Acabo de terminar la tarea de pagar la factura, regístrala como completada" : "nlu_fallback",
    "Ya hice todo lo de la presentación, actualiza mi lista" : "nlu_fallback",
    "Marca como hecha la tarea 'llevar el coche al taller'" : "nlu_fallback",
    "Terminé la tarea de comprar el regalo, ¿puedes actualizar mi lista?" : "nlu_fallback",
    "Quiero que marques como finalizada la tarea de 'estudiar para examen'" : "nlu_fallback",
    "Pato, confirma que he completado la última tarea que agregué" : "nlu_fallback",

    "¿Qué tareas ya he completado?" : "nlu_fallback",
    "Muéstrame la lista de tareas terminadas" : "nlu_fallback",
    "Quiero ver las tareas que ya he hecho" : "nlu_fallback",
    "¿Cuáles son las tareas que ya completé?" : "nlu_fallback",
    "Dame un resumen de mis tareas finalizadas" : "nlu_fallback",
    "Pato, enséñame las cosas que ya terminé" : "nlu_fallback",
    "¿Cuántas tareas he logrado completar hasta ahora?" : "nlu_fallback",
    "Recuérdame las tareas que ya marqué como hechas" : "nlu_fallback",
    "Quiero ver las tareas cerradas" : "nlu_fallback",
    "Lista las últimas cinco tareas que completé" : "nlu_fallback"
}

# 📌 Variables para análisis de errores
errores_por_intent = defaultdict(int)
aciertos_por_intent = defaultdict(int)
errores_detallados = []

def test_nlu():
    """Prueba la detección de intents con Rasa NLU y analiza los errores."""
    print("\n📌 INICIANDO TEST DE NLU")
    total_tests = len(test_intents)
    errores = 0

    for frase, intent_esperado in test_intents.items():
        print(f"\n🔍 Probando NLU con: \"{frase}\"")

        intent_detectado = nlu.detectar_intent(frase)

        if intent_detectado is None:
            intent_detectado = "nlu_fallback"

        # 📌 Registro de aciertos y errores por intent
        if intent_detectado == intent_esperado:
            aciertos_por_intent[intent_esperado] += 1
            print(f"✅ Intent detectado correctamente: {intent_detectado}")
        else:
            errores_por_intent[intent_esperado] += 1
            errores += 1
            errores_detallados.append([frase, intent_esperado, intent_detectado])
            print(f"❌ ERROR: Se esperaba \"{intent_esperado}\", pero se detectó \"{intent_detectado}\"")

    # 📊 Resultados finales
    print("\n📊 RESULTADOS GLOBALES:")
    print(f"🔹 Precisión total: {((total_tests - errores) / total_tests) * 100:.2f}%")
    print(f"❌ Total de errores: {errores} / {total_tests}")

    # 📊 Análisis de errores por intent
    print("\n📊 ERRORES POR INTENT:")
    for intent, count in errores_por_intent.items():
        total_tests_intent = errores_por_intent[intent] + aciertos_por_intent[intent]
        precision = (aciertos_por_intent[intent] / total_tests_intent) * 100 if total_tests_intent > 0 else 0
        print(f"❌ {intent}: {count} errores | Precisión: {precision:.2f}%")

    # 📂 Guardar reporte de errores en CSV
    df_errores = pd.DataFrame(errores_detallados, columns=["Frase", "Intent esperado", "Intent detectado"])
    df_errores.to_csv("test_nlu_errores.csv", index=False, encoding="utf-8")
    print("\n📂 Reporte de errores guardado en 'test_nlu_errores.csv'")

if __name__ == "__main__":
    test_nlu()