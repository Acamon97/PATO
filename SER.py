"""
SER.py - Módulo de reconocimiento de emociones en audio

Este módulo utiliza el modelo `iic/emotion2vec_plus_base` de funasr para analizar 
las emociones presentes en archivos de audio.

Funcionalidad:
- Carga el modelo de SER (Speech Emotion Recognition).
- Procesa un archivo de audio y detecta la emoción predominante.
- Maneja errores si el archivo no existe o si el modelo falla.

Dependencias:
- `funasr`: Para cargar el modelo de reconocimiento de emociones.
- `os`: Para verificar la existencia del archivo de audio.

Clases:
- `SER`: Maneja la detección de emociones en archivos de audio.

Métodos principales:
- `detect_emotion(wav_file)`: Analiza un archivo de audio y devuelve la emoción detectada.
"""

import warnings
warnings.filterwarnings("ignore")  # Ignorar advertencias innecesarias

import os
from funasr import AutoModel


class SER:
    """
    Clase para realizar reconocimiento de emociones a partir de un archivo de audio.
    
    Utiliza el modelo `iic/emotion2vec_plus_base` de funasr.
    """

    def __init__(self, model_id="iic/emotion2vec_plus_base", output_dir="./Resources", emotions=None):
        """
        Inicializa el modelo de reconocimiento de emociones.

        Parámetros:
        - model_id (str): Identificador del modelo a utilizar.
        - output_dir (str): Directorio donde se guardarán los resultados.
        - emotions (dict): Diccionario de mapeo entre índices y emociones.

        Si `emotions` no se proporciona, se usa un conjunto de emociones por defecto.
        """
        self.output_dir = output_dir

        # Emociones por defecto
        self.emotions = emotions or {
            0: 'angry', 1: 'disgusted', 2: 'fearful', 3: 'happy',
            4: 'neutral', 5: 'other', 6: 'sad', 7: 'surprised', 8: 'unknown'
        }

        try:
            self.model = AutoModel(model=model_id, disable_update=True, log_level="CRITICAL")
            print("Modelo de SER cargado correctamente.")
        except Exception as e:
            print(f"ERROR: No se pudo cargar el modelo SER: {e}")
            self.model = None

    def detect_emotion(self, wav_file):
        """
        Detecta la emoción presente en el archivo de audio proporcionado.

        Parámetros:
        - wav_file (str): Ruta del archivo de audio a analizar.

        Retorna:
        - (str): Emoción detectada o "unknown" si no se pudo determinar.
        """
        if not os.path.exists(wav_file):
            print(f"ERROR: El archivo {wav_file} no existe.")
            return "unknown"

        if self.model is None:
            print("ERROR: El modelo SER no está disponible.")
            return "unknown"

        try:
            # Procesar el archivo de audio y obtener las emociones detectadas
            result = self.model.generate(
                wav_file, output_dir=self.output_dir,
                granularity="utterance", extract_embedding=False, disable_pbar=True
            )

            # Verificar si se obtuvo un resultado válido
            if not result or not result[0].get('scores'):
                print("ERROR: No se obtuvieron resultados del modelo.")
                return "unknown"

            # Seleccionar la emoción con mayor puntuación
            scores = result[0]['scores']
            emotion_detected_index = scores.index(max(scores))
            emotion_detected = self.emotions.get(emotion_detected_index, "unknown")

            print(f"\nSER -> Emoción detectada: {emotion_detected}")
            return emotion_detected

        except Exception as e:
            print(f"ERROR: Error al detectar la emoción: {e}")
            return "unknown"
