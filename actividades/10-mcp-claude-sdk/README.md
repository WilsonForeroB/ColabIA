# Actividad 10 — MCP Avanzado con Ollama: Tools, Prompts, Sampling y Elicitation

## Objetivo de aprendizaje

Dominar los cuatro conceptos avanzados del **SDK oficial de MCP de Anthropic** (`mcp` package)
usando Ollama como LLM gratuito. Esta actividad va más allá de definir herramientas básicas:
explora los mecanismos que hacen de MCP un protocolo bidireccional completo.

Al finalizar el estudiante sabrá:
- Definir **MCP Tools** con `@mcp.tool()` y JSON Schema automático desde type hints
- Definir **MCP Prompts** reutilizables con `@mcp.prompt()` y argumentos parametrizados
- Implementar **Sampling**: el servidor delega una completación LLM al cliente, que la resuelve con Ollama
- Implementar **Elicitation**: el servidor solicita datos estructurados al usuario durante la ejecución de una tool
- Distinguir cuándo usar cada mecanismo según el flujo del agente

## Prerrequisitos

- Actividad 09 (servidor MCP básico con FastMCP + SSE transport + Gradio)
- Token de Ngrok en Colab Secrets como `NGROK_TOKEN`
- GPU T4 activa en Colab (necesaria para Ollama)

## Stack tecnológico

| Rol | Herramienta |
|-----|-------------|
| Entorno | Google Colab (GPU T4) |
| LLM | Ollama + llama3.2:1b (gratuito) |
| MCP SDK | `mcp>=1.9.0` — paquete oficial de Anthropic |
| Servidor MCP | FastMCP con transporte SSE (uvicorn) |
| Cliente MCP | ClientSession + sse_client |
| Interfaz | Gradio `gr.Blocks` con 4 pestañas |
| Publicación | Ngrok vía pyngrok |

## Los cuatro conceptos MCP de esta actividad

| Concepto | Dirección | Quién actúa | Para qué |
|----------|-----------|-------------|----------|
| **Tools** | Cliente → Servidor | El servidor ejecuta funciones | Realizar acciones concretas |
| **Prompts** | Cliente → Servidor | El servidor devuelve plantillas | Configurar el comportamiento del LLM |
| **Sampling** | Servidor → Cliente | El cliente genera texto con su LLM | El servidor necesita razonamiento IA |
| **Elicitation** | Servidor → Cliente → Usuario | El usuario rellena un formulario | El servidor necesita datos adicionales |

## Arquitectura

```
  Gradio UI (4 pestañas)
       │
       ▼
  MCP Client (Python) + Ollama sampling_callback
       │ HTTP / SSE                    │
       ▼                               │ Sampling: Ollama HTTP
  MCP Server — puerto 8000             │ (cuando el servidor lo pide)
  ├── buscar_receta(nombre, personas)  ─── Tool básica
  ├── calcular_calorias(plato, gramos) ─── Tool básica
  ├── sugerir_maridaje(plato)          ─── Tool básica
  ├── analizar_receta_con_ia(nombre)   ─── Tool con SAMPLING
  ├── adaptar_receta(nombre)           ─── Tool con ELICITATION
  ├── prompt_chef_experto(cocina)      ─── Prompt
  └── prompt_adaptacion_dieta(dieta)  ─── Prompt
```

## Estructura del notebook

```
McpClaudeSdk.ipynb
│
├── Parte 1  — Instalación: Ollama + GPU + paquete mcp + imports
├── Parte 2  — Los cuatro conceptos MCP (markdown + diagramas)
├── Parte 3  — Servidor v1: 3 tools básicas + 2 prompts (%%writefile + arranque)
├── Parte 4  — Verificar tools y prompts (list_tools, call_tool, list_prompts, get_prompt)
├── Parte 5  — Sampling: añadir analizar_receta_con_ia al servidor (%%writefile)
├── Parte 6  — Elicitation: añadir adaptar_receta al servidor (%%writefile final)
├── Parte 7  — Interfaz Gradio completa (4 pestañas: Tools, Sampling, Elicitation, Prompts)
├── Parte 8  — Reflexión (5 preguntas)
├── Parte 9  — Retos opcionales (3 retos con celda vacía)
├── Parte 10 — Ngrok (5 celdas estándar)
└── Limpieza de recursos + Rúbrica de evaluación
```

## Instrucciones de ejecución

1. Descarga `McpClaudeSdk.ipynb`
2. Ve a [colab.research.google.com](https://colab.research.google.com)
3. **Archivo → Subir notebook** y selecciona el archivo
4. **Entorno de ejecución → Cambiar tipo → GPU T4**
5. Añade tu token de Ngrok en **Secretos** con el nombre `NGROK_TOKEN`
6. Ejecuta las celdas **de arriba a abajo** con `Shift + Enter`
7. En la Parte 10 obtendrás la URL pública con las 4 pestañas

> **Importante:** Cada vez que se reescribe `mcp_server.py` (Partes 5 y 6),
> el servidor anterior se termina y se arranca el nuevo. Si reinicias el kernel,
> debes ejecutar desde la Parte 1.

## Diferencia clave respecto a la Actividad 09

| Actividad 09 | Actividad 10 |
|---|---|
| Tools básicas con @mcp.tool() | Tools + Sampling + Elicitation |
| Sin Prompts MCP | Prompts parametrizados con @mcp.prompt() |
| El cliente solo invoca tools | El servidor también puede pedir al cliente |
| Comunicación unidireccional (cliente→servidor) | Bidireccional (cliente⇄servidor) |
