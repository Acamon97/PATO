import sys
import os

# Agregar el directorio padre al path para importar LLM.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from TaskManager import TaskManager

task_manager = TaskManager()

def test_task_manager():
    print("\n🔍 Probando gestión de tareas")

    # Añadir tarea
    assert task_manager.añadir_tarea("Comprar pan") == True
    print("✅ Añadir tarea: PASSED")

    # Consultar tareas
    tareas = task_manager.consultar_tareas()
    assert "Comprar pan" in json.dumps(tareas)
    print("✅ Consultar tareas: PASSED")

    # Completar tarea
    assert task_manager.completar_tarea("Comprar pan") == True
    print("✅ Completar tarea: PASSED")

    # Restaurar tarea
    assert task_manager.restaurar_tarea_pendiente("Comprar pan") == True
    print("✅ Restaurar tarea: PASSED")

    # Eliminar tarea
    assert task_manager.eliminar_tarea("Comprar pan") == True
    print("✅ Eliminar tarea: PASSED")

if __name__ == "__main__":
    test_task_manager()
