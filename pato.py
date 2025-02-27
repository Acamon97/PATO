import os
import ASR
import TTS
import time  
from DialogManager import DialogManager 

class AsistenteVirtual:
    def __init__(self):
        print("Inicializando PATO...")
        self.should_run = True
        self.dialog_manager = None 
        try:
            self.dialog_manager = DialogManager(self) 
        except Exception as e:
            print(f"Error al inicializar DialogManager: {e}")
            self.should_run = False  

    def run(self):
        #os.system('cls')
        print("ASISTENTE P.A.T.O. ACTIVO\n")
        TTS.quack(2)
        while self.should_run:
            command, command_wav_file = ASR.listen_for_command()
            if command and self.dialog_manager:
                self.dialog_manager.procesar_comando(command, command_wav_file)
            time.sleep(0.1)  

    def shutdown(self):
        '''Cierra correctamente los procesos antes de apagar PATO.'''
        #print("Apagando PATO...")
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
        if asistente.should_run: 
            asistente.run()
    except KeyboardInterrupt:  
        if asistente:
            asistente.shutdown()
        print("PATO ha sido apagado manualmente.")
