# PATO: Asistente Virtual Basado en IA

Este repositorio contiene el código fuente de PATO, un prototipo de asistente virtual que integra:
- **Reconocimiento Automático de Voz (ASR)**
- **Detección de Emociones (SER)**
- **Procesamiento y Comprensión del Lenguaje Natural (NLU)**
- **Generación de Respuestas en Formato JSON y/o Texto Libre**
- **Síntesis de Voz (TTS)**

El objetivo principal de PATO es ofrecer una experiencia de gestión de tareas mediante lenguaje natural, permitiendo organizar, modificar y consultar listas de tareas de forma sencilla y personalizable.

---

## Características Principales

- **Arquitectura Modular**: Cada funcionalidad (ASR, SER, NLU, LLM, TTS) se implementa como un módulo independiente.
- **Integración de un LLM**: Utiliza un Large Language Model para procesar e interpretar peticiones complejas.
- **Reconocimiento de Emociones**: Ajusta su respuesta en función de la emoción detectada en la voz del usuario.
- **Salida en Formato JSON**: Facilita la coordinación con otros servicios y la automatización de acciones.
- **Modo Conversacional**: Conserva cierto contexto de diálogo para peticiones sucesivas.

---

## Requisitos Previos

- **Python 3.9+**
- **Librerías de IA y PLN** (por ejemplo, `rasa`, `torch`, `transformers`, etc.)
- **Módulos de Síntesis y Reconocimiento de Voz** (dependiendo del sistema operativo)

> **Nota**: Las versiones exactas de cada dependencia se especifican en el archivo [`requirements.txt`](./requirements.txt), si se ha incluido.

---

## Instalación y Configuración

1. **Clona este repositorio**:
   ```bash
   git clone https://github.com/Acamon97/PATO.git
   ```

2. **Instala las dependencias**:
   ```bash
   cd PATO
   pip install -r resources/requirements.txt
   ```

3. **Configura tu entorno**:
   - Asegúrate de contar con micrófono y altavoces configurados si planeas usar funciones de reconocimiento y síntesis de voz.
   - Opcionalmente, configura credenciales o variables de entorno para servicios de voz externos, si son requeridos.

---

## Ejecución

- **Iniciar el asistente**:
   ```bash
   python pato.py
   ```
   Dependiendo de la configuración, se abrirá una ventana o consola donde podrás interactuar con PATO vía voz.
---

## Uso Básico

Una vez iniciado, PATO te guiará en la creación, modificación y consulta de tareas. Por ejemplo:
- `Añade la tarea de comprar pan con prioridad alta.`
- `¿Qué tareas me quedan pendientes?`
- `Completa la tarea de enviar informes.`

Si detecta un tono de frustración o cansancio en tu voz, PATO puede ajustar el lenguaje de respuesta o dar sugerencias para aligerar tu lista de tareas.

---

## Contribuciones

Las contribuciones son bienvenidas. Si deseas proponer nuevas funcionalidades, corregir errores o mejorar la documentación, crea un _issue_ o envía un _pull request_.

---

## Contacto

Para más información, revisa el Anexo de Código en el TFM correspondiente o contacta a [Acamon97](https://github.com/Acamon97).

¡Gracias por tu interés en PATO!
