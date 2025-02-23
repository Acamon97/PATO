import requests

def detect_intent_rasa(message: str) -> dict:
    """
    Envía un mensaje a la API de Rasa y devuelve la respuesta de NLU.
    """
    url = "http://localhost:5005/model/parse"
    payload = {"text": message}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return {"intent": {"name": "nlu_fallback", "confidence": 0.0}}
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con Rasa: {e}")
        return {"intent": {"name": "nlu_fallback", "confidence": 0.0}}


