import sys
import os

# Agregar el directorio padre al path para importar SER.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from SER import SER

test_audios = {
    "angry_audio.wav": "angry",
    "happy_audio.wav": "happy",
    "neutral_audio.wav": "neutral",
}

ser = SER()

def test_ser():
    for audio, emocion_esperada in test_audios.items():
        print(f"\n🔍 Probando SER con: {audio}")
        emocion_detectada = ser.detect_emotion(audio)
        print(f"✅ Emoción detectada: {emocion_detectada} | Esperada: {emocion_esperada}")
        assert emocion_detectada == emocion_esperada, f"❌ Error en {audio}"

if __name__ == "__main__":
    test_ser()
