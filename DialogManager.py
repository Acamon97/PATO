"""
DialogManager.py - Gestor de diálogos del asistente P.A.T.O.

Este módulo gestiona la interacción del usuario con el asistente, incluyendo:
- Procesamiento de comandos de voz y detección de intents.
- Integración con modelos NLU y LLM para generar respuestas.
- Manejo de tareas pendientes y completadas.
- Control de estado de conversación (pausa, inactividad, apagado).

Clases:
- DialogManager: Controla la interacción entre el usuario y el asistente.

Dependencias:
- NLU: Módulo para la detección de intents.
- SER: Módulo para análisis de emociones en audio.
- LLM: Modelo de lenguaje que genera respuestas en función del contexto.
- TaskHandler: Manejador de tareas del usuario.
"""

import json
import re
import time
import threading
import TTS
from SER import SER  # Análisis de emociones en voz
from NLU import NLU  # Procesamiento del lenguaje natural
from TaskHandler import TaskHandler  # Gestión de tareas
from LLM import LLM  # Modelo de lenguaje para generación de respuestas


class DialogManager:
    """
    Clase que gestiona el flujo de conversación del asistente virtual P.A.T.O.

    Atributos:
    - INACTIVITY_TIMEOUT: Tiempo límite sin interacción antes de desactivar la conversación.
    - PAUSE_TIMEOUT: Tiempo límite cuando la conversación está pausada.
    
    Métodos principales:
    - procesar_comando: Recibe y gestiona comandos del usuario.
    - procesar_intent: Determina el intent del usuario y responde apropiadamente.
    - generar_respuesta: Consulta el LLM y responde al usuario.
    - manejar_intent_control: Gestiona intents de control como pausa, reinicio o apagado.
    - shutdown: Apaga correctamente el gestor de diálogo.
    """

    INACTIVITY_TIMEOUT = 60  # Tiempo límite en segundos para conversación activa
    PAUSE_TIMEOUT = 120  # Tiempo límite en segundos cuando la conversación está pausada

    def __init__(self, asistente):
        """Inicializa el gestor de diálogo con instancias de NLU, SER, LLM y TaskHandler."""
        self.asistente = asistente
        self.nlu = NLU()
        self.ser = SER()
        self.llm = LLM()
        self.task_handler = TaskHandler()
        self.conversacion_activa = False
        self.pausa_activada = False  # Indica si la conversación está pausada
        self.ultima_actividad = time.time()  # Marca de tiempo de la última actividad

        # Palabras clave para activar y apagar el asistente
        self.wake_words = re.compile(r'\boye,?\s+pato\b', re.IGNORECASE)
        self.shutdown_words = re.compile(r'\bapagar,?\s+pato\b', re.IGNORECASE)

        # Hilo para monitorear inactividad
        self.inactividad_thread = threading.Thread(target=self.monitor_inactividad, daemon=True)
        self.inactividad_thread.start()

    def extraer_comando(self, command: str) -> str:
        """Extrae el comando tras la palabra de activación."""
        match = re.search(r'\boye,?\s+pato\b[,:]?\s(.*)', command, re.IGNORECASE)
        return match.group(1).strip() if match and match.group(1) else None

    def procesar_comando(self, command: str, command_wav_file: str):
        """Gestiona un comando detectado y controla el flujo de la conversación."""
        self.ultima_actividad = time.time()  # Actualizar marca de tiempo
        emotion_detected = self.ser.detect_emotion(command_wav_file)

        if not command:
            return

        if not self.conversacion_activa:
            if self.shutdown_words.search(command):
                self.shutdown()
                return

            if self.wake_words.search(command):
                self.conversacion_activa = True
                TTS.quack(1)  # Señal de activación
                comando_extraido = self.extraer_comando(command)
                self.procesar_intent(comando_extraido if comando_extraido else "hola", emotion_detected)
                return

        if self.conversacion_activa:
            self.procesar_intent(command, emotion_detected)

    def procesar_intent(self, user_message: str, emotion_detected: str):
        """Detecta el intent del usuario y maneja la conversación en consecuencia."""
        self.ultima_actividad = time.time()

        intent = self.nlu.detectar_intent(user_message)
        print(f"\nNLU -> Intent detectado: {intent}")

        if intent in {
            "despedir", "terminar_conversacion", "reiniciar_conversacion",
            "pausar_conversacion", "continuar_conversacion", "mostrar_comandos"
        }:
            self.manejar_intent_control(intent)
            return

        if not self.pausa_activada:
            self.generar_respuesta(user_message, emotion_detected)

    def generar_respuesta(self, user_message: str, emotion_detected: str):
        """Genera una respuesta basada en el contexto y la entrada del usuario."""
		
        tareas_pendientes_txt = self.task_handler.task_manager.consultar_tareas(False)
        tareas_completadas_txt = self.task_handler.task_manager.consultar_tareas_completadas(False)
        
        print(f"\nDM -> Listas de tareas pendientes:\n{tareas_pendientes_txt}")
        print(f"\nDM -> Listas de tareas completadas:\n{tareas_completadas_txt}")
		
        tareas_pendientes = self.task_handler.task_manager.consultar_tareas()
        tareas_completadas = self.task_handler.task_manager.consultar_tareas_completadas()

        contexto = {**tareas_pendientes, **tareas_completadas}
        respuesta_json = self.llm.generar_respuesta(user_message, contexto=json.dumps(contexto), emotion_detected=emotion_detected)
        respuesta_json = json.loads(respuesta_json)

        respuesta_final = (
            self.task_handler.procesar_acciones(respuesta_json) 
            if respuesta_json and respuesta_json.get("tool_calls") 
            else respuesta_json.get("response", "No tengo una respuesta adecuada en este momento.")
        )
        
        tareas_pendientes_txt = self.task_handler.task_manager.consultar_tareas(False)
        tareas_completadas_txt = self.task_handler.task_manager.consultar_tareas_completadas(False)
        print(f"\nDM -> Listas de tareas pendientes:\n{tareas_pendientes_txt}")
        print(f"\nDM -> Listas de tareas completadas:\n{tareas_completadas_txt}")																						   
        # Responder al usuario
        TTS.speak(json.dumps(respuesta_final, ensure_ascii=False))

    def manejar_intent_control(self, intent: str):
        """Maneja intents de control como pausar, continuar o apagar la conversación."""
        intent_map = {
            "despedir": self.terminar_conversacion,
            "terminar_conversacion": self.terminar_conversacion,
            "reiniciar_conversacion": self.reiniciar_conversacion,
            "pausar_conversacion": lambda: self.cambiar_estado_pausa(True),
            "continuar_conversacion": lambda: self.cambiar_estado_pausa(False),
            "mostrar_comandos": lambda: TTS.speak("Puedes decir detener conversación, reiniciar conversación, pausar conversación o continuar conversación"),
        }

        if self.pausa_activada and intent != "continuar_conversacion":
            return

        action = intent_map.get(intent)
        if action:
            action()
            
    def terminar_conversacion(self):
        """Termina una conversación"""
        print("\nDM -> Conversación terminada")									   
        self.conversacion_activa = False
        TTS.speak("Hasta luego!")

    def reiniciar_conversacion(self):
        """Reinicia la conversación manteniendo las tareas registradas."""
        self.llm.borrar_memoria()
        TTS.speak("He reiniciado la conversación, pero las tareas siguen disponibles.")

    def cambiar_estado_pausa(self, pausar: bool):
        """Activa o desactiva la pausa de la conversación."""
        if pausar:
            self.pausa_activada = True
            print("\nDM -> Conversación en pausa")									   
            TTS.speak("Conversación pausada. Avísame cuando quieras continuar.")
        else:
            if self.pausa_activada:
                self.pausa_activada = False
                print("\nDM -> Conversación reactivada")										 
                TTS.speak("Conversación reanudada. ¿Cómo puedo ayudarte?")
            else:
                TTS.speak("La conversación ya está activa.")

    def shutdown(self):
        """Apaga correctamente el gestor de diálogo y finaliza la ejecución de PATO."""
        self.nlu.stop_rasa_nlu()
        TTS.speak("Hasta luego.")
        TTS.quack(2)
        self.asistente.should_run = False
        print("\n PATO se ha apagado correctamente.")

    def monitor_inactividad(self):
        """Monitorea la inactividad y apaga la conversación si se excede el tiempo de espera."""
        while True:
            tiempo_espera = self.PAUSE_TIMEOUT if self.pausa_activada else self.INACTIVITY_TIMEOUT
            if self.conversacion_activa and (time.time() - self.ultima_actividad > tiempo_espera):
                print("\nTiempo de inactividad excedido. Finalizando la conversación automáticamente.")
                self.conversacion_activa = False
                TTS.speak("No has dicho nada en un rato, así que me oculto.")
            time.sleep(0.5)
