# Actividad 09 — Servidor MCP de Búsqueda de Hoteles

## Objetivo de aprendizaje

Construir un servidor MCP (Model Context Protocol de Anthropic) con herramientas de búsqueda real de hoteles y destinos, y un cliente Gradio con tres agentes especializados que tienen acceso controlado a diferentes subconjuntos de herramientas.

Al finalizar el estudiante sabrá:
- Qué es MCP y cómo se diferencia de las herramientas ad-hoc de LangChain
- Definir Tools con JSON Schema usando el decorador `@mcp.tool()`
- Ejecutar un servidor MCP como proceso independiente con transporte SSE
- Conectarse al servidor desde un cliente Python con `ClientSession` y `sse_client`
- Implementar control de acceso por agente: cada cliente solo puede llamar sus tools asignadas
- Construir una interfaz Gradio multi-tab donde cada pestaña es un agente con perfil diferente

## Prerrequisitos

- Actividad 08 (agente LangChain con DuckDuckGo — contexto de búsqueda de hoteles)
- Token de Ngrok en Colab Secrets como `NGROK_TOKEN`
- GPU T4 activa en Colab (no necesaria para el core de la actividad; requerida para el reto opcional con Ollama)

## Stack tecnológico

| Rol | Herramienta |
|-----|-------------|
| Entorno | Google Colab (GPU T4) |
| Protocolo agente-herramienta | MCP — `mcp` (Anthropic) |
| Servidor MCP | `FastMCP` con transporte SSE (uvicorn) |
| Cliente MCP | `ClientSession` + `sse_client` |
| Búsqueda web | DuckDuckGo (`duckduckgo-search`) |
| Interfaz | Gradio `gr.Blocks` con 3 pestañas |
| Publicación | Ngrok vía pyngrok |

## Arquitectura

```
  Gradio UI (3 pestañas)
       │ control de acceso por agente
       ▼
  MCP Client (Python) + nest_asyncio
       │ HTTP / SSE
       ▼
  MCP Server — proceso independiente, puerto 8000
  ├── buscar_hoteles_espana(ciudad, presupuesto)   ──┐
  ├── buscar_destinos_espana(tipo)                  ──┤
  ├── buscar_hoteles_europa(ciudad, pais, presup.)  ──┤── DuckDuckGo
  ├── buscar_destinos_europa(pais, tipo)             ──┤
  ├── buscar_hoteles_global(ciudad, pais, presup.)  ──┤
  └── buscar_destinos_global(region, tipo)           ──┘
```

## Control de acceso por agente

| Agente | Tools disponibles | Alcance |
|--------|------------------|---------|
| 🇪🇸 España | `buscar_hoteles_espana`, `buscar_destinos_espana` | Solo España |
| 🌍 Europa | `buscar_hoteles_europa`, `buscar_destinos_europa` | Cualquier país europeo |
| 🌐 Global | `buscar_hoteles_global`, `buscar_destinos_global` | Sin restricción |

## Estructura del notebook

```
mcp_hoteles.ipynb
│
├── Parte 1  — Instalación de dependencias (mcp, duckduckgo-search, gradio, pyngrok, uvicorn)
├── Parte 2  — ¿Qué es MCP? diagrama servidor/cliente, transporte SSE vs stdio
├── Parte 3  — Escribir el servidor (%%writefile mcp_server.py, 6 tools con @mcp.tool())
├── Parte 4  — Arrancar el servidor como subprocess + health check de puerto
├── Parte 5  — Probar cada tool directamente (list_tools + call_tool por separado)
├── Parte 6  — Cliente MCP con control de acceso (AGENT_TOOLS + ejecutar_con_control)
├── Parte 7  — Verificar restricciones: acceso permitido, denegado y de Europa
├── Parte 8  — Interfaz Gradio con 3 pestañas (una por agente)
├── Parte 9  — Reflexión (4 preguntas)
├── Parte 10 — Retos opcionales (agente Latam, Ollama como decisor, panel de auditoría)
├── Parte 11 — Ngrok (5 celdas estándar)
└── Limpieza de recursos + Rúbrica de evaluación
```

## Instrucciones de ejecución

1. Descarga `mcp_hoteles.ipynb`
2. Ve a [colab.research.google.com](https://colab.research.google.com)
3. **Archivo → Subir notebook** y selecciona el archivo
4. Añade tu token de Ngrok en **Secretos** con el nombre `NGROK_TOKEN`
5. Ejecuta las celdas **de arriba a abajo** con `Shift + Enter`
6. En la Parte 11 obtendrás la URL pública de los tres agentes

> El servidor MCP corre en un proceso separado iniciado en la Parte 4. Si reinicias el kernel deberás volver a ejecutar esa celda antes de usar la interfaz.

## Diferencia clave respecto a la Actividad 08

| Actividad 08 (LangChain) | Actividad 09 (MCP) |
|--------------------------|---------------------|
| Herramientas acopladas al agente | Herramientas en servidor independiente y reutilizable |
| Sin contrato formal de tipos | JSON Schema define entradas y salidas |
| Un solo cliente con acceso total | Múltiples clientes con acceso controlado |
| Difícil de consumir desde otros sistemas | Cualquier cliente MCP puede conectarse |
