import warnings
warnings.filterwarnings("ignore")


import os  # noqa: E402
from funasr import AutoModel  # noqa: E402

class SER:
    """
    Clase para realizar reconocimiento de emociones a partir de un archivo de audio.
    Utiliza el modelo 'iic/emotion2vec_plus_base' de funasr.
    """
    def __init__(self, model_id="iic/emotion2vec_plus_base", output_dir="./Resources", emotions=None):
        self.output_dir = output_dir
        # Define las emociones por defecto
        self.emotions = emotions or {
            0: 'angry',
            1: 'disgusted',
            2: 'fearful',
            3: 'happy',
            4: 'neutral',
            5: 'other',
            6: 'sad',
            7: 'surprised',
            8: 'unknown'
        }

        try:
            self.model = AutoModel(model=model_id, disable_update=True, log_level="CRITICAL")
            print("Modelo de SER cargado correctamente.")
        except Exception as e:
            print(f"ERROR: Error al cargar el modelo SER: {e}")
            self.model = None

    def detect_emotion(self, wav_file):
        """
        Detecta la emoción presente en el archivo de audio `wav_file`.
        Devuelve la emoción detectada (string) o None si ocurre algún error.
        """
        if not os.path.exists(wav_file):
            print(f"ERROR: El archivo {wav_file} no existe.")
            return None
        
        if self.model is None:
            print("ERROR: El modelo SER no está disponible.")
            return None

        try:
            # Se guarda la salida en el directorio especificado
            result = self.model.generate(wav_file, output_dir=self.output_dir,
                                         granularity="utterance", extract_embedding=False, disable_pbar=True)
            if not result or not result[0].get('scores'):
                print("ERROR: No se obtuvieron resultados del modelo.")
                return None

            scores = result[0]['scores']
            # Se selecciona el índice con mayor puntuación
            emotion_detected_value = max(scores)
            emotion_detected_index = scores.index(emotion_detected_value)
            emotion_detected = self.emotions.get(emotion_detected_index, "unknown")
            
            print(f"Emoción detectada: {emotion_detected}")
            return emotion_detected
        except Exception as e:
            print(f"ERROR: Error al detectar la emoción: {e}")
            return None
