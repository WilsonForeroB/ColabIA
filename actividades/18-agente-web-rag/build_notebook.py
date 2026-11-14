"""Script para generar AgenteWebRAG.ipynb (Actividad 18)."""
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
<a href="https://colab.research.google.com/github/WilsonForeroB/ColabIA/blob/develop/actividades/18-agente-web-rag/AgenteWebRAG.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# 🎓 Actividad 18 — Agente de búsqueda web + RAG sobre las páginas encontradas

## ¿Qué vas a construir?

Un sistema en **dos fases** con LangChain y un LLM local (Ollama):

1. **Fase Agente:** un agente con la herramienta `buscar_en_internet` decide qué buscar, lee los resultados
   y **devuelve una respuesta** citando las URLs.
2. **Fase RAG:** las páginas que encontró el agente se **descargan completas, se dividen en fragmentos,
   se convierten en vectores y se guardan en FAISS**. Después le hacemos preguntas de seguimiento que se
   responden **solo con el contenido real de esas webs**.

```
                 ┌──────────────── FASE 1: AGENTE ─────────────────┐
  Pregunta ──► LLM (qwen3:4b) ──tool_call──► buscar_en_internet (DuckDuckGo)
                 ▲                                   │
                 └──────────── ToolMessage ◄─────────┘   → respuesta + URLs
                 └─────────────────────────────────────────────────┘
                                     │ URLs encontradas
                 ┌──────────────── FASE 2: RAG ────────────────────┐
  WebBaseLoader ─► TextSplitter ─► OllamaEmbeddings ─► FAISS
                                                          │ top-k fragmentos
  Pregunta de seguimiento ─► Prompt + contexto ─► LLM ─► Respuesta con fuentes
                 └─────────────────────────────────────────────────┘
```

**¿Por qué dos fases?** El buscador solo devuelve un *snippet* (2-3 líneas) de cada página. El agente
responde rápido, pero con poca información. El RAG trabaja con **el texto completo** de esas mismas páginas.

## Mapa de la actividad

| Parte | Tema |
|-------|------|
| 1 | Preparar Colab: Ollama, LangChain, modelos y configuración |
| 2 | **La herramienta:** `buscar_en_internet` con DuckDuckGo |
| 3 | **El agente:** tool calling y bucle Razonar → Actuar → Observar |
| 4 | **Cargar las webs** encontradas con `WebBaseLoader` |
| 5 | **Indexar:** fragmentos, embeddings y FAISS |
| 6 | **Cadena RAG** con LCEL y preguntas de seguimiento |
| 7 | Pipeline completo: de la pregunta al RAG en una función |
| 8 | Interfaz Gradio con las dos fases |
| 9 | Reflexión |
| 10 | Retos opcionales |
| 11 | Publicación con Ngrok + limpieza + rúbrica |

**⏱️ Duración:** 90–120 minutos · **GPU:** T4 (*Entorno de ejecución → Cambiar tipo de entorno → T4 GPU*)

> 💡 **Recuerda:** tú solo ejecutas las celdas de arriba a abajo. Los comentarios del código explican todo.
"""))

# ─── PARTE 1 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## ⚙️ PARTE 1 — Preparar Colab

| Librería | ¿Para qué la usamos? |
|----------|----------------------|
| Ollama | Servidor que ejecuta el LLM y el modelo de embeddings en la GPU |
| `ddgs` | Buscador DuckDuckGo (no necesita API key) |
| `langchain-core` | Mensajes, herramientas (`@tool`), prompts y LCEL |
| `langchain-ollama` | `ChatOllama` y `OllamaEmbeddings` |
| `langchain-community` | `WebBaseLoader` y el vectorstore `FAISS` |
| `langchain-text-splitters` | Dividir el texto en fragmentos |
| `faiss-cpu` + `beautifulsoup4` | Búsqueda vectorial y lectura del HTML |
| `gradio` + `pyngrok` | Interfaz y publicación |
"""))

cells.append(code(r"""
# ============================================================
# CELDA 1.1 — Comprobar que tenemos GPU
# ============================================================
# Sin GPU el LLM tarda 10-20 veces más y la actividad se vuelve inviable.

!nvidia-smi --query-gpu=name,memory.total --format=csv

# Si ves un error: Entorno de ejecución → Cambiar tipo de entorno → T4 GPU, y vuelve a empezar.
print('✅ Revisa arriba que aparezca la GPU (Tesla T4)')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 1.2 — Instalar Ollama (1-2 min)
# ============================================================
# zstd     → descomprime el binario de Ollama
# pciutils → permite a Ollama detectar la GPU (sin él, ¡correría en CPU!)
import os
os.environ['DEBIAN_FRONTEND'] = 'noninteractive'   # Evita que apt haga preguntas interactivas

!sudo apt-get update -qq 2>/dev/null
!sudo apt-get install -y -qq zstd pciutils 2>/dev/null
!curl -fsSL https://ollama.com/install.sh | sh 2>&1 | grep -v systemd

!ollama --version
print('✅ Ollama instalado')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 1.3 — Instalar LangChain y librerías de búsqueda y RAG
# ============================================================
# -U actualiza a la última versión: LangChain evoluciona rápido y conviene
# que todas sus piezas (core, community, ollama) sean compatibles entre sí.

!pip install -q -U ddgs langchain-core langchain-community langchain-ollama \
                langchain-text-splitters faiss-cpu beautifulsoup4

print('✅ LangChain y librerías de RAG instaladas')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 1.4 — Instalar Gradio y pyngrok
# ============================================================
# gradio>=5,<6 → interfaz web (versión fijada para que el notebook no cambie de comportamiento)
# pyngrok      → publicaremos la app al final

!pip install -q 'gradio>=5,<6' pyngrok

print('✅ Gradio y pyngrok instalados')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 1.5 — Arrancar el servidor Ollama
# ============================================================
# subprocess.Popen lanza el proceso en paralelo (no bloquea el notebook).
# Así el servidor queda corriendo en background mientras continuamos.
import subprocess, time, requests

ollama_proc = subprocess.Popen(
    ['ollama', 'serve'],           # Equivalente a escribir 'ollama serve' en una terminal
    stdout=subprocess.DEVNULL,     # Descarta la salida estándar para no saturar el notebook
    stderr=subprocess.DEVNULL      # Descarta los mensajes de log del servidor
)

# Esperamos hasta 30 s a que el servidor responda en su puerto (11434)
for _ in range(30):
    try:
        requests.get('http://localhost:11434', timeout=2)   # Si responde, el servidor ya está listo
        print('✅ Servidor Ollama activo en localhost:11434')
        break
    except requests.ConnectionError:
        time.sleep(1)                                       # Aún arrancando: esperamos 1 s
else:
    raise RuntimeError('❌ Ollama no arrancó. Repite la celda 1.2 y después esta.')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 1.6 — Descargar los dos modelos (2-4 min)
# ============================================================
# Necesitamos DOS modelos con papeles distintos:
#   qwen3:4b          → LLM de chat. Soporta "tool calling" (imprescindible para el agente)
#                       y escribe bien en español. ~2.5 GB.
#   nomic-embed-text  → modelo de EMBEDDINGS: convierte texto en vectores para el RAG. ~270 MB.
# Alternativas con tool calling: llama3.1:8b o qwen3:8b (mejores, pero más lentos).
# ⚠️ Modelos sin tool calling (tinyllama, llama3.2:1b...) NO sirven para la Parte 3.

LLM_MODEL = 'qwen3:4b'
EMBED_MODEL = 'nomic-embed-text'

!ollama pull {LLM_MODEL}
!ollama pull {EMBED_MODEL}
!ollama list

print('✅ Modelos descargados')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 1.7 — Configuración de la actividad
# ============================================================
# Este diccionario es el panel de control. Puedes cambiar los valores y
# volver a ejecutar desde aquí para ver cómo cambian los resultados.

# WebBaseLoader avisa si no hay USER_AGENT: es la "firma" con la que pedimos las páginas
os.environ['USER_AGENT'] = 'Mozilla/5.0 (ColabIA-AgenteWebRAG)'

config = {
    'temperatura': 0.1,       # 0 = respuestas deterministas; 1 = más creativas
    'max_resultados': 5,      # resultados que devuelve cada búsqueda web
    'region': 'es-es',        # región de DuckDuckGo (prioriza resultados en español)
    'max_iteraciones': 4,     # límite del bucle del agente (evita bucles infinitos)
    'chunk_size': 1000,       # tamaño de cada fragmento de texto (en caracteres)
    'chunk_overlap': 150,     # caracteres compartidos entre fragmentos vecinos
    'k': 4,                   # fragmentos que recupera el RAG por pregunta
}

for clave, valor in config.items():
    print(f'   {clave:<16} {valor}')
print('✅ Configuración lista')
"""))

# ─── PARTE 2 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🔎 PARTE 2 — La herramienta de búsqueda

Una **tool** de LangChain es una función de Python normal con el decorador `@tool`. El LLM **nunca ejecuta
código**: solo lee el **nombre**, el **docstring** y los **parámetros** de la herramienta, y decide si
pedir que la ejecutemos nosotros.

```
  def buscar_en_internet(consulta: str)      ← nombre y parámetros → el "contrato"
      '''Busca información actual...'''      ← docstring → cuándo usarla (lo lee el LLM)
```

Además de devolver los resultados, nuestra herramienta **guarda las URLs** en `fuentes_encontradas`:
serán la materia prima del RAG.
"""))

cells.append(code(r"""
# ============================================================
# CELDA 2.1 — Definir la herramienta buscar_en_internet
# ============================================================
from ddgs import DDGS                       # Cliente de DuckDuckGo (gratuito, sin API key)
from langchain_core.tools import tool       # Decorador que convierte una función en herramienta

# Diccionario url → título. Se va llenando con cada búsqueda.
# Lo usaremos en la Parte 4 para descargar esas páginas.
fuentes_encontradas = {}

@tool
def buscar_en_internet(consulta: str) -> str:
    '''Busca información actual en internet. Úsala siempre que necesites datos
    recientes o que no conozcas. La entrada es una consulta breve con palabras clave.'''
    try:
        resultados = DDGS().text(
            consulta,                                 # Lo que el LLM decidió buscar
            region=config['region'],                  # Prioriza resultados de esa región
            max_results=config['max_resultados']      # Cuántos resultados traer
        )
    except Exception as e:
        # Si el buscador falla, devolvemos el error como texto: el agente lo leerá
        # y podrá reintentar con otra consulta en lugar de romper el programa.
        return f'Error en la búsqueda: {e}'

    if not resultados:
        return 'No se encontraron resultados.'

    bloques = []
    for i, r in enumerate(resultados, 1):
        fuentes_encontradas[r['href']] = r['title']    # Guardamos la URL para el RAG
        # Cada resultado trae: title (título), href (URL) y body (snippet de 2-3 líneas)
        bloques.append(f"[{i}] {r['title']}\nURL: {r['href']}\n{r['body']}")
    return '\n\n'.join(bloques)

print(f'✅ Herramienta definida: {buscar_en_internet.name}')
print(f'   Descripción que verá el LLM: {buscar_en_internet.description[:80]}...')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 2.2 — Probar la herramienta SIN LLM
# ============================================================
# Antes de dársela al agente, comprobamos que funciona por sí sola.
# .invoke() es la forma estándar de ejecutar cualquier componente de LangChain.

resultado = buscar_en_internet.invoke('qué es LangChain')
print(resultado[:1000])

print(f'\n🌐 URLs guardadas hasta ahora: {len(fuentes_encontradas)}')
# Si ves "Error en la búsqueda" con un mensaje de límite (ratelimit), espera 1 minuto y repite.
print('✅ La herramienta funciona')
"""))

# ─── PARTE 3 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🤖 PARTE 3 — El agente

Un **agente** es un LLM que puede **pedir que se ejecuten herramientas** y usar sus resultados. El ciclo es:

```
  ┌─► 1. RAZONAR: el LLM lee la conversación y decide
  │         ├── ¿necesito buscar? → devuelve un tool_call {name, args}
  │         └── ¿ya lo sé?        → devuelve la respuesta final (texto)
  │
  │   2. ACTUAR: nosotros ejecutamos la herramienta pedida
  │
  └── 3. OBSERVAR: añadimos el resultado como ToolMessage y volvemos a 1
```

Vamos a construirlo paso a paso: primero el LLM solo, luego con herramientas y al final el bucle completo.
"""))

cells.append(code(r"""
# ============================================================
# CELDA 3.1 — El LLM solo (sin herramientas)
# ============================================================
# ChatOllama conecta LangChain con el servidor Ollama de la celda 1.5.
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model=LLM_MODEL,                       # El modelo descargado en la celda 1.6
    temperature=config['temperatura'],     # Baja = respuestas más estables
    reasoning=False                        # Desactiva el modo "thinking" de qwen3 → más rápido
)

# Una pregunta sobre algo reciente: el modelo solo sabe lo que vio al entrenarse
respuesta = llm.invoke('¿Cuál es la última versión de LangChain y qué novedades trae?')
print(respuesta.content)

print('\n💡 Observa: el modelo no tiene datos actuales; puede inventar o quedarse corto.')
print('✅ LLM funcionando')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 3.2 — Darle la herramienta al LLM y ver qué pide
# ============================================================
# bind_tools envía al modelo la "ficha" de cada herramienta (nombre, descripción,
# parámetros). El modelo NO la ejecuta: si la quiere usar, responde con un tool_call.
from langchain_core.messages import HumanMessage

llm_con_tools = llm.bind_tools([buscar_en_internet])

ai_msg = llm_con_tools.invoke([HumanMessage('Busca las novedades de la última versión de LangChain')])

print('Texto de la respuesta:', repr(ai_msg.content))   # Suele estar vacío cuando pide una herramienta
print('Herramientas pedidas :', ai_msg.tool_calls)       # Lista de {name, args, id}

# Si tool_calls sale vacío, el modelo decidió no buscar: repite la celda
# o revisa que usas un modelo con tool calling (celda 1.6).
print('✅ El LLM sabe pedir la herramienta')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 3.3 — Definir el bucle del agente
# ============================================================
# Implementamos el ciclo Razonar → Actuar → Observar a mano para ver qué pasa por dentro.
# (En LangChain 1.x, langchain.agents.create_agent hace este mismo bucle por ti.)
from datetime import date
from langchain_core.messages import SystemMessage, ToolMessage

# Diccionario nombre → herramienta: para encontrar la función que pidió el LLM
tools_map = {buscar_en_internet.name: buscar_en_internet}

# El mensaje de sistema fija el comportamiento. Le damos la fecha porque el
# modelo no la conoce y la necesita para buscar "lo último".
SYSTEM_AGENTE = (
    f'Eres un asistente de investigación. Hoy es {date.today().isoformat()}. '
    'Para responder, usa SIEMPRE la herramienta buscar_en_internet. '
    'Responde en español, de forma concisa, y cita las URLs que utilizaste.'
)

def agente_web(pregunta, verbose=True):
    # La "memoria" del agente es simplemente la lista de mensajes de esta conversación
    mensajes = [SystemMessage(SYSTEM_AGENTE), HumanMessage(pregunta)]

    for paso in range(config['max_iteraciones']):
        ai_msg = llm_con_tools.invoke(mensajes)       # 1. RAZONAR
        mensajes.append(ai_msg)

        if not ai_msg.tool_calls:                     # Sin tool_calls = respuesta final
            return ai_msg.content

        for call in ai_msg.tool_calls:                # 2. ACTUAR
            if verbose:
                print(f"🛠️  Paso {paso + 1}: {call['name']}({call['args']})")
            resultado = tools_map[call['name']].invoke(call['args'])
            # 3. OBSERVAR: tool_call_id enlaza el resultado con la petición concreta
            mensajes.append(ToolMessage(content=resultado, tool_call_id=call['id']))

    # Si se agotan las iteraciones, pedimos una respuesta con lo que ya tiene
    mensajes.append(HumanMessage('Responde ya con la información obtenida.'))
    return llm.invoke(mensajes).content

print('✅ Bucle del agente definido')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 3.4 — Ejecutar el agente
# ============================================================
# Cambia PREGUNTA por un tema de tu interés. Esa misma búsqueda será la base del RAG.

PREGUNTA = '¿Qué novedades tiene la última versión de LangChain?'   # 👈 cámbiala

fuentes_encontradas.clear()          # Empezamos con la lista de URLs vacía
respuesta_agente = agente_web(PREGUNTA)

print('\n' + '=' * 70)
print('🤖 RESPUESTA DEL AGENTE\n')
print(respuesta_agente)
print('=' * 70)

print(f'\n🌐 {len(fuentes_encontradas)} páginas encontradas:')
for url, titulo in fuentes_encontradas.items():
    print(f'   • {titulo}\n     {url}')
print('✅ Fase 1 completada: tenemos respuesta y URLs')
"""))

# ─── PARTE 4 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🌐 PARTE 4 — Cargar las webs encontradas

El agente solo vio *snippets* de 2-3 líneas. Ahora descargamos **cada página completa** con `WebBaseLoader`:

```
  URL ──requests──► HTML ──BeautifulSoup──► texto plano ──► Document(page_content, metadata={source})
```

Un `Document` es la unidad básica de LangChain: un texto + metadatos (aquí, la URL de origen, que
luego usaremos para citar fuentes).
"""))

cells.append(code(r"""
# ============================================================
# CELDA 4.1 — Definir la función que descarga las páginas
# ============================================================
from langchain_community.document_loaders import WebBaseLoader

def cargar_webs(urls):
    docs = []
    # Cargamos UNA URL cada vez: si una web está caída o bloquea a los bots,
    # la saltamos sin romper todo el proceso. (La opción continue_on_failure
    # de WebBaseLoader no protege la carga normal, por eso usamos try/except.)
    for url in urls:
        try:
            loader = WebBaseLoader(
                url,
                raise_for_status=True,                   # Trata errores HTTP (403, 404...) como fallo
                requests_kwargs={'timeout': 15},         # No esperar más de 15 s por página
                bs_get_text_kwargs={'separator': '\n',   # Separa los bloques del HTML con saltos
                                    'strip': True},      # y quita espacios sobrantes
            )
            for d in loader.load():
                if len(d.page_content) > 200:            # Descarta páginas casi vacías
                    docs.append(d)
        except Exception as e:
            print(f'   ⚠️  No se pudo cargar {url}: {type(e).__name__}')
    return docs

print('✅ Función cargar_webs definida')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 4.2 — Descargar las páginas del agente
# ============================================================
# list(diccionario) devuelve sus claves: las URLs.
documentos = cargar_webs(list(fuentes_encontradas))

print(f'\n📄 Páginas descargadas: {len(documentos)} de {len(fuentes_encontradas)}')
for d in documentos:
    print(f"   • {len(d.page_content):>7,} caracteres · {d.metadata['source']}")

if not documentos:
    print('❌ Ninguna página se pudo descargar: cambia la PREGUNTA en la celda 3.4 y repite.')
else:
    print(f"\nInicio de la primera página:\n{documentos[0].page_content[:400]}")
    print('✅ Páginas cargadas')
"""))

# ─── PARTE 5 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🗄️ PARTE 5 — Indexar: fragmentos, embeddings y FAISS

Una página puede tener 50.000 caracteres: no cabe entera en el prompt y además casi todo sería
irrelevante. Por eso:

```
  Página ──split──► [frag 1] [frag 2] ... [frag N]        ← chunks de ~1000 caracteres
                       │        │            │
                   embedding embedding   embedding        ← vectores de 768 números
                       └────────┴─────┬──────┘
                                    FAISS                  ← índice para buscar por similitud
```

Al preguntar, la pregunta también se convierte en vector y FAISS devuelve los `k` fragmentos más
parecidos **en significado**, aunque no compartan las mismas palabras.
"""))

cells.append(code(r"""
# ============================================================
# CELDA 5.1 — Dividir las páginas en fragmentos (chunks)
# ============================================================
# RecursiveCharacterTextSplitter intenta cortar primero por párrafos, luego por
# líneas, luego por frases... así evita partir ideas por la mitad.
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=config['chunk_size'],         # Tamaño máximo de cada fragmento
    chunk_overlap=config['chunk_overlap']    # Solapamiento: evita perder contexto en los cortes
)
chunks = splitter.split_documents(documentos)   # Cada chunk conserva la URL en sus metadatos

print(f'✂️  {len(documentos)} páginas → {len(chunks)} fragmentos')
print(f"\nEjemplo de fragmento ({chunks[0].metadata['source']}):\n{chunks[0].page_content[:300]}")
print('✅ Fragmentos listos')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 5.2 — Probar el modelo de embeddings
# ============================================================
# Comprobamos con 3 frases que textos de significado parecido dan vectores parecidos.
import numpy as np
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(model=EMBED_MODEL)

frases = ['El agente busca en internet', 'La IA consulta la web', 'Receta de paella valenciana']
vectores = np.array(embeddings.embed_documents(frases))   # Una fila (vector) por frase

def similitud(a, b):
    # Similitud coseno: 1 = misma dirección (mismo significado), ~0 = sin relación
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

sim_parecidas = similitud(vectores[0], vectores[1])    # Mismo tema, distintas palabras
sim_distintas = similitud(vectores[0], vectores[2])    # Temas sin relación

print(f'Dimensión de cada vector: {vectores.shape[1]}')
print(f'"{frases[0]}" vs "{frases[1]}": {sim_parecidas:.3f}')
print(f'"{frases[0]}" vs "{frases[2]}": {sim_distintas:.3f}')

if sim_parecidas > sim_distintas:
    print('✅ Embeddings funcionando: las frases del mismo tema son más parecidas')
else:
    print('⚠️ Resultado inesperado: revisa que EMBED_MODEL sea un modelo de embeddings (celda 1.6)')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 5.3 — Crear el índice vectorial FAISS
# ============================================================
# from_documents calcula el embedding de cada chunk (llamando a Ollama) y los
# guarda en un índice en memoria RAM. Puede tardar unos segundos.
from langchain_community.vectorstores import FAISS

vectorstore = FAISS.from_documents(chunks, embeddings)

# as_retriever convierte el índice en un "buscador" que devuelve los k chunks más similares
retriever = vectorstore.as_retriever(search_kwargs={'k': config['k']})

print(f'🗄️  Índice FAISS con {vectorstore.index.ntotal} vectores')
print('✅ Índice creado')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 5.4 — Ver qué recupera el retriever
# ============================================================
# Antes de usar el LLM, miramos qué fragmentos considera relevantes: esta es la "R" de RAG.

consulta = 'principales novedades'   # 👈 prueba otras consultas
for i, d in enumerate(retriever.invoke(consulta), 1):
    print(f"--- Fragmento {i} · {d.metadata['source']}")
    print(d.page_content[:250], '...\n')
print('✅ Recuperación funcionando')
"""))

# ─── PARTE 6 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🔗 PARTE 6 — La cadena RAG con LCEL

**LCEL** (*LangChain Expression Language*) encadena componentes con el operador `|`, como una tubería:

```
  pregunta ─┬─► retriever ─► formatear ─► {contexto} ─┐
            └──────────────────────────► {pregunta} ──┴─► prompt ─► llm ─► texto
```

El prompt obliga al modelo a responder **solo** con el contexto y a decir que no lo sabe si la información
no está: así reducimos las alucinaciones.
"""))

cells.append(code(r"""
# ============================================================
# CELDA 6.1 — Definir el prompt del RAG
# ============================================================
from langchain_core.prompts import ChatPromptTemplate

# {contexto} y {pregunta} son huecos que la cadena rellenará en cada llamada
prompt_rag = ChatPromptTemplate.from_messages([
    ('system',
     'Responde a la pregunta usando ÚNICAMENTE el contexto, extraído de páginas web. '
     'Si la respuesta no está en el contexto, di que no aparece en las fuentes. '
     'Responde en español y cita entre corchetes la URL de la que sale cada dato.\n\n'
     'CONTEXTO:\n{contexto}'),
    ('human', '{pregunta}'),
])

print('✅ Prompt definido con las variables:', prompt_rag.input_variables)
"""))

cells.append(code(r"""
# ============================================================
# CELDA 6.2 — Construir la cadena RAG
# ============================================================
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

def formatear_docs(docs):
    # Une los fragmentos en un solo texto, cada uno precedido de su URL (para poder citarla)
    return '\n\n'.join(f"[{d.metadata['source']}]\n{d.page_content}" for d in docs)

def crear_cadena(retriever):
    return (
        {'contexto': retriever | RunnableLambda(formatear_docs),   # pregunta → chunks → texto
         'pregunta': RunnablePassthrough()}                        # pasa la pregunta tal cual
        | prompt_rag                                               # rellena la plantilla
        | llm                                                      # genera la respuesta
        | StrOutputParser()                                        # AIMessage → str
    )

cadena_rag = crear_cadena(retriever)

def preguntar_rag(pregunta):
    respuesta = cadena_rag.invoke(pregunta)
    # Volvemos a pedir los chunks solo para mostrar de qué URLs salió la respuesta
    fuentes = sorted({d.metadata['source'] for d in retriever.invoke(pregunta)})
    return respuesta + '\n\n📚 Fuentes consultadas:\n' + '\n'.join(f'• {u}' for u in fuentes)

print('✅ Cadena RAG lista')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 6.3 — Pregunta de seguimiento sobre las webs
# ============================================================
# Compara con la respuesta del agente (celda 3.4): ahora el modelo trabaja con el
# texto completo de las páginas, no con los snippets del buscador.

print(preguntar_rag('Resume los puntos más importantes que mencionan las fuentes.'))   # 👈 cámbiala
print('\n✅ RAG respondiendo con las webs encontradas')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 6.4 — Pregunta fuera de tema
# ============================================================
# Las webs no hablan de cocina: un buen RAG debe reconocer que no tiene la información
# en lugar de inventarla.

print(preguntar_rag('¿Cuál es la receta de la paella valenciana?'))
print('\n✅ Comprueba que dice que la información no aparece en las fuentes')
"""))

# ─── PARTE 7 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🧩 PARTE 7 — Pipeline completo

Juntamos todo en una sola función: **pregunta → agente → URLs → RAG listo**. Es lo que usará la interfaz.
"""))

cells.append(code(r"""
# ============================================================
# CELDA 7.1 — Función investigar(): agente + construcción del RAG
# ============================================================
def investigar(pregunta):
    # global → actualizamos las variables que usa preguntar_rag()
    global vectorstore, retriever, cadena_rag

    fuentes_encontradas.clear()                    # Cada investigación empieza de cero
    respuesta = agente_web(pregunta)               # FASE 1: agente + búsqueda

    docs = cargar_webs(list(fuentes_encontradas))  # FASE 2: descargar páginas
    if not docs:
        return respuesta, '⚠️ No se pudo descargar ninguna web: el RAG no se actualizó.'

    vectorstore = FAISS.from_documents(splitter.split_documents(docs), embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={'k': config['k']})
    cadena_rag = crear_cadena(retriever)

    estado = (f'✅ RAG construido con {len(docs)} webs ({vectorstore.index.ntotal} fragmentos):\n'
              + '\n'.join(f'• {d.metadata["source"]}' for d in docs))
    return respuesta, estado

print('✅ Función investigar definida')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 7.2 — Probar el pipeline con un tema nuevo
# ============================================================
respuesta, estado = investigar('¿Qué es el protocolo MCP de Anthropic?')   # 👈 cámbiala

print('🤖 AGENTE:\n', respuesta, '\n')
print(estado, '\n')
print('📚 RAG:\n', preguntar_rag('¿Qué componentes tiene la arquitectura de MCP?'))
print('\n✅ Pipeline completo funcionando')
"""))

# ─── PARTE 8 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🖥️ PARTE 8 — Interfaz Gradio

Dos pestañas, una por fase:

```
  ┌─ 1 · Investigar ───────────────┐   ┌─ 2 · Preguntar a las webs ─┐
  │ pregunta → investigar()        │──►│ chat → preguntar_rag()     │
  │ respuesta del agente + estado  │   │ respuestas con fuentes     │
  └────────────────────────────────┘   └────────────────────────────┘
```
"""))

cells.append(code(r"""
# ============================================================
# CELDA 8.1 — Funciones que conectan la interfaz con el sistema
# ============================================================
def ui_investigar(pregunta):
    try:
        return investigar(pregunta)                       # Devuelve (respuesta, estado)
    except Exception as e:
        return f'⚠️ Error: {e}', 'El RAG no se actualizó.'

def ui_chat_rag(mensaje, historial):
    # historial lo gestiona Gradio; aquí cada pregunta se responde de forma independiente
    try:
        return preguntar_rag(mensaje)
    except Exception as e:
        return f'⚠️ Error: {e}'

print('✅ Funciones de la interfaz definidas')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 8.2 — Construir la interfaz con gr.Blocks
# ============================================================
import gradio as gr

CSS = '''
.gradio-container {max-width: 900px !important; margin: auto;}
#titulo {text-align: center;}
'''

with gr.Blocks(title='Agente Web + RAG', theme='soft', css=CSS) as demo:
    gr.Markdown('# 🔎 Agente de búsqueda web + 📚 RAG', elem_id='titulo')

    with gr.Tab('1 · Investigar en internet'):
        entrada = gr.Textbox(label='Pregunta', placeholder='¿Qué es el protocolo MCP?')
        boton = gr.Button('Buscar y construir RAG', variant='primary')
        salida = gr.Markdown()                                  # Respuesta del agente
        estado = gr.Textbox(label='Estado del RAG', lines=6)    # Webs indexadas
        # click → llama a ui_investigar con el texto y reparte las 2 salidas
        boton.click(ui_investigar, inputs=entrada, outputs=[salida, estado])

    with gr.Tab('2 · Preguntar a las webs (RAG)'):
        gr.ChatInterface(fn=ui_chat_rag, type='messages')       # Chat listo para usar

print('✅ Interfaz construida')
"""))

cells.append(code(r"""
# ============================================================
# CELDA 8.3 — Probar la interfaz dentro de Colab
# ============================================================
# share=False → solo se ve aquí dentro; la publicaremos con Ngrok en la Parte 11.
# Prueba primero la pestaña 1 y después pregunta en la pestaña 2.

demo.launch(share=False, quiet=True)
print('✅ Interfaz funcionando en Colab')
"""))

# ─── PARTE 9 — REFLEXIÓN ─────────────────────────────────────────────────────
cells.append(md(r"""
## 🤔 PARTE 9 — Reflexión

Responde en la celda de abajo:

1. **Conceptual:** ¿qué diferencia hay entre la respuesta del agente (Parte 3) y la del RAG (Parte 6)? ¿De dónde sale la información en cada caso?
2. **Código:** ¿por qué el bucle del agente añade un `ToolMessage` con `tool_call_id` en lugar de pegar el resultado de la búsqueda como un mensaje normal?
3. **Implicaciones:** el sistema lee páginas de internet y las mete en el prompt. ¿Qué riesgos tiene (desinformación, *prompt injection* escondido en una web, derechos de autor)? ¿Cómo los mitigarías?
4. **Comparativa:** ¿qué ventajas e inconvenientes tiene este RAG "al vuelo" frente al de la Actividad 01, donde los documentos estaban fijos de antemano?
5. **Experimento:** cambia `chunk_size` a 300 y luego a 3000 (celda 1.7) y repite las Partes 5-6. ¿Qué cambia en los fragmentos recuperados y en las respuestas?
"""))

cells.append(md(r"""
**✍️ Mis respuestas:**

1.
2.
3.
4.
5.
"""))

# ─── PARTE 10 — RETOS ────────────────────────────────────────────────────────
cells.append(md(r"""
## 🚀 PARTE 10 — Retos opcionales

1. **Búsqueda en un sitio concreto:** crea una segunda herramienta `buscar_en_sitio(consulta, dominio)`.
   *Pista:* DuckDuckGo entiende `site:dominio.com consulta`; añádela a `bind_tools` y a `tools_map`.
2. **El RAG como herramienta:** convierte `preguntar_rag` en una tool `consultar_webs_indexadas` para que el
   agente decida solo si buscar en internet o en lo que ya indexó.
   *Pista:* decórala con `@tool` y escribe un docstring que explique cuándo usarla.
3. **Persistir el índice:** guarda el índice en Google Drive y recárgalo en otra sesión.
   *Pista:* `vectorstore.save_local(ruta)` y `FAISS.load_local(ruta, embeddings, allow_dangerous_deserialization=True)`.
"""))

cells.append(code(r"""
# ============================================================
# CELDA 10.1 — Tu espacio para experimentar
# ============================================================

"""))

# ─── PARTE 11 — NGROK ────────────────────────────────────────────────────────
cells.append(md(r"""
## 🌐 PARTE 11 — Publicación con Ngrok

Hasta ahora la app solo vive dentro de Colab. Con **Ngrok** creamos un **túnel** hacia Internet para que
tus compañeros investiguen sus propios temas desde el navegador.

```
  Compañero (navegador)
        │  https://xxxx.ngrok-free.app
        ▼
  Servidor de Ngrok  ───túnel───►  Colab (localhost:7860)
                                          │
                                          ▼
                              App Gradio ──► Agente + RAG (Ollama)
```

**Antes de empezar:** crea una cuenta gratuita en [ngrok.com](https://ngrok.com), copia tu *Authtoken*
y guárdalo en Colab: icono 🔑 **Secrets** → *Add new secret* → nombre `NGROK_TOKEN` → pega el token → activa *Notebook access*.
"""))

cells.append(code(r"""
# ============================================================
# CELDA 11.1 — Instalar pyngrok
# ============================================================
# Ya lo instalamos en la celda 1.4; repetirlo es instantáneo y garantiza que esté
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
# CELDA 11.3 — Abrir el túnel y relanzar la app
# ============================================================
# Orden importante: cerrar lo anterior → abrir túnel → lanzar la app.

demo.close()    # Cierra la app lanzada en la Parte 8 para liberar el puerto
ngrok.kill()    # Cierra túneles anteriores (el plan gratuito solo permite uno a la vez)

# connect(7860) crea un túnel público hacia el puerto local 7860
tunel = ngrok.connect(7860)
print(f'🌍 URL pública: {tunel.public_url}')
print('   Compártela con tus compañeros para que investiguen sus propios temas.')

# server_name='0.0.0.0' = acepta conexiones externas (las que llegan por el túnel)
# server_port=7860       = el mismo puerto que expusimos con Ngrok
# share=False            = no usamos el enlace temporal de Gradio; Ngrok es más estable
demo.launch(server_name='0.0.0.0', server_port=7860, share=False, quiet=True)

print('✅ App publicada con Ngrok')
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

DOMINIO_ESTATICO = ''   # Ej: 'mi-agente-web.ngrok-free.app'

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
# Orden: túnel → interfaz → procesos → memoria.

# 1. Cerrar el túnel Ngrok
ngrok.kill()
print('✅ Túnel Ngrok cerrado')

# 2. Cerrar la interfaz Gradio
demo.close()
print('✅ Interfaz Gradio cerrada')

# 3. Detener el servidor Ollama (al terminar libera también la memoria de la GPU)
ollama_proc.terminate()                                   # Pide al proceso que se cierre
subprocess.run(['pkill', '-f', 'ollama'], capture_output=True)   # Por si quedó algún subproceso
print('✅ Servidor Ollama detenido')

# 4. Liberar la memoria RAM del índice y las fuentes
del vectorstore, retriever, cadena_rag
fuentes_encontradas.clear()
print('✅ Índice FAISS y fuentes liberados')

print('\n✅ Todos los recursos liberados. Puedes cerrar el notebook.')
"""))

cells.append(md(r"""
## 📊 Rúbrica de Evaluación

| Criterio | Excelente (5) | Satisfactorio (3) | En desarrollo (1) |
|----------|---------------|-------------------|-------------------|
| **Herramienta y agente** | Explica el ciclo Razonar → Actuar → Observar con los `tool_calls` reales de su ejecución | Ejecuta el agente sin explicar el ciclo | El agente no llega a buscar |
| **Carga e indexación** | Relaciona páginas, fragmentos y vectores con sus propios números y justifica `chunk_size` | Construye el índice sin interpretar los números | No logra construir el índice |
| **Cadena RAG** | Compara respuesta del agente vs RAG y comprueba que el RAG no inventa (celda 6.4) | Obtiene respuestas RAG sin compararlas | La cadena falla |
| **Interfaz Gradio** | Las dos pestañas funcionan con un tema propio | Funciona solo una pestaña | Sin interfaz |
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

salida = Path(__file__).parent / "AgenteWebRAG.ipynb"
salida.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"✅ {salida.name} generado con {len(cells)} celdas")
