from datetime import datetime, timedelta
import json
from langchain_ollama import ChatOllama
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from pydantic import BaseModel, Field, ValidationError


class ToolCall(BaseModel):
    """Estructura de las acciones que el LLM puede generar."""
    action: str = Field(..., description="Acción a realizar: añadir_tarea, eliminar_tarea, completar_tarea, modificar_tarea, deshacer_ultima_accion, consultar_tarea")
    task: str | None = Field(None, description="Nombre de la tarea (Opcional en 'deshacer_ultima_accion')")
    new_task: str | None = Field(None, description="Nuevo nombre de la tarea (solo si se modifica)")
    due_date: str | None = Field(None, description="Fecha de vencimiento en formato YYYY-MM-DD (Opcional)")
    priority: str = Field("normal", description="Prioridad: baja, normal, alta, urgente")


class LLMResponse(BaseModel):
    """Estructura completa esperada en la respuesta del LLM."""
    response: str = Field(..., description="Texto explicativo para el usuario")
    tool_calls: list[ToolCall] = Field([], description="Lista de acciones de tareas")


class LLM:
    def __init__(self, model_name="llama3.2:3b-instruct-q3_K_M", max_reintentos=3):
        """Inicializa el modelo de Ollama usando LangChain con memoria optimizada."""
        
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
        """Genera una respuesta estructurada y válida en JSON con reintentos en caso de error."""
        return self.generar_respuesta_con_reintentos(self.get_formated_prompt(mensaje_usuario, emotion_detected, contexto))


    def generar_respuesta_con_reintentos(self, prompt):
        """Genera una respuesta y la valida, reintentando si es necesario."""
        for intento in range(self.max_reintentos):
            #print(f"\n Intento {intento + 1}: Enviando prompt al LLM...")

            respuesta_raw = self.llm.invoke(prompt).content.strip()

            print(f"\nLLM -> Respuesta (Intento {intento+1}):\n{respuesta_raw}")

            if "tool_calls" not in respuesta_raw:
                print("Advertencia: La respuesta no contiene 'tool_calls'. Reintentando...")
                continue  # Reintentar

            respuesta_validada = self.validar_respuesta(respuesta_raw)

            if respuesta_validada:
                return respuesta_validada

            print(f"Intento {intento + 1}/{self.max_reintentos} fallido. Reintentando...")

        print("Se agotaron los intentos. No se pudo obtener un JSON válido.")
        return {
            "response": "Lo siento, ocurrió un error al procesar la respuesta.",
            "tool_calls": []
        }
        

    def validar_respuesta(self, respuesta_raw):
        """Verifica que la respuesta del LLM sea un JSON válido y cumpla con la estructura esperada."""
        try:
            respuesta_json = json.loads(respuesta_raw)
            respuesta_validada = LLMResponse(**respuesta_json)
            return json.dumps(respuesta_validada.dict(), ensure_ascii=False)
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"ERROR: Validación del JSON fallida: {e}")
            return None


    def get_formated_prompt(self, mensaje_usuario, emotion_detected, contexto):
                # Al generar el prompt, inyecta la "summary" de la memoria y/o su contenido:
        history_summary = self.memory.load_memory_variables({}).get("history", "")


        system_template =""" 
Eres PATO, un asistente virtual especializado en gestionar tareas y conversar de forma amistosa.

Tienes acceso a la siguiente información histórica de la conversación hasta ahora:
{history_summary}

La fecha actual es:
{fecha_actual}

INSTRUCCIONES DE SALIDA:
1. Devuelve siempre un único JSON con la forma:
{{
    "response": "Mensaje amigable para el usuario o explicación",
    "tool_calls": [...]

2. NUNCA incluyas nada fuera del JSON. Tampoco incluyas explicaciones o el esquema.

3. Si el usuario quiere ACCIONES DE TAREAS (añadir_tarea, eliminar_tarea, completar_tarea, modificar_tarea, deshacer_ultima_accion, consultar_tarea), añade objetos en "tool_calls" con:
    - "action": Acción a realizar (ej. "añadir_tarea")
    - "task": Nombre de la tarea (si aplica)
    - "new_task": Nuevo nombre de la tarea (solo si modificas)
    - "due_date": Fecha de vencimiento en formato YYYY-MM-DD si detectas fechas (incluso relativas como "mañana")
    - "priority": Priodidad si el usuario la menciona (baja, normal, alta o urgente)

4. Si el usuario no menciona prioridad, NO incluyas el campo "priority" en ese objeto.

5. Si el usuario solo quiere conversar y no solicita acciones sobre tareas, "tool_calls" debe ser [].
            
6. Ten en cuenta la emoción detectada: {emotion_detected} y ajusta tu respuesta en "response" de forma empática o apropiada al contexto.

7. Convierte fechas relativas como "mañana", "próximo viernes", etc. a YYYY-MM-DD. Ejemplo:
    - Usuario: "¿Qué tareas tengo para mañana?"
    - Salida: "due_date": "{fecha_mañana}".

8. No incluyas emojis ni caracteres especiales.

9. Corrige en lo posible errores de comandos. Sé amable y proactivo.

10. Para consultas sobre las tareas existentes (por ejemplo "¿qué tareas tengo para mañana?" o "¿tengo algo urgente?"):
    - Usa "consultar_tarea" en "tool_calls" para cada tarea consultada.
    - En el campo "response", incluye un resumen amigable sin saltos de linea que mencione cada tarea encontrada con su fecha y, si aplica, su prioridad.


Ejemplo de salida para conversación:
{{
    "response": "¡Hola! ¿En qué puedo ayudarte?",
    "tool_calls": []
}}

Ejemplo de salida para acción de tareas:
{{
    "response": "He añadido 'comprar leche' a tu lista.",
    "tool_calls": [
        {{
            "action": "añadir_tarea",
            "task": "Comprar leche",
            "due_date": "2025-02-25",
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
        
        hoy = datetime.today()
        fecha_actual = hoy.strftime('%Y-%m-%d')
        fecha_mañana = (hoy + timedelta(1)).strftime('%Y-%m-%d')
        
        # Creación del prompt de manera correcta
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])

        formatted_prompt = prompt.format_prompt(
            mensaje_usuario=mensaje_usuario,
            contexto=contexto,
            emotion_detected=emotion_detected,
            history_summary=history_summary,
            fecha_actual=fecha_actual,
            fecha_mañana=fecha_mañana,
        ).to_string()
        
        return formatted_prompt
    
    
    def borrar_memoria(self):
        self.memory.clear()