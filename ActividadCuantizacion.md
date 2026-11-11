# Actividad (2 h): Cuantiza un LLM y sírvelo con vLLM

**Notebook:** [CuantizacionVLLM.ipynb](https://colab.research.google.com/github/WilsonForeroB/ColabIA/blob/main/CuantizacionVLLM.ipynb)
**Modelo:** `Qwen/Qwen2.5-1.5B-Instruct` (o `Qwen2.5-0.5B-Instruct` si vas justo de tiempo)
**GPU recomendada:** L4 (Colab Pro). En una T4 gratuita también se puede, usando bitsandbytes e INT8.

Esta actividad continúa la parte de QLoRA de la sesión 6 ("comprimir W a 4 bits"). Aquí la compresión
la hacemos nosotros, sin entrenar nada, y comprobamos lo que se gana y lo que se pierde.

## Agenda

| Min | Bloque | Resultado |
|---|---|---|
| 0–15 | Entorno: GPU, instalar `vllm` + `llmcompressor`, ejecutar el modelo base | Línea base (VRAM, tok/s, calidad) |
| 15–25 | Conceptos: FP16/FP8/INT8/INT4, W4A16 frente a W8A8, GPTQ/AWQ/SmoothQuant | Saber qué técnica elegir |
| 25–40 | **A.** Sin crear nada: cuantización al vuelo (`fp8`, `bitsandbytes`) y modelos AWQ del Hub | 2–3 filas en la tabla |
| 40–55 | **B.** FP8 dinámico con LLM Compressor (no necesita calibración) | Modelo `-FP8-Dynamic` |
| 55–85 | **C.** INT4 W4A16 con GPTQ o AWQ (128 ejemplos de calibración) | Modelo `-W4A16` |
| 85–95 | **D.** INT8 W8A8 con SmoothQuant + GPTQ (la mejor opción en T4) | Modelo `-W8A8` |
| 95–110 | Comparar resultados y servir el modelo con `vllm serve` (API compatible con OpenAI) | Tabla final y API funcionando |
| 110–120 | Entrega y conclusiones | |

**Mínimo para aprobar:** base, una alternativa A, una de B/C/D y la tabla comparativa.

## Las 4 alternativas de un vistazo

| | Cómo | Calibración | Tiempo | Cuándo usarla |
|---|---|---|---|---|
| **A1. Al vuelo** | `LLM(model, quantization="fp8" \| "bitsandbytes")` | No | 0 | Para probar rápido. No genera un artefacto que se pueda reutilizar |
| **A2. Del Hub** | `LLM("Qwen/...-AWQ")` | Ya está hecha | 0 | Cuando ya existe una versión oficial cuantizada |
| **B. FP8 dinámico** | `QuantizationModifier(scheme="FP8_DYNAMIC")` | No | ~1 min | GPUs L4/H100. Casi no pierde calidad |
| **C. INT4 (GPTQ/AWQ)** | `GPTQModifier(scheme="W4A16")` / `AWQModifier(...)` | Sí | 3–10 min | Cuando la VRAM es escasa (4× menos memoria) |
| **D. INT8 W8A8** | `SmoothQuantModifier` + `GPTQModifier(scheme="W8A8")` | Sí | 3–10 min | T4/A100 con muchos usuarios simultáneos |

## Receta de LLM Compressor (siempre son los mismos 3 pasos)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from llmcompressor import oneshot
from llmcompressor.modifiers.quantization import QuantizationModifier

model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype="auto", device_map="auto")   # 1. cargar
oneshot(model=model, recipe=QuantizationModifier(targets="Linear", scheme="FP8_DYNAMIC",
                                                 ignore=["lm_head"]))                          # 2. cuantizar
model.save_pretrained("mi-modelo-FP8", save_compressed=True)                                     # 3. guardar
AutoTokenizer.from_pretrained(MODEL_ID).save_pretrained("mi-modelo-FP8")
```

```bash
vllm serve ./mi-modelo-FP8 --served-model-name mi-modelo   # vLLM detecta el formato solo
```

## Preguntas de la entrega
1. ¿Cuánto se redujeron el tamaño en disco y la VRAM de los pesos con cada técnica?
2. ¿Cambió la velocidad? ¿Por qué crees que en tu GPU fue así?
3. ¿Notaste pérdida de calidad en alguna respuesta?
4. Tienes que desplegar un modelo de 8B para 50 usuarios en una L4 de 24 GB: ¿qué técnica eliges y por qué?
