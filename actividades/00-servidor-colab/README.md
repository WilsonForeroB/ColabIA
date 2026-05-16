# Actividad 00 — Colab como Servidor Externo de IA con GPU

## Objetivo de aprendizaje

Convertir Google Colab en un servidor de IA accesible desde cualquier lugar del mundo usando un túnel Ngrok. Esta actividad es **transversal** al curso: el servidor que levantes aquí puede ser consumido por todas las demás actividades.

Al finalizar el estudiante sabrá:
- Verificar y aprovechar la GPU T4 de Colab para servir modelos de IA
- Levantar un servidor LLM accesible por HTTP desde fuera de Colab
- Conectarse al servidor desde otra notebook de Colab, una máquina local o cualquier cliente compatible con OpenAI API
- Elegir entre Ollama (sencillo) y vLLM (alto rendimiento) según el caso de uso

## Cuándo usar esta actividad

Usa **00a** (Ollama) cuando:
- Quieres setup rápido y simple
- Vas a usar modelos del catálogo de Ollama
- El resto del curso consume el servidor con LangChain o requests

Usa **00b** (vLLM) cuando:
- Necesitas máximo rendimiento (throughput, latencia)
- Quieres usar modelos de HuggingFace directamente
- Los clientes hablan la API de OpenAI (`openai` SDK)

## Prerrequisitos

- Cuenta de Google con acceso a Colab GPU T4
- Token de Ngrok en Colab Secrets como `NGROK_TOKEN`
- Para 00b: token de HuggingFace en Colab Secrets como `HF_TOKEN` (cuenta gratuita en huggingface.co)

## Notebooks incluidos

| Archivo | Motor | API | Duración |
|---|---|---|---|
| `00a_servidor_ollama.ipynb` | Ollama | Propia + compatible OpenAI | 30–40 min |
| `00b_servidor_vllm.ipynb` | vLLM | Compatible OpenAI nativa | 40–50 min |

## Cómo conectarse al servidor desde otra notebook

Una vez que tengas la URL de Ngrok (ej: `https://xxxx-xxxx.ngrok-free.app`), cualquier cliente puede usarla:

```python
# Con requests (Ollama)
import requests
resp = requests.post("https://TU-URL.ngrok-free.app/api/generate",
                     json={"model": "tinyllama", "prompt": "Hola", "stream": False})
print(resp.json()["response"])

# Con OpenAI SDK (vLLM o Ollama modo OpenAI)
from openai import OpenAI
client = OpenAI(base_url="https://TU-URL.ngrok-free.app/v1", api_key="ollama")
resp = client.chat.completions.create(model="tinyllama", messages=[{"role":"user","content":"Hola"}])
print(resp.choices[0].message.content)
```
