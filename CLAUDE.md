# ColabIA — Guía para Claude

## Descripción del proyecto

Repositorio de actividades para un **curso de Inteligencia Artificial** usando Google Colab y Claude Desktop. Las actividades se entregan como notebooks `.ipynb` listos para ejecutar celda a celda.

## Convención de actividades

Cada actividad vive en su propia carpeta dentro de `actividades/`:

```
actividades/
└── NN-nombre-descriptivo/
    ├── NombreNotebook.ipynb   ← notebook listo para ejecutar en Colab
    └── README.md              ← descripción de la actividad
```

- Las carpetas se numeran con prefijo de dos dígitos (`01-`, `02-`, ...)
- El `README.md` de cada actividad debe incluir: **objetivo de aprendizaje, prerrequisitos, stack tecnológico e instrucciones de ejecución**
- Nunca colocar notebooks sueltos en la raíz del repositorio

## Actividades del proyecto

| Carpeta | Descripción |
|---|---|
| `actividades/01-ollama-rag/` | LLMs locales con Ollama + RAG con LangChain |
| `actividades/02-web-search-rag/` | RAG multi-agente con búsqueda web y Gradio |
| `actividades/11-seguridad-ia-llm/` | Seguridad en IA: app React + FastAPI vulnerable y defendida |

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
- `/pull-request` — crea PRs hacia `develop` con formato Conventional Commits; pide confirmación antes de ejecutar
