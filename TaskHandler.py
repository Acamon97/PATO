"""
taskHandler.py - Módulo de gestión de tareas a través de comandos del LLM

Este módulo se encarga de procesar las acciones relacionadas con tareas 
que devuelve el modelo de lenguaje (LLM). 

Funcionalidad:
- Añadir, eliminar, completar y modificar tareas.
- Deshacer la última acción realizada.
- Consultar tareas registradas.

Dependencias:
- `TaskManager`: Manejador de almacenamiento y consulta de tareas.

Clases y métodos principales:
- `procesar_acciones(respuesta_json)`: Procesa las acciones devueltas por el LLM.
- `registrar_accion(accion, datos)`: Registra una acción en el historial para permitir su deshacer.
- `deshacer()`: Revierte la última acción ejecutada.
"""

from TaskManager import TaskManager


class TaskHandler:
    """
    Clase encargada de procesar acciones relacionadas con tareas, 
    permitiendo la gestión de tareas y el historial de acciones.
    """

    MAX_HISTORIAL = 10  # Número máximo de acciones almacenadas en el historial

    def __init__(self):
        """
        Inicializa el `TaskHandler` con un `TaskManager` y un historial de acciones.
        """
        self.task_manager = TaskManager()
        self.historial_acciones = []  # Historial de acciones ejecutadas
        self.historial_respaldo = []  # Respaldo en caso de deshacer una acción incorrectamente

    def procesar_acciones(self, respuesta_json):
        """
        Procesa las acciones devueltas por el LLM en formato JSON.

        Parámetros:
        - respuesta_json (dict): JSON con la estructura {"response": "texto", "tool_calls": [{...}]}.

        Retorna:
        - (str): Respuesta del LLM, posiblemente modificada con información adicional de tareas.
        """

        acciones = respuesta_json.get("tool_calls", [])
        informacion_tareas = " "

        for action_data in acciones:
            action = action_data.get("action")
            task = action_data.get("task")
            due_date = action_data.get("due_date", None)
            priority = action_data.get("priority", None)
            new_task = action_data.get("new_task", task)
            
            if due_date == "Null": 
                due_date = None
            if priority == "Null": 
                priority = None

            if action in ["añadir", "eliminar", "completar", "modificar"] and not task:
                print(f"Error: El campo 'task' es obligatorio para la acción '{action}'.")
                continue  

            if action == "añadir":
                self.registrar_accion("eliminar", {"task": task, "due_date": due_date, "priority": priority})
                self.task_manager.añadir_tarea(task, due_date, priority)

            elif action == "eliminar":
                coincidencias = self.task_manager.buscar_tarea(task, due_date, priority)
                if coincidencias:
                    for tarea in coincidencias:
                        self.registrar_accion("añadir", tarea)
                        self.task_manager.eliminar_tarea(**tarea)

            elif action == "completar":
                coincidencias = self.task_manager.buscar_tarea(task, due_date, priority)
                if coincidencias:
                    for tarea in coincidencias:
                        self.registrar_accion("restaurar_pendiente", tarea)
                        self.task_manager.completar_tarea(**tarea)

            elif action == "modificar":
                tarea_original = self.task_manager.buscar_tarea(task, due_date, priority)
                if tarea_original:
                    self.registrar_accion("modificar", {
                        "task": new_task,
                        "new_task": task,
                        "due_date": tarea_original[0].get("due_date"),
                        "priority": tarea_original[0].get("priority")
                    })
                    self.task_manager.modificar_tarea(task, new_task, due_date, priority)

            elif action == "deshacer":
                return self.deshacer()
            
            elif action == "consultar":                
                if task and task.lower() not in respuesta_json["response"].lower():
                    informacion_tareas += task + ", "

            else:
                print(f"Acción desconocida en TaskHandler: {action}")
        
                
        return respuesta_json["response"] + informacion_tareas

    def registrar_accion(self, accion, datos):
        """
        Guarda una acción en el historial, eliminando la más antigua si supera el límite.

        Parámetros:
        - accion (str): Tipo de acción a registrar.
        - datos (dict): Datos relacionados con la acción.
        """
        if len(self.historial_acciones) >= self.MAX_HISTORIAL:
            self.historial_acciones.pop(0)  # Mantener el historial dentro del límite
        self.historial_acciones.append({"action": accion, "data": datos})

    def deshacer(self):
        """
        Deshace la última acción registrada, si es posible.

        Retorna:
        - (str): Mensaje indicando el resultado de la operación.
        """
        if not self.historial_acciones:
            return "No hay acciones recientes para deshacer."

        ultima_accion = self.historial_acciones.pop()

        if ultima_accion["action"] == "deshacer":
            return "No puedes deshacer una acción que ya fue revertida."

        self.historial_respaldo.append(self.historial_acciones[:])  # Respaldo antes de deshacer

        action = ultima_accion["action"]
        data = ultima_accion["data"]

        if action == "añadir":
            self.task_manager.eliminar_tarea(**data)
        elif action == "eliminar":
            self.task_manager.añadir_tarea(**data)
        elif action == "modificar":
            self.task_manager.modificar_tarea(**data)
        elif action == "restaurar_pendiente":
            self.task_manager.completar_tarea(**data)

        return "La última acción ha sido revertida con éxito."
