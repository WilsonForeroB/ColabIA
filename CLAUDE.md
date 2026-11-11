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
| `actividades/12-gradio-para-frontend/` | Gradio para perfiles frontend: componentes, layout, eventos y CSS |
| `actividades/13-python-colab-basico/` | Nivelación: Colab y Python desde cero (recomendada antes de las demás) |
| `actividades/14-rag-hibrido-reranking/` | RAG híbrido: bge-m3 + BM25, fusión RRF, reranker bge-reranker-v2-m3 y llama3.2 |
| `actividades/15-modelos-multimodales/` | Multimodal: tokenizador visual (parches CLIP ViT), gemma3 con imágenes, Whisper y vídeo por fotogramas clave |
| `actividades/16-cuantizacion-vllm/` | Cuantización con vLLM: bitsandbytes, AWQ del Hub, W8A8 (SmoothQuant + GPTQ) y W4A16 (GPTQ) con LLM Compressor; arena Gradio original vs cuantizado |
| `actividades/17-fine-tuning-qlora/` | Fine-tuning QLoRA con TRL + PEFT: clasificador de tickets a JSON, evaluación antes/después, adaptador y fusión |

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
