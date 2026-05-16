# 🤖 Actividad: Interfaz Multimodal con Ollama y Gradio

## Resumen

Actividad práctica donde el estudiante levanta dos modelos de IA dentro de Google Colab — uno de generación de texto y otro de generación de imágenes — y construye una interfaz web unificada con Gradio que permite elegir entre ambos. Al final publica la app en Internet usando Ngrok para compartirla con la clase.

-----

## 📋 Ficha Técnica

|Campo                |Detalle                            |
|---------------------|-----------------------------------|
|**Archivo**          |`Actividad_LLM_Ollama_Gradio.ipynb`|
|**Entorno**          |Google Colab con GPU T4            |
|**Duración estimada**|90 – 120 minutos                   |
|**Nivel**            |Intermedio                         |
|**Partes**           |7 partes + limpieza + rúbrica      |

-----

## 🎯 Objetivos de Aprendizaje

1. Levantar modelos LLM localmente usando Ollama dentro de Google Colab
1. Distinguir entre un modelo de generación de texto y uno de generación de imágenes
1. Construir una interfaz interactiva con Gradio que seleccione y use ambos modelos
1. Integrar llamadas a APIs REST con interfaces de usuario en Python
1. Publicar una aplicación web en Internet usando un túnel Ngrok

-----

## 🗺️ Estructura de la Actividad

### PARTE 1 — Instalación del Entorno

Instala todas las dependencias de Python necesarias y Ollama en el sistema operativo.

**Celdas:**

- Celda 1: `pip install gradio requests pillow httpx`
- Celda 2: Instalar Ollama con `curl -fsSL https://ollama.com/install.sh | sh`

-----

### PARTE 2 — Modelo de Texto con Ollama

Levanta el servidor Ollama como proceso en background, descarga TinyLlama y prueba que responde correctamente antes de construir la interfaz.

**Modelo:** TinyLlama (1.1B parámetros, ~637 MB)

**Celdas:**

- Celda 3: Iniciar servidor Ollama con `subprocess.Popen` en background, verificar con `requests.get`
- Celda 4: Descargar modelo con `ollama pull tinyllama`
- Celda 5: Definir `consultar_modelo_texto()` — hace POST a `localhost:11434/api/generate` con `stream: False` — y prueba con un prompt de ejemplo

-----

### PARTE 3 — Modelo de Generación de Imágenes

Instala `diffusers`, carga Stable Diffusion en GPU con float16 y prueba generando una imagen antes de integrar.

**Modelo:** Stable Diffusion v1.4 (CompVis, ~4 GB, HuggingFace)

**Celdas:**

- Celda 6: `pip install diffusers transformers accelerate torch torchvision`
- Celda 7: Cargar `StableDiffusionPipeline.from_pretrained()` con `torch_dtype=float16`, mover a GPU con `.to(device)`, activar `enable_attention_slicing()`
- Celda 8: Definir `generar_imagen()` — usa `torch.autocast`, `num_inference_steps`, `guidance_scale=7.5` — y prueba con un prompt de ejemplo

-----

### PARTE 4 — Interfaz Gradio Unificada

Construye la interfaz completa con `gr.Blocks`. Incluye selector de modo, campo de prompt, salidas dinámicas (texto o imagen), ejemplos precargados y lógica de eventos.

**Celdas:**

- Celda 9: Definir `procesar_solicitud()` — función router que dirige al modelo correcto según el modo y retorna `(texto, None)` o `(None, imagen)`
- Celda 10: Construir la interfaz completa con:
  - `gr.Radio` para seleccionar el modo
  - `gr.Accordion` con `gr.Slider` para pasos de difusión
  - `gr.Textbox` para el prompt
  - `gr.Button` Generar + `gr.ClearButton` Limpiar
  - `gr.Textbox` de salida de texto (`visible=True` por defecto)
  - `gr.Image` de salida de imagen (`visible=False` por defecto)
  - `gr.Examples` con 6 prompts de ejemplo (3 texto, 3 imagen)
  - Eventos: `modo.change()`, `btn_enviar.click()`, `prompt_input.submit()`
  - `demo.launch(share=True)` como publicación temporal

-----

### PARTE 5 — Reflexión

Cuatro preguntas que el estudiante responde en una celda markdown:

1. Diferencia entre TinyLlama y Stable Diffusion (datos de entrenamiento)
1. Por qué `gr.update(visible=True/False)` en Gradio
1. Por qué Stable Diffusion funciona mejor en inglés (implicaciones de accesibilidad)
1. Ventajas de modelos locales vs APIs en la nube

-----

### PARTE 6 — Retos Opcionales

Tres retos con una celda vacía para experimentar:

- **Reto A:** Historial de conversación con `gr.Chatbot()`
- **Reto B:** Streaming de texto con `stream: True` y `yield`
- **Reto C:** Traducción automática del prompt al inglés con `deep_translator`

-----

### PARTE 7 — Publicación con Ngrok

Reemplaza el `share=True` de Gradio por un túnel Ngrok estable y compartible con toda la clase.

**Celdas:**

- Celda 11: `pip install pyngrok`
- Celda 12: Autenticar — lee token desde `userdata.get('NGROK_TOKEN')` (Colab Secrets), con fallback a variable manual y validación de placeholder
- Celda 13: `ngrok.kill()` → `ngrok.connect(7860, 'http')` → `demo.launch(server_name='0.0.0.0', share=False, server_port=7860)`
- Celda 14: Inspeccionar túneles con `ngrok.get_tunnels()`
- Celda 15: (Opcional) Dominio estático con `ngrok.connect(domain=DOMINIO_ESTATICO)`

-----

### Limpieza Final

Una celda que libera todos los recursos en orden: túnel Ngrok, interfaz Gradio, proceso Ollama, memoria GPU.

-----

## 🛠️ Stack Técnico

|Componente      |Herramienta          |Detalle                       |
|----------------|---------------------|------------------------------|
|Modelo de texto |Ollama + TinyLlama   |API REST en localhost:11434   |
|Modelo de imagen|HuggingFace diffusers|Stable Diffusion v1.4, float16|
|Interfaz        |Gradio gr.Blocks     |CSS personalizado, modo oscuro|
|Publicación     |Ngrok vía pyngrok    |Token desde Colab Secrets     |
|GPU             |NVIDIA T4 (Colab)    |CUDA con attention slicing    |

-----

## ⚠️ Requisitos Previos del Estudiante

- Cuenta de Google (para Colab)
- Cuenta gratuita en [ngrok.com](https://ngrok.com) con token generado
- Token de Ngrok guardado en Colab Secrets como `NGROK_TOKEN`
- Activar GPU T4 antes de ejecutar

-----

## 📊 Rúbrica

|Criterio                   |Excelente (5)                       |Satisfactorio (3)               |En desarrollo (1)              |
|---------------------------|------------------------------------|--------------------------------|-------------------------------|
|Instalación y configuración|Todos los modelos corren sin errores|Al menos un modelo corre        |No logra levantar ningún modelo|
|Interfaz funcional         |Gradio responde a ambos modos       |Un solo modo funciona           |La interfaz no carga           |
|Calidad de prompts         |5+ prompts variados y creativos     |3-4 prompts básicos             |Solo usa los ejemplos provistos|
|Publicación con Ngrok      |URL pública funcionando y compartida|Ngrok instalado pero con errores|No intenta la publicación      |
|Reflexión escrita          |Respuestas detalladas con ejemplos  |Respuestas incompletas          |Sin respuestas                 |
|Reto opcional              |Implementa y explica al menos uno   |Intenta uno parcialmente        |No intenta los retos           |

-----

## 📎 Entrega

El estudiante entrega:

1. El notebook `.ipynb` con todas las celdas ejecutadas
1. Las preguntas de reflexión respondidas en la celda markdown de la Parte 5
1. Una captura de pantalla de la URL de Ngrok funcionando en el navegador
