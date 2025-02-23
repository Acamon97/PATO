'''
Asistente Virtual PATO (Personal Assistant for Task Optimization)

'''

import re
import time
import logging
import ASR
import TTS

class AsistenteVirtual:
    def __init__(self):
        self.should_run = True
        self.wake_words = re.compile(r'\¡?oye\,? pato\!?')
        self.shutdown_words = re.compile(r'\¡?adi(ó|o)s\,? pato\!?')
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
    
    def procesar_comando(self, command):
        if command is None:
            return
        command = command.lower()
        if self.wake_words.search(command):
            TTS.quack(1)
            TTS.hola("Hola, ¿En qué puedo ayudarte?")
            # Aquí se puede integrar la detección de intenciones, por ejemplo:
            # intent = NLP.detect_intent(command)
            # TASK.ejecutar_tarea(intent)
        elif self.shutdown_words.search(command):
            TTS.quack(2)
            self.should_run = False
    
    def run(self):
        TTS.quack(2)
        while self.should_run:
            command = ASR.listen_for_command()
            logging.info(f"Comando recibido: {command}")
            self.procesar_comando(command)
            time.sleep(1)

if __name__ == "__main__":
    asistente = AsistenteVirtual()
    asistente.run()