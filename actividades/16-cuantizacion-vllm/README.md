# 🗜️ Actividad: Cuantización de LLMs con vLLM

## Resumen

Actividad para entender y practicar la **cuantización de modelos de lenguaje**: guardar los pesos con menos bits para que el modelo ocupe menos memoria y, según la GPU, vaya más rápido. Primero se abre la caja negra: se calcula cuánto ocupa un modelo en cada formato y se cuantiza un grupo de pesos "a mano" para ver qué hacen la escala, el redondeo y los *outliers*. Después se sirve `Qwen2.5-1.5B-Instruct` con **vLLM** como línea base y se comparan cuatro alternativas: cuantización **al vuelo** con bitsandbytes, un modelo **AWQ ya publicado** en el Hub y dos modelos creados por el estudiante con **LLM Compressor** (**W8A8 INT8** con SmoothQuant + GPTQ y **W4A16 INT4** con GPTQ). Termina con una *arena* en Gradio que enfrenta el modelo original al cuantizado, publicada con Ngrok.

Continúa la parte de **QLoRA** de la sesión de Fine Tuning ("QLoRA = LoRA + comprimir W a 4 bits").

-----

## 📋 Ficha Técnica

|Campo                |Detalle                            |
|---------------------|-----------------------------------|
|**Archivo**          |`CuantizacionVLLM.ipynb`           |
|**Entorno**          |Google Colab con GPU **T4**        |
|**Duración estimada**|110 – 130 minutos                  |
|**Nivel**            |Avanzado                           |
|**Partes**           |11 partes + limpieza + rúbrica     |

-----

## 🎯 Objetivos de Aprendizaje

1. Calcular la memoria de un modelo según su formato (FP32, FP16, INT8, INT4)
1. Explicar qué hace la cuantización con un peso (escala, redondeo y error) y por qué los *outliers* la complican
1. Distinguir **W4A16** (solo pesos) de **W8A8** (pesos y activaciones) y saber cuándo conviene cada uno
1. Servir un modelo con vLLM y medir VRAM, velocidad y calidad de forma reproducible
1. Cuantizar sin pasos previos: al vuelo con bitsandbytes y con modelos ya cuantizados del Hub
1. Crear modelos cuantizados con LLM Compressor (SmoothQuant + GPTQ y GPTQ) usando datos de calibración
1. Relacionar los resultados con el hardware: qué formatos acelera una T4 y cuáles necesitan L4/H100
1. Servir dos modelos a la vez con `vllm serve` (API compatible con OpenAI) y compararlos en una app Gradio publicada con Ngrok

-----

## ✅ Prerrequisitos

- Haber hecho la actividad [00 — Servidor Colab](../00-servidor-colab/) (recomendado, la parte 00b de vLLM)
- Conceptos de la sesión de Fine Tuning: pesos de una red, LoRA y QLoRA
- Python básico (ver [actividad 13](../13-python-colab-basico/))
- Cuenta de Google (para Colab) con GPU T4 disponible
- Cuenta gratuita en [ngrok.com](https://ngrok.com) y su token guardado en Colab Secrets como `NGROK_TOKEN` (con *Notebook access* activado)

-----

## 🛠️ Stack Tecnológico

|Componente            |Herramienta                              |Detalle                                                     |
|----------------------|-----------------------------------------|------------------------------------------------------------|
|Entorno               |Google Colab                             |GPU T4 (compute capability 7.5)                             |
|Modelo                |`Qwen/Qwen2.5-1.5B-Instruct`             |~3 GB en FP16 · alternativa rápida: `Qwen2.5-0.5B-Instruct` |
|Inferencia            |vLLM                                     |Script de benchmark en un proceso aparte y `vllm serve`     |
|Cuantización          |LLM Compressor (`llmcompressor`)         |SmoothQuant + GPTQ (W8A8) y GPTQ (W4A16), formato `compressed-tensors`|
|Cuantización al vuelo |bitsandbytes                             |NF4, el formato de QLoRA                                    |
|Modelo pre-cuantizado |`Qwen/Qwen2.5-1.5B-Instruct-AWQ`         |AWQ INT4 oficial de Qwen                                    |
|Calibración           |`HuggingFaceH4/ultrachat_200k`           |128 conversaciones de 512 tokens                            |
|Interfaz              |Gradio 5.x (`gr.Blocks`)                 |Arena original vs cuantizado · versión fijada a `>=5,<6`    |
|Publicación           |Ngrok vía pyngrok                        |Token desde Colab Secrets                                   |

-----

## 🗺️ Estructura de la Actividad

|Parte|Contenido                                                                                   |
|-----|--------------------------------------------------------------------------------------------|
|1    |GPU, instalación de vLLM + LLM Compressor, Gradio/pyngrok, versiones y configuración       |
|2    |**Conceptos con código:** memoria por formato, cuantización INT4 a mano y efecto de los outliers|
|3    |**Línea base:** script de benchmark, función `medir()` y modelo original en FP16            |
|4    |**Vía rápida:** bitsandbytes al vuelo y AWQ del Hub                                         |
|5    |**W8A8 INT8:** datos de calibración, receta SmoothQuant + GPTQ, `oneshot`, guardar y medir  |
|6    |**W4A16 INT4:** receta GPTQ, `oneshot`, guardar y medir                                     |
|7    |Tabla comparativa y gráfico memoria/velocidad                                               |
|8    |Dos servidores `vllm serve` a la vez y arena Gradio                                         |
|9    |Reflexión (5 preguntas)                                                                     |
|10   |Retos: AWQ propio, calibración en español, FP8 dinámico (L4/H100)                           |
|11   |Publicación con Ngrok (5 celdas) + limpieza + rúbrica                                       |

```
  Original FP16 ──► bitsandbytes (al vuelo) ─┐
               ──► AWQ del Hub ──────────────┤
               ──► LLM Compressor W8A8 ──────┼──► medir() ──► tabla ──► arena Gradio ──► Ngrok
               ──► LLM Compressor W4A16 ─────┘
```

### Qué formato aprovecha cada GPU

|GPU                |FP8     |INT8 (W8A8)|INT4 (W4A16)                 |bitsandbytes|
|-------------------|--------|-----------|-----------------------------|------------|
|**T4** (Colab gratis)|❌    |✅         |✅ con kernel de respaldo (ahorra memoria, poca velocidad)|✅|
|**L4** / **H100**  |✅      |✅         |✅ kernels Marlin/Machete    |✅          |

-----

## ▶️ Instrucciones de Ejecución

1. Abre `CuantizacionVLLM.ipynb` en [Google Colab](https://colab.research.google.com) (*Archivo → Subir cuaderno*, o desde GitHub)
1. Activa la GPU: *Entorno de ejecución → Cambiar tipo de entorno → T4 GPU*
1. Ejecuta las celdas **de arriba a abajo**, una por una, leyendo los comentarios. La instalación (celda 1.2) tarda 3-5 minutos
1. Cada `medir()` carga el modelo en vLLM dentro de un proceso aparte: tarda 1-3 minutos y al terminar deja la GPU libre
1. Las cuantizaciones con LLM Compressor (celdas 5.5 y 6.3) tardan 3-8 minutos cada una en T4
1. En la Parte 8 prueba la arena con los ejemplos y con tus propias preguntas
1. Responde la reflexión (Parte 9), intenta al menos un reto (Parte 10) y publica con Ngrok (Parte 11). Ejecuta la celda de limpieza al terminar

**Si vas justo de tiempo:** usa `Qwen/Qwen2.5-0.5B-Instruct` en la celda 1.5 y completa al menos las Partes 1-5, 7, 8 y 11.

-----

## ⚠️ Solución de Problemas

|Problema                                         |Solución                                                                  |
|-------------------------------------------------|--------------------------------------------------------------------------|
|Error al importar `torch` o `vllm` en la celda 1.4|*Entorno de ejecución → Reiniciar sesión* y continúa desde la celda 1.4  |
|`❌ La prueba falló` en `medir()`                 |Lee las últimas líneas del log que se muestran: suelen indicar memoria o formato no soportado|
|`CUDA out of memory` al cuantizar                |Algún modelo sigue en memoria: ejecuta la celda de guardar/liberar (5.6 o 6.4) o reinicia la sesión|
|`CUDA out of memory` al medir                    |Hay un servidor de la Parte 8 encendido: ejecuta la celda de limpieza     |
|`Bfloat16 is only supported on GPUs with compute capability >= 8.0`|Estás en T4: el notebook ya usa `half`; comprueba que ejecutaste la celda 1.4|
|El modelo INT4 va igual o más lento que el original|Normal en T4: no tiene kernels Marlin. Es una pregunta de la reflexión  |
|Error de import en `llmcompressor`               |La API actual es `from llmcompressor import oneshot` (versiones antiguas usaban `llmcompressor.transformers`)|
|Un servidor de la celda 8.2 no arranca           |Revisa `!tail -n 30 /content/vllm_8001.log`; baja `--gpu-memory-utilization` si falta memoria|
|`❌ Falta el token` en la celda 11.2              |Guarda el token en Secrets como `NGROK_TOKEN` y activa *Notebook access*  |

-----

## 📎 Recursos

- [vLLM — Quantization](https://docs.vllm.ai/en/latest/features/quantization/) · [hardware soportado por formato](https://docs.vllm.ai/en/latest/features/quantization/supported_hardware.html)
- [LLM Compressor](https://github.com/vllm-project/llm-compressor) (ejemplos de W8A8, W4A16, AWQ y FP8)
- [GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers](https://arxiv.org/abs/2210.17323)
- [AWQ: Activation-aware Weight Quantization](https://arxiv.org/abs/2306.00978)
- [SmoothQuant: Accurate and Efficient Post-Training Quantization for LLMs](https://arxiv.org/abs/2211.10438)
- [QLoRA: Efficient Finetuning of Quantized LLMs (NF4)](https://arxiv.org/abs/2305.14314)
