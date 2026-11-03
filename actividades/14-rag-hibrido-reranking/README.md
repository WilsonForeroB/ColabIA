# 🔎 Actividad: RAG Híbrido con Reranking

## Resumen

Construye, paso a paso, un asistente que responde preguntas sobre un documento (la guía del huésped de un hotel ficticio) usando **RAG híbrido**: búsqueda por significado (embeddings `bge-m3` + similitud coseno) y búsqueda por palabras clave (**BM25**), fusionadas con **Reciprocal Rank Fusion (RRF)**, reordenadas con el reranker **`bge-reranker-v2-m3`** y respondidas por **`llama3.2`** usando solo ese contexto. Termina con una interfaz Gradio para experimentar con tres tipos de pregunta y distintos tamaños de fragmento, publicada con Ngrok.

-----

## 📋 Ficha Técnica

|Campo                |Detalle                               |
|---------------------|--------------------------------------|
|**Archivo**          |`RAGHibridoReranking.ipynb`           |
|**Entorno**          |Google Colab con GPU **T4**           |
|**Duración estimada**|90 – 120 minutos                      |
|**Nivel**            |Avanzado                              |
|**Partes**           |9 partes + limpieza + rúbrica         |

-----

## 🎯 Objetivos de Aprendizaje

1. Instalar Ollama en Colab y servir un modelo de embeddings (`bge-m3`) y un LLM (`llama3.2`)
1. Dividir un texto en fragmentos con solape y entender el compromiso del tamaño de fragmento
1. Implementar la búsqueda semántica con similitud coseno sobre embeddings
1. Implementar BM25 desde cero y entender frecuencia, IDF y normalización por longitud
1. Fusionar rankings heterogéneos con RRF y reordenarlos con un cross-encoder (reranker)
1. Forzar al LLM a responder solo con el contexto recuperado y a reconocer cuándo no sabe
1. Evaluar experimentalmente tres tipos de pregunta (literal, paráfrasis, síntesis) con tres tamaños de fragmento
1. Construir una interfaz con `gr.Blocks` y publicarla con Ngrok

-----

## ✅ Prerrequisitos

- Haber hecho la actividad [03 — Embeddings, tokens y similitud](../03-embeddings-tokens-similitud/) (recomendado) o conocer qué es un embedding
- Python básico: funciones, listas, diccionarios (ver [actividad 13](../13-python-colab-basico/))
- Cuenta de Google (para Colab) con GPU T4 disponible
- Cuenta gratuita en [ngrok.com](https://ngrok.com) y su token guardado en Colab Secrets como `NGROK_TOKEN` (con *Notebook access* activado)

-----

## 🛠️ Stack Tecnológico

|Componente        |Herramienta                                   |Detalle                                          |
|------------------|----------------------------------------------|-------------------------------------------------|
|Entorno           |Google Colab                                  |GPU T4                                           |
|Embeddings        |Ollama + `bge-m3`                             |1024 dimensiones, multilingüe (~1.2 GB)          |
|Búsqueda léxica   |BM25 implementado en Python                   |Sin librerías externas, para ver la fórmula      |
|Fusión            |Reciprocal Rank Fusion                        |`k = 60`                                         |
|Reranker          |`BAAI/bge-reranker-v2-m3` (sentence-transformers)|Cross-encoder en GPU con float16 (~2.2 GB)     |
|LLM generador     |Ollama + `llama3.2` (3B)                      |`temperature = 0.1` (~2 GB)                      |
|Interfaz          |Gradio 5.x (`gr.Blocks`)                      |Versión fijada a `>=5,<6`                        |
|Publicación       |Ngrok vía pyngrok                             |Token desde Colab Secrets                        |

-----

## 🗺️ Estructura de la Actividad

|Parte|Contenido                                                                           |
|-----|------------------------------------------------------------------------------------|
|1    |Preparar Colab: GPU, Ollama, librerías, descarga de `bge-m3` y `llama3.2`           |
|2    |Documento, fragmentación con solape (probada con un ejemplo) y vectorización        |
|3    |Búsqueda semántica (coseno), tokenizador, BM25 desde cero y comparación de ambas    |
|4    |Fusión RRF, carga y prueba del reranker, pipeline de recuperación híbrida           |
|5    |Prompt con reglas de "solo contexto", llamada a `llama3.2`, prueba con pregunta sin respuesta|
|6    |Experimento 3 tipos de pregunta × 3 tamaños (40/120/300 palabras) + interfaz Gradio |
|7    |Reflexión (5 preguntas)                                                             |
|8    |Retos opcionales: ablación de piezas, fragmentos por sección, documento propio      |
|9    |Publicación con Ngrok (5 celdas) + limpieza + rúbrica                               |

```
Pregunta ─┬─► bge-m3 + coseno ─┐
          └─► BM25 ────────────┴─► RRF ─► bge-reranker-v2-m3 ─► top_k ─► llama3.2 ─► Respuesta
```

-----

## ▶️ Instrucciones de Ejecución

1. Abre `RAGHibridoReranking.ipynb` en [Google Colab](https://colab.research.google.com) (*Archivo → Subir cuaderno*, o desde GitHub)
1. Activa la GPU: *Entorno de ejecución → Cambiar tipo de entorno → T4 GPU*
1. Ejecuta las celdas **de arriba a abajo**, una por una, leyendo los comentarios. La Parte 1 tarda 5-8 minutos (descarga ~4 GB de modelos) y la carga del reranker (celda 4.3) 1-2 minutos más
1. En la Parte 6, analiza la tabla del experimento y luego usa la interfaz: prueba los tres ejemplos moviendo el slider de tamaño de fragmento y revisa las pestañas de cada etapa
1. Responde las preguntas de la Parte 7 en su celda markdown e intenta al menos un reto de la Parte 8
1. Publica la app con Ngrok (Parte 9), comparte la URL y ejecuta la celda de limpieza al terminar

### Tres tipos de pregunta del experimento

|Tipo         |Pregunta                                                            |Qué pone a prueba                       |
|-------------|--------------------------------------------------------------------|----------------------------------------|
|🔤 Literal    |¿Cuál es la contraseña del WiFi?                                    |Coincidencia exacta de términos (BM25)  |
|💭 Paráfrasis |Me dejé el cargador del móvil en el cuarto al irme, ¿cómo lo recupero?|Comprensión del significado (embeddings)|
|🧩 Síntesis   |¿Qué opciones hay para comer en el hotel y en qué horarios?         |Reunir información repartida en varias secciones|

-----

## ⚠️ Solución de Problemas

|Problema                                      |Solución                                                                  |
|----------------------------------------------|--------------------------------------------------------------------------|
|`nvidia-smi` falla o el reranker carga en CPU |Activa la GPU T4 y reinicia la sesión; ejecuta desde la celda 1.1         |
|`❌ Ollama no arrancó`                         |*Entorno de ejecución → Reiniciar sesión* y vuelve a la celda 1.2         |
|Error al descargar `bge-m3` o `llama3.2`      |Repite la celda de descarga; las descargas grandes a veces se cortan      |
|`ConnectionError` al vectorizar o preguntar   |El servidor Ollama se detuvo: vuelve a ejecutar la celda 1.4              |
|`CUDA out of memory`                          |Reinicia la sesión; no cargues el reranker más de una vez                 |
|El modelo inventa datos                       |Baja `top_k` o revisa en la pestaña de fragmentos si llegó el contexto correcto|
|`❌ Falta el token` en la celda 9.2            |Guarda el token en Secrets como `NGROK_TOKEN` y activa *Notebook access*  |

-----

## 📎 Recursos

- [bge-m3 en Ollama](https://ollama.com/library/bge-m3) · [llama3.2 en Ollama](https://ollama.com/library/llama3.2)
- [BAAI/bge-reranker-v2-m3 en HuggingFace](https://huggingface.co/BAAI/bge-reranker-v2-m3)
- [Reciprocal Rank Fusion (Cormack et al., 2009)](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)
- [The Probabilistic Relevance Framework: BM25 and Beyond](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
- [Documentación de Gradio](https://www.gradio.app/docs)
