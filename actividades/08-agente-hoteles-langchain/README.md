# Actividad 08 — Agente de Búsqueda de Hoteles con LangChain

## Objetivo de aprendizaje

Construir un agente de IA con LangChain que busque hoteles en la web y recomiende la mejor opción precio-calidad dado el destino y el presupuesto del usuario.

Al finalizar el estudiante sabrá:
- Qué es el paradigma ReAct (Razonamiento + Acción) y cómo lo implementa LangChain
- Configurar un agente `ZERO_SHOT_REACT_DESCRIPTION` con herramientas de búsqueda
- Usar DuckDuckGo como fuente de búsqueda gratuita sin clave de API
- Diseñar un `system prompt` efectivo para orientar al agente hacia un dominio concreto
- Construir una interfaz Gradio con historial de conversación e inputs compuestos
- Publicar la aplicación completa vía Ngrok desde Colab

## Prerrequisitos

- Haber completado la **Actividad 00a** (servidor Ollama) o tener Ollama ya operativo
- El modelo `llama3.2:1b` descargado en Ollama (el notebook lo descarga automáticamente)
- Token de Ngrok en Colab Secrets como `NGROK_TOKEN`
- Conexión activa a GPU T4 en Colab (necesaria para ejecutar Ollama)

## Stack tecnológico

| Rol | Herramienta |
|-----|-------------|
| Entorno | Google Colab (GPU T4) |
| LLM | Ollama + llama3.2:1b |
| Framework agente | LangChain (`langchain`, `langchain-community`, `langchain-ollama`) |
| Búsqueda web | DuckDuckGo (`duckduckgo-search`, `DuckDuckGoSearchRun`) |
| Interfaz | Gradio (`gr.Blocks`) |
| Publicación | Ngrok vía pyngrok |

## Arquitectura del agente

```
Usuario (Gradio)
     │  ciudad + presupuesto + preferencias
     ▼
LangChain ReAct Agent
     │
     ├─ Razona: ¿qué buscar?
     ├─ Actúa: DuckDuckGo search
     ├─ Observa: resultados web
     └─ Razona: ¿suficiente info? → responde
     │
     ▼
Recomendación estructurada
  🏨 hotel  💰 precio  ⭐ valoración  📍 ubicación
```

## Estructura del notebook

```
agente_hoteles.ipynb
│
├── Parte 1  — Instalación de dependencias
├── Parte 2  — Arrancar Ollama + descargar llama3.2:1b
├── Parte 3  — Concepto ReAct explicado con diagrama
├── Parte 4  — Configurar DuckDuckGoSearchRun
├── Parte 5  — System prompt: rol de experto hotelero
├── Parte 6  — Crear el agente LangChain ReAct
├── Parte 7  — Función buscar_hotel (wrapper del agente)
├── Parte 8  — Interfaz Gradio con historial y ejemplos
├── Parte 9  — Reflexión (4 preguntas)
├── Parte 10 — Retos opcionales
├── Parte 11 — Ngrok: publicar la interfaz
└── Limpieza + rúbrica de evaluación
```

## Instrucciones de ejecución

1. Descarga `agente_hoteles.ipynb`
2. Ve a [colab.research.google.com](https://colab.research.google.com)
3. **Archivo → Subir notebook** y selecciona el archivo
4. Cambia el entorno de ejecución a **GPU T4** (Entorno de ejecución → Cambiar tipo de entorno de ejecución)
5. Añade tu token de Ngrok en **Secretos** de Colab con el nombre `NGROK_TOKEN`
6. Ejecuta las celdas **de arriba a abajo** con `Shift + Enter`
7. En la Parte 11 obtendrás la URL pública de tu agente

> La Parte 11 (Ngrok) es la última en ejecutarse. Todas las celdas anteriores deben completarse sin errores antes de publicar.

## Parámetros ajustables

| Parámetro | Ubicación | Valor por defecto |
|-----------|-----------|-------------------|
| `temperature` | Parte 6 | `0.1` (respuestas consistentes) |
| `max_iterations` | Parte 6 | `6` |
| `max_results` | Parte 4 | `5` resultados DuckDuckGo |
| Rango presupuesto | Parte 8 | `20–500 €` |
| Modelo Ollama | Parte 2 | `llama3.2:1b` |
