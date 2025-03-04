"""
taskManager.py - Módulo de gestión de almacenamiento de tareas

Este módulo permite la creación, modificación, eliminación y consulta de tareas 
almacenadas en archivos JSON, incluyendo tareas completadas.

Funcionalidad:
- Carga y guarda tareas en archivos JSON.
- Permite agregar, eliminar, completar y modificar tareas.
- Ofrece consultas en formato JSON o texto.
- Permite restaurar tareas completadas a la lista de pendientes.

Dependencias:
- `json`: Para manejar almacenamiento de tareas en archivos JSON.
- `os`: Para verificar y gestionar archivos.
- `datetime`: Para registrar fechas de creación y finalización.

Clases y métodos principales:
- `load_tasks(file_path)`: Carga tareas desde un archivo JSON.
- `añadir_tarea(task, due_date, priority)`: Agrega una tarea si no existe.
- `eliminar_tarea(task, due_date, priority)`: Elimina una tarea.
- `completar_tarea(task, due_date, priority)`: Mueve una tarea a completadas.
- `modificar_tarea(original_task, new_task, new_due_date, new_priority)`: Modifica una tarea.
- `consultar_tareas(formato_json)`: Devuelve la lista de tareas pendientes.
- `consultar_tareas_completadas(formato_json)`: Devuelve la lista de tareas completadas.
"""

import json
import os
from datetime import datetime


class TaskManager:
    """
    Clase para gestionar el almacenamiento y manipulación de tareas en archivos JSON.

    Permite agregar, eliminar, completar, modificar y consultar tareas almacenadas en
    archivos JSON, garantizando persistencia.
    """

    TASKS_FILE = os.path.join("Resources", "tasks.json")
    COMPLETED_TASKS_FILE = os.path.join("Resources", "completed_tasks.json")

    def __init__(self):
        """Carga las tareas existentes desde los archivos JSON."""
        self.tasks = self.load_tasks(self.TASKS_FILE)
        self.completed_tasks = self.load_tasks(self.COMPLETED_TASKS_FILE)

    def load_tasks(self, file_path):
        """
        Carga tareas desde un archivo JSON.

        Parámetros:
        - file_path (str): Ruta del archivo JSON.

        Retorna:
        - list: Lista de tareas cargadas o una lista vacía si hay un error.
        """
        if not os.path.exists(file_path):
            self.save_tasks(file_path, [])  # Crear archivo si no existe
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            print(f"⚠ Error al cargar {file_path}, inicializando una lista vacía.")
            self.save_tasks(file_path, [])  # Restaurar archivo corrupto
            return []

    def save_tasks(self, file_path, tasks):
        """
        Guarda las tareas en un archivo JSON.

        Parámetros:
        - file_path (str): Ruta del archivo JSON.
        - tasks (list): Lista de tareas a guardar.
        """
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=4, ensure_ascii=False)

    def buscar_tarea(self, task, due_date=None, priority=None, created_at=None):
        """
        Busca una tarea específica basándose en múltiples criterios.

        - Primero filtra por nombre de la tarea. 
        - Si hay una sola coincidencia, la devuelve directamente. 
        - Si hay varias coincidencias con el mismo nombre, se afinan los resultados
        usando due_date, priority, created_at.
        
        Retorna:
        - list: Lista de coincidencias o `None` si no hay resultados.
        """

        # 1. Filtrar solo por nombre de la tarea
        coincidencias_nombre = [
            t for t in self.tasks 
            if t["task"].lower() == task.lower()
        ]

        # Si no hay coincidencias por nombre, retornamos None
        if not coincidencias_nombre:
            return None

        # Si hay exactamente 1 coincidencia por nombre, devolvemos directamente
        if len(coincidencias_nombre) == 1:
            return coincidencias_nombre

        # 2. Si hay varias coincidencias con el mismo nombre, afinamos con los filtros
        coincidencias = [
            t for t in coincidencias_nombre 
            if (due_date is None or t["due_date"] == due_date)
            and (priority is None or t["priority"] == priority)
            and (created_at is None or t["created_at"] == created_at)
        ]

        return coincidencias if coincidencias else None


    def añadir_tarea(self, task, due_date=None, priority="normal"):
        """
        Añade una tarea a la lista si no existe una igual.

        Parámetros:
        - task (str): Nombre de la tarea.
        - due_date (str, opcional): Fecha de vencimiento.
        - priority (str, opcional): Prioridad (por defecto "normal").

        Retorna:
        - bool: `True` si la tarea se añadió, `False` si ya existía.
        """
        created_at = datetime.today().strftime('%Y-%m-%d')

        if self.buscar_tarea(task, due_date, priority, created_at):
            print("La tarea ya existe. No se añadirá nuevamente.")
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
        """
        Elimina una tarea basada en múltiples criterios.

        Retorna:
        - bool: `True` si se eliminó alguna tarea, `False` si no hubo coincidencias.
        """
        coincidencias = self.buscar_tarea(task, due_date, priority, created_at)
        if coincidencias:
            for tarea in coincidencias:
                self.tasks.remove(tarea)
            self.save_tasks(self.TASKS_FILE, self.tasks)
            return True
        return False

    def completar_tarea(self, task, due_date=None, priority=None, created_at=None):
        """
        Marca una tarea como completada y la mueve al archivo de tareas completadas.

        Retorna:
        - bool: `True` si se completó una tarea, `False` si no hubo coincidencias.
        """
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
        """
        Modifica una tarea existente.

        Retorna:
        - str: Mensaje de éxito o error.
        """
        for tarea in self.tasks:
            if tarea["task"] == original_task:
                if new_task:
                    tarea["task"] = new_task
                if new_due_date:
                    tarea["due_date"] = new_due_date
                if new_priority:
                    tarea["priority"] = new_priority
                self.save_tasks(self.TASKS_FILE, self.tasks)
                return f"Tarea actualizada: {tarea}"
        return "No se encontró la tarea."

    def restaurar_tarea_pendiente(self, task, due_date=None, priority=None, created_at=None):
        """
        Restaura una tarea completada a la lista de pendientes.

        Retorna:
        - bool: `True` si se restauró una tarea, `False` si no hubo coincidencias.
        """
        coincidencias = [
            t for t in self.completed_tasks if
            t["task"].lower() == task.lower()
            and (due_date is None or t["due_date"] == due_date)
            and (priority is None or t["priority"] == priority)
            and (created_at is None or t["created_at"] == created_at)
        ]

        if coincidencias:
            for tarea in coincidencias:
                tarea.pop("completed_at", None)  
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