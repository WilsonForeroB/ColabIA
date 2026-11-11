"""Script para generar CuantizacionVLLM.ipynb (Actividad 16)."""
import json
from pathlib import Path


def code(source):
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": source.strip("\n") + "\n"}


def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source.strip("\n") + "\n"}


cells = []

# ─── CABECERA ────────────────────────────────────────────────────────────────
cells.append(md(r"""
<a href="https://colab.research.google.com/github/WilsonForeroB/ColabIA/blob/develop/actividades/16-cuantizacion-vllm/CuantizacionVLLM.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# 🗜️ Actividad 16 — Cuantización de LLMs con vLLM

## ¿Qué vas a descubrir?

En la sesión de Fine Tuning vimos que **QLoRA = LoRA + comprimir W a 4 bits**: un modelo de 7B
pasa de ~14 GB a ~4 GB. Hoy hacemos esa compresión **nosotros mismos** (sin entrenar nada) y la
servimos con **vLLM**, el motor de inferencia más usado en producción.

```
  Peso original (FP16, 16 bits)        Peso cuantizado (INT4, 4 bits)
   0.0731  -0.2104   0.5402   ...  ──►     1     -3      7    ...   + 1 escala por grupo
   ─────────── 3 GB ───────────            ───── ~1 GB ─────
                                │
                                ▼   al ejecutar:  peso ≈ entero × escala
                         vLLM sirve el modelo comprimido
```

## Mapa de la actividad

| Parte | Tema |
|-------|------|
| 1 | Preparar Colab: vLLM, LLM Compressor, Gradio y pyngrok |
| 2 | **Conceptos con código:** memoria por formato y cuantización "a mano" |
| 3 | **Línea base:** el modelo original en FP16 servido con vLLM |
| 4 | **Vía rápida:** cuantización al vuelo (bitsandbytes) y modelo AWQ del Hub |
| 5 | **INT8 W8A8:** SmoothQuant + GPTQ con LLM Compressor |
| 6 | **INT4 W4A16:** GPTQ con LLM Compressor |
| 7 | Comparar resultados: disco, VRAM, velocidad y calidad |
| 8 | Interfaz Gradio: *arena* modelo original vs cuantizado |
| 9 | Reflexión |
| 10 | Retos opcionales |
| 11 | Publicación con Ngrok + limpieza + rúbrica |

**⏱️ Duración:** 110–130 minutos · **GPU:** T4 (*Entorno de ejecución → Cambiar tipo de entorno → T4 GPU*)

> 💡 **Recuerda:** tú solo ejecutas las celdas de arriba a abajo. Los comentarios del código explican todo.
"""))

# ─── PARTE 1 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## ⚙️ PARTE 1 — Preparar Colab

| Librería | ¿Para qué la usamos? |
|----------|----------------------|
| `vllm` | Motor de inferencia: carga y sirve modelos (originales y cuantizados) |
| `llmcompressor` | Librería del proyecto vLLM para **crear** modelos cuantizados (GPTQ, SmoothQuant, AWQ, FP8) |
| `bitsandbytes` | Cuantización a 4 bits "al vuelo", la misma que usa QLoRA |
| `datasets` | Descargar los textos de calibración |
| `gradio` + `pyngrok` + `openai` | Interfaz, publicación y cliente de la API |

```
  llmcompressor ──► crea la carpeta del modelo cuantizado (formato compressed-tensors)
                                   │
                                   ▼
  vllm ──► lee config.json, detecta la cuantización y elige el kernel de GPU adecuado
```
"""))

cells.append(code(r"""
# ============================================================
# CELDA 1.1 — Comprobar que tenemos GPU
# ============================================================
# compute_cap es la "generación" de la GPU. Decide qué formatos puede ejecutar rápido vLLM:
#   7.5 = T4 (Turing)  → INT8 ✅  bitsandbytes ✅  AWQ/GPTQ ✅  FP8 ❌
#   8.9 = L4 (Ada)     → todo, incluido FP8

!nvidia-smi --query-gpu=name,memory.total,compute_cap --format=csv

# Si ves un error: Entorno de ejecución → Cambiar tipo de entorno → T4 GPU, y vuelve a empezar.
print('✅ Revisa arriba que aparezca la GPU (Tesla T4)')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 1.2 — Instalar vLLM y LLM Compressor (3-5 min)
# ============================================================
# Se instalan JUNTOS en un solo comando para que pip elija versiones compatibles entre sí
# (las dos dependen de PyTorch y de transformers).
# uv es un instalador mucho más rápido que pip; --system instala en el Python de Colab.

!pip install -q uv
!uv pip install --system -q vllm llmcompressor bitsandbytes datasets

# ⚠️ vLLM trae su propia versión de PyTorch. Si en la celda 1.4 aparece un error de import,
#    haz Entorno de ejecución → Reiniciar sesión y continúa desde la celda 1.4.
print('✅ vLLM y LLM Compressor instalados')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 1.3 — Instalar Gradio, pyngrok y el cliente de OpenAI
# ============================================================
# gradio>=5,<6 → interfaz web (versión fijada para que el notebook no cambie de comportamiento)
# pyngrok      → publicaremos la app al final
# openai       → cliente para hablar con la API de vLLM (es compatible con OpenAI)

!pip install -q 'gradio>=5,<6' pyngrok openai

print('✅ Gradio, pyngrok y openai instalados')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 1.4 — Verificar versiones y capacidades de la GPU
# ============================================================
import torch, vllm, llmcompressor   # Si falla este import: reinicia la sesión (ver celda 1.2)

print(f'   torch          {torch.__version__}')
print(f'   vllm           {vllm.__version__}')
print(f'   llmcompressor  {llmcompressor.__version__}')

# get_device_capability() devuelve una tupla, por ejemplo (7, 5) en una T4
CAPACIDAD = torch.cuda.get_device_capability()
print(f'\nGPU: {torch.cuda.get_device_name()}  ·  compute capability {CAPACIDAD[0]}.{CAPACIDAD[1]}')

# La T4 no soporta bfloat16 → usaremos float16 ('half') al lanzar vLLM
DTYPE_VLLM = 'half' if CAPACIDAD < (8, 0) else 'auto'
print(f'dtype para vLLM: {DTYPE_VLLM}')
print('FP8 ejecutable:', '✅' if CAPACIDAD >= (8, 9) else '❌ (en T4 usaremos INT8 e INT4)')

print('✅ Entorno listo')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 1.5 — Configuración de la actividad
# ============================================================
import os

# 🔧 PARÁMETRO: modelo a cuantizar. Qwen2.5-1.5B-Instruct ocupa ~3 GB en FP16 y cuantiza en minutos.
#    Si vas justo de tiempo usa 'Qwen/Qwen2.5-0.5B-Instruct' (todo irá ~3 veces más rápido).
MODELO_ID = 'Qwen/Qwen2.5-1.5B-Instruct'

# Carpeta donde guardaremos los modelos cuantizados que creemos
CARPETA = '/content/modelos'
os.makedirs(CARPETA, exist_ok=True)   # exist_ok=True: no falla si ya existe

# Nombre corto del modelo (lo usaremos para nombrar las carpetas): 'Qwen2.5-1.5B-Instruct'
NOMBRE_CORTO = MODELO_ID.split('/')[-1]

# Archivo donde cada prueba de vLLM irá guardando sus resultados (una línea JSON por prueba)
RESULTADOS = '/content/resultados.jsonl'

print(f'Modelo: {MODELO_ID}')
print(f'✅ Los modelos cuantizados se guardarán en {CARPETA}')
"""))

# ─── PARTE 2 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🧮 PARTE 2 — Conceptos con código

Antes de usar las librerías, abrimos la caja negra: **¿cuánto ocupa un modelo?** y **¿qué hace
exactamente la cuantización con un peso?**

### Nomenclatura que verás en toda la actividad: **WxAy**
- **W** = bits de los **pesos** (*weights*) · **A** = bits de las **activaciones** (lo que fluye entre capas)
- **W4A16** (*weight-only*): pesos en INT4, cálculo en FP16 → máximo ahorro de memoria
- **W8A8**: pesos **y** activaciones en 8 bits → usa los tensor cores de 8 bits (más velocidad con muchos usuarios)
"""))

cells.append(code(r"""
# ============================================================
# CELDA 2.1 — ¿Cuánto ocupa un modelo según su formato?
# ============================================================
# Regla básica: memoria de los pesos = nº de parámetros × bytes por parámetro.
# (Además, vLLM reserva memoria aparte para el KV cache de las conversaciones.)
import pandas as pd

BYTES_POR_PARAMETRO = {     # Cuántos bytes ocupa cada peso en cada formato
    'FP32': 4,              # 32 bits = 4 bytes (formato de entrenamiento clásico)
    'FP16 / BF16': 2,       # 16 bits = 2 bytes (formato habitual de los modelos publicados)
    'FP8 / INT8': 1,        # 8 bits  = 1 byte
    'INT4': 0.5,            # 4 bits  = medio byte
}
PARAMETROS = {'1.5B (hoy)': 1.5e9, '7B': 7e9, '70B': 70e9}

# Construimos la tabla: filas = formato, columnas = tamaño del modelo, valores en GB
tabla = pd.DataFrame({nombre: {fmt: f'{n * b / 1e9:.1f} GB' for fmt, b in BYTES_POR_PARAMETRO.items()}
                      for nombre, n in PARAMETROS.items()})
display(tabla)

print('✅ Una T4 tiene 15 GB: un 7B solo cabe cómodo cuantizado; un 70B ni en INT4')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 2.2 — Cuantizar un grupo de pesos "a mano" (INT4)
# ============================================================
# Este es el método más simple, RTN (round-to-nearest). GPTQ y AWQ son versiones más listas.
torch.manual_seed(0)                    # Semilla fija para que todos veamos los mismos números

pesos = torch.randn(8) * 0.1            # 8 pesos "realistas": valores pequeños alrededor de 0

# INT4 con signo representa enteros de -8 a 7. Usamos el rango simétrico [-7, 7].
escala = pesos.abs().max() / 7          # Una sola escala para el grupo: el peso más grande → 7
enteros = torch.round(pesos / escala).clamp(-7, 7)   # Dividir, redondear y recortar al rango
recuperados = enteros * escala          # Lo que hará la GPU al ejecutar: entero × escala

print('Original    :', [f'{x:+.4f}' for x in pesos.tolist()])
print('Enteros INT4:', [int(x) for x in enteros.tolist()])
print('Recuperados :', [f'{x:+.4f}' for x in recuperados.tolist()])
print(f'Escala      : {escala:.5f}')
print(f'Error medio : {(pesos - recuperados).abs().mean():.5f}')
print('✅ Guardamos 8 enteros de 4 bits + 1 escala en lugar de 8 números de 16 bits')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 2.3 — El problema de los outliers (por qué existen GPTQ, AWQ y SmoothQuant)
# ============================================================
# Si UN peso del grupo es muy grande, la escala crece y todos los demás pierden precisión.

def error_cuantizacion(x, bits):
    # Error medio absoluto tras cuantizar x de forma simétrica con 'bits' bits
    maximo = 2 ** (bits - 1) - 1                # 7 para INT4, 127 para INT8
    escala = x.abs().max() / maximo             # Escala del grupo
    return (x - torch.round(x / escala).clamp(-maximo, maximo) * escala).abs().mean().item()

normal = torch.randn(128) * 0.1                 # Un grupo de 128 pesos (tamaño de grupo habitual)
con_outlier = normal.clone()
con_outlier[0] = 3.0                            # Un único valor 30 veces mayor que el resto

for nombre, x in [('Sin outlier', normal), ('Con 1 outlier', con_outlier)]:
    print(f'{nombre:<14} → error INT8: {error_cuantizacion(x, 8):.5f} · error INT4: {error_cuantizacion(x, 4):.5f}')

print('\n💡 Soluciones que veremos:')
print('   · Grupos pequeños (128 pesos): un outlier solo afecta a su grupo')
print('   · GPTQ: corrige el redondeo de cada peso compensando el error de los anteriores')
print('   · SmoothQuant / AWQ: reescalan canales para "aplanar" los outliers antes de cuantizar')
print('✅ Concepto de outlier comprobado')
"""))

cells.append(md(r"""
### Métodos que vamos a usar

| Método | Idea | ¿Datos de calibración? | ¿Funciona en T4? | Parte |
|---|---|---|---|---|
| **bitsandbytes** (NF4) | Se cuantiza al cargar, igual que en QLoRA | No | ✅ | 4 |
| **AWQ** (del Hub) | Protege el ~1% de pesos "importantes" | Ya viene hecho | ✅ | 4 |
| **SmoothQuant + GPTQ** (W8A8) | Pasa los outliers de las activaciones a los pesos y luego GPTQ | Sí | ✅ | 5 |
| **GPTQ** (W4A16) | Redondeo capa a capa compensando el error | Sí | ✅ (kernel de respaldo) | 6 |
| **FP8 dinámico** | FP8 sin calibración, casi sin pérdida | No | ❌ necesita L4/H100 | Reto |
"""))

# ─── PARTE 3 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 📏 PARTE 3 — Línea base: el modelo original con vLLM

Para comparar necesitamos medir **siempre igual**. Creamos un pequeño script que:
1. carga un modelo en vLLM, 2. responde 4 preguntas fijas, 3. mide la velocidad con 32 peticiones a la vez.

**¿Por qué un script aparte y no código en el notebook?** vLLM reserva casi toda la GPU y no la
suelta fácilmente. Si cada prueba corre en su propio proceso, al terminar la GPU queda libre por completo
y podemos cuantizar o probar otro modelo sin reiniciar la sesión.

```
  Notebook ──► python bench_vllm.py --modelo X ──► vLLM carga X ──► mide ──► imprime RESULTADO_JSON
     ▲                                                                              │
     └───────────────── lee el resultado y lo añade a resultados.jsonl ◄────────────┘
```
"""))

cells.append(code(r"""
%%writefile /content/bench_vllm.py
# ============================================================
# CELDA 3.1 — Script de benchmark (se guarda como archivo)
# ============================================================
# %%writefile guarda el contenido de esta celda en un archivo en vez de ejecutarlo.
import argparse, json, time, torch
from vllm import LLM, SamplingParams

# Argumentos que le pasaremos desde el notebook
p = argparse.ArgumentParser()
p.add_argument('--modelo', required=True)          # Ruta local o id de HuggingFace
p.add_argument('--cuantizacion', default=None)     # Solo para cuantizar al vuelo (p. ej. bitsandbytes)
a = p.parse_args()

# Las 4 preguntas fijas: explicación, código, razonamiento y traducción
PREGUNTAS = [
    'Explica qué es la cuantización de un modelo de lenguaje en 3 frases.',
    'Escribe una función en Python que devuelva los números primos menores que n.',
    'Tengo 3 manzanas, compro el doble de las que tengo y me como 2. ¿Cuántas tengo? Razona paso a paso.',
    "Traduce al inglés: 'La seguridad de los LLM empieza por validar sus entradas.'",
]

opciones = dict(
    model=a.modelo,
    max_model_len=2048,            # Contexto máximo: suficiente y ahorra memoria de KV cache
    gpu_memory_utilization=0.85,   # Fracción de la VRAM que vLLM puede reservar
    enforce_eager=True,            # Sin CUDA graphs: arranca más rápido (ideal para pruebas cortas)
)
if a.cuantizacion:
    opciones['quantization'] = a.cuantizacion      # vLLM cuantiza los pesos al cargarlos
if torch.cuda.get_device_capability() < (8, 0):
    opciones['dtype'] = 'half'                     # La T4 no soporta bfloat16

inicio = time.time()
llm = LLM(**opciones)                              # Descarga (si hace falta) y carga el modelo
segundos_carga = time.time() - inicio

params = SamplingParams(temperature=0.0, max_tokens=256)    # temperature=0 → respuestas deterministas
conversaciones = [[{'role': 'user', 'content': q}] for q in PREGUNTAS]

llm.chat(conversaciones[:1], params)               # Calentamiento: la primera llamada siempre es más lenta

lote = conversaciones * 8                          # 32 peticiones a la vez (simula varios usuarios)
inicio = time.time()
salidas = llm.chat(lote, params)
segundos = time.time() - inicio
tokens = sum(len(s.outputs[0].token_ids) for s in salidas)  # Tokens generados en total

for q, s in zip(PREGUNTAS, salidas):               # Las 4 primeras salidas = una por pregunta
    print(f'❓ {q}')
    print(f'💬 {s.outputs[0].text.strip()[:500]}\n')

# Línea con un prefijo fijo para que el notebook la encuentre y la lea
print('RESULTADO_JSON=' + json.dumps({
    'carga_s': round(segundos_carga, 1),
    'tokens_s': round(tokens / segundos, 1),
    'respuesta_mates': salidas[2].outputs[0].text.strip()[-150:],
}, ensure_ascii=False))
"""))

cells.append(code(r"""
# ============================================================
# CELDA 3.2 — Función para lanzar el benchmark y guardar el resultado
# ============================================================
import subprocess, json, re

def medir(nombre, modelo, cuantizacion=None):
    # Ejecuta bench_vllm.py en un proceso aparte, muestra las respuestas y guarda las métricas.
    comando = ['python', '/content/bench_vllm.py', '--modelo', modelo]
    if cuantizacion:
        comando += ['--cuantizacion', cuantizacion]
    print(f'⏳ Midiendo {nombre} (cargar el modelo tarda 1-3 min)...')
    proc = subprocess.run(comando, capture_output=True, text=True)   # Espera a que termine
    log = proc.stdout + proc.stderr                                  # Juntamos todo lo que imprimió

    linea = re.search(r'RESULTADO_JSON=(.*)', log)
    if proc.returncode != 0 or not linea:
        # Si falló, enseñamos el final del log, que es donde aparece el error real
        print('❌ La prueba falló. Últimas líneas del log:\n')
        print('\n'.join(log.strip().splitlines()[-25:]))
        return None

    # vLLM escribe en su log "Model loading took X GiB": es la VRAM que ocupan los pesos
    vram = re.search(r'Model loading took ([\d.]+) ?GiB', log)
    fila = {'nombre': nombre, 'modelo': modelo, **json.loads(linea.group(1)),
            'vram_pesos_gib': round(float(vram.group(1)), 2) if vram else None}

    # Mostramos solo las preguntas y respuestas
    print('\n'.join(l for l in proc.stdout.splitlines() if l.startswith(('❓', '💬'))))
    with open(RESULTADOS, 'a') as f:                                 # 'a' = añadir al final
        f.write(json.dumps(fila, ensure_ascii=False) + '\n')
    print(f"\n📊 VRAM pesos: {fila['vram_pesos_gib']} GiB · velocidad: {fila['tokens_s']} tokens/s")
    return fila

print('✅ Función medir() lista')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 3.3 — Medir el modelo original (FP16)
# ============================================================
# Este es el punto de referencia. Fíjate en la VRAM, la velocidad y si la respuesta
# de matemáticas es correcta (3 + 6 - 2 = 7).

base = medir('0 · Original FP16', MODELO_ID)

if base:
    print('✅ Línea base registrada')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 3.4 — Tamaño en disco del modelo original
# ============================================================
# HuggingFace guarda los modelos descargados en ~/.cache/huggingface/hub/models--<org>--<nombre>
carpeta_cache = os.path.expanduser('~/.cache/huggingface/hub/models--' + MODELO_ID.replace('/', '--'))

!du -sh {carpeta_cache}

print('✅ Ese es el tamaño que vamos a reducir')
"""))

# ─── PARTE 4 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## ⚡ PARTE 4 — Vía rápida: cuantizar sin crear nada

Dos atajos que no requieren ningún paso previo:

| Atajo | Cómo | Ventaja | Inconveniente |
|---|---|---|---|
| **Al vuelo** | `LLM(modelo, quantization='bitsandbytes')` | Cero pasos | Sin calibración; se repite en cada arranque |
| **Del Hub** | `LLM('Qwen/Qwen2.5-1.5B-Instruct-AWQ')` | Calidad cuidada por el fabricante | Solo si alguien lo publicó |

vLLM detecta la cuantización de un modelo del Hub leyendo la sección `quantization_config` de su `config.json`.
En HuggingFace busca sufijos como `-AWQ`, `-GPTQ-Int4`, `-W8A8`, `-FP8`.
"""))

cells.append(code(r"""
# ============================================================
# CELDA 4.1 — Cuantización al vuelo con bitsandbytes (4 bits NF4)
# ============================================================
# NF4 (NormalFloat 4) es el formato de QLoRA: 16 valores repartidos según una campana de Gauss,
# porque los pesos de una red neuronal se distribuyen así.

bnb = medir('A · bitsandbytes 4 bits (al vuelo)', MODELO_ID, cuantizacion='bitsandbytes')

if bnb:
    print('✅ Compara la VRAM con la línea base')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 4.2 — Modelo ya cuantizado con AWQ desde el Hub
# ============================================================
# No pasamos 'cuantizacion': vLLM la detecta sola en el config.json del modelo.

awq_hub = medir('A · AWQ INT4 (Hub)', MODELO_ID + '-AWQ')

if awq_hub:
    print('✅ Modelo pre-cuantizado servido sin ningún paso previo')
"""))

# ─── PARTE 5 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🎯 PARTE 5 — INT8 W8A8 con LLM Compressor (SmoothQuant + GPTQ)

Ahora **creamos** nuestro propio modelo cuantizado. LLM Compressor siempre sigue 3 pasos:

```
  1. Cargar el modelo (transformers)
  2. oneshot(modelo, receta, datos de calibración)   ← aquí ocurre la cuantización
  3. save_pretrained(carpeta, save_compressed=True)  ← vLLM ya puede cargar esa carpeta
```

**Datos de calibración:** unos cientos de conversaciones reales. El algoritmo las pasa por el modelo,
observa los valores que fluyen por cada capa y elige el redondeo que **menos cambia la salida**.

**Por qué W8A8 en una T4:** la T4 tiene tensor cores de INT8, así que este formato no solo ahorra memoria:
también puede acelerar cuando hay muchos usuarios a la vez.
"""))

cells.append(code(r"""
# ============================================================
# CELDA 5.1 — Descargar los textos de calibración
# ============================================================
from datasets import load_dataset

# 🔧 PARÁMETROS de calibración (valores de clase; en producción se usan 256-512 y 2048)
NUM_EJEMPLOS = 128      # Más ejemplos = mejor calidad, pero más lento
LONGITUD_MAX = 512      # Tokens máximos por ejemplo

# ultrachat_200k: conversaciones de chat reales. [:128] descarga solo las primeras 128.
datos = load_dataset('HuggingFaceH4/ultrachat_200k', split=f'train_sft[:{NUM_EJEMPLOS}]')
datos = datos.shuffle(seed=42)    # Mezclamos para no calibrar solo con un tipo de conversación

print(datos)
print('\nEjemplo de mensaje:', datos[0]['messages'][0]['content'][:200])
print('✅ Datos de calibración descargados')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 5.2 — Preparar los textos con la plantilla de chat y tokenizarlos
# ============================================================
from transformers import AutoTokenizer

tokenizador = AutoTokenizer.from_pretrained(MODELO_ID)

# apply_chat_template añade las marcas especiales del chat (<|im_start|>user ...).
# Calibramos con el MISMO formato que el modelo verá cuando lo usemos.
datos = datos.map(lambda ej: {'text': tokenizador.apply_chat_template(ej['messages'], tokenize=False)})

# Convertimos cada texto en tokens. truncation corta los textos más largos que LONGITUD_MAX.
datos_calibracion = datos.map(
    lambda ej: tokenizador(ej['text'], max_length=LONGITUD_MAX, truncation=True,
                           padding=False, add_special_tokens=False),   # Las marcas ya las puso la plantilla
    remove_columns=datos.column_names)                                 # Solo nos quedamos con los tokens

print(datos_calibracion)
print('✅ Datos de calibración listos')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 5.3 — Cargar el modelo original con transformers
# ============================================================
from transformers import AutoModelForCausalLM

# torch_dtype='auto' respeta el formato original (16 bits); device_map='auto' lo pone en la GPU
modelo = AutoModelForCausalLM.from_pretrained(MODELO_ID, torch_dtype='auto', device_map='auto')

print(f'VRAM ocupada: {torch.cuda.memory_allocated() / 2**30:.2f} GiB')
print('✅ Modelo original cargado')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 5.4 — Definir la receta W8A8
# ============================================================
# Una receta es una lista de "modificadores" que se aplican en orden.
from llmcompressor.modifiers.smoothquant import SmoothQuantModifier
from llmcompressor.modifiers.quantization import GPTQModifier

receta_int8 = [
    # Paso 1: divide los canales de activación con outliers y multiplica los pesos por lo mismo.
    # El resultado matemático no cambia, pero ahora activaciones Y pesos son fáciles de cuantizar.
    # smoothing_strength=0.8: cuánta "dificultad" se pasa de las activaciones a los pesos (0-1).
    SmoothQuantModifier(smoothing_strength=0.8),
    # Paso 2: GPTQ cuantiza pesos y activaciones a INT8.
    GPTQModifier(
        targets='Linear',      # Todas las capas lineales (atención y MLP): >95% de los pesos
        scheme='W8A8',         # Pesos INT8 + activaciones INT8
        ignore=['lm_head'],    # La capa final de salida es muy sensible: la dejamos en 16 bits
    ),
]

print(receta_int8)
print('✅ Receta W8A8 definida')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 5.5 — Cuantizar con oneshot (3-8 min en T4)
# ============================================================
# oneshot pasa los datos de calibración por el modelo capa a capa y aplica la receta.
# "One shot" = de una sola vez, sin reentrenar el modelo.
from llmcompressor import oneshot

oneshot(
    model=modelo,                          # El modelo se modifica en el sitio (in-place)
    dataset=datos_calibracion,             # Textos para observar las activaciones
    recipe=receta_int8,                    # Qué hacer
    max_seq_length=LONGITUD_MAX,
    num_calibration_samples=NUM_EJEMPLOS,
)

print('✅ Modelo cuantizado a W8A8')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 5.6 — Guardar el modelo cuantizado y liberar la GPU
# ============================================================
import gc

CARPETA_INT8 = f'{CARPETA}/{NOMBRE_CORTO}-W8A8-INT8'

# save_compressed=True guarda los pesos ya empaquetados en formato compressed-tensors
modelo.save_pretrained(CARPETA_INT8, save_compressed=True)
tokenizador.save_pretrained(CARPETA_INT8)        # vLLM también necesita el tokenizador

# Liberamos la GPU: vLLM (en la celda 5.8) necesita la memoria libre
del modelo              # Borra la referencia al modelo
gc.collect()            # Recolector de basura de Python
torch.cuda.empty_cache()  # Devuelve a la GPU la memoria que PyTorch tenía reservada

print(f'✅ Guardado en {CARPETA_INT8} · GPU liberada')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 5.7 — Mirar dentro: tamaño y config.json
# ============================================================
# La sección quantization_config es lo que vLLM lee para saber cómo ejecutar el modelo.

!du -sh {CARPETA_INT8}

with open(f'{CARPETA_INT8}/config.json') as f:
    config_q = json.load(f)['quantization_config']
print(json.dumps(config_q, indent=1)[:800])   # Solo los primeros 800 caracteres

print('✅ Fíjate en "format", "num_bits" y en la lista "ignore"')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 5.8 — Medir el modelo INT8 en vLLM
# ============================================================
int8 = medir('B · W8A8 INT8 (SmoothQuant+GPTQ)', CARPETA_INT8)

if int8:
    print('✅ Modelo propio W8A8 funcionando en vLLM')
"""))

# ─── PARTE 6 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🗜️ PARTE 6 — INT4 W4A16 con GPTQ (máxima compresión)

Mismo flujo que en la Parte 5, cambiando solo la receta: pesos a **4 bits**, cálculo en 16 bits.
Reutilizamos los mismos datos de calibración.

**Cómo trabaja GPTQ:** cuantiza los pesos de una capa **uno a uno**. Cada vez que redondea un peso,
ajusta los pesos que aún no ha redondeado para compensar el error, usando información de cómo se
relacionan entre sí las entradas de esa capa (la matriz Hessiana).

> ⚠️ **En T4** los kernels rápidos de INT4 (Marlin) no existen; vLLM usa un kernel de respaldo.
> Ahorrarás mucha memoria, pero **puede que no ganes velocidad**. Es una de las preguntas de la reflexión.
"""))

cells.append(code(r"""
# ============================================================
# CELDA 6.1 — Cargar de nuevo el modelo original
# ============================================================
# oneshot modificó el modelo anterior, así que partimos otra vez del original.
modelo = AutoModelForCausalLM.from_pretrained(MODELO_ID, torch_dtype='auto', device_map='auto')

print('✅ Modelo original cargado de nuevo')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 6.2 — Definir la receta W4A16
# ============================================================
receta_int4 = GPTQModifier(
    targets='Linear',      # Todas las capas lineales
    scheme='W4A16',        # Pesos INT4 simétricos en grupos de 128 · activaciones en 16 bits
    ignore=['lm_head'],    # Capa de salida en 16 bits
)

print(receta_int4)
print('✅ Receta W4A16 definida')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 6.3 — Cuantizar con GPTQ (3-8 min en T4)
# ============================================================
oneshot(
    model=modelo,
    dataset=datos_calibracion,
    recipe=receta_int4,
    max_seq_length=LONGITUD_MAX,
    num_calibration_samples=NUM_EJEMPLOS,
)

print('✅ Modelo cuantizado a W4A16')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 6.4 — Guardar y liberar la GPU
# ============================================================
CARPETA_INT4 = f'{CARPETA}/{NOMBRE_CORTO}-W4A16-GPTQ'

modelo.save_pretrained(CARPETA_INT4, save_compressed=True)
tokenizador.save_pretrained(CARPETA_INT4)

del modelo
gc.collect()
torch.cuda.empty_cache()

!du -sh {CARPETA_INT4}
print(f'✅ Guardado en {CARPETA_INT4} · GPU liberada')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 6.5 — Medir el modelo INT4 en vLLM
# ============================================================
int4 = medir('C · W4A16 INT4 (GPTQ)', CARPETA_INT4)

if int4:
    print('✅ Modelo propio W4A16 funcionando en vLLM')
"""))

# ─── PARTE 7 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 📊 PARTE 7 — Comparar resultados

Cada llamada a `medir()` añadió una fila a `resultados.jsonl`. Ahora las juntamos.
Si repetiste alguna prueba, se queda la última.
"""))

cells.append(code(r"""
# ============================================================
# CELDA 7.1 — Tabla comparativa
# ============================================================
df = pd.read_json(RESULTADOS, lines=True).drop_duplicates('nombre', keep='last')

def tamano_disco(modelo):
    # du -sh devuelve el tamaño de una carpeta; los modelos del Hub están en la caché
    ruta = modelo if os.path.isdir(modelo) else os.path.expanduser(
        '~/.cache/huggingface/hub/models--' + modelo.replace('/', '--'))
    salida = subprocess.run(['du', '-sh', ruta], capture_output=True, text=True).stdout
    return salida.split()[0] if salida else '-'

df['disco'] = df['modelo'].map(tamano_disco)
df['mates_ok'] = df['respuesta_mates'].str.contains('7')     # Comprobación sencilla de calidad
velocidad_base = df.loc[df['nombre'].str.startswith('0'), 'tokens_s']
if len(velocidad_base):
    df['x_vs_base'] = (df['tokens_s'] / velocidad_base.iloc[0]).round(2)   # >1 = más rápido

display(df[['nombre', 'disco', 'vram_pesos_gib', 'tokens_s', 'x_vs_base', 'mates_ok']])
print('✅ Tabla lista: haz una captura para la entrega')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 7.2 — Gráfico: memoria vs velocidad
# ============================================================
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4))    # Dos gráficos lado a lado
ax1.barh(df['nombre'], df['vram_pesos_gib'], color='#4C78A8')
ax1.set_title('VRAM de los pesos (GiB) — menos es mejor')
ax2.barh(df['nombre'], df['tokens_s'], color='#F58518')
ax2.set_title('Velocidad con 32 peticiones (tokens/s) — más es mejor')
ax2.set_yticks([])                                       # Las etiquetas ya están en el gráfico izquierdo
plt.tight_layout()
plt.show()

print('✅ ¿Qué técnica ofrece el mejor equilibrio en tu GPU?')
"""))

# ─── PARTE 8 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🥊 PARTE 8 — Interfaz Gradio: arena original vs cuantizado

Levantamos **dos servidores vLLM a la vez** en la misma T4 (los dos caben gracias a que son pequeños)
y una interfaz que envía la misma pregunta a ambos para comparar respuesta y velocidad.

```
                         ┌──► vLLM :8000  (original FP16)   ──┐
  Gradio :7860 ── misma ─┤                                    ├──► respuestas lado a lado
               pregunta  └──► vLLM :8001  (tu modelo INT4)  ──┘
```

`vllm serve` expone una **API compatible con OpenAI**: el mismo código cliente sirve para OpenAI, Ollama o vLLM.
"""))

cells.append(code(r"""
# ============================================================
# CELDA 8.1 — Función para arrancar un servidor vLLM en segundo plano
# ============================================================
import time, requests

def arrancar_servidor(modelo, puerto, nombre_api):
    # subprocess.Popen lanza el servidor en paralelo: el notebook no se queda bloqueado.
    log = open(f'/content/vllm_{puerto}.log', 'w')        # Guardamos su salida en un archivo
    proceso = subprocess.Popen(
        ['vllm', 'serve', modelo,
         '--port', str(puerto),                    # Cada servidor en su propio puerto
         '--served-model-name', nombre_api,        # Nombre con el que lo pediremos en la API
         '--gpu-memory-utilization', '0.40',       # 40% de la VRAM cada uno → caben los dos
         '--max-model-len', '2048',
         '--enforce-eager',                        # Arranque más rápido y menos memoria
         '--dtype', 'half' if CAPACIDAD < (8, 0) else 'auto'],
        stdout=log, stderr=subprocess.STDOUT)
    # Esperamos hasta que el endpoint /health responda (máximo ~5 min)
    for _ in range(100):
        try:
            if requests.get(f'http://localhost:{puerto}/health', timeout=2).status_code == 200:
                print(f'✅ {nombre_api} listo en el puerto {puerto}')
                return proceso
        except requests.exceptions.ConnectionError:
            pass                                   # Aún arrancando
        if proceso.poll() is not None:             # El proceso murió: no tiene sentido seguir esperando
            break
        time.sleep(3)
    print(f'❌ {nombre_api} no arrancó. Revisa: !tail -n 30 /content/vllm_{puerto}.log')
    return proceso

print('✅ Función arrancar_servidor() lista')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 8.2 — Arrancar los dos servidores (2-4 min)
# ============================================================
# 🔧 PARÁMETRO: el modelo cuantizado que quieres enfrentar al original
MODELO_CUANTIZADO = CARPETA_INT4      # Prueba también CARPETA_INT8

servidor_original = arrancar_servidor(MODELO_ID, 8000, 'original')
servidor_cuantizado = arrancar_servidor(MODELO_CUANTIZADO, 8001, 'cuantizado')

!nvidia-smi --query-gpu=memory.used,memory.total --format=csv
print('✅ Dos modelos sirviéndose a la vez en la misma GPU')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 8.3 — Probar cada servidor por separado
# ============================================================
from openai import OpenAI

# Un cliente por servidor. api_key es obligatoria para el SDK, pero vLLM no la valida.
clientes = {
    'original': OpenAI(base_url='http://localhost:8000/v1', api_key='vllm'),
    'cuantizado': OpenAI(base_url='http://localhost:8001/v1', api_key='vllm'),
}

for nombre, cliente in clientes.items():
    r = cliente.chat.completions.create(
        model=nombre,                                    # El --served-model-name del servidor
        messages=[{'role': 'user', 'content': 'Di hola en una frase.'}],
        max_tokens=30)
    print(f'{nombre:>10}: {r.choices[0].message.content}')

print('✅ Los dos servidores responden')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 8.4 — Función que pregunta a un modelo y mide su velocidad
# ============================================================
def preguntar(nombre, pregunta, max_tokens):
    inicio = time.time()
    r = clientes[nombre].chat.completions.create(
        model=nombre,
        messages=[{'role': 'user', 'content': pregunta}],
        max_tokens=int(max_tokens),
        temperature=0.0)                                 # Determinista: comparación justa
    segundos = time.time() - inicio
    tokens = r.usage.completion_tokens                   # Tokens generados (lo informa la API)
    metricas = f'⏱️ {segundos:.1f} s · {tokens} tokens · {tokens / segundos:.1f} tokens/s'
    return r.choices[0].message.content, metricas

# Prueba individual antes de integrarla en la interfaz
texto, metricas = preguntar('cuantizado', '¿Qué es un LLM?', 60)
print(texto, '\n', metricas)
print('✅ Función preguntar() probada')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 8.5 — Construir la interfaz con gr.Blocks
# ============================================================
import gradio as gr

def comparar(pregunta, max_tokens):
    # Envía la misma pregunta a los dos modelos y devuelve 4 salidas
    r1, m1 = preguntar('original', pregunta, max_tokens)
    r2, m2 = preguntar('cuantizado', pregunta, max_tokens)
    return r1, m1, r2, m2

CSS = '.metricas textarea {font-family: monospace; font-size: 0.9em}'

with gr.Blocks(title='Arena de cuantización', css=CSS) as demo:
    gr.Markdown(f'# 🥊 Arena: original vs cuantizado\n`{MODELO_ID}` frente a `{os.path.basename(MODELO_CUANTIZADO)}`')
    with gr.Row():
        pregunta = gr.Textbox(label='Pregunta', lines=3, scale=4,
                              value='Explica en 3 puntos qué ventajas tiene cuantizar un LLM.')
        max_tokens = gr.Slider(32, 512, value=200, step=16, label='Máx. tokens', scale=1)
    boton = gr.Button('Comparar', variant='primary')
    with gr.Row():
        with gr.Column():
            gr.Markdown('### 🧊 Original (FP16)')
            salida_1 = gr.Textbox(label='Respuesta', lines=10)
            metricas_1 = gr.Textbox(label='Métricas', elem_classes='metricas')
        with gr.Column():
            gr.Markdown('### 🗜️ Cuantizado')
            salida_2 = gr.Textbox(label='Respuesta', lines=10)
            metricas_2 = gr.Textbox(label='Métricas', elem_classes='metricas')
    gr.Examples(['Tengo 3 manzanas, compro el doble y me como 2. ¿Cuántas tengo?',
                 'Escribe una función en Python que invierta una cadena.',
                 'Resume en dos frases qué es vLLM.'], inputs=pregunta)
    # click(función, entradas, salidas): al pulsar, Gradio llama a comparar() con los valores
    boton.click(comparar, [pregunta, max_tokens], [salida_1, metricas_1, salida_2, metricas_2])

print('✅ Interfaz construida')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 8.6 — Lanzar la interfaz dentro de Colab
# ============================================================
demo.launch(quiet=True)

print('✅ Interfaz visible arriba 👆 — prueba los ejemplos')
"""))

# ─── PARTE 9 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🤔 PARTE 9 — Reflexión

Responde en esta misma celda (doble clic para editarla). Entre 2 y 5 líneas por pregunta.

1. **Conceptual:** ¿Qué diferencia hay entre W4A16 y W8A8? ¿En qué situación (pocos usuarios con poca VRAM o muchos usuarios a la vez) elegirías cada uno?

   *Tu respuesta:*

2. **Código:** En la celda 5.4 la receta deja `lm_head` sin cuantizar y en la celda 5.2 usamos `apply_chat_template` para los datos de calibración. ¿Por qué crees que se hace cada una de estas dos cosas?

   *Tu respuesta:*

3. **Implicaciones:** Según tu tabla de la Parte 7, ¿notaste pérdida de calidad? Si cuantizas un modelo que se usa en un ámbito sensible (salud, banca, legal), ¿cómo comprobarías que no ha empeorado antes de ponerlo en producción?

   *Tu respuesta:*

4. **Comparativa:** ¿Qué ventajas e inconvenientes tiene cuantizar al vuelo con bitsandbytes frente a crear tu propio modelo con LLM Compressor? ¿Y frente a descargar uno ya cuantizado del Hub?

   *Tu respuesta:*

5. **Rendimiento:** ¿El modelo INT4 fue más rápido que el original en tu GPU? Explica el resultado usando lo que viste sobre los kernels de la T4.

   *Tu respuesta:*
"""))

# ─── PARTE 10 ────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🏆 PARTE 10 — Retos opcionales

Cada reto tiene una celda vacía debajo. No están resueltos: solo una pista para empezar.

- **Reto A — AWQ propio:** cuantiza tú mismo el modelo con AWQ en vez de GPTQ y compáralo con el GPTQ de la Parte 6 y con el AWQ del Hub.
  *Pista:* `from llmcompressor.modifiers.awq import AWQModifier` y receta `AWQModifier(targets=['Linear'], scheme='W4A16_ASYM', ignore=['lm_head'])`; el resto es igual que las celdas 6.1-6.5.

- **Reto B — Calibración en español:** el dataset de calibración está en inglés. Calibra con conversaciones en español y comprueba si mejoran las respuestas en español.
  *Pista:* busca en HuggingFace un dataset de instrucciones en español con columna de mensajes, o construye una lista de dicts `{'messages': [...]}` y conviértela con `Dataset.from_list`.

- **Reto C — FP8 dinámico (necesita GPU L4 o H100):** crea un modelo FP8 sin datos de calibración y mídelo.
  *Pista:* `QuantizationModifier(targets='Linear', scheme='FP8_DYNAMIC', ignore=['lm_head'])` de `llmcompressor.modifiers.quantization`, y `oneshot(model=modelo, recipe=receta)` sin `dataset`. Se puede crear en T4, pero solo se ejecuta rápido en GPUs de compute capability ≥ 8.9.
"""))

for letra, num in [('A', 1), ('B', 2), ('C', 3)]:
    cells.append(code(f"""
# ============================================================
# CELDA 10.{num} — Reto {letra}: tu espacio para experimentar
# ============================================================
# (celda vacía a propósito)
"""))

# ─── PARTE 11 — NGROK ────────────────────────────────────────────────────────
cells.append(md(r"""
## 🌐 PARTE 11 — Publicación con Ngrok

Hasta ahora la arena solo vive dentro de Colab. Con **Ngrok** creamos un **túnel** hacia Internet
para que tus compañeros comparen los modelos desde su navegador.

```
  Compañero (navegador)
        │  https://xxxx.ngrok-free.app
        ▼
  Servidor de Ngrok  ───túnel───►  Colab (localhost:7860)
                                          │
                                          ▼
                                 Arena Gradio ──► vLLM :8000 / :8001
```

**Antes de empezar:** crea una cuenta gratuita en [ngrok.com](https://ngrok.com), copia tu *Authtoken*
y guárdalo en Colab: icono 🔑 **Secrets** → *Add new secret* → nombre `NGROK_TOKEN` → pega el token → activa *Notebook access*.
"""))

cells.append(code(r"""
# ============================================================
# CELDA 11.1 — Instalar pyngrok
# ============================================================
# Ya lo instalamos en la celda 1.3; repetirlo es instantáneo y garantiza que esté
# disponible aunque hayas reiniciado la sesión.

!pip install -q pyngrok

print('✅ pyngrok instalado')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 11.2 — Autenticar con el token de Ngrok
# ============================================================
# El token es como una contraseña: NUNCA lo escribas directamente en el notebook
# si vas a compartirlo, porque cualquiera podría usar tu cuenta.
# Por eso lo leemos desde Colab Secrets.

from pyngrok import ngrok            # Librería para crear el túnel

try:
    from google.colab import userdata                 # Acceso a los Secrets de Colab
    NGROK_TOKEN = userdata.get('NGROK_TOKEN')         # Lee el secreto llamado NGROK_TOKEN
except Exception as e:
    # Si Secrets no está disponible o el secreto no existe, usamos la variable manual.
    print(f'⚠️ No se pudo leer el Secret: {e}')
    print('⚠️ SEGURIDAD: si escribes el token aquí, bórralo antes de compartir el notebook.')
    NGROK_TOKEN = 'PEGA_TU_TOKEN_AQUI'                # Solo como último recurso

# Validamos que no quedó el texto de ejemplo
if NGROK_TOKEN == 'PEGA_TU_TOKEN_AQUI':
    raise ValueError('❌ Falta el token. Guárdalo en Secrets con el nombre NGROK_TOKEN y reintenta.')

ngrok.set_auth_token(NGROK_TOKEN)   # Registra el token para esta sesión

print('✅ Token de Ngrok configurado')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 11.3 — Abrir el túnel y relanzar la arena
# ============================================================
# Orden importante: cerrar lo anterior → abrir túnel → lanzar la app.

demo.close()    # Cierra la app lanzada en la Parte 8 para liberar el puerto
ngrok.kill()    # Cierra túneles anteriores (el plan gratuito solo permite uno a la vez)

# connect(7860) crea un túnel público hacia el puerto local 7860
tunel = ngrok.connect(7860)
print(f'🌍 URL pública: {tunel.public_url}')
print('   Compártela con tus compañeros para que comparen los modelos.')

# server_name='0.0.0.0' = acepta conexiones externas (las que llegan por el túnel)
# server_port=7860       = el mismo puerto que expusimos con Ngrok
# share=False            = no usamos el enlace temporal de Gradio; Ngrok es más estable
demo.launch(server_name='0.0.0.0', server_port=7860, share=False, quiet=True)

print('✅ Arena publicada con Ngrok')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 11.4 — Verificar los túneles activos
# ============================================================
# get_tunnels() lista los túneles abiertos en esta sesión.

tuneles = ngrok.get_tunnels()

if tuneles:
    print(f'✅ {len(tuneles)} túnel(es) activo(s):')
    for t in tuneles:
        print(f'   {t.public_url}  →  {t.config["addr"]}')
else:
    print('❌ No hay túneles activos. Ejecuta de nuevo la celda 11.3.')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 11.5 — (Opcional) Dominio estático
# ============================================================
# Con el plan gratuito puedes reclamar UN dominio fijo en dashboard.ngrok.com → Domains.
# Así la URL no cambia entre sesiones. Si no tienes uno, sáltate esta celda.

DOMINIO_ESTATICO = ''   # Ej: 'mi-arena-cuantizacion.ngrok-free.app'

if DOMINIO_ESTATICO:
    ngrok.kill()                                                    # Cierra el túnel aleatorio
    tunel = ngrok.connect(7860, domain=DOMINIO_ESTATICO)            # Abre el túnel con tu dominio
    print(f'✅ URL fija: {tunel.public_url}')
else:
    print('ℹ️ Sin dominio estático configurado: se mantiene la URL aleatoria.')
"""))

cells.append(code(r"""
# ============================================================
# CELDA LIMPIEZA — Liberar todos los recursos al terminar
# ============================================================
# Orden: túnel → interfaz → procesos → memoria GPU.

# 1. Cerrar el túnel Ngrok
ngrok.kill()
print('✅ Túnel Ngrok cerrado')

# 2. Cerrar la interfaz Gradio
demo.close()
print('✅ Interfaz Gradio cerrada')

# 3. Detener los dos servidores vLLM (al morir el proceso se libera su VRAM)
for proceso in [servidor_original, servidor_cuantizado]:
    proceso.terminate()     # Pide al proceso que termine
    proceso.wait()          # Espera a que termine de verdad
print('✅ Servidores vLLM detenidos')

# 4. Liberar la memoria GPU que pudiera quedar en este notebook
gc.collect()
torch.cuda.empty_cache()
print('✅ Memoria GPU liberada')

print('\n✅ Todos los recursos liberados. Puedes cerrar el notebook.')
"""))

cells.append(md(r"""
## 📊 Rúbrica de Evaluación

| Criterio | Excelente (5) | Satisfactorio (3) | En desarrollo (1) |
|----------|---------------|-------------------|-------------------|
| **Entorno y línea base** | vLLM instalado y línea base medida (VRAM, tokens/s, calidad) sin errores | Funciona tras algún reintento o reinicio | No logra servir el modelo original |
| **Conceptos de cuantización** | Explica escala, redondeo, outliers y la diferencia W4A16 / W8A8 con sus propios datos | Ejecuta la Parte 2 pero explica solo parte | No identifica qué hace la cuantización |
| **Modelos cuantizados** | Crea y mide W8A8 y W4A16 con LLM Compressor, además de las vías rápidas | Completa solo una técnica de LLM Compressor | No logra crear un modelo cuantizado |
| **Análisis de resultados** | Tabla y gráfico completos, con conclusiones sobre memoria, velocidad y calidad en su GPU | Tabla completa sin conclusiones | Sin tabla comparativa |
| **Publicación con Ngrok** | Arena pública funcionando y abierta desde otro dispositivo | Ngrok conecta pero sin verificar desde otro dispositivo | No intenta la publicación |
| **Reflexión y retos** | 5 respuestas razonadas e intenta al menos un reto | Respuestas incompletas o genéricas | Sin respuestas |
"""))

notebook = {
    "nbformat": 4, "nbformat_minor": 0,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"},
        "colab": {"provenance": [], "gpuType": "T4"},
        "accelerator": "GPU",
    },
    "cells": cells,
}

salida = Path(__file__).parent / "CuantizacionVLLM.ipynb"
salida.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"✅ {salida.name} generado con {len(cells)} celdas")
