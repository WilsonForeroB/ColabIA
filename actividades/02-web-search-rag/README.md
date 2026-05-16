# Actividad 02 — RAG Multi-Agente: Síntesis de Fuentes Web

## Objetivo de aprendizaje

Construir paso a paso un sistema multi-agente que consulta dos fuentes de internet definidas por el usuario, sintetiza la información y expone una interfaz conversacional accesible desde cualquier navegador.

Al finalizar el estudiante sabrá:
- Qué es un sistema multi-agente y cómo se diferencia de un LLM simple
- Cómo crear herramientas (tools) que un agente puede invocar automáticamente
- Cómo gestionar memoria de conversación (buffer y ventana deslizante)
- Cómo publicar una interfaz Gradio en tiempo real con Ngrok

## Prerrequisitos

- Haber completado la **Actividad 01** (conceptos de Ollama y Gradio)
- Token de Ngrok guardado en Colab Secrets como `NGROK_TOKEN`
- Conexión a internet activa durante la ejecución (para las búsquedas web)

## Stack tecnológico

| Rol | Herramienta |
|-----|-------------|
| Entorno | Google Colab (GPU T4) |
| Modelo de texto | llama3.2:1b vía Ollama |
| Búsqueda web | DuckDuckGo Search (site-specific) |
| Orquestación | LangChain AgentExecutor |
| Memoria | ConversationBufferMemory / BufferWindowMemory |
| Interfaz | Gradio `gr.Blocks` con CSS personalizado |
| Publicación | Ngrok vía pyngrok |

## Instrucciones de ejecución

1. Abrir `WebSearchRAG.ipynb` en Google Colab
2. Ir a **Entorno de ejecución → Cambiar tipo de entorno de ejecución** y seleccionar **GPU T4**
3. Agregar el token de Ngrok en **Secretos de Colab** con el nombre `NGROK_TOKEN`
4. (Opcional) Modificar las variables `FUENTE_A` y `FUENTE_B` para cambiar los sitios consultados
5. Ejecutar todas las celdas de arriba a abajo con **Entorno de ejecución → Ejecutar todo**
6. Al final, copiar la URL pública de Ngrok y compartirla con la clase
