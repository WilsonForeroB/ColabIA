# 🎓 Actividad: Fine-tuning con QLoRA

## Resumen

Actividad práctica de ***Supervised Fine-Tuning* con QLoRA** sobre un LLM pequeño (`Qwen2.5-1.5B-Instruct`). El caso de negocio es un **clasificador de tickets de soporte**: el modelo recibe un ticket en texto libre y debe devolver un JSON con la clasificación de la empresa (`categoria`, `prioridad`, `producto`, `cliente`). Se empieza comprobando a mano cuántos parámetros ahorra LoRA (`W + A·B`), se genera un dataset de tickets etiquetados en formato *prompt → completion*, se carga el modelo en 4 bits y se mide su rendimiento **antes** de entrenar. Después se entrena el adaptador con `SFTTrainer`, se mide **después** (incluidas frases que el modelo nunca vio) y se guarda el adaptador y el modelo fusionado. Termina con una app Gradio que compara el modelo base con el afinado, publicada con Ngrok.

Lleva a la práctica la parte de **SFT, LoRA y QLoRA** de la sesión de Fine Tuning. El modelo fusionado se puede cuantizar después con la [Actividad 16](../16-cuantizacion-vllm/).

-----

## 📋 Ficha Técnica

|Campo                |Detalle                            |
|---------------------|-----------------------------------|
|**Archivo**          |`FineTuningQLoRA.ipynb`            |
|**Entorno**          |Google Colab con GPU **T4**        |
|**Duración estimada**|110 – 130 minutos                  |
|**Nivel**            |Avanzado                           |
|**Partes**           |12 partes + limpieza + rúbrica     |

-----

## 🎯 Objetivos de Aprendizaje

1. Explicar con números por qué LoRA entrena solo una pequeña fracción de los parámetros (`W' = W + A·B`)
1. Preparar un dataset de *Supervised Fine-Tuning* en formato *prompt → completion* y separar un test que mida la generalización
1. Cargar un modelo en 4 bits (NF4) con bitsandbytes: la "Q" de QLoRA
1. Medir de forma objetiva un modelo antes y después del entrenamiento (JSON válido, acierto por campo, todo correcto)
1. Configurar y ejecutar un entrenamiento QLoRA con PEFT y TRL, e interpretar la curva de pérdida
1. Reconocer *underfitting* y *overfitting* según la cantidad de datos y de épocas
1. Guardar un adaptador LoRA y fusionarlo con el modelo base para desplegarlo
1. Comparar modelo base y afinado en una app Gradio publicada con Ngrok

-----

## ✅ Prerrequisitos

- Conceptos de la sesión de Fine Tuning: ciclo de entrenamiento, SFT, LoRA y QLoRA
- Python básico (ver [actividad 13](../13-python-colab-basico/))
- Cuenta de Google (para Colab) con GPU T4 disponible
- Cuenta gratuita en [ngrok.com](https://ngrok.com) y su token guardado en Colab Secrets como `NGROK_TOKEN` (con *Notebook access* activado)

-----

## 🛠️ Stack Tecnológico

|Componente            |Herramienta                              |Detalle                                                     |
|----------------------|-----------------------------------------|------------------------------------------------------------|
|Entorno               |Google Colab                             |GPU T4 (fp16; bf16 si la GPU lo soporta)                    |
|Modelo base           |`Qwen/Qwen2.5-1.5B-Instruct`             |Alternativa rápida: `Qwen2.5-0.5B-Instruct`                 |
|Cuantización 4 bits   |bitsandbytes                             |NF4 + *double quant*                                        |
|LoRA                  |PEFT                                     |`r=16`, `alpha=32`, `target_modules='all-linear'`           |
|Entrenamiento         |TRL `SFTTrainer`                         |Formato prompt/completion: pérdida solo sobre la respuesta  |
|Datos                 |Generador de tickets sintéticos          |300 de entrenamiento, 60 de test (con frases reservadas)    |
|Interfaz              |Gradio 5.x (`gr.Blocks`)                 |Base vs afinado con `disable_adapter()` · versión fijada a `>=5,<6`|
|Publicación           |Ngrok vía pyngrok                        |Token desde Colab Secrets                                   |

-----

## 🗺️ Estructura de la Actividad

|Parte|Contenido                                                                                   |
|-----|--------------------------------------------------------------------------------------------|
|1    |GPU, instalación (transformers, TRL, PEFT, bitsandbytes), Gradio/pyngrok, versiones y dtype |
|2    |**LoRA a mano:** parámetros de `W` frente a `A + B` y por qué `B` empieza en cero           |
|3    |**Dataset:** catálogos, generador de tickets, prueba y formato prompt/completion            |
|4    |**Modelo base en 4 bits:** configuración NF4, tokenizador, carga y prueba con un ticket     |
|5    |**Evaluación ANTES:** generación en lote, métricas y resultados del modelo base             |
|6    |**Entrenamiento QLoRA:** configuración LoRA y de entrenamiento, `SFTTrainer`, entrenar y curva de pérdida|
|7    |**Evaluación DESPUÉS:** tabla antes/después y frases nunca vistas                           |
|8    |Guardar el adaptador y fusionarlo con el modelo en 16 bits                                  |
|9    |App Gradio: modelo base vs afinado                                                          |
|10   |Reflexión (5 preguntas)                                                                     |
|11   |Retos: *underfitting*/*overfitting*, servir el adaptador con vLLM, rango mínimo             |
|12   |Publicación con Ngrok (5 celdas) + limpieza + rúbrica                                       |

```
  tickets ─► formato prompt/completion ─► Qwen2.5 en 4 bits + A·B ─► SFTTrainer
                                                                        │
                    evaluación ANTES ◄── mismo test ──► evaluación DESPUÉS
                                                                        │
                       adaptador (MB) ──► fusionar (GB) ──► Gradio + Ngrok
```

-----

## ▶️ Instrucciones de Ejecución

1. Abre `FineTuningQLoRA.ipynb` en [Google Colab](https://colab.research.google.com) (*Archivo → Subir cuaderno*, o desde GitHub)
1. Activa la GPU: *Entorno de ejecución → Cambiar tipo de entorno → T4 GPU*
1. Ejecuta las celdas **de arriba a abajo**, una por una, leyendo los comentarios. La instalación tarda 1-2 minutos
1. La evaluación (celdas 5.3 y 7.1) tarda 1-2 minutos cada una y el entrenamiento (celda 6.4) 5-10 minutos en T4
1. Anota los resultados de la tabla antes/después y fíjate en las frases nunca vistas (celda 7.2)
1. En la Parte 9 prueba los ejemplos y escribe tus propios tickets
1. Responde la reflexión (Parte 10), intenta al menos un reto (Parte 11) y publica con Ngrok (Parte 12). Ejecuta la celda de limpieza al terminar

**Si vas justo de tiempo:** usa `Qwen/Qwen2.5-0.5B-Instruct` en la celda 4.2; la fusión (celda 8.2) es opcional.

-----

## ⚠️ Solución de Problemas

|Problema                                         |Solución                                                                  |
|-------------------------------------------------|--------------------------------------------------------------------------|
|`nvidia-smi` falla o PyTorch usa CPU             |Activa la GPU T4 y reinicia la sesión; ejecuta desde la celda 1.1         |
|`CUDA out of memory` al entrenar                 |En la celda 6.2 baja `per_device_train_batch_size` a 4 y sube `gradient_accumulation_steps` a 4, o usa el modelo 0.5B|
|`SFTConfig got an unexpected keyword 'max_length'`|Versión antigua de TRL: cambia a `max_seq_length=512` o repite la celda 1.2|
|La pérdida aparece como `nan`                    |Baja `learning_rate` a `1e-4` en la celda 6.2                             |
|El entrenamiento va muy lento                    |Comprueba que la GPU está activa (celda 1.1) o usa el modelo 0.5B         |
|La celda 8.2 tarda o se queda sin RAM            |La fusión es opcional: sáltala; el adaptador ya está guardado en la 8.1   |
|`❌ Falta el token` en la celda 12.2              |Guarda el token en Secrets como `NGROK_TOKEN` y activa *Notebook access*  |

-----

## 📎 Recursos

- [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685)
- [QLoRA: Efficient Finetuning of Quantized LLMs](https://arxiv.org/abs/2305.14314)
- [TRL — SFTTrainer](https://huggingface.co/docs/trl/sft_trainer) · [PEFT — LoRA](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [Unsloth](https://docs.unsloth.ai/) y [LLaMA-Factory](https://llamafactory.readthedocs.io/) (alternativas vistas en la sesión)
- [vLLM — LoRA adapters](https://docs.vllm.ai/en/latest/features/lora.html)
