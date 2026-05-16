# 🧠 Actividad: Tipos de Memoria en LangChain

## Resumen

Actividad práctica donde el estudiante explora los diferentes tipos de memoria que ofrece LangChain para gestionar el historial de conversación en chatbots. A través de experimentos aislados con cada tipo de memoria y una interfaz web interactiva construida con Gradio, el estudiante comprende cómo los modelos de lenguaje "recuerdan" y por qué eso importa. Al final publica la app en Internet usando Ngrok para compartirla con la clase.

-----

## 📋 Ficha Técnica

|Campo                |Detalle                       |
|---------------------|------------------------------|
|**Archivo**          |`langchain_memoria.ipynb`     |
|**Entorno**          |Google Colab con GPU T4       |
|**Duración estimada**|90 – 120 minutos              |
|**Nivel**            |Intermedio                    |
|**Partes**           |12 partes + limpieza + rúbrica|

-----

## 🎯 Objetivos de Aprendizaje

1. Comprender por qué los modelos de lenguaje no tienen memoria por defecto y cómo LangChain resuelve este problema
1. Distinguir entre los cuatro tipos principales de memoria de LangChain y sus casos de uso
1. Observar el estado interno de la memoria en tiempo real durante una conversación
1. Construir una interfaz interactiva con Gradio que permita cambiar el tipo de memoria en vivo
1. Publicar una aplicación web en Internet usando un túnel Ngrok

-----

## 🗺️ Estructura de la Actividad

### PARTE 1 — Instalación del Entorno

Instala todas las dependencias necesarias para la actividad completa en una sola celda.

**Celdas:**

- Celda 1: `pip install langchain langchain-community langchain-ollama gradio pyngrok`

-----

### PARTE 2 — Configuración de Ollama y Selección de Modelo

Levanta el servidor Ollama como proceso en background, descarga TinyLlama y verifica que el modelo responde correctamente antes de avanzar.

**Modelo por defecto:** TinyLlama (1.1B parámetros, ~637 MB)
**Modelo recomendado para Parte 6:** llama3.2 (~2 GB)

**Celdas:**

- Celda 2: Instalar Ollama con `curl -fsSL https://ollama.com/install.sh | sh`
- Celda 3: Iniciar servidor con `subprocess.Popen(['ollama', 'serve'], stdout=DEVNULL)` en background
- Celda 4: Descargar modelo con `ollama pull tinyllama`
- Celda 5: Definir variable `MODELO_ACTIVO = 'tinyllama'` (punto central de configuración del modelo)
- Celda 6: Instanciar `ChatOllama` y verificar con un mensaje de prueba

-----

### PARTE 3 — ¿Qué es la Memoria en LangChain?

Bloque conceptual que explica el problema fundamental (los LLMs no recuerdan entre llamadas) y presenta los 4 tipos de memoria mediante diagramas ASCII y tabla comparativa.

**Conceptos clave:** contexto de llamada, historial de conversación, `ConversationChain`, el rol del objeto de memoria como intermediario entre el usuario y el LLM.

-----

### PARTE 4 — ConversationBufferMemory

Guarda el historial completo de la conversación sin ningún límite. Cada turno se agrega al buffer y el LLM recibe siempre la conversación íntegra.

**Cuándo usarla:** conversaciones cortas donde el contexto completo es esencial.

**Celdas:**

- Celda 7: Configurar `ConversationBufferMemory(return_messages=True)` y `ConversationChain`
- Celda 8: Definir `chatear_y_mostrar()` — función auxiliar que envía un mensaje y imprime el estado interno de `memoria.chat_memory.messages` después de cada turno
- Celda 9: Conversación de prueba de 3 turnos — observar cómo el buffer crece de 2 → 4 → 6 mensajes

-----

### PARTE 5 — ConversationBufferWindowMemory

Guarda solo las últimas `k` interacciones. Lo más antiguo se elimina automáticamente cuando se supera la ventana.

**Configuración:** `k=2` (ventana de 2 interacciones)
**Cuándo usarla:** conversaciones largas donde solo importa el contexto reciente.

**Celdas:**

- Celda 10: Configurar `ConversationBufferWindowMemory(k=2, return_messages=True)`
- Celda 11: Conversación de prueba de 3 turnos — observar cómo el primer turno desaparece al llegar el tercero

-----

### PARTE 6 — ConversationSummaryMemory

En lugar de guardar mensajes exactos, usa el LLM para resumir progresivamente la conversación. El resumen se actualiza en cada turno.

**Cuándo usarla:** conversaciones muy largas donde los detalles exactos no importan, solo la esencia.

> ⚠️ **Nota de modelo:** esta parte incluye un aviso explícito para cambiar a `llama3.2`, ya que TinyLlama genera resúmenes de baja calidad que pueden confundir al estudiante sobre si el problema es la memoria o el modelo.

**Celdas:**

- Celda 12: Configurar `ConversationSummaryMemory(llm=llm, return_messages=True)`
- Celda 13: Definir `chatear_y_mostrar_summary()` — versión adaptada que muestra `memoria.moving_summary_buffer` en lugar de una lista de mensajes
- Celda 14: Conversación de prueba — observar cómo el resumen reemplaza los mensajes exactos

-----

### PARTE 7 — ConversationTokenBufferMemory

Guarda el historial hasta un límite máximo de tokens. Cuando se supera el límite, elimina los mensajes más antiguos.

**Configuración:** `max_token_limit=200` (bajo a propósito para ver el efecto rápidamente)
**Cuándo usarla:** cuando el costo del modelo se mide en tokens y se necesita control preciso del gasto.

**Celdas:**

- Celda 15: Configurar `ConversationTokenBufferMemory(llm=llm, max_token_limit=200)`
- Celda 16: Conversación de prueba con mensajes largos — observar cuándo los mensajes anteriores empiezan a desaparecer

-----

### PARTE 8 — Chat Interactivo con Gradio

Interfaz web de dos columnas: chat a la izquierda y panel con el estado interno de la memoria en tiempo real a la derecha. El estudiante puede cambiar el tipo de memoria en cualquier momento desde un dropdown; el chat se reinicia automáticamente con un mensaje de aviso.

**Celdas:**

- Celda 17: Importaciones y definición del diccionario `TIPOS_MEMORIA` que mapea nombres legibles a códigos internos
- Celda 18: Definir `crear_memoria(tipo)` — factory que instancia la memoria correcta según el tipo seleccionado
- Celda 19: Definir `obtener_estado_memoria(memoria, tipo)` — formatea el estado interno para el panel lateral (adapta su lectura según si es Summary o los otros tipos)
- Celda 20: Inicializar `estado_app` — diccionario mutable compartido para gestionar el estado entre llamadas de Gradio
- Celda 21: Definir `cambiar_memoria()`, `responder()` y `limpiar_chat()` — lógica completa del chat
- Celda 22: Construir la interfaz con `gr.Blocks`, CSS personalizado, layout de dos columnas, dropdown, chatbot, campo de texto y conexión de eventos
- Celda 23: `demo.launch(server_name='0.0.0.0', server_port=7860, share=False)` — prueba local

-----

### PARTE 9 — Reflexión

Cinco preguntas que el estudiante responde en una celda markdown:

1. Diferencia fundamental entre `BufferMemory` y `WindowMemory` y cuándo elegir cada una
1. Por qué `SummaryMemory` y `TokenBufferMemory` necesitan recibir un LLM como parámetro
1. Riesgos de usar el mismo LLM para resumir y para responder en `SummaryMemory` (costos, errores, privacidad)
1. Cuándo elegir `TokenBufferMemory` sobre `BufferMemory` a pesar de su mayor complejidad
1. Reflexión personal sobre qué tipo de memoria sería más útil para un asistente de aprendizaje

-----

### PARTE 10 — Retos Opcionales

Tres retos con una celda vacía para experimentar:

- **Reto 1:** Ajustar `k` en WindowMemory a `k=1` y `k=5` para encontrar el punto en que el modelo empieza a olvidar información relevante
- **Reto 2:** Añadir un System Prompt con personalidad definida y verificar si se conserva con todos los tipos de memoria
- **Reto 3:** Medir el consumo de tokens por llamada y comparar cómo crece con `BufferMemory` vs `TokenBufferMemory`

-----

### PARTE 11 — 🚀 Módulo Avanzado: EntityMemory y KGMemory

> **Opcional.** Requiere `llama3.2` o superior. TinyLlama no extrae entidades ni relaciones con suficiente precisión.

Estas memorias no tratan el historial como texto lineal: extraen **estructura** de la conversación. `EntityMemory` construye un perfil por cada persona, lugar o concepto mencionado. `KGMemory` va más allá y detecta las relaciones entre entidades, formando un grafo de conocimiento.

**Celdas:**

- Celda 24: Descargar `llama3.2` e instanciar `llm_avanzado = ChatOllama(model='llama3.2')`
- Celda 25: Configurar `ConversationEntityMemory` con `ENTITY_MEMORY_CONVERSATION_TEMPLATE`
- Celda 26: Definir `mostrar_entidades()` — imprime `memoria.entity_store.store` de forma legible
- Celda 27: Conversación de prueba con EntityMemory — introducir personas con roles y observar el diccionario de entidades
- Celda 28: Configurar `ConversationKGMemory`
- Celda 29: Conversación de prueba con KGMemory — observar tripletas `(sujeto, predicado, objeto)` extraídas del texto

-----

### PARTE 12 — Publicación con Ngrok

Reemplaza la prueba local por un túnel Ngrok estable con URL pública compartible con toda la clase.

**Celdas:**

- Celda 30: `pip install pyngrok`
- Celda 31: Autenticar — lee token desde `userdata.get('NGROK_TOKEN')` (Colab Secrets), con fallback a `input()` manual y advertencia de seguridad
- Celda 32: `ngrok.kill()` → `demo.close()` → `ngrok.connect(7860)` → `demo.launch(server_name='0.0.0.0', share=False)`
- Celda 33: Inspeccionar túneles activos con `ngrok.get_tunnels()`

-----

### Limpieza Final

Una celda que libera todos los recursos en orden:

1. Túnel Ngrok (`ngrok.kill()`)
1. Interfaz Gradio (`demo.close()`)
1. Servidor Ollama (`ollama_process.terminate()`)
1. Memoria GPU (`del llm_avanzado` + `torch.cuda.empty_cache()`)

-----

## 🛠️ Stack Técnico

|Componente        |Herramienta       |Detalle                                          |
|------------------|------------------|-------------------------------------------------|
|Modelo de lenguaje|Ollama + TinyLlama|API REST en localhost:11434                      |
|Modelo avanzado   |Ollama + llama3.2 |Para módulo EntityMemory / KGMemory              |
|Memoria           |LangChain         |Buffer, Window, Summary, TokenBuffer, Entity, KG |
|Interfaz          |Gradio gr.Blocks  |CSS personalizado, panel de estado en tiempo real|
|Publicación       |Ngrok vía pyngrok |Token desde Colab Secrets                        |
|GPU               |NVIDIA T4 (Colab) |Requerida para llama3.2 y módulo avanzado        |

-----

## ⚠️ Requisitos Previos del Estudiante

- Cuenta de Google (para Colab)
- Cuenta gratuita en [ngrok.com](https://ngrok.com) con token generado
- Token de Ngrok guardado en Colab Secrets como `NGROK_TOKEN`
- Activar GPU T4 antes de ejecutar: `Entorno de ejecución → Cambiar tipo de entorno de ejecución → T4 GPU`

-----

## 📊 Rúbrica

|Criterio                               |Excelente (5)                                                                         |Satisfactorio (3)                                              |En desarrollo (1)                                     |
|---------------------------------------|--------------------------------------------------------------------------------------|---------------------------------------------------------------|------------------------------------------------------|
|**Ejecución del notebook**             |Todas las celdas ejecutadas sin errores, de arriba a abajo                            |La mayoría de celdas funcionan; algún error menor no bloqueante|Más de 2 partes no ejecutan correctamente             |
|**Comprensión de los tipos de memoria**|Las 5 preguntas de reflexión muestran comprensión clara y diferenciada de cada tipo   |Responde correctamente al menos 3 preguntas                    |Respuestas superficiales o confunde los tipos entre sí|
|**Experimentación con la interfaz**    |Probó todos los tipos en Gradio y describe diferencias observadas                     |Probó al menos 2 tipos y describe una diferencia               |Solo usó el tipo por defecto sin explorar             |
|**Módulo avanzado**                    |Ejecutó EntityMemory y KGMemory, observó y describió entidades y relaciones detectadas|Intentó el módulo avanzado aunque con errores parciales        |No intentó el módulo avanzado                         |
|**Publicación con Ngrok**              |URL pública generada, funcional y compartida con el docente                           |URL generada pero con acceso intermitente                      |No se pudo generar la URL pública                     |
|**Retos opcionales**                   |Completó al menos 1 reto con código funcional y documentado                           |Intentó un reto con código parcial                             |No intentó los retos opcionales                       |

-----

## 📎 Entrega

El estudiante entrega:

1. El notebook `.ipynb` con todas las celdas ejecutadas
1. Las preguntas de reflexión respondidas en la celda markdown de la Parte 9
1. Una captura de pantalla de la URL de Ngrok funcionando en el navegador
