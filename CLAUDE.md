# ColabIA — Guía para Claude

## Descripción del proyecto

Repositorio de actividades para un **curso de Inteligencia Artificial** usando Google Colab y Claude Desktop. Las actividades se entregan como notebooks `.ipynb` listos para ejecutar celda a celda.

## Archivos del proyecto

| Archivo | Descripción |
|---|---|
| `OllamaColab.ipynb` | Notebook para correr modelos locales con Ollama en Colab |
| `WebSearchRAG.ipynb` | Notebook de RAG con búsqueda web |

## Principio de diseño

**El estudiante solo ejecuta. El notebook explica.**

Todas las actividades siguen la filosofía documentada en `.claude/commands/diseno-actividades.md`. Antes de crear o modificar cualquier notebook, consulta ese documento.

## Stack tecnológico

- **Entorno:** Google Colab (GPU T4)
- **Modelos de texto:** Ollama + TinyLlama
- **Modelos de imagen:** HuggingFace diffusers (SD v1.4, float16)
- **Interfaz:** Gradio (`gr.Blocks`)
- **Publicación:** Ngrok vía pyngrok (token desde Colab Secrets)

## Skills disponibles

- `/diseno-actividades` — filosofía y checklist para diseñar nuevas actividades
