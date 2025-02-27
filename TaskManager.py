import json
import os
from datetime import datetime

class TaskManager:
    TASKS_FILE = os.path.join("Resources", "tasks.json")
    COMPLETED_TASKS_FILE = os.path.join("Resources", "completed_tasks.json")

    def __init__(self):
        """Carga las tareas existentes, tanto pendientes como completadas."""
        self.tasks = self.load_tasks(self.TASKS_FILE)
        self.completed_tasks = self.load_tasks(self.COMPLETED_TASKS_FILE)

    def load_tasks(self, file_path):
        """Carga tareas desde un archivo JSON con manejo de errores."""
        if not os.path.exists(file_path):
            self.save_tasks(file_path, [])  # Crear archivo vacío si no existe
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            print(f"⚠ Error al cargar {file_path}, inicializando una lista vacía.")
            self.save_tasks(file_path, [])  # Restablecer el archivo si está corrupto
            return []

    def save_tasks(self, file_path, tasks):
        """Guarda las tareas en un archivo JSON."""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=4, ensure_ascii=False)

    def obtener_tarea(self, task_name):
        """Devuelve los detalles de una tarea si existe."""
        for task in self.tasks + self.completed_tasks:  # Buscar en ambas listas
            if task["task"].lower() == task_name.lower():
                return task
        return None

    def buscar_tarea(self, task, due_date=None, priority=None, created_at=None):
        """Busca tareas específicas basadas en múltiples criterios."""
        coincidencias = [
            t for t in self.tasks if
            t["task"].lower() == task.lower()
            and (due_date is None or t["due_date"] == due_date)
            and (priority is None or t["priority"] == priority)
            and (created_at is None or t["created_at"] == created_at)
        ]
        return coincidencias if coincidencias else None

    def añadir_tarea(self, task, due_date=None, priority="normal"):
        """Añade una tarea solo si no existe una igual."""
        created_at = datetime.today().strftime('%Y-%m-%d')

        if self.buscar_tarea(task, due_date, priority, created_at):
            print("⚠ La tarea ya existe. No se añadirá nuevamente.")
            return False

        nueva_tarea = {
            "task": task,
            "created_at": created_at,
            "due_date": due_date,
            "priority": priority
        }
        self.tasks.append(nueva_tarea)
        self.save_tasks(self.TASKS_FILE, self.tasks)
        return True

    def eliminar_tarea(self, task, due_date=None, priority=None, created_at=None):
        """Elimina una tarea específica basada en múltiples criterios."""
        coincidencias = self.buscar_tarea(task, due_date, priority, created_at)
        if coincidencias:
            for tarea in coincidencias:
                self.tasks.remove(tarea)
            self.save_tasks(self.TASKS_FILE, self.tasks)
            return True
        return False

    def completar_tarea(self, task, due_date=None, priority=None, created_at=None):
        """Marca una tarea como completada y la mueve al archivo de tareas completadas."""
        coincidencias = self.buscar_tarea(task, due_date, priority, created_at)
        if coincidencias:
            for tarea in coincidencias:
                tarea["completed_at"] = datetime.today().strftime('%Y-%m-%d')
                self.tasks.remove(tarea)
                self.completed_tasks.append(tarea)
            self.save_tasks(self.TASKS_FILE, self.tasks)
            self.save_tasks(self.COMPLETED_TASKS_FILE, self.completed_tasks)
            return True
        return False
    
    def modificar_tarea(self, original_task, new_task=None, new_due_date=None, new_priority=None):
        """Modifica una tarea existente."""
        for tarea in self.tasks:
            if tarea["task"] == original_task:
                if new_task:
                    tarea["task"] = new_task
                if new_due_date:
                    tarea["due_date"] = new_due_date
                if new_priority:
                    tarea["priority"] = new_priority
                self.save_tasks(self.TASKS_FILE, self.tasks)
                self.save_tasks(self.COMPLETED_TASKS_FILE, self.completed_tasks)
                return f"Tarea actualizada: {tarea}"
        return "No se encontró la tarea."


    def restaurar_tarea_pendiente(self, task, due_date=None, priority=None, created_at=None):
        """Restaura una tarea completada a la lista de pendientes."""
        coincidencias = [
            t for t in self.completed_tasks if
            t["task"].lower() == task.lower()
            and (due_date is None or t["due_date"] == due_date)
            and (priority is None or t["priority"] == priority)
            and (created_at is None or t["created_at"] == created_at)
        ]

        if coincidencias:
            for tarea in coincidencias:
                tarea.pop("completed_at", None)  # Eliminar fecha de finalización
                self.completed_tasks.remove(tarea)
                self.tasks.append(tarea)
            self.save_tasks(self.TASKS_FILE, self.tasks)
            self.save_tasks(self.COMPLETED_TASKS_FILE, self.completed_tasks)
            return True
        return False

    def consultar_tareas(self, formato_json=True):
        """Devuelve la lista de tareas pendientes. Puede devolverse como JSON o texto."""
        if not self.tasks:
            return {"mensaje": "No tienes tareas pendientes."} if formato_json else "No tienes tareas pendientes."
        if formato_json:
            return {"tareas_pendientes": self.tasks}
        return "\n".join(
            [f"{i + 1}. {t['task']} (Prioridad: {t['priority']})" for i, t in enumerate(self.tasks)]
        )

    def consultar_tareas_completadas(self, formato_json=True):
        """Devuelve la lista de tareas completadas. Puede devolverse como JSON o texto."""
        if not self.completed_tasks:
            return {"mensaje": "No tienes tareas completadas."} if formato_json else "No tienes tareas completadas."
        if formato_json:
            return {"tareas_completadas": self.completed_tasks}
        return "\n".join(
            [f"{i + 1}. {t['task']} (Finalizada el {t['completed_at']})" for i, t in enumerate(self.completed_tasks)]
        )
