import subprocess
import requests
import time
import os
import glob
from psutil import pid_exists

class NLU:
    port = '5005'
    def __init__(self, server_url="http://localhost:" + port + "/model/parse", models_path="models/"):
        '''Inicia Rasa NLU como API si no está en ejecución, usando el último modelo disponible.'''
        self.server_url = server_url
        self.model_path = self.get_latest_nlu_model(models_path)
        self.rasa_process = None

        if not self.model_path:
            raise FileNotFoundError(f"No se encontró ningún modelo NLU en la carpeta {models_path}")

        if self.is_rasa_running():
            print("Servidor Rasa NLU ya está en ejecución.")
        else:
            print(f"Iniciando servidor Rasa NLU: {self.server_url}...")
            self.start_rasa_nlu()
            #self.wait_for_rasa()

    def get_latest_nlu_model(self, models_path):
        '''Busca el modelo NLU más reciente en la carpeta de modelos.'''
        model_files = glob.glob(os.path.join(models_path, "nlu-*.tar.gz"))
        if not model_files:
            return None
        latest_model = max(model_files, key=os.path.getctime)
        print(f"Modelo NLU seleccionado: {latest_model}")
        return latest_model

    def is_rasa_running(self):
        try:
            print("Probando conexión con el servidor rasa...")
            response = requests.get("http://localhost:5005/status")  
            return response.status_code == 200
        except requests.ConnectionError:
            return False

    def start_rasa_nlu(self):
        '''Lanza el servidor de Rasa con el modelo NLU más reciente y guarda el proceso.'''
        conda_exe = r"C:\Users\acamo\anaconda3\Scripts\conda.exe"  # Ajusta según tu ruta
        self.rasa_process = subprocess.Popen(
            [conda_exe, "run", "-n", "rasa_env", "rasa", "run", "--enable-api", "-m", self.model_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            shell=False  # Mantén shell=False si vas a meter la ruta absoluta
        )       

        self.wait_for_rasa()

    def wait_for_rasa(self):
        '''Espera a que el servidor de Rasa esté disponible.'''
        print("Esperando al servidor")
        time.sleep(10)  # Esperar unos segundos para que arranque
        timeout = 20  # Esperar hasta 60 segundos
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.is_rasa_running():
                print("Servidor Rasa NLU está listo.")
                return
            time.sleep(5)
            
        raise TimeoutError("Tiempo de espera agotado. Rasa NLU no inició correctamente.")


    def stop_rasa_nlu(self):
        '''Detiene el servidor de Rasa si está en ejecución.'''
        if self.rasa_process and pid_exists(self.rasa_process.pid):
            #print("Deteniendo el servidor Rasa NLU...")
            self.rasa_process.terminate()
            self.rasa_process.wait()
            #print("Servidor Rasa NLU detenido.")
        # else:
        #     print("No hay un proceso activo de Rasa para detener.")

    def detectar_intent(self, mensaje):
        '''Envía el mensaje a Rasa NLU y obtiene el intent y entidades.'''
        payload = {"text": mensaje}
        try:
            with requests.Session() as session:
                response = session.post(self.server_url, json=payload, timeout=10)
            response.raise_for_status()

            resultado = response.json()
            intent = resultado.get("intent", {}).get("name", "desconocido")

            return intent
        except requests.RequestException as e:
            print(f"Error en la API de Rasa: {e}")
            return None, None
