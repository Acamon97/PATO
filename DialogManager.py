import json
import re
import time
import threading
import TTS
from SER import SER  # noqa: E402
from NLU import NLU
from TaskHandler import TaskHandler
from LLM import LLM

class DialogManager:
    INACTIVITY_TIMEOUT = 30  # Tiempo límite en segundos para conversación activa
    PAUSE_TIMEOUT = 60  # Tiempo límite en segundos cuando la conversación está pausada

    def __init__(self, asistente):
        """Inicializa el gestor de diálogo con instancias propias de LLM y TaskHandler"""
        self.asistente = asistente
        self.nlu = NLU()
        self.ser = SER()
        self.llm = LLM()
        self.task_handler = TaskHandler()
        self.conversacion_activa = False
        self.pausa_activada = False  # Estado de pausa de la conversación
        self.ultima_actividad = time.time()  # Marca de tiempo de la última actividad

        # Patrones de activación y apagado
        self.wake_words = re.compile(r'\boye,?\s+pato\b', re.IGNORECASE)
        self.shutdown_words = re.compile(r'\bapagar,?\s+pato\b', re.IGNORECASE)

        # Iniciar el monitor de inactividad en un hilo separado
        self.inactividad_thread = threading.Thread(target=self.monitor_inactividad, daemon=True)
        self.inactividad_thread.start()

    def extraer_comando(self, command: str) -> str:
        """Extrae el comando tras la palabra de activación."""
        match = re.search(r'\boye\,?\s+pato\b[,:]?\s(.*)', command, re.IGNORECASE)
        return match.group(1).strip() if match and match.group(1) else None

    def procesar_comando(self, command: str, command_wav_file: str):
        """Gestiona un comando detectado y controla la conversación."""
        self.ultima_actividad = time.time()  # Actualizar el tiempo de actividad
        emotion_detected = self.ser.detect_emotion(command_wav_file)
        if (self.conversacion_activa) :
            print("\nDM -> Conversación activa")
            if (self.pausa_activada) :
                print("\nDM -> En pausa")

        if not command:
            return

        if not self.conversacion_activa:
            if self.shutdown_words.search(command):
                self.shutdown()
                return

            if self.wake_words.search(command):
                self.conversacion_activa = True
                TTS.quack(1)
                comando_extraido = self.extraer_comando(command)
                if comando_extraido:
                    self.procesar_intent(comando_extraido, emotion_detected)
                else:
                    self.procesar_intent("hola", emotion_detected)
                return

        if self.conversacion_activa:
            self.procesar_intent(command, emotion_detected)

    def procesar_intent(self, user_message: str, emotion_detected: str):
        """Maneja el mensaje del usuario y consulta el LLM para generar la respuesta."""
        self.ultima_actividad = time.time()  # Actualizar el tiempo de actividad
        intent = self.nlu.detectar_intent(user_message)

        # Verificar si el intent es de control
        if intent in {
            "despedir", "terminar_conversacion", "reiniciar_conversacion",
            "pausar_conversacion", "continuar_conversacion", "mostrar_comandos"
        }:
            print(f"\nNLU -> Intent detectado: {intent}")
            self.manejar_intent_control(intent)
            return

        # Si la conversación está pausada, ignorar cualquier input
        if self.pausa_activada:
            return
        
        self.generar_respuesta(user_message, emotion_detected)
      

    def generar_respuesta(self, user_message, emotion_detected):
        
        tareas_pendientes_txt = self.task_handler.task_manager.consultar_tareas(False)
        tareas_completadas_txt = self.task_handler.task_manager.consultar_tareas_completadas(False)
        print(f"\nDM -> Mensaje usuario: {user_message}")
        print(f"\nDM -> Listas de tareas pendientes:\n{tareas_pendientes_txt}")
        print(f"\nDM -> Listas de tareas completadas:\n{tareas_completadas_txt}")

        tareas_pendientes_json = self.task_handler.task_manager.consultar_tareas()
        tareas_completadas_json = self.task_handler.task_manager.consultar_tareas_completadas()
        
        contexto = {**tareas_pendientes_json, **tareas_completadas_json}
        # Consultar el LLM
        respuesta_json = self.llm.generar_respuesta(user_message, contexto=json.dumps(contexto), emotion_detected=emotion_detected)

        respuesta_json = json.loads(respuesta_json)
        # Procesar las acciones devueltas por el LLM
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

    def manejar_intent_control(self, intent):
        """Maneja los intents de control directamente en `DialogManager`."""
                
        intent_map = {
            "despedir": lambda: self.shutdown(),
            "terminar_conversacion": lambda: self.shutdown(),
            "reiniciar_conversacion": lambda: self._reiniciar_conversacion(),
            "pausar_conversacion": lambda: self._cambiar_estado_pausa(True),
            "continuar_conversacion": lambda: self._cambiar_estado_pausa(False),
            "mostrar_comandos": lambda: TTS.speak("Puedes decir detener conversación, reiniciar conversación, pausar conversación o continuar conversación"),
        }

        action = intent_map.get(intent)
        if action:
            if self.pausa_activada and intent != "continuar_conversacion":
                return
            action()

    def _reiniciar_conversacion(self):
        """Reinicia la conversación manteniendo las tareas disponibles."""
        self.llm.borrar_memoria()
        TTS.speak("He reiniciado la conversación, pero las tareas siguen disponibles.")


    def _cambiar_estado_pausa(self, pausar):
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
        """Apaga correctamente el gestor de diálogo, incluyendo el servidor Rasa."""
        #print("Cerrando DialogManager y Rasa NLU...")
        self.nlu.stop_rasa_nlu()
        TTS.speak("Hasta luego.")
        TTS.quack(2)
        self.asistente.should_run = False
        print("\n PATO se ha apagado correctamente.")

    def monitor_inactividad(self):
        """Hilo que monitoriza la inactividad y desactiva la conversación si no hay actividad."""
        while True:
            tiempo_espera = self.PAUSE_TIMEOUT if self.pausa_activada else self.INACTIVITY_TIMEOUT
            if self.conversacion_activa and (time.time() - self.ultima_actividad > tiempo_espera):
                print("\nTiempo de inactividad excedido. Finalizando la conversación automáticamente.")
                self.conversacion_activa = False
                TTS.speak("No has dicho nada en un rato, así que me oculto.")
            time.sleep(0.5)  # Revisar cada 5 segundos
