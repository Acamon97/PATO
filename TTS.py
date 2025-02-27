'''
Módulo TTS (Text-to-Speech)
Implementación de síntesis de voz usando el pipeline de Kokoro y eSpeak.
'''

import os
from kokoro import KPipeline
import soundfile as sf
from playsound import playsound
import sounddevice as sd
from phonemizer.backend.espeak.wrapper import EspeakWrapper


# Configuración de la librería eSpeak (usa cadenas raw para rutas)
_ESPEAK_LIBRARY = r'C:\Program Files\eSpeak NG\libespeak-ng.dll'
EspeakWrapper.set_library(_ESPEAK_LIBRARY)



# Inicialización del pipeline de Kokoro para TTS
pipeline = KPipeline(lang_code='e')

def speak(text):
    '''
    Sintetiza y reproduce el texto dado utilizando el pipeline de Kokoro.
    Guarda cada fragmento de audio generado en la carpeta Resources con un nombre único.
    '''
    
    print(f"\nTTS -> {text}\n")
    print("-" * 50)
    
    # Divide el texto en oraciones separadas por '. ' o usa '\n' para fragmentos largos
    text_chunks = text.split('. ')
    
    for chunk in text_chunks:
        generator = pipeline(
            chunk,  # Pasamos el fragmento en lugar del texto completo
            voice='ef_dora',
            speed=1,
            split_pattern=r'\n+'  # Se asegura de dividir adecuadamente
        )
    
    for i, (gs, ps, audio) in enumerate(generator):
        # Reproduce el audio y espera a que termine la reproducción
        sd.play(audio, 25000)
        sd.wait()
        
        # Guarda cada fragmento en un archivo separado para evitar sobrescrituras
        filename = os.path.join("Resources", "response.wav")
        sf.write(filename, audio, 25000)
        #print(f"Fragmento de respuesta guardado en: {filename}")

def quack(times):
    '''Reproduce el sonido de 'quack' el número de veces especificado.'''
    quack_path = os.path.abspath(os.path.join("Resources", "QUACK.wav"))  # Obtener ruta absoluta
    for _ in range(times):
        playsound(quack_path)  # No usar comillas dobles