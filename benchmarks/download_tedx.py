import os
import tarfile
import pandas as pd
import shutil
import random
import chardet  # 🔹 Librería para detectar codificación

# 📌 Nombre correcto del archivo descargado
DATASET_FILE = "tedx_spanish_corpus.tgz"
DATASET_FOLDER = "tedx_spanish_corpus/tedx_spanish_corpus"
AUDIO_FOLDER = "test_audios"
MAX_AUDIOS = 100  # Se ajusta el límite a 100 audios

def detect_encoding(file_path):
    """Detecta la codificación de un archivo y la devuelve."""
    with open(file_path, "rb") as f:
        result = chardet.detect(f.read())
    return result["encoding"]

def extract_dataset():
    """Extrae los archivos del dataset de TEDx Spanish sin extraer todo."""
    if not os.path.exists(DATASET_FOLDER):
        print("📦 Extrayendo dataset...")
        with tarfile.open(DATASET_FILE, "r:gz") as tar:
            tar.extractall("tedx_spanish_corpus")  # 🔹 Extraer en la carpeta correcta

        print("✅ Extracción completada.")
    else:
        print("✅ Dataset ya está extraído.")

def select_audios():
    """Selecciona los audios y copia a test_audios/."""
    os.makedirs(AUDIO_FOLDER, exist_ok=True)

    # 🔹 Corregimos la ruta de los archivos de transcripción
    transcription_path = os.path.join(DATASET_FOLDER, "files", "TEDx_Spanish.transcription")
    paths_path = os.path.join(DATASET_FOLDER, "files", "TEDx_Spanish.paths")

    if not os.path.exists(transcription_path) or not os.path.exists(paths_path):
        raise FileNotFoundError(f"⚠ No se encontraron `TEDx_Spanish.transcription` o `TEDx_Spanish.paths` en {DATASET_FOLDER}/files/.")

    print(f"✅ Archivos de transcripción encontrados en: {transcription_path} y {paths_path}")

    # 🔹 Detectar y corregir la codificación de los archivos
    transcription_encoding = detect_encoding(transcription_path)
    paths_encoding = detect_encoding(paths_path)

    print(f"📌 Codificación detectada en transcripciones: {transcription_encoding}")
    print(f"📌 Codificación detectada en paths: {paths_encoding}")

    # Cargar transcripciones y paths con la codificación correcta
    df_transcripts = pd.read_csv(transcription_path, sep="\t", encoding=transcription_encoding, names=["sentence"])
    df_paths = pd.read_csv(paths_path, sep="\t", encoding=paths_encoding, names=["path"])

    # 🔹 Corregir rutas eliminando "./speech/"
    df_paths["path"] = df_paths["path"].str.replace("./speech/", "", regex=False)

    # 🔹 Eliminar el ID del audio al final de cada transcripción
    df_transcripts["sentence"] = df_transcripts["sentence"].apply(lambda x: " ".join(x.split()[:-1]))

    # 🔹 Convertir todo a UTF-8 correctamente
    df_transcripts["sentence"] = df_transcripts["sentence"].apply(lambda x: x.encode("utf-8").decode("utf-8"))

    # 🔹 Fusionar paths y transcripciones en un solo dataframe
    df = pd.concat([df_paths, df_transcripts], axis=1)

    # 🚀 Seleccionar 100 audios aleatorios
    df = df.sample(frac=1, random_state=42).head(MAX_AUDIOS)
    print(f"🔹 Número final de audios a copiar: {len(df)}")  

    # Ruta de los clips
    clips_folder = os.path.join(DATASET_FOLDER, "speech")

    # Copiar audios a test_audios/
    for _, row in df.iterrows():
        src = os.path.join(clips_folder, row["path"])
        dst = os.path.join(AUDIO_FOLDER, os.path.basename(row["path"]))  # 🔹 Solo el nombre del archivo

        print(f"🔍 Verificando archivo: {src}")

        if os.path.exists(src):
            shutil.copy(src, dst)
            print(f"✅ Copiado: {src} → {dst}")
        else:
            print(f"⚠ ERROR: Archivo de audio no encontrado: {src}")

    # Guardar transcripciones esperadas con codificación UTF-8
    df.to_csv(os.path.join(AUDIO_FOLDER, "transcriptions.csv"), index=False, encoding="utf-8")

    print(f"✅ {len(df)} audios copiados a '{AUDIO_FOLDER}/'. Transcripciones guardadas.")

if __name__ == "__main__":
    extract_dataset()
    select_audios()
    print("\n🎙 Dataset reducido listo para pruebas en `test_asr.py`.")
