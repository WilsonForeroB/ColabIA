"""Script para generar FineTuningQLoRA.ipynb (Actividad 17)."""
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
<a href="https://colab.research.google.com/github/WilsonForeroB/ColabIA/blob/develop/actividades/17-fine-tuning-qlora/FineTuningQLoRA.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# 🎓 Actividad 17 — Fine-tuning con QLoRA

## ¿Qué vas a construir?

Un **clasificador de tickets de soporte** a partir de un LLM pequeño. El modelo recibe un ticket en
texto libre y devuelve un **JSON** con la clasificación interna de la empresa:

```
  📨 "Hola, soy Ana López. Me habéis cobrado dos veces el Router X200. Es urgente."
                                   │
                                   ▼   LLM + adaptador LoRA entrenado hoy
  🏷️ {"categoria": "facturacion", "prioridad": "alta", "producto": "Router X200", "cliente": "Ana López"}
```

Un modelo genérico **entiende** el ticket, pero **no conoce nuestras reglas** (qué nombres de categoría
usamos, qué cuenta como prioridad `alta`, el formato exacto). Eso es justo lo que enseña el *fine-tuning*:
**el conocimiento es el mismo, solo cambia el comportamiento**.

## Del concepto a la práctica (sesión de Fine Tuning)

```
  SFT    → aprender con pares instrucción → respuesta esperada
  LoRA   → W' = W + A·B     (W congelado, solo se entrenan A y B: ~1% de los parámetros)
  QLoRA  → W en 4 bits + A·B en 16 bits   → cabe en una GPU T4 gratuita
```

## Mapa de la actividad

| Parte | Tema |
|-------|------|
| 1 | Preparar Colab: transformers, PEFT, TRL, bitsandbytes, Gradio y pyngrok |
| 2 | **LoRA a mano:** cuántos parámetros ahorra `W + A·B` |
| 3 | **Dataset:** generar tickets etiquetados y darles formato de entrenamiento |
| 4 | **Modelo base en 4 bits** (la "Q" de QLoRA) |
| 5 | **Evaluación ANTES** del entrenamiento |
| 6 | **Entrenamiento QLoRA** con `SFTTrainer` |
| 7 | **Evaluación DESPUÉS** y frases nunca vistas |
| 8 | Guardar el adaptador y fusionarlo con el modelo |
| 9 | Interfaz Gradio: modelo base vs modelo afinado |
| 10 | Reflexión |
| 11 | Retos opcionales |
| 12 | Publicación con Ngrok + limpieza + rúbrica |

**⏱️ Duración:** 110–130 minutos · **GPU:** T4 (*Entorno de ejecución → Cambiar tipo de entorno → T4 GPU*)

> 💡 **Recuerda:** tú solo ejecutas las celdas de arriba a abajo. Los comentarios del código explican todo.
"""))

# ─── PARTE 1 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## ⚙️ PARTE 1 — Preparar Colab

| Librería | ¿Para qué la usamos? |
|----------|----------------------|
| `transformers` | Cargar el modelo y el tokenizador desde HuggingFace |
| `bitsandbytes` | Comprimir los pesos a 4 bits (la "Q" de QLoRA) |
| `peft` | Implementación de LoRA: añade y entrena las matrices A y B |
| `trl` | `SFTTrainer`: el entrenador de *Supervised Fine-Tuning* |
| `gradio` + `pyngrok` | Interfaz y publicación |

```
  transformers ─► modelo Qwen2.5 ─► bitsandbytes (4 bits) ─► peft (A·B) ─► trl (entrena)
```
"""))

cells.append(code(r"""
# ============================================================
# CELDA 1.1 — Comprobar que tenemos GPU
# ============================================================
# Entrenar en CPU sería inviable: necesitamos la GPU para las multiplicaciones de matrices.

!nvidia-smi --query-gpu=name,memory.total,compute_cap --format=csv

# Si ves un error: Entorno de ejecución → Cambiar tipo de entorno → T4 GPU, y vuelve a empezar.
print('✅ Revisa arriba que aparezca la GPU (Tesla T4)')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 1.2 — Instalar las librerías de fine-tuning (1-2 min)
# ============================================================
# -U actualiza a la última versión: TRL y PEFT evolucionan rápido y se apoyan en
# funciones recientes de transformers.

!pip install -q -U transformers trl peft bitsandbytes accelerate datasets

print('✅ Librerías de fine-tuning instaladas')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 1.3 — Instalar Gradio y pyngrok
# ============================================================
# gradio>=5,<6 → interfaz web (versión fijada para que el notebook no cambie de comportamiento)
# pyngrok      → publicaremos la app al final

!pip install -q 'gradio>=5,<6' pyngrok

print('✅ Gradio y pyngrok instalados')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 1.4 — Verificar versiones y elegir el tipo de número de la GPU
# ============================================================
import torch, transformers, trl, peft

for nombre, modulo in [('torch', torch), ('transformers', transformers), ('trl', trl), ('peft', peft)]:
    print(f'   {nombre:<13} {modulo.__version__}')

# bfloat16 solo existe en GPUs de compute capability >= 8.0 (A100, L4...).
# La T4 (7.5) usa float16: mismo tamaño (16 bits) pero menos rango numérico.
BF16 = torch.cuda.get_device_capability() >= (8, 0)
DTYPE = torch.bfloat16 if BF16 else torch.float16

print(f'\nGPU: {torch.cuda.get_device_name()} · cálculos en {DTYPE}')
print('✅ Entorno listo')
"""))

# ─── PARTE 2 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🧮 PARTE 2 — LoRA a mano

En lugar de modificar una matriz de pesos enorme `W` (d × d), LoRA entrena dos matrices pequeñas:
`A` (d × r) y `B` (r × d). Su producto tiene el mismo tamaño que `W`, así que se puede **sumar**.

```
        W (congelado)          A           B           W' = W + (α/r)·A·B
   ┌──────────────────┐     ┌──┐   ┌──────────────┐
   │   1536 × 1536    │  +  │  │ × │   16 × 1536  │   = misma forma que W
   │  2.359.296 pesos │     │16│   └──────────────┘
   └──────────────────┘     └──┘    solo 49.152 pesos entrenables
                         1536 × 16
```
"""))

cells.append(code(r"""
# ============================================================
# CELDA 2.1 — Contar parámetros: matriz completa vs LoRA
# ============================================================
d = 1536    # Tamaño oculto de Qwen2.5-1.5B (cada capa de atención tiene matrices de 1536 × 1536)
r = 16      # Rango de LoRA: el "ancho" de las matrices A y B

completa = d * d                # Pesos de W
lora = d * r + r * d            # Pesos de A + pesos de B

print(f'Matriz W completa : {completa:>10,} parámetros')
print(f'LoRA (A + B), r={r}: {lora:>10,} parámetros  →  {lora / completa:.2%} de W')
print('✅ Con LoRA entrenamos una pequeña fracción de cada capa')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 2.2 — Comprobar que W + A·B tiene la misma forma que W
# ============================================================
W = torch.randn(d, d)                  # Pesos originales (congelados)
A = torch.randn(d, r) * 0.01           # Matriz A: se inicializa con valores pequeños aleatorios
B = torch.zeros(r, d)                  # Matriz B: se inicializa a CERO

W_nueva = W + A @ B                    # @ es la multiplicación de matrices

print('Forma de W      :', tuple(W.shape))
print('Forma de A·B    :', tuple((A @ B).shape))
# Como B empieza en cero, al principio A·B = 0 y el modelo se comporta EXACTAMENTE como el original.
print('¿W\' == W al inicio?', torch.equal(W_nueva, W))
print('✅ El entrenamiento solo moverá A y B; el modelo parte del comportamiento original')
"""))

cells.append(md(r"""
### Hiperparámetros que vas a usar

| Parámetro | Valor hoy | Qué controla | Si lo subes... |
|---|---|---|---|
| `r` | 16 | Tamaño de A y B | Más capacidad, más memoria |
| `lora_alpha` | 32 | Escala de la actualización (regla práctica: 2·r) | Cambios más fuertes |
| `target_modules` | `all-linear` | En qué capas se insertan A·B | Mejor adaptación, más parámetros |
| `learning_rate` | 2e-4 | Tamaño de cada paso de aprendizaje | Aprende rápido, pero puede volverse inestable |
| `num_train_epochs` | 2 | Veces que ve el dataset | Riesgo de **overfitting** |
| Nº de ejemplos | 300 | Datos de entrenamiento | Pocos → **underfitting** |
"""))

# ─── PARTE 3 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🗂️ PARTE 3 — Dataset de tickets

En un proyecto real exportarías tickets históricos ya etiquetados. Aquí los **generamos** con plantillas
para que toda la clase tenga los mismos datos.

**Truco para medir si generaliza:** la última frase de cada categoría **solo aparece en el test**.
Si el modelo acierta con ellas, ha aprendido la regla y no solo ha memorizado frases.
"""))

cells.append(code(r"""
# ============================================================
# CELDA 3.1 — Catálogos: productos, clientes y frases por categoría
# ============================================================
PRODUCTOS = ['Router X200', 'Smartwatch Fit3', 'Plan Fibra 600', 'Portátil Nova 14',
             'Cafetera BrewPro', 'Altavoz Sonix', 'Tablet Lumo 10', 'Impresora Inkjet P5']
NOMBRES = ['Ana', 'Luis', 'Marta', 'Carlos', 'Lucía', 'Javier', 'Sofía', 'Pablo', 'Elena', 'Diego']
APELLIDOS = ['García', 'López', 'Martínez', 'Sánchez', 'Pérez', 'Gómez', 'Ruiz', 'Díaz', 'Moreno']

# {p} = producto, {n} = un número. La ÚLTIMA frase de cada lista se reserva para el test.
PROBLEMAS = {
    'facturacion': ['me habéis cobrado dos veces el {p} este mes',
                    'la factura del {p} tiene un importe que no cuadra',
                    'quiero que me devolváis el dinero del {p}',
                    'no me ha llegado la factura de mi {p}',
                    'en el extracto del banco aparece un cargo del {p} que no reconozco'],
    'soporte_tecnico': ['el {p} se queda colgado al arrancar',
                        'no consigo conectar el {p} a la wifi',
                        'el {p} muestra el error E-{n} desde ayer',
                        'la app del {p} se cierra sola',
                        'desde la última actualización el {p} va lentísimo y se reinicia'],
    'envio': ['mi pedido del {p} lleva {n} días sin llegar',
              'me ha llegado el {p} con la caja destrozada',
              'el seguimiento del {p} no se actualiza',
              'he recibido un {p} que no pedí',
              'el repartidor dice que entregó el {p} pero yo no tengo nada'],
    'cuenta': ['no puedo iniciar sesión para gestionar mi {p}',
               'quiero cambiar el email asociado a mi {p}',
               'me han bloqueado la cuenta después de comprar el {p}',
               'quiero darme de baja del servicio del {p}',
               'alguien ha cambiado la contraseña de mi cuenta del {p} sin mi permiso'],
}

# La prioridad se deduce de cómo se expresa el cliente: esa es nuestra "regla de negocio"
PRIORIDAD = {
    'alta': ['Es urgente, lo necesito hoy.', 'Mi negocio está parado por esto.',
             'Necesito una solución YA, es inaceptable.', 'Por favor, prioridad máxima.'],
    'media': ['¿Podéis revisarlo esta semana?', 'Agradecería una respuesta pronto.',
              'Me gustaría resolverlo en los próximos días.', 'Espero noticias vuestras en breve.'],
    'baja': ['No corre prisa.', 'Cuando podáis, sin urgencia.',
             'Solo quería que lo supierais.', 'Sin prisa, es por si os sirve.'],
}
SALUDOS = ['Hola, soy {c}.', 'Buenas, me llamo {c}.', 'Buenos días, os escribe {c}.', '']
DESPEDIDAS = ['Gracias.', 'Un saludo, {c}', 'Atentamente, {c}', 'Saludos.']

print(f'{len(PRODUCTOS)} productos · {len(PROBLEMAS)} categorías · {len(PRIORIDAD)} prioridades')
print('✅ Catálogos definidos')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 3.2 — Función que genera un ticket con su etiqueta
# ============================================================
import random, json

def generar_ticket(rng, test=False):
    # rng es un generador aleatorio con semilla: así todos obtenemos los mismos tickets
    categoria = rng.choice(list(PROBLEMAS))
    prioridad = rng.choice(list(PRIORIDAD))
    producto = rng.choice(PRODUCTOS)
    cliente = f'{rng.choice(NOMBRES)} {rng.choice(APELLIDOS)}'

    # En entrenamiento excluimos la última frase ([:-1]); en test se usan todas
    frases = PROBLEMAS[categoria] if test else PROBLEMAS[categoria][:-1]
    problema = rng.choice(frases).format(p=producto, n=rng.randint(2, 999))

    saludo, despedida = rng.choice(SALUDOS), rng.choice(DESPEDIDAS)
    if '{c}' not in saludo + despedida:          # El nombre del cliente debe aparecer siempre
        saludo = 'Hola, soy {c}.'

    partes = [saludo.format(c=cliente),
              problema[0].upper() + problema[1:] + '.',    # Mayúscula inicial y punto final
              rng.choice(PRIORIDAD[prioridad]),
              despedida.format(c=cliente)]
    texto = ' '.join(p for p in partes if p)               # Unimos saltando partes vacías

    etiqueta = {'categoria': categoria, 'prioridad': prioridad, 'producto': producto, 'cliente': cliente}
    return texto, etiqueta

print('✅ Función generar_ticket() lista')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 3.3 — Probar el generador
# ============================================================
rng_prueba = random.Random(0)      # Semilla 0: siempre los mismos 3 ejemplos

for _ in range(3):
    texto, etiqueta = generar_ticket(rng_prueba)
    print('📨', texto)
    print('🏷️', json.dumps(etiqueta, ensure_ascii=False), '\n')

print('✅ El generador produce tickets variados con su etiqueta correcta')
"""))

cells.append(md(r"""
### Formato de entrenamiento: *prompt → completion*

Cada ejemplo es una conversación partida en dos:
- **prompt**: instrucciones del sistema + el ticket del usuario
- **completion**: la respuesta correcta del asistente (el JSON)

Con este formato, `SFTTrainer` calcula el error **solo sobre la completion**: no queremos que el modelo
aprenda a escribir tickets, sino a **responderlos**.
"""))

cells.append(code(r"""
# ============================================================
# CELDA 3.4 — Construir los datasets de entrenamiento y test
# ============================================================
from datasets import Dataset

# Instrucciones que verá el modelo en todos los casos (antes y después de entrenar)
SISTEMA = ('Eres un clasificador de tickets de soporte. Devuelve SOLO un JSON con las claves '
           'categoria (facturacion | soporte_tecnico | envio | cuenta), '
           'prioridad (alta | media | baja), producto y cliente.')

def a_ejemplo(texto, etiqueta):
    # Convierte un ticket en el formato prompt/completion que espera SFTTrainer
    return {
        'prompt': [{'role': 'system', 'content': SISTEMA},
                   {'role': 'user', 'content': texto}],
        'completion': [{'role': 'assistant', 'content': json.dumps(etiqueta, ensure_ascii=False)}],
    }

# 🔧 PARÁMETROS: tamaño de cada conjunto
N_TRAIN, N_TEST = 300, 60

rng_train, rng_test = random.Random(42), random.Random(2024)   # Semillas distintas → tickets distintos
dataset_train = Dataset.from_list([a_ejemplo(*generar_ticket(rng_train)) for _ in range(N_TRAIN)])
tickets_test = [generar_ticket(rng_test, test=True) for _ in range(N_TEST)]   # Lista de (texto, etiqueta)

print(dataset_train)
print(json.dumps(dataset_train[0], ensure_ascii=False, indent=1))
print(f'✅ {N_TRAIN} ejemplos de entrenamiento y {N_TEST} de test')
"""))

# ─── PARTE 4 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🗜️ PARTE 4 — Modelo base en 4 bits (la "Q" de QLoRA)

`BitsAndBytesConfig` comprime los pesos a **NF4** al cargarlos. Los pesos en 4 bits quedan **congelados**;
solo las matrices A y B (en 16 bits) se entrenarán.
"""))

cells.append(code(r"""
# ============================================================
# CELDA 4.1 — Configurar la cuantización a 4 bits
# ============================================================
from transformers import BitsAndBytesConfig

config_4bits = BitsAndBytesConfig(
    load_in_4bit=True,                   # Guardar los pesos en 4 bits
    bnb_4bit_quant_type='nf4',           # NormalFloat4: 16 niveles repartidos como una campana de Gauss
    bnb_4bit_use_double_quant=True,      # Cuantiza también las escalas → ahorra ~0,4 bits por peso
    bnb_4bit_compute_dtype=DTYPE,        # Los cálculos se hacen en 16 bits (más precisión)
)

print('✅ Configuración de 4 bits lista')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 4.2 — Cargar el tokenizador
# ============================================================
from transformers import AutoTokenizer

# 🔧 PARÁMETRO: modelo base. El de 0.5B entrena ~3 veces más rápido si vas justo de tiempo.
MODELO_ID = 'Qwen/Qwen2.5-1.5B-Instruct'    # Alternativa: 'Qwen/Qwen2.5-0.5B-Instruct'

tokenizador = AutoTokenizer.from_pretrained(MODELO_ID)

print(f'Vocabulario: {len(tokenizador):,} tokens')
print('✅ Tokenizador cargado')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 4.3 — Cargar el modelo en 4 bits
# ============================================================
from transformers import AutoModelForCausalLM

modelo = AutoModelForCausalLM.from_pretrained(
    MODELO_ID,
    quantization_config=config_4bits,    # Aplica la compresión a 4 bits al cargar
    device_map='auto',                   # Coloca el modelo en la GPU automáticamente
    torch_dtype=DTYPE,                   # Las capas no cuantizadas, en 16 bits
)

print(f'VRAM ocupada en 4 bits: {torch.cuda.memory_allocated() / 2**30:.2f} GiB  (en FP16 serían ~3 GiB)')
print('✅ Modelo base cargado en 4 bits')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 4.4 — Probar el modelo base con un ticket
# ============================================================
texto, etiqueta = tickets_test[0]

# apply_chat_template construye el prompt con las marcas de chat del modelo.
# add_generation_prompt=True añade el inicio del turno del asistente para que responda.
prompt = tokenizador.apply_chat_template(
    [{'role': 'system', 'content': SISTEMA}, {'role': 'user', 'content': texto}],
    tokenize=False, add_generation_prompt=True)

entrada = tokenizador(prompt, return_tensors='pt').to(modelo.device)     # Texto → tokens en la GPU
salida = modelo.generate(**entrada, max_new_tokens=80, do_sample=False)  # do_sample=False → determinista
respuesta = tokenizador.decode(salida[0, entrada['input_ids'].shape[1]:], skip_special_tokens=True)

print('📨', texto)
print('✅ esperado:', json.dumps(etiqueta, ensure_ascii=False))
print('🤖 modelo  :', respuesta.strip())
print('✅ El modelo base responde (fíjate en si respeta nuestras categorías)')
"""))

# ─── PARTE 5 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 📏 PARTE 5 — Evaluación ANTES del entrenamiento

Usamos métricas sencillas y objetivas sobre los 60 tickets de test:
- **json_valido**: ¿la salida se puede leer como JSON?
- **acierto por campo**: ¿coincide exactamente con la etiqueta?
- **todo_ok**: los 4 campos bien → el ticket se enruta sin intervención humana
"""))

cells.append(code(r"""
# ============================================================
# CELDA 5.1 — Función para generar respuestas en lote
# ============================================================
@torch.no_grad()        # No calculamos gradientes: solo inferencia (más rápido, menos memoria)
def generar(modelo, textos, tam_lote=16, max_tokens=80):
    tokenizador.padding_side = 'left'    # Para generar en lote, el relleno va a la IZQUIERDA
    respuestas = []
    for i in range(0, len(textos), tam_lote):
        prompts = [tokenizador.apply_chat_template(
                       [{'role': 'system', 'content': SISTEMA}, {'role': 'user', 'content': t}],
                       tokenize=False, add_generation_prompt=True)
                   for t in textos[i:i + tam_lote]]
        entrada = tokenizador(prompts, return_tensors='pt', padding=True).to(modelo.device)
        salida = modelo.generate(**entrada, max_new_tokens=max_tokens, do_sample=False,
                                 use_cache=True, pad_token_id=tokenizador.pad_token_id)
        # Quitamos los tokens del prompt y nos quedamos solo con lo que generó el modelo
        respuestas += tokenizador.batch_decode(salida[:, entrada['input_ids'].shape[1]:],
                                               skip_special_tokens=True)
    tokenizador.padding_side = 'right'   # Restauramos el valor por defecto para el entrenamiento
    return respuestas

print('✅ Función generar() lista')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 5.2 — Función para puntuar las respuestas
# ============================================================
import re
import pandas as pd

def leer_json(texto):
    # Busca el primer bloque {...} en la respuesta y lo convierte en diccionario
    encontrado = re.search(r'\{.*\}', texto, re.S)    # re.S: el punto también acepta saltos de línea
    try:
        return json.loads(encontrado.group(0)) if encontrado else None
    except json.JSONDecodeError:
        return None                                   # Parece JSON pero está mal formado

def evaluar(modelo, nombre):
    respuestas = generar(modelo, [t for t, _ in tickets_test])
    filas = []
    for (_, esperado), respuesta in zip(tickets_test, respuestas):
        predicho = leer_json(respuesta)
        fila = {'json_valido': predicho is not None}
        for campo in esperado:      # Comparamos cada campo sin distinguir mayúsculas
            fila[campo] = bool(predicho) and str(predicho.get(campo, '')).strip().lower() == esperado[campo].lower()
        fila['todo_ok'] = all(fila[c] for c in esperado)
        filas.append(fila)
    # La media de True/False es el porcentaje de aciertos
    return (pd.DataFrame(filas).mean() * 100).round(1).rename(nombre), respuestas

print('✅ Función evaluar() lista')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 5.3 — Evaluar el modelo base (1-2 min)
# ============================================================
puntos_antes, respuestas_antes = evaluar(modelo, 'ANTES (%)')

print(puntos_antes.to_string(), '\n')
for (texto, esperado), respuesta in list(zip(tickets_test, respuestas_antes))[:3]:
    print('📨', texto)
    print('✅', json.dumps(esperado, ensure_ascii=False))
    print('🤖', respuesta.strip(), '\n')

print('✅ Evaluación inicial registrada: ¿inventa categorías? ¿añade texto fuera del JSON?')
"""))

# ─── PARTE 6 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🏋️ PARTE 6 — Entrenamiento QLoRA

```
  ticket ─► modelo (W 4 bits congelado + A·B) ─► respuesta ─► comparar con el JSON correcto
                         ▲                                              │
                         └──────── ajustar SOLO A y B (backprop) ◄──────┘   × cientos de pasos
```
"""))

cells.append(code(r"""
# ============================================================
# CELDA 6.1 — Configurar LoRA
# ============================================================
from peft import LoraConfig

config_lora = LoraConfig(
    r=16,                          # Rango de A·B (ver Parte 2)
    lora_alpha=32,                 # Escala de la actualización: W' = W + (alpha/r)·A·B
    lora_dropout=0.05,             # Apaga un 5% de conexiones al azar → reduce el overfitting
    target_modules='all-linear',   # Añade A·B en todas las capas lineales (atención y MLP)
    task_type='CAUSAL_LM',         # Tipo de modelo: genera texto token a token
)

print('✅ Configuración LoRA lista')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 6.2 — Configurar el entrenamiento
# ============================================================
from trl import SFTConfig

config_entreno = SFTConfig(
    output_dir='/content/qlora-tickets',   # Carpeta de trabajo del entrenador
    num_train_epochs=2,                    # Pasadas completas por el dataset
    per_device_train_batch_size=8,         # Ejemplos procesados a la vez en la GPU
    gradient_accumulation_steps=2,         # Acumula 2 lotes antes de actualizar → lote efectivo de 16
    learning_rate=2e-4,                    # Alto comparado con un full fine-tuning: A y B parten de cero
    lr_scheduler_type='cosine',            # El learning rate baja suavemente hasta el final
    warmup_ratio=0.05,                     # El primer 5% de pasos sube el LR poco a poco (estabilidad)
    logging_steps=5,                       # Muestra la pérdida cada 5 pasos
    max_length=512,                        # Tokens máximos por ejemplo (nuestros tickets son cortos)
    bf16=BF16, fp16=not BF16,              # Precisión mixta según la GPU (T4 → fp16)
    gradient_checkpointing=True,           # Recalcula activaciones en vez de guardarlas → menos VRAM
    save_strategy='no',                    # No guardamos checkpoints intermedios (ahorra disco y tiempo)
    report_to='none',                      # Sin servicios externos de seguimiento (wandb, etc.)
)

print('✅ Configuración de entrenamiento lista')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 6.3 — Crear el entrenador
# ============================================================
from trl import SFTTrainer

# SFTTrainer añade las matrices A·B al modelo (peft_config) y prepara el modelo de 4 bits para entrenar
entrenador = SFTTrainer(
    model=modelo,
    args=config_entreno,
    train_dataset=dataset_train,
    peft_config=config_lora,
    processing_class=tokenizador,
)

# Muestra cuántos parámetros se van a entrenar frente al total
entrenador.model.print_trainable_parameters()
print('✅ Entrenador listo: fíjate en el % de parámetros entrenables')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 6.4 — Entrenar (5-10 min en T4)
# ============================================================
# Observa la columna "loss": debe bajar rápido al principio y luego estabilizarse.
# Si llega casi a 0 muy pronto, sospecha de overfitting (memorización).

estadisticas = entrenador.train()

print(f"\n⏱️ Duración: {estadisticas.metrics['train_runtime']:.0f} s")
print(f'💾 VRAM máxima usada: {torch.cuda.max_memory_allocated() / 2**30:.2f} GiB')
print('✅ Entrenamiento completado')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 6.5 — Dibujar la curva de pérdida
# ============================================================
import matplotlib.pyplot as plt

# log_history guarda lo que el entrenador fue registrando; nos quedamos con las entradas de 'loss'
historial = pd.DataFrame([x for x in entrenador.state.log_history if 'loss' in x])

plt.figure(figsize=(8, 3.5))
plt.plot(historial['step'], historial['loss'], marker='o')
plt.xlabel('paso de entrenamiento')
plt.ylabel('pérdida (loss)')
plt.title('Curva de pérdida')
plt.grid(alpha=0.3)
plt.show()

print('✅ Curva de pérdida dibujada')
"""))

# ─── PARTE 7 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 📈 PARTE 7 — Evaluación DESPUÉS del entrenamiento

Mismos 60 tickets de test, misma función de evaluación. Solo cambia el modelo.
"""))

cells.append(code(r"""
# ============================================================
# CELDA 7.1 — Comparar antes y después
# ============================================================
modelo_ft = entrenador.model     # El modelo con el adaptador LoRA ya entrenado
modelo_ft.eval()                 # Modo inferencia (desactiva el dropout)

puntos_despues, respuestas_despues = evaluar(modelo_ft, 'DESPUÉS (%)')

display(pd.concat([puntos_antes, puntos_despues], axis=1))
print('✅ Comparación lista: haz una captura para la entrega')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 7.2 — ¿Generaliza a frases nunca vistas?
# ============================================================
# Buscamos en el test los tickets que usan la frase reservada (la última de cada categoría)
inicios_nuevos = [PROBLEMAS[c][-1].split('{')[0][:25].lower() for c in PROBLEMAS]
indices = [i for i, (t, _) in enumerate(tickets_test) if any(x in t.lower() for x in inicios_nuevos)]

print(f'{len(indices)} tickets del test usan frases que el modelo NUNCA vio al entrenar:\n')
for i in indices[:4]:
    texto, esperado = tickets_test[i]
    print('📨', texto)
    print('✅', json.dumps(esperado, ensure_ascii=False))
    print('🤖', respuestas_despues[i].strip(), '\n')

print('✅ Revisa si acierta también con estas frases')
"""))

# ─── PARTE 8 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 💾 PARTE 8 — Guardar y fusionar

Tras QLoRA **no se guarda el modelo**, solo las matrices A y B: el **adaptador** (decenas de MB).
Para desplegar hay dos caminos:

```
  1) base + adaptador   → un modelo base, muchos adaptadores (uno por cliente o tarea)
  2) fusionar W' = W + A·B → un modelo normal, que luego se puede cuantizar (Actividad 16)
```
"""))

cells.append(code(r"""
# ============================================================
# CELDA 8.1 — Guardar solo el adaptador LoRA
# ============================================================
CARPETA_ADAPTADOR = '/content/lora-tickets'

modelo_ft.save_pretrained(CARPETA_ADAPTADOR)        # Guarda A, B y su configuración
tokenizador.save_pretrained(CARPETA_ADAPTADOR)      # El tokenizador acompaña al adaptador

!du -sh {CARPETA_ADAPTADOR}
!ls -lh {CARPETA_ADAPTADOR}
print('✅ Adaptador guardado: compara su tamaño con los ~3 GB del modelo')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 8.2 — Fusionar el adaptador con el modelo original (2-3 min, en CPU)
# ============================================================
# Fusionamos sobre el modelo ORIGINAL en 16 bits (no sobre el de 4 bits) para no arrastrar
# el error de la cuantización. Lo hacemos en CPU para no ocupar la GPU que usa la interfaz.
from peft import PeftModel

base_16bits = AutoModelForCausalLM.from_pretrained(MODELO_ID, torch_dtype=torch.float16, device_map='cpu')
fusionado = PeftModel.from_pretrained(base_16bits, CARPETA_ADAPTADOR).merge_and_unload()  # W' = W + A·B

CARPETA_FUSIONADO = '/content/qwen-tickets-fusionado'
fusionado.save_pretrained(CARPETA_FUSIONADO)
tokenizador.save_pretrained(CARPETA_FUSIONADO)

del base_16bits, fusionado      # Liberamos la RAM: ya está guardado en disco
!du -sh {CARPETA_FUSIONADO}
print('✅ Modelo fusionado guardado: se puede cuantizar con la Actividad 16 o servir con vLLM')
"""))

# ─── PARTE 9 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🖥️ PARTE 9 — Interfaz Gradio: base vs afinado

PEFT permite **apagar el adaptador** temporalmente con `disable_adapter()`. Así comparamos el modelo
base y el afinado con **un solo modelo en memoria**.

```
  ticket ─┬─► modelo con adaptador apagado   ─► 🧊 respuesta base
          └─► modelo con adaptador encendido ─► 🔥 respuesta afinada
```
"""))

cells.append(code(r"""
# ============================================================
# CELDA 9.1 — Función que clasifica un ticket con ambos modelos
# ============================================================
def clasificar(ticket):
    with modelo_ft.disable_adapter():             # Dentro de este bloque, A·B no se aplica
        base = generar(modelo_ft, [ticket])[0].strip()
    afinado = generar(modelo_ft, [ticket])[0].strip()
    # Si la respuesta afinada es JSON válido la mostramos bonita; si no, tal cual
    datos = leer_json(afinado)
    return base, json.dumps(datos, ensure_ascii=False, indent=2) if datos else afinado

# Prueba individual antes de integrarla en la interfaz
b, a = clasificar('Buenas, me llamo Irene Castro. El Router X200 parpadea en rojo y no hay internet. '
                  'Mi negocio está parado por esto.')
print('🧊 BASE   :', b)
print('🔥 AFINADO:', a)
print('✅ Función clasificar() probada')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 9.2 — Construir la interfaz con gr.Blocks
# ============================================================
import gradio as gr

CSS = '.json-salida textarea {font-family: monospace}'

EJEMPLOS = [
    'Hola, soy Marta Ruiz. La impresora Inkjet P5 no imprime en color desde ayer. Cuando podáis, sin urgencia.',
    'Me han cobrado dos veces el Plan Fibra 600. Es inaceptable, necesito una solución ya. Carlos Díaz',
    'Buenos días, os escribe Pablo Gómez. El pedido de la Tablet Lumo 10 no llega. ¿Podéis revisarlo esta semana?',
]

with gr.Blocks(title='Clasificador de tickets', css=CSS) as demo:
    gr.Markdown('# 🎫 Clasificador de tickets\nEl mismo modelo **sin** y **con** el adaptador LoRA entrenado hoy.')
    ticket = gr.Textbox(label='Ticket del cliente', lines=4, placeholder='Escribe un ticket...')
    boton = gr.Button('Clasificar', variant='primary')
    with gr.Row():
        salida_base = gr.Textbox(label='🧊 Modelo base', lines=8, elem_classes='json-salida')
        salida_ft = gr.Textbox(label='🔥 Modelo afinado (QLoRA)', lines=8, elem_classes='json-salida')
    gr.Examples(EJEMPLOS, inputs=ticket)
    # click(función, entradas, salidas): al pulsar, Gradio llama a clasificar() con el texto
    boton.click(clasificar, inputs=ticket, outputs=[salida_base, salida_ft])

print('✅ Interfaz construida')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 9.3 — Lanzar la interfaz dentro de Colab
# ============================================================
demo.launch(quiet=True)

print('✅ Interfaz visible arriba 👆 — prueba los ejemplos y escribe tus propios tickets')
"""))

# ─── PARTE 10 ────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🤔 PARTE 10 — Reflexión

Responde en esta misma celda (doble clic para editarla). Entre 2 y 5 líneas por pregunta.

1. **Conceptual:** ¿Qué diferencia hay entre un *full fine-tuning*, LoRA y QLoRA? Usa los números que viste en la Parte 2 y en la celda 6.3.

   *Tu respuesta:*

2. **Código:** ¿Por qué en la celda 2.2 la matriz `B` empieza en cero? ¿Y por qué en la celda 3.4 usamos el formato `prompt`/`completion` en lugar de un único texto?

   *Tu respuesta:*

3. **Implicaciones:** El modelo afinado clasifica tickets automáticamente. ¿Qué riesgos tendría ponerlo en producción sin supervisión? ¿Qué pasaría si los datos de entrenamiento tuvieran sesgos (por ejemplo, ciertos clientes siempre con prioridad baja)?

   *Tu respuesta:*

4. **Comparativa:** Para este problema, ¿qué ventajas e inconvenientes tiene el fine-tuning frente a escribir un *prompt* muy detallado con ejemplos (*few-shot*)? ¿Y frente a RAG?

   *Tu respuesta:*

5. **Resultados:** ¿Qué campo mejoró más tras el entrenamiento y por qué crees que el campo `cliente` ya funcionaba bien antes?

   *Tu respuesta:*
"""))

# ─── PARTE 11 ────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🏆 PARTE 11 — Retos opcionales

Cada reto tiene una celda vacía debajo. No están resueltos: solo una pista para empezar.

- **Reto A — Underfitting vs overfitting:** repite el entrenamiento con `N_TRAIN = 20` y, después, con `N_TRAIN = 50` y `num_train_epochs = 10`. Compara `todo_ok` y la curva de pérdida.
  *Pista:* libera memoria con `del entrenador, modelo_ft, modelo; gc.collect(); torch.cuda.empty_cache()` y vuelve a ejecutar desde la celda 3.4 (cambiando el parámetro) hasta la 7.1.

- **Reto B — Servir el adaptador con vLLM:** vLLM puede cargar el modelo base una vez y aplicar adaptadores LoRA por petición.
  *Pista:* en un notebook nuevo (vLLM cambia la versión de PyTorch), sube la carpeta del adaptador y usa `vllm serve Qwen/Qwen2.5-1.5B-Instruct --enable-lora --max-lora-rank 16 --lora-modules tickets=/content/lora-tickets`. Revisa la Actividad 00b para el arranque del servidor en Colab.

- **Reto C — Rango mínimo:** ¿basta con `r = 2` para esta tarea? Entrena con `r = 2, lora_alpha = 4` y compara el % de parámetros entrenables y los resultados.
  *Pista:* solo cambia la celda 6.1; recuerda liberar memoria y recargar el modelo (celda 4.3) antes.
"""))

for letra, num in [('A', 1), ('B', 2), ('C', 3)]:
    cells.append(code(f"""
# ============================================================
# CELDA 11.{num} — Reto {letra}: tu espacio para experimentar
# ============================================================
# (celda vacía a propósito)
"""))

# ─── PARTE 12 — NGROK ────────────────────────────────────────────────────────
cells.append(md(r"""
## 🌐 PARTE 12 — Publicación con Ngrok

Hasta ahora el clasificador solo vive dentro de Colab. Con **Ngrok** creamos un **túnel** hacia Internet
para que tus compañeros le envíen sus propios tickets desde el navegador.

```
  Compañero (navegador)
        │  https://xxxx.ngrok-free.app
        ▼
  Servidor de Ngrok  ───túnel───►  Colab (localhost:7860)
                                          │
                                          ▼
                              App Gradio ──► Qwen2.5 + adaptador LoRA
```

**Antes de empezar:** crea una cuenta gratuita en [ngrok.com](https://ngrok.com), copia tu *Authtoken*
y guárdalo en Colab: icono 🔑 **Secrets** → *Add new secret* → nombre `NGROK_TOKEN` → pega el token → activa *Notebook access*.
"""))

cells.append(code(r"""
# ============================================================
# CELDA 12.1 — Instalar pyngrok
# ============================================================
# Ya lo instalamos en la celda 1.3; repetirlo es instantáneo y garantiza que esté
# disponible aunque hayas reiniciado la sesión.

!pip install -q pyngrok

print('✅ pyngrok instalado')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 12.2 — Autenticar con el token de Ngrok
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
# CELDA 12.3 — Abrir el túnel y relanzar la app
# ============================================================
# Orden importante: cerrar lo anterior → abrir túnel → lanzar la app.

demo.close()    # Cierra la app lanzada en la Parte 9 para liberar el puerto
ngrok.kill()    # Cierra túneles anteriores (el plan gratuito solo permite uno a la vez)

# connect(7860) crea un túnel público hacia el puerto local 7860
tunel = ngrok.connect(7860)
print(f'🌍 URL pública: {tunel.public_url}')
print('   Compártela con tus compañeros para que prueben sus propios tickets.')

# server_name='0.0.0.0' = acepta conexiones externas (las que llegan por el túnel)
# server_port=7860       = el mismo puerto que expusimos con Ngrok
# share=False            = no usamos el enlace temporal de Gradio; Ngrok es más estable
demo.launch(server_name='0.0.0.0', server_port=7860, share=False, quiet=True)

print('✅ App publicada con Ngrok')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 12.4 — Verificar los túneles activos
# ============================================================
# get_tunnels() lista los túneles abiertos en esta sesión.

tuneles = ngrok.get_tunnels()

if tuneles:
    print(f'✅ {len(tuneles)} túnel(es) activo(s):')
    for t in tuneles:
        print(f'   {t.public_url}  →  {t.config["addr"]}')
else:
    print('❌ No hay túneles activos. Ejecuta de nuevo la celda 12.3.')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 12.5 — (Opcional) Dominio estático
# ============================================================
# Con el plan gratuito puedes reclamar UN dominio fijo en dashboard.ngrok.com → Domains.
# Así la URL no cambia entre sesiones. Si no tienes uno, sáltate esta celda.

DOMINIO_ESTATICO = ''   # Ej: 'mi-clasificador-tickets.ngrok-free.app'

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
import gc

# 1. Cerrar el túnel Ngrok
ngrok.kill()
print('✅ Túnel Ngrok cerrado')

# 2. Cerrar la interfaz Gradio
demo.close()
print('✅ Interfaz Gradio cerrada')

# 3. Procesos del sistema: esta actividad no lanza servidores en segundo plano
print('✅ No hay procesos extra que detener')

# 4. Liberar la memoria GPU del modelo y del entrenador
del entrenador, modelo_ft, modelo   # Borra las referencias al modelo
gc.collect()                        # Recolector de basura de Python
torch.cuda.empty_cache()            # Devuelve a la GPU la memoria reservada por PyTorch
print('✅ Memoria GPU liberada')

print('\n✅ Todos los recursos liberados. Puedes cerrar el notebook.')
"""))

cells.append(md(r"""
## 📊 Rúbrica de Evaluación

| Criterio | Excelente (5) | Satisfactorio (3) | En desarrollo (1) |
|----------|---------------|-------------------|-------------------|
| **Preparación y dataset** | Entorno sin errores; explica el formato prompt/completion y por qué hay frases reservadas para el test | Ejecuta las Partes 1-3 sin explicar el formato | No logra generar el dataset |
| **LoRA y QLoRA** | Relaciona `W + A·B`, el % de parámetros entrenables y la carga en 4 bits con sus propios números | Ejecuta las Partes 2 y 4 pero explica solo parte | No distingue LoRA de QLoRA |
| **Entrenamiento** | Entrena sin errores e interpreta la curva de pérdida | Entrena pero no interpreta la curva | El entrenamiento falla |
| **Evaluación** | Tabla antes/después completa y análisis de las frases nunca vistas | Tabla completa sin análisis | Sin comparación |
| **Publicación con Ngrok** | App pública funcionando y abierta desde otro dispositivo | Ngrok conecta pero sin verificar desde otro dispositivo | No intenta la publicación |
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

salida = Path(__file__).parent / "FineTuningQLoRA.ipynb"
salida.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"✅ {salida.name} generado con {len(cells)} celdas")
