"""Genera ColabOllama.ipynb de la actividad 11.

El notebook es deliberadamente minimal: su único objetivo es levantar
Ollama en Colab y exponerlo con Ngrok. El resto de la actividad (frontend
React + backend FastAPI) ocurre en la máquina local del estudiante.

Ejecutar:  python build_notebook.py
"""
import json


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def code(text):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.splitlines(keepends=True),
    }


cells = [
    md("""# 🔐 Actividad 11 — Seguridad en Entornos de IA

Este notebook **solo** hace una cosa: levantar **Ollama** en Colab y exponerlo
con **Ngrok**. La URL pública que obtengas al final es lo único que necesitas
de aquí.

El resto de la actividad —una app web con **React + FastAPI**— se ejecuta en tu
**máquina local** y se conecta a este Ollama a través de esa URL.

```
  COLAB (este notebook)              TU MÁQUINA LOCAL
  ┌─────────────────┐               ┌──────────────────────┐
  │ Ollama :11434   │   OLLAMA_URL  │ FastAPI :8000        │
  │      ▲          │◄──────────────│   main.py / secure.py│
  │ Ngrok túnel ────┼──> https://…  │ React  :5173         │
  └─────────────────┘               └──────────────────────┘
```

**Objetivo de la actividad:** experimentar las vulnerabilidades clásicas de las
apps con LLM (prompt injection, scope drift, data exfiltration y jailbreak por
roleplay) y luego implementar las defensas. Todo eso ocurre en la carpeta
`app/` de tu equipo; este notebook es solo el motor de inferencia.

> ⚠️ Antes de empezar: activa la GPU en **Entorno de ejecución → Cambiar tipo
> de entorno → T4 GPU**."""),

    md("""## PARTE 1 — Verificar GPU

Sin GPU, el modelo va 10-20× más lento. Comprobamos que Colab nos ha asignado
una T4 antes de continuar."""),
    code("""# ============================================================
# CELDA 1 — Verificar que hay GPU disponible
# ============================================================

import subprocess   # Para ejecutar comandos del sistema desde Python

# nvidia-smi muestra el estado de la GPU. Si falla, no tenemos GPU asignada.
result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)

if result.returncode != 0:
    # Mensaje claro de qué hacer si no hay GPU (no dejamos al estudiante perdido).
    raise RuntimeError(
        "❌ No se detectó GPU.\\n"
        "Ve a Entorno de ejecución → Cambiar tipo de entorno → T4 GPU y reejecuta."
    )

print(result.stdout)              # Mostramos la tabla de nvidia-smi
print('✅ GPU disponible')"""),

    md("""## PARTE 2 — Instalar Ollama

Ollama es un servidor que gestiona modelos LLM en local y expone una API REST
en el puerto **11434**. Lo instalamos con el script oficial."""),
    code("""# ============================================================
# CELDA 2 — Instalar Ollama y librerías necesarias
# ============================================================

import os   # Para configurar variables de entorno del sistema

# Evita que apt haga preguntas interactivas (bloquearían la celda en Colab).
os.environ['DEBIAN_FRONTEND'] = 'noninteractive'

# Dependencias del sistema:
#   - pciutils: necesario para que Ollama detecte la GPU (¡sin esto va en CPU!)
print('📦 Instalando dependencias del sistema...')
!sudo apt-get update -qq && sudo apt-get install -y -qq pciutils

# Script oficial de instalación de Ollama (descarga el binario y lo coloca en PATH).
print('📦 Instalando Ollama...')
!curl -fsSL https://ollama.com/install.sh | sh

# pyngrok: cliente Python del túnel Ngrok (lo usaremos en la Parte 6).
print('📦 Instalando pyngrok...')
!pip install -q pyngrok

print('✅ Ollama y pyngrok instalados')"""),

    md("""## PARTE 3 — Arrancar el servidor Ollama

Lanzamos Ollama como proceso en **background** para que el notebook siga
disponible. `OLLAMA_HOST=0.0.0.0` es imprescindible para que Ngrok pueda
alcanzarlo desde fuera."""),
    code("""# ============================================================
# CELDA 3 — Arrancar el servidor Ollama en background
# ============================================================

import time       # Para esperar a que el servidor termine de arrancar
import requests   # Para comprobar que el servidor responde

# OLLAMA_HOST a 0.0.0.0 hace que Ollama escuche en todas las interfaces,
# no solo en localhost. Ngrok necesita esto para tunelizarlo.
os.environ['OLLAMA_HOST'] = '0.0.0.0:11434'

# subprocess.Popen lanza 'ollama serve' en paralelo (no bloquea el notebook).
# Guardamos el proceso en una variable para poder cerrarlo en la limpieza final.
print('🚀 Iniciando servidor Ollama...')
ollama_proc = subprocess.Popen(
    ['ollama', 'serve'],
    stdout=subprocess.DEVNULL,   # Descartamos la salida para no saturar el log
    stderr=subprocess.DEVNULL,
)

time.sleep(5)   # Damos unos segundos al servidor para que arranque

# Health check: reintentamos hasta 3 veces antes de rendirnos.
for intento in range(3):
    try:
        r = requests.get('http://localhost:11434', timeout=10)
        print('✅ Servidor Ollama respondiendo en localhost:11434')
        break
    except Exception:
        print(f'  ...esperando al servidor (intento {intento + 1}/3)')
        time.sleep(3)
else:
    raise RuntimeError('❌ El servidor Ollama no respondió. Reejecuta esta celda.')"""),

    md("""## PARTE 4 — Descargar el modelo

Usamos **llama3.2:1b**: muy ligero (~1.3 GB) y rápido en una T4, suficiente
para una demo de seguridad. Puedes cambiarlo por `llama3.2:3b` para mejor
calidad (recuerda usar el mismo nombre en el `.env` de la app)."""),
    code("""# ============================================================
# CELDA 4 — Descargar el modelo
# ============================================================

# Este nombre debe COINCIDIR con MODEL_NAME en app/backend/.env
MODEL = 'llama3.2:1b'

print(f'📥 Descargando {MODEL} (puede tardar 1-3 minutos)...')
!ollama pull {MODEL}

print('\\n✅ Modelos disponibles:')
!ollama list"""),

    md("""## PARTE 5 — Verificar el endpoint

Antes de exponerlo, comprobamos que el modelo responde a una petición real
de chat. Si esto funciona, el backend local funcionará igual."""),
    code("""# ============================================================
# CELDA 5 — Probar el endpoint de chat localmente
# ============================================================

# Hacemos una petición de prueba al mismo endpoint /api/chat que usará el
# backend FastAPI. Así verificamos el modelo ANTES de exponerlo con Ngrok.
prueba = requests.post(
    'http://localhost:11434/api/chat',
    json={
        'model': MODEL,
        'messages': [{'role': 'user', 'content': 'Di "hola" en una palabra.'}],
        'stream': False,                  # Respuesta completa de una vez
    },
    timeout=120,
)

# Mostramos lo que respondió el modelo para confirmar que todo funciona.
print('Respuesta del modelo:', prueba.json()['message']['content'])
print('✅ El endpoint de chat funciona')"""),

    md("""## PARTE 6 — Publicar con Ngrok

Colab no tiene IP pública, así que Ngrok crea un túnel HTTPS hacia el puerto
11434. La URL que obtengas es la que pondrás en `app/backend/.env` como
`OLLAMA_URL`.

> 🔑 Necesitas tu token de Ngrok en **Secrets de Colab** (icono 🔑 a la
> izquierda) con el nombre **`NGROK_AUTHTOKEN`**. Consíguelo en
> https://dashboard.ngrok.com/get-started/your-authtoken"""),
    code("""# ============================================================
# CELDA 6.1 — Cargar el token de Ngrok desde Secrets
# ============================================================

from google.colab import userdata   # Acceso seguro a los Secrets de Colab

# Nunca hardcodeamos el token en el código: lo leemos de Secrets.
try:
    NGROK_AUTHTOKEN = userdata.get('NGROK_AUTHTOKEN')
    print(f'✅ Token cargado: {NGROK_AUTHTOKEN[:2]}...{NGROK_AUTHTOKEN[-2:]}')
except Exception:
    raise ValueError(
        '❌ No se encontró NGROK_AUTHTOKEN en Secrets.\\n'
        'Añádelo en el panel 🔑 (Secrets) con tu token de ngrok.com'
    )"""),
    code("""# ============================================================
# CELDA 6.2 — Crear el túnel Ngrok hacia Ollama
# ============================================================

from pyngrok import ngrok

ngrok.kill()                          # Cierra túneles previos por si los hubiera
time.sleep(2)
ngrok.set_auth_token(NGROK_AUTHTOKEN) # Autentica con nuestro token

# host_header='localhost:11434' es CRÍTICO: Ollama solo acepta peticiones cuyo
# header Host sea localhost. Sin esto, Ngrok recibiría 403 en cada llamada.
tunnel = ngrok.connect(
    addr='11434',
    proto='http',
    host_header='localhost:11434',
)

OLLAMA_URL = tunnel.public_url
print(f'🌐 OLLAMA_URL = {OLLAMA_URL}')"""),
    code("""# ============================================================
# CELDA 6.3 — Verificar el túnel desde fuera
# ============================================================

# Llamamos al endpoint /api/tags A TRAVÉS de la URL pública de Ngrok.
# El header ngrok-skip-browser-warning evita la página intersticial de Ngrok.
verif = requests.get(
    f'{OLLAMA_URL}/api/tags',
    headers={'ngrok-skip-browser-warning': 'true'},
    timeout=30,
)

print('Modelos accesibles vía Ngrok:', [m['name'] for m in verif.json()['models']])
print('\\n✅ Túnel verificado')"""),
    code("""# ============================================================
# CELDA 6.4 — Tu URL para la app local
# ============================================================

# ESTA URL ES TODO LO QUE NECESITAS DEL NOTEBOOK.
# Cópiala en app/backend/.env como OLLAMA_URL y deja esta pestaña abierta
# (si la cierras, el túnel muere y tendrás que reejecutar la Parte 6).
print('Copia esta línea en app/backend/.env:\\n')
print(f'OLLAMA_URL={OLLAMA_URL}')
print(f'MODEL_NAME={MODEL}')"""),

    md("""## 🧹 Limpieza final

Ejecuta esta celda **al terminar la sesión** para liberar el túnel y el
servidor. Mientras trabajes en la app local, NO la ejecutes (necesitas el
túnel vivo)."""),
    code("""# ============================================================
# CELDA 7 — Limpieza de recursos
# ============================================================

ngrok.kill()                  # 1) Cierra el túnel Ngrok
ollama_proc.terminate()       # 2) Detiene el proceso del servidor Ollama
print('✅ Túnel Ngrok y servidor Ollama cerrados')"""),
]

notebook = {
    "cells": cells,
    "metadata": {
        "colab": {"provenance": []},
        "kernelspec": {"display_name": "Python 3", "name": "python3"},
        "language_info": {"name": "python"},
        "accelerator": "GPU",
    },
    "nbformat": 4,
    "nbformat_minor": 0,
}

with open("ColabOllama.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)

print("✅ ColabOllama.ipynb generado")
