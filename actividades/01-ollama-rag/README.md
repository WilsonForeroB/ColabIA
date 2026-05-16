# Actividad 01 — LLMs Locales en la Nube: Ollama + RAG con LangChain

## Objetivo de aprendizaje

Aprender a levantar un servidor de LLMs en Google Colab (GPU gratuita), exponerlo al exterior con Ngrok, y construir un sistema RAG (Retrieval-Augmented Generation) con LangChain que responda preguntas sobre documentos propios.

Al finalizar el estudiante sabrá:
- Qué es RAG y por qué mejora las respuestas de un LLM
- Cómo instalar y usar Ollama en un entorno efímero como Colab
- Cómo indexar documentos y hacer búsqueda semántica con FAISS
- Cómo orquestar un pipeline RAG completo con LangChain Expression Language (LCEL)

## Prerrequisitos

- Cuenta de Google (para usar Colab con GPU T4 gratuita)
- Token de Ngrok (gratis en [ngrok.com](https://ngrok.com)) guardado en Colab Secrets como `NGROK_TOKEN`
- Sin conocimientos previos de LLMs requeridos

## Stack tecnológico

| Rol | Herramienta |
|-----|-------------|
| Entorno | Google Colab (GPU T4) |
| Servidor LLM | Ollama |
| Modelo de texto | qwen3:4b (2.5 GB) |
| Embeddings | nomic-embed-text |
| Vector store | FAISS |
| Orquestación | LangChain + LCEL |
| Interfaz | Gradio `gr.Blocks` |
| Publicación | Ngrok vía pyngrok |

## Instrucciones de ejecución

1. Abrir `OllamaColab.ipynb` en Google Colab
2. Ir a **Entorno de ejecución → Cambiar tipo de entorno de ejecución** y seleccionar **GPU T4**
3. Agregar el token de Ngrok en **Secretos de Colab** con el nombre `NGROK_TOKEN`
4. Ejecutar todas las celdas de arriba a abajo con **Entorno de ejecución → Ejecutar todo**
5. Al final, copiar la URL pública de Ngrok y compartirla con la clase
