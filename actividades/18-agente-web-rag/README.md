# 🎓 Actividad 18: Agente de búsqueda web + RAG

## Resumen

Actividad práctica que une los dos patrones más usados con LLMs: **agentes con herramientas** y **RAG**. Primero, un agente de LangChain con la herramienta `buscar_en_internet` (DuckDuckGo) decide qué buscar, lee los resultados y devuelve una respuesta citando las URLs. Después, esas mismas páginas se **descargan completas** con `WebBaseLoader`, se dividen en fragmentos, se convierten en vectores con `nomic-embed-text` y se indexan en FAISS. Así se pueden hacer preguntas de seguimiento que se responden **solo con el contenido real de esas webs**. La actividad termina con una app Gradio de dos pestañas (investigar / preguntar a las webs) publicada con Ngrok.

Amplía la [Actividad 02](../02-web-search-rag/), donde se buscaba en la web pero sin indexar las páginas, y la [Actividad 01](../01-ollama-rag/), donde el RAG usaba documentos fijos.

-----

## 📋 Ficha Técnica

|Campo                |Detalle                            |
|---------------------|-----------------------------------|
|**Archivo**          |`AgenteWebRAG.ipynb`               |
|**Entorno**          |Google Colab con GPU **T4**        |
|**Duración estimada**|90 – 120 minutos                   |
|**Nivel**            |Intermedio – Avanzado              |
|**Partes**           |11 partes + limpieza + rúbrica     |

-----

## 🎯 Objetivos de Aprendizaje

1. Crear una herramienta de LangChain con `@tool` y entender qué información de ella ve el LLM
1. Usar *tool calling* (`bind_tools`, `tool_calls`, `ToolMessage`) e implementar a mano el bucle Razonar → Actuar → Observar
1. Descargar páginas web y convertirlas en `Document` con `WebBaseLoader`, tolerando webs caídas
1. Dividir texto en fragmentos, generar embeddings y construir un índice FAISS
1. Construir una cadena RAG con LCEL que cite fuentes y no invente cuando falta información
1. Comparar la respuesta del agente (basada en *snippets*) con la del RAG (basada en el texto completo)
1. Publicar la app con Gradio y Ngrok

-----

## ✅ Prerrequisitos

- Haber completado la [Actividad 01](../01-ollama-rag/) (Ollama + RAG) y, recomendable, la [Actividad 02](../02-web-search-rag/)
- Python básico (ver [Actividad 13](../13-python-colab-basico/))
- Cuenta de Google (para Colab) con GPU T4 disponible
- Cuenta gratuita en [ngrok.com](https://ngrok.com) y su token guardado en Colab Secrets como `NGROK_TOKEN` (con *Notebook access* activado)

-----

## 🛠️ Stack Tecnológico

|Componente          |Herramienta                         |Detalle                                                  |
|--------------------|------------------------------------|---------------------------------------------------------|
|Entorno             |Google Colab                        |GPU T4                                                   |
|LLM                 |`qwen3:4b` vía Ollama               |Con *tool calling*; `reasoning=False` para ir más rápido |
|Embeddings          |`nomic-embed-text` vía Ollama       |Vectores de 768 dimensiones                              |
|Búsqueda web        |`ddgs` (DuckDuckGo)                 |Sin API key                                              |
|Agente              |LangChain `bind_tools` + bucle propio|Equivalente a `create_agent` de LangChain 1.x           |
|Carga de webs       |`WebBaseLoader` + BeautifulSoup     |Una URL cada vez, con *timeout* y control de errores     |
|Índice vectorial    |FAISS (`faiss-cpu`)                 |`chunk_size=1000`, `chunk_overlap=150`, `k=4`            |
|Cadena RAG          |LCEL (`|`)                          |Prompt que obliga a citar URLs                           |
|Interfaz            |Gradio 5.x (`gr.Blocks`)            |Dos pestañas · versión fijada a `>=5,<6`                 |
|Publicación         |Ngrok vía pyngrok                   |Token desde Colab Secrets                                |

-----

## 🗺️ Estructura de la Actividad

|Parte|Contenido                                                                              |
|-----|---------------------------------------------------------------------------------------|
|1    |GPU, instalación de Ollama y librerías, servidor, modelos y configuración              |
|2    |**Herramienta:** `buscar_en_internet` y prueba sin LLM                                  |
|3    |**Agente:** LLM solo, `bind_tools`, bucle del agente y ejecución                        |
|4    |**Cargar webs:** `WebBaseLoader` sobre las URLs encontradas                             |
|5    |**Indexar:** fragmentos, prueba de embeddings, FAISS y retriever                        |
|6    |**Cadena RAG:** prompt, LCEL, pregunta de seguimiento y pregunta fuera de tema          |
|7    |Pipeline completo `investigar()`                                                        |
|8    |Interfaz Gradio con dos pestañas                                                        |
|9    |Reflexión (5 preguntas)                                                                 |
|10   |Retos: búsqueda por sitio, RAG como herramienta del agente, persistir el índice         |
|11   |Publicación con Ngrok (5 celdas) + limpieza + rúbrica                                   |

```
  Pregunta ─► Agente (qwen3:4b + buscar_en_internet) ─► respuesta + URLs
                                                              │
       WebBaseLoader ─► fragmentos ─► nomic-embed-text ─► FAISS
                                                              │
  Pregunta de seguimiento ─► retriever ─► prompt ─► LLM ─► respuesta con fuentes
```

-----

## ▶️ Instrucciones de Ejecución

1. Abre `AgenteWebRAG.ipynb` en [Google Colab](https://colab.research.google.com) (*Archivo → Subir cuaderno*, o desde GitHub)
1. Activa la GPU: *Entorno de ejecución → Cambiar tipo de entorno → T4 GPU*
1. Ejecuta las celdas **de arriba a abajo**, una por una, leyendo los comentarios. La instalación y la descarga de modelos tardan 3-6 minutos
1. En la celda 3.4 cambia `PREGUNTA` por un tema de tu interés: esa búsqueda es la base del RAG
1. Compara la respuesta del agente (celda 3.4) con la del RAG (celda 6.3) y comprueba la pregunta fuera de tema (celda 6.4)
1. En la Parte 8 prueba la pestaña 1 y después pregunta en la pestaña 2
1. Responde la reflexión (Parte 9), intenta al menos un reto (Parte 10) y publica con Ngrok (Parte 11). Ejecuta la celda de limpieza al terminar

-----

## ⚠️ Solución de Problemas

|Problema                                              |Solución                                                                       |
|------------------------------------------------------|-------------------------------------------------------------------------------|
|`Error en la búsqueda: ... ratelimit`                 |DuckDuckGo limita las peticiones seguidas: espera 1 minuto y repite            |
|`tool_calls` vacío en la celda 3.2                    |El modelo decidió no buscar: repite la celda. Si persiste, usa `qwen3:8b` o `llama3.1:8b`|
|`does not support tools`                              |El modelo elegido no tiene *tool calling*: vuelve a `qwen3:4b` en la celda 1.6 |
|`⚠️ No se pudo cargar ...` en la celda 4.2            |Normal: algunas webs bloquean descargas automáticas. Si fallan todas, cambia la pregunta|
|Respuestas muy lentas                                 |Comprueba la GPU (celda 1.1) y que `ollama ps` muestre GPU                     |
|`❌ Falta el token` en la celda 11.2                   |Guarda el token en Secrets como `NGROK_TOKEN` y activa *Notebook access*       |

-----

## 📎 Recursos

- [LangChain — Tool calling](https://python.langchain.com/docs/concepts/tool_calling/)
- [LangChain — WebBaseLoader](https://python.langchain.com/docs/integrations/document_loaders/web_base/)
- [LangChain — Build a RAG app](https://python.langchain.com/docs/tutorials/rag/)
- [Ollama — modelos con tool calling](https://ollama.com/search?c=tools)
- [FAISS](https://github.com/facebookresearch/faiss)
