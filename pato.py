'''
Asistente Virtual PATO (Personal Assistant for Task Optimization)

'''
import os
import warnings
import re  # noqa: E402
import time  # noqa: E402  # noqa: E402

warnings.filterwarnings("ignore")

# Importamos módulos
import ASR  # noqa: E402
import TTS  # noqa: E402
from SER import SER  # noqa: E402


# Clase principal del asistente
class AsistenteVirtual:
    def __init__(self):
        print("Inicializando Personal Assistant for Task Optimization...")

        self.should_run = True
        self.wake_words = re.compile(r'\¡?oye\,? pato\!?')
        self.shutdown_words = re.compile(r'\¡?adi(ó|o)s\,? pato\!?')
        
         # Instanciar los módulos como clases
        self.ser = SER()
        os.system('cls')
        print("PATO a tu servicio.")

        # Configurar logging
            
    def procesar_comando(self, command, command_wav_file):
        if command is None:
            return
        command = command.lower()
        
        emotion_detected = self.ser.detect_emotion(command_wav_file)

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
            command, command_wav_file = ASR.listen_for_command()
            print(f"Comando recibido: {command}")
            self.procesar_comando(command, command_wav_file)
            time.sleep(1)

if __name__ == "__main__":
    asistente = AsistenteVirtual()
    asistente.run()