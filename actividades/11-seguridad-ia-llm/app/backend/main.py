"""
============================================================
BACKEND VULNERABLE — main.py
============================================================

Este backend es INTENCIONALMENTE INSEGURO. Su único propósito es
que el estudiante experimente cómo se materializan las vulnerabilidades
clásicas de las aplicaciones que conectan un LLM:

    1. Prompt injection      → el usuario reescribe el rol del asistente
    2. Scope drift           → el asistente responde fuera de su dominio
    3. Data exfiltration     → el asistente revela su system prompt
    4. Jailbreak por roleplay → el asistente adopta una personalidad sin filtros

NO uses este patrón en producción. La versión defendida está en secure.py.

Arranque:
    uvicorn main:app --reload --port 8000
"""

import os                          # Para leer variables de entorno (.env)
import httpx                       # Cliente HTTP async para hablar con Ollama (en Colab vía Ngrok)
from dotenv import load_dotenv     # Carga el .env a variables de entorno
from fastapi import FastAPI        # Framework web ligero y async
from fastapi.middleware.cors import CORSMiddleware  # Permite llamadas desde el frontend (otro puerto)
from pydantic import BaseModel     # Validación/tipado del cuerpo de las peticiones

# load_dotenv lee el fichero .env del directorio actual y vuelca sus claves
# en os.environ. Así NO hardcodeamos URLs ni prompts en el código fuente.
load_dotenv()

# ------------------------------------------------------------
# Configuración leída desde el .env (nunca hardcodeada)
# ------------------------------------------------------------
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")  # URL pública de Ngrok del notebook
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2:1b")             # Modelo descargado en Ollama
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "Eres un asistente de soporte técnico.")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "500"))               # Tope de tokens por respuesta
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.4"))           # Aleatoriedad del modelo

# Indica al frontend (StatusBadge) en qué modo está corriendo este backend.
MODE = "vulnerable"


# ------------------------------------------------------------
# Modelo del cuerpo de la petición POST /api/chat
# ------------------------------------------------------------
class ChatRequest(BaseModel):
    text: str                       # Texto que el usuario pega/escribe
    file_content: str | None = None  # Contenido de un fichero subido (opcional)


# ------------------------------------------------------------
# Aplicación FastAPI + CORS
# ------------------------------------------------------------
app = FastAPI(title="Actividad 11 — Backend VULNERABLE")

# CORS abierto a localhost:5173 (el frontend de Vite en desarrollo).
# allow_origins en producción NUNCA debe ser "*"; aquí es solo educativo.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def ask_ollama(messages: list[dict]) -> str:
    """Envía una conversación al endpoint /api/chat de Ollama y devuelve el texto.

    messages sigue el formato estándar de chat: lista de
    {"role": "system"|"user"|"assistant", "content": "..."}.
    """
    # El header ngrok-skip-browser-warning evita la página intersticial de Ngrok,
    # que de lo contrario devolvería HTML en lugar del JSON de Ollama.
    headers = {"ngrok-skip-browser-warning": "true"}

    # Construimos el payload que espera Ollama. stream=False para recibir
    # la respuesta completa de una vez (más simple de manejar en el frontend).
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": TEMPERATURE,
            "num_predict": MAX_TOKENS,
        },
    }

    # timeout alto porque Colab + Ngrok + modelo pequeño puede tardar varios segundos.
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(f"{OLLAMA_URL}/api/chat", json=payload, headers=headers)
        resp.raise_for_status()                 # Lanza excepción si Ollama devolvió error HTTP
        data = resp.json()
        return data["message"]["content"]       # Ollama devuelve el texto aquí


@app.get("/api/health")
async def health():
    """Comprobación rápida de que el backend está vivo."""
    return {"status": "ok"}


@app.get("/api/status")
async def status():
    """Devuelve la configuración actual al frontend.

    ⚠️ VULNERABILIDAD (data exfiltration): expone el SYSTEM_PROMPT COMPLETO.
    Cualquiera que abra /api/status ve las instrucciones internas del asistente.
    En secure.py solo se devuelve una vista previa recortada.
    """
    return {
        "ollama_url": OLLAMA_URL,
        "model": MODEL_NAME,
        "mode": MODE,
        "system_prompt_preview": SYSTEM_PROMPT,  # ⚠️ se filtra entero
    }


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Punto de entrada del chat. VERSIÓN VULNERABLE.

    El texto del usuario y el contenido del fichero se concatenan y se mandan
    al LLM SIN ninguna validación. No hay defensa contra ninguna de las 4
    vulnerabilidades: por eso todos los ataques del AttackPanel funcionarán.
    """
    # Si el usuario subió un fichero, su contenido se inyecta como "contexto".
    # ⚠️ El contenido del fichero es input NO confiable igual que el texto,
    # pero aquí lo tratamos como si fuera de confianza (raíz del problema).
    if req.file_content:
        user_content = f"Contexto del fichero:\n{req.file_content}\n\nPregunta del usuario:\n{req.text}"
    else:
        user_content = req.text

    # El system prompt se concatena con el input sin separación de confianza.
    # El modelo no distingue entre "instrucción del desarrollador" y
    # "instrucción inyectada por el usuario": ahí nace el prompt injection.
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    # ⚠️ Log inseguro: imprime el system prompt completo en consola.
    # En un servidor real esto acabaría en logs accesibles a terceros.
    print(f"[VULNERABLE] system={SYSTEM_PROMPT!r}")
    print(f"[VULNERABLE] user={user_content!r}")

    # Llamada directa al LLM, sin filtrar ni la entrada ni la salida.
    answer = await ask_ollama(messages)

    return {"response": answer, "mode": MODE, "blocked": False}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
