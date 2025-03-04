"""
NLU.py - Módulo de procesamiento del lenguaje natural (NLU) con Rasa

Este módulo gestiona la comunicación con Rasa NLU, encargándose de:
- Detectar intents en mensajes de texto.
- Iniciar y detener el servidor Rasa si no está en ejecución.
- Seleccionar el modelo NLU más reciente disponible en el sistema.

Dependencias:
- `requests`: Para comunicarse con el servidor Rasa NLU.
- `subprocess`: Para iniciar el proceso de Rasa si no está en ejecución.
- `psutil`: Para verificar si el proceso de Rasa sigue activo.
- `glob`: Para buscar modelos NLU en la carpeta especificada.

Clases:
- NLU: Proporciona métodos para interactuar con Rasa NLU, incluyendo detección de intents 
  y gestión del servidor.

Métodos principales:
- `detectar_intent(mensaje)`: Envía un mensaje a Rasa y obtiene el intent detectado.
- `start_rasa_nlu()`: Inicia el servidor Rasa si no está en ejecución.
- `stop_rasa_nlu()`: Detiene el servidor Rasa si está en ejecución.
"""

import json
import subprocess
import requests
import time
import os
import glob
from psutil import pid_exists


class NLU:
    """
    Clase para la gestión de Rasa NLU en el asistente virtual.

    Se encarga de iniciar el servidor Rasa si no está en ejecución, detectar intents 
    en mensajes y detener el servidor cuando sea necesario.
    """

    port = '5005'  # Puerto en el que Rasa NLU está configurado para ejecutarse

    def __init__(self, server_url=f"http://localhost:{port}/model/parse", models_path="models/"):
        """Inicializa el servicio de Rasa NLU verificando si está en ejecución o iniciándolo."""
        self.server_url = server_url
        self.model_path = self.get_latest_nlu_model(models_path)
        self.rasa_process = None  # Proceso del servidor Rasa NLU

        if not self.model_path:
            raise FileNotFoundError(f"No se encontró ningún modelo NLU en la carpeta {models_path}")

        if self.is_rasa_running():
            print("Servidor Rasa NLU ya está en ejecución.")
        else:
            print(f"Iniciando servidor Rasa NLU en {self.server_url}...")
            self.start_rasa_nlu()

    def get_latest_nlu_model(self, models_path):
        """Busca el modelo NLU más reciente en la carpeta de modelos."""
        model_files = glob.glob(os.path.join(models_path, "nlu-*.tar.gz"))
        if not model_files:
            return None
        latest_model = max(model_files, key=os.path.getctime)  # Seleccionar el modelo más reciente
        print(f"Modelo NLU seleccionado: {latest_model}")
        return latest_model

    def is_rasa_running(self):
        """Verifica si el servidor de Rasa NLU está en ejecución."""
        try:
            print("Probando conexión con el servidor Rasa...")
            response = requests.get(f"http://localhost:{self.port}/status", timeout=5)
            return response.status_code == 200
        except requests.ConnectionError:
            return False

    def start_rasa_nlu(self):
        """Inicia el servidor Rasa con el modelo NLU más reciente."""
        conda_exe = r"C:\Users\acamo\anaconda3\Scripts\conda.exe"  # Ajusta según tu ruta

        self.rasa_process = subprocess.Popen(
            [conda_exe, "run", "-n", "rasa_env", "rasa", "run", "--enable-api", "-m", self.model_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            shell=False  # shell=False se recomienda para evitar problemas de seguridad
        )

        self.wait_for_rasa()

    def wait_for_rasa(self, timeout=20):
        """Espera hasta que el servidor Rasa NLU esté listo o agota el tiempo de espera."""
        print("Esperando a que el servidor Rasa NLU se inicie...")
        print("Esperando al servidor")
        time.sleep(10)  # Esperar unos segundos para que arranque														 
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.is_rasa_running():
                print("Servidor Rasa NLU está listo.")
                return
            time.sleep(5)  # Verificar cada 5 segundos

        raise TimeoutError("Tiempo de espera agotado. Rasa NLU no inició correctamente.")

    def stop_rasa_nlu(self):
        """Detiene el servidor Rasa si está en ejecución."""
        if self.rasa_process and pid_exists(self.rasa_process.pid):
            print("Deteniendo el servidor Rasa NLU...")
            self.rasa_process.terminate()
            self.rasa_process.wait()
            print("Servidor Rasa NLU detenido.")

    def detectar_intent(self, mensaje):
        """
        Envía un mensaje a Rasa NLU y obtiene el intent detectado.

        Parámetros:
        - mensaje (str): Texto que se enviará a Rasa NLU para análisis.

        Retorna:
        - intent (str): Nombre del intent detectado.
        """
        payload = {"text": mensaje}

        try:
            with requests.Session() as session:
                response = session.post(self.server_url, json=payload, timeout=10)
            response.raise_for_status()  # Lanza un error si la solicitud falla

            resultado = response.json()
            intent = resultado.get("intent", {}).get("name", "desconocido")
            confidence = resultado.get("intent", {}).get("confidence", 0)
            if confidence < 1:
                return "nlu_fallback"
            return intent

        except requests.RequestException as e:
            print(f"Error en la API de Rasa: {e}")
            return None
