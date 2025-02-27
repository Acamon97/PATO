from TaskManager import TaskManager

class TaskHandler:
    MAX_HISTORIAL = 10  

    def __init__(self):
        """Inicializa el TaskHandler con el TaskManager y mantiene un historial de acciones para deshacer."""
        self.task_manager = TaskManager()
        self.historial_acciones = []  # Almacena el historial de acciones para revertirlas
        self.historial_respaldo = []  # Respaldo en caso de deshacer una acción incorrectamente

    def procesar_acciones(self, respuesta_json):
        """
        Procesa las acciones devueltas por el LLM en formato JSON.
        :param respuesta_json: JSON con la estructura {"response": "texto", "tool_calls": [{...}]}
        """
        
        acciones = respuesta_json.get("tool_calls", [])
        informacion_tareas = " "

        for action_data in acciones:
            action = action_data.get("action")
            task = action_data.get("task")
            due_date = action_data.get("due_date", None)
            priority = action_data.get("priority", None)
            new_task = action_data.get("new_task", task)

            if action in ["añadir_tarea", "eliminar_tarea", "completar_tarea", "modificar_tarea"] and not task:
                print(f"Error: El campo 'task' es obligatorio para la acción '{action}'.")
                continue  

            if action == "añadir_tarea":
                self.registrar_accion("eliminar_tarea", {"task": task, "due_date": due_date, "priority": priority})
                self.task_manager.añadir_tarea(task, due_date, priority)

            elif action == "eliminar_tarea":
                coincidencias = self.task_manager.buscar_tarea(task, due_date, priority)
                if coincidencias:
                    for tarea in coincidencias:
                        self.registrar_accion("añadir_tarea", tarea)
                        self.task_manager.eliminar_tarea(**tarea)

            elif action == "completar_tarea":
                coincidencias = self.task_manager.buscar_tarea(task, due_date, priority)
                if coincidencias:
                    for tarea in coincidencias:
                        self.registrar_accion("restaurar_tarea_pendiente", tarea)
                        self.task_manager.completar_tarea(**tarea)

            elif action == "modificar_tarea":
                tarea_original = self.task_manager.buscar_tarea(task, due_date, priority)
                if tarea_original:
                    self.registrar_accion("modificar_tarea", {
                        "task": new_task,
                        "new_task": task,
                        "due_date": tarea_original[0].get("due_date"),
                        "priority": tarea_original[0].get("priority")
                    })
                    self.task_manager.modificar_tarea(task, new_task, due_date, priority)

            elif action == "deshacer_ultima_accion":
                return self.deshacer_ultima_accion()
            
            elif action == "consultar_tarea":                
                informacion_tareas += task + ", "

            else:
                print(f"Acción desconocida en TaskHandler: {action}")

        return respuesta_json["response"] + informacion_tareas

    def registrar_accion(self, accion, datos):
        """Guarda la acción en el historial, eliminando la más antigua si supera el límite."""
        if len(self.historial_acciones) >= self.MAX_HISTORIAL:
            self.historial_acciones.pop(0)  
        self.historial_acciones.append({"action": accion, "data": datos})

    def deshacer_ultima_accion(self):
        """Deshace la última acción ejecutada si es posible, evitando bucles infinitos de deshacer."""
        if not self.historial_acciones:
            return "No hay acciones recientes para deshacer."

        if self.historial_acciones[-1]["action"] == "deshacer_ultima_accion":
            return "No puedes deshacer una acción que ya fue revertida."

        self.historial_respaldo.append(self.historial_acciones[:]) 

        ultima_accion = self.historial_acciones.pop()
        action = ultima_accion["action"]
        data = ultima_accion["data"]

        if action == "añadir_tarea":
            self.task_manager.eliminar_tarea(**data)
        elif action == "eliminar_tarea":
            self.task_manager.añadir_tarea(**data)
        elif action == "modificar_tarea":
            self.task_manager.modificar_tarea(**data)
        elif action == "restaurar_tarea_pendiente":
            self.task_manager.completar_tarea(**data)

        return "La última acción ha sido revertida con éxito."
