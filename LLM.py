"""
LLM.py - Módulo de interacción con el modelo de lenguaje (LLM)

Este módulo gestiona la comunicación con el modelo de lenguaje (LLM) usando LangChain y Ollama.
Se encarga de:
- Generar respuestas estructuradas en JSON.
- Validar la salida del modelo antes de procesarla.
- Mantener un historial de conversación usando memoria optimizada.
- Extraer y estructurar acciones de tareas desde la conversación.

Dependencias:
- `langchain_ollama`: Para invocar el modelo de lenguaje.
- `langchain.memory`: Para manejar memoria conversacional.
- `pydantic`: Para validar la estructura de las respuestas generadas.

Clases:
- `ToolCall`: Representa una acción de tareas generada por el LLM.
- `LLMResponse`: Modelo estructurado para la respuesta completa del LLM.
- `LLM`: Maneja la comunicación con el modelo y la validación de respuestas.

Métodos principales:
- `generar_respuesta()`: Genera y valida una respuesta estructurada del LLM.
- `validar_respuesta()`: Verifica que la salida sea un JSON válido y estructurado.
- `get_formated_prompt()`: Construye el prompt con instrucciones detalladas.
- `borrar_memoria()`: Limpia la memoria conversacional.
"""

from datetime import datetime, timedelta
import json
from langchain_ollama import ChatOllama
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from pydantic import BaseModel, Field, ValidationError


class ToolCall(BaseModel):
    """Estructura de las acciones que el LLM puede generar en su respuesta."""
    action: str = Field(..., description="Acción a realizar: añadir, eliminar, completar, modificar, deshacer, consultar")
    task: str | None = Field(None, description="Nombre de la tarea (Opcional en 'deshacer')")
    new_task: str | None = Field(None, description="Nuevo nombre de la tarea (solo si se modifica)")
    due_date: str | None = Field(None, description="Fecha de vencimiento en formato YYYY-MM-DD (Opcional)")
    priority: str = Field("normal", description="Prioridad: baja, normal, alta, urgente")


class LLMResponse(BaseModel):
    """Estructura completa esperada en la respuesta del LLM."""
    response: str = Field(..., description="Texto explicativo para el usuario")
    tool_calls: list[ToolCall] = Field([], description="Lista de acciones de tareas")


class LLM:
    """
    Clase que gestiona la comunicación con el modelo de lenguaje (LLM).

    Se encarga de:
    - Enviar prompts con historial conversacional.
    - Generar respuestas estructuradas en JSON.
    - Validar la estructura de la respuesta generada.
    """

    def __init__(self, model_name="llama3.2:3b-instruct-q3_K_M", max_reintentos=3):
        """Inicializa el modelo de lenguaje con memoria optimizada y configuración de respuesta."""
        
        self.model_name = model_name
        self.llm = ChatOllama(
            model=model_name,
            temperature=0.2,
            num_ctx=4096,
            repeat_penalty=1.2,
            format='json',
            max_tokens=256,
        )

        self.memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            memory_key="history",
            max_token_limit=1024
        )

        self.max_reintentos = max_reintentos  # Número máximo de intentos si el JSON falla

    def generar_respuesta(self, mensaje_usuario, contexto="", emotion_detected="neutral"):
        """Genera una respuesta estructurada en JSON, con validación y reintentos en caso de error."""
        prompt = self.get_formated_prompt(mensaje_usuario, emotion_detected, contexto)
        return self.generar_respuesta_con_reintentos(prompt)

    def generar_respuesta_con_reintentos(self, prompt):
        """Genera una respuesta válida en JSON, reintentando en caso de error."""
        for intento in range(self.max_reintentos):
            respuesta_raw = self.llm.invoke(prompt).content.strip()

            if "tool_calls" not in respuesta_raw:
                print("Advertencia: La respuesta no contiene 'tool_calls'. Reintentando...")
                continue  # Reintentar

            respuesta_validada = self.validar_respuesta(respuesta_raw)

            if respuesta_validada:
                respuesta_texto = respuesta_validada.get("response")
                respuesta_acciones = respuesta_validada.get("tool_calls", [])
                print(f"\nLLM -> Respuesta: {respuesta_texto}")
                if respuesta_acciones:
                    print(f"\nLLM -> Acciones:\n{json.dumps(respuesta_acciones, indent=4, ensure_ascii=False)}")

                return json.dumps(respuesta_validada, ensure_ascii=False)

            print(f"Intento {intento + 1}/{self.max_reintentos} fallido. Reintentando...")

        print("Se agotaron los intentos. No se pudo obtener un JSON válido.")
        return json.dumps({
            "response": "Lo siento, ocurrió un error al procesar la respuesta.",
            "tool_calls": []
        }, ensure_ascii=False)

    def validar_respuesta(self, respuesta_raw):
        """Verifica que la respuesta del LLM sea un JSON válido y cumpla con la estructura esperada."""
        try:
            respuesta_json = json.loads(respuesta_raw)
            respuesta_validada = LLMResponse(**respuesta_json)
            return respuesta_validada.dict()
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"ERROR: Validación del JSON fallida: {e}")
            return None

    def get_formated_prompt(self, mensaje_usuario, emotion_detected, contexto):
        """Construye el prompt formateado con contexto y memoria conversacional."""
        
        history_summary = self.memory.load_memory_variables({}).get("history", "")

        hoy = datetime.today()
        fecha_actual = hoy.strftime('%Y-%m-%d')
        fecha_mañana = (hoy + timedelta(1)).strftime('%Y-%m-%d')

        system_template = """ 
        Eres PATO, un asistente virtual especializado en gestionar tareas y conversar de forma amistosa.

        Tienes acceso al siguiente historial de conversación:
        {history_summary}

        Fecha actual:
        {fecha_actual}

        INSTRUCCIONES:
        1. Devuelve SIEMPRE un JSON con la siguiente estructura:
        {{
            "response": "Texto amigable para el usuario.",
            "tool_calls": [...]
        }}

        2. No incluyas nada fuera del JSON, ni explicaciones adicionales.

        3. Si el usuario menciona acciones de tareas (añadir, eliminar, completar, modificar, deshacer, consultar), usa "tool_calls":
            - "action": Acción a realizar.
            - "task": Nombre de la tarea (si aplica).
            - "due_date": Convertir fechas relativas como "mañana" a YYYY-MM-DD.
            - "priority": Solo incluir si el usuario la menciona.

        4. Si el usuario solo quiere conversar, "tool_calls" debe ser una lista vacía.

        5. Ten en cuenta la emoción detectada: {emotion_detected} y ajusta tu respuesta en "response" de forma empática o apropiada al contexto.

        6. Convierte fechas relativas como "mañana", "próximo viernes", etc. a YYYY-MM-DD. Ejemplo:
            - Usuario: "¿Qué tareas tengo para mañana?"
            - Salida: "due_date": "{fecha_mañana}".			
            
        7. No uses saltos de linea ni '\n' en "response", escríbelo en la misma frase.

        Ejemplo 1 de salida:
        {{
            "response": "He añadido 'comprar leche' a tu lista.",
            "tool_calls": [
                {{
                    "action": "añadir",
                    "task": "Comprar leche",
                    "due_date": "{fecha_mañana}",
                    "priority": "normal"
                }}
            ]
        }}
        
        Ejemplo 2 de salida:
        {{
            "response": "Estas son tus tareas pendientes: 'comprar leche' y 'comprar cereales'.",
            "tool_calls": [
                {{
                    "action": "consultar",
                    "task": "Comprar leche",
                    "due_date": "{fecha_mañana}",
                    "priority": "normal"
                }},
                 {{
                    "action": "consultar",
                    "task": "Comprar cereales",
                    "due_date": "{fecha_mañana}",
                    "priority": "normal"
                }}
                
            ]
        }}
        """

        human_template = """
        Emoción detectada: {emotion_detected}
        Contexto: {contexto}

        Usuario: {mensaje_usuario}
        """

        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])

        return prompt.format_prompt(
            mensaje_usuario=mensaje_usuario,
            contexto=contexto,
            emotion_detected=emotion_detected,
            history_summary=history_summary,
            fecha_actual=fecha_actual,
            fecha_mañana=fecha_mañana,
        ).to_string()

    def borrar_memoria(self):
        """Borra la memoria conversacional almacenada."""
        self.memory.clear()
