"""
pato.py - Módulo principal del asistente virtual P.A.T.O.

Este script inicializa y ejecuta el asistente virtual P.A.T.O., gestionando la 
interacción por voz a través de los módulos ASR (Reconocimiento Automático de Voz) 
y TTS (Síntesis de Voz). 

Clases:
- AsistenteVirtual: Maneja el ciclo de vida del asistente, incluyendo su inicialización,
  procesamiento de comandos y apagado.

Dependencias:
- ASR: Módulo de reconocimiento de voz.
- TTS: Módulo de síntesis de voz.
- DialogManager: Gestiona los diálogos y la lógica de respuesta del asistente.

El asistente se ejecuta en un bucle continuo hasta que se recibe una señal de apagado.
"""

import ASR
import TTS
import time  
from DialogManager import DialogManager 

class AsistenteVirtual:
    """
    Clase que representa al asistente virtual P.A.T.O.

    Métodos:
    - __init__: Inicializa el asistente y el gestor de diálogo.
    - run: Ejecuta el asistente en un bucle continuo, procesando comandos de voz.
    - shutdown: Apaga el asistente liberando recursos correctamente.
    """

    def __init__(self):
        """Inicializa el asistente virtual y su gestor de diálogo."""
        print("Inicializando PATO...")
        self.should_run = True
        self.dialog_manager = None  
        
        try:
            self.dialog_manager = DialogManager(self) 
        except Exception as e:
            print(f"Error al inicializar DialogManager: {e}")
            self.should_run = False  # Evita la ejecución si falla la inicialización.

    def run(self):
        """Ejecuta el asistente en un bucle continuo, procesando comandos de voz."""
        print("ASISTENTE P.A.T.O. ACTIVO\n")
        TTS.quack(2)  # Señal sonora para indicar que está listo.

        while self.should_run:
            command, command_wav_file = ASR.listen_for_command()
            
            if command and self.dialog_manager:
                self.dialog_manager.procesar_comando(command, command_wav_file)
            
            time.sleep(0.1)  # Pequeña pausa para evitar uso excesivo de CPU.

    def shutdown(self):
        """Apaga el asistente liberando los recursos utilizados."""
        try:
            if self.dialog_manager:
                self.dialog_manager.shutdown()
        except Exception as e:
            print(f"Error al cerrar DialogManager: {e}")
        self.should_run = False

if __name__ == "__main__":
    asistente = None  

    try:
        asistente = AsistenteVirtual()
        if asistente.should_run:  # Solo ejecuta si la inicialización fue exitosa.
            asistente.run()
    except KeyboardInterrupt:  # Captura Ctrl+C para apagado manual.
        if asistente:
            asistente.shutdown()
        print("PATO ha sido apagado manualmente.")
