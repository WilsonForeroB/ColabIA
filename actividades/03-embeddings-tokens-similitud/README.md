# 🧠 Guía de Actividad: Embeddings, Tokens y Similitud Semántica con Ollama

**Curso:** Inteligencia Artificial Práctica  
**Herramientas:** Google Colab · Ollama · Gradio · Ngrok  
**Nivel:** Intermedio  
**Duración estimada:** 60–90 minutos

-----

## 📌 Descripción general

En esta actividad construirás una interfaz interactiva desde cero para explorar tres conceptos fundamentales del procesamiento de lenguaje natural con modelos de IA:

- **Tokenización:** cómo los modelos descomponen el texto en unidades mínimas
- **Embeddings:** cómo un modelo convierte texto en vectores numéricos
- **Similitud semántica:** cómo comparar el significado de dos textos usando álgebra lineal

Todo corre directamente en Google Colab, sin necesidad de instalar nada en tu computadora.

-----

## 🎯 Objetivos de aprendizaje

Al finalizar esta actividad serás capaz de:

1. Instalar y correr Ollama como servidor local dentro de un entorno Colab
1. Consumir la API de Ollama para obtener tokens y embeddings desde Python
1. Implementar la similitud coseno manualmente, entendiendo cada paso matemático
1. Construir una interfaz web funcional con Gradio
1. Exponer una aplicación local a internet usando Ngrok

-----

## 🛠️ Herramientas y tecnologías

|Herramienta     |Rol en la actividad                               |Documentación                                   |
|----------------|--------------------------------------------------|------------------------------------------------|
|**Ollama**      |Servidor local que corre los modelos de embeddings|[ollama.com](https://ollama.com)                |
|**Gradio**      |Framework para construir la interfaz web          |[gradio.app](https://gradio.app)                |
|**Ngrok**       |Túnel para exponer la app al exterior             |[ngrok.com](https://ngrok.com)                  |
|**httpx**       |Cliente HTTP para comunicarse con Ollama          |[python-httpx.org](https://www.python-httpx.org)|
|**Google Colab**|Entorno de ejecución en la nube                   |[colab.google](https://colab.google)            |

-----

## 📦 Modelos de embeddings disponibles

La actividad usa tres modelos que se descargan automáticamente:

|Modelo             |Dimensiones|Velocidad|Uso recomendado                        |
|-------------------|-----------|---------|---------------------------------------|
|`nomic-embed-text` |768        |⚡⚡⚡      |Uso general, textos en inglés y español|
|`mxbai-embed-large`|1024       |⚡⚡       |Mayor precisión semántica              |
|`all-minilm`       |384        |⚡⚡⚡⚡     |Muy liviano, ideal para pruebas rápidas|

-----

## 🗂️ Estructura del notebook

El notebook está dividido en 8 celdas con propósitos claros:

```
actividad_embeddings_ollama.ipynb
│
├── Celda 0 — Introducción a la actividad
├── Celda 1 — Instalación de dependencias
├── Celda 2 — Arranque de Ollama + descarga de modelos
├── Celda 3 — Concepto: ¿Qué es un token?          [Markdown teórico]
├── Celda 4 — Concepto: ¿Qué es la similitud coseno? [Markdown teórico]
├── Celda 5 — Funciones Python (tokens, embeddings, coseno)
├── Celda 6 — Interfaz Gradio (3 tabs)
└── Celda 7 — Exposición pública con Ngrok
```

-----

## 🚀 Instrucciones paso a paso

### Paso 1 — Prerrequisitos

Antes de abrir el notebook, asegúrate de tener:

- [ ] Una cuenta en [Google](https://google.com) para usar Colab
- [ ] Una cuenta gratuita en [ngrok.com](https://ngrok.com)
- [ ] Tu **authtoken de Ngrok** copiado desde el dashboard

Para obtener tu authtoken:

1. Inicia sesión en [dashboard.ngrok.com](https://dashboard.ngrok.com)
1. Ve a **Getting Started → Your Authtoken**
1. Copia el token (es una cadena larga que empieza con números)

-----

### Paso 2 — Abrir el notebook en Colab

1. Descarga el archivo `actividad_embeddings_ollama.ipynb`
1. Ve a [colab.research.google.com](https://colab.research.google.com)
1. Haz clic en **Archivo → Subir notebook**
1. Selecciona el archivo `.ipynb` descargado

> 💡 **Tip:** Si tienes el notebook en Google Drive, también puedes abrirlo directamente desde Colab con **Archivo → Abrir notebook → Google Drive**.

-----

### Paso 3 — Ejecutar las celdas en orden

> ⚠️ Es importante ejecutar las celdas **de arriba hacia abajo**, una por una.

**Celda 1 — Instalación** (~1-2 min)  
Instala Ollama, Gradio, httpx y pyngrok. Verás `✅ Instalación completada` al terminar.

**Celda 2 — Arranque de Ollama** (~3-5 min)  
Inicia el servidor y descarga los 3 modelos. Verás un `✅` por cada modelo descargado.

**Celdas 3 y 4 — Teoría**  
Solo lectura. Revisa los conceptos antes de continuar.

**Celda 5 — Funciones Python**  
Define las funciones core. Verás `✅ Funciones definidas correctamente`.

**Celda 6 — Interfaz Gradio**  
Lanza la app en el puerto 7860 local. Verás `✅ Interfaz Gradio corriendo`.

**Celda 7 — Ngrok**

1. Reemplaza `"PEGA_TU_TOKEN_AQUÍ"` con tu authtoken real
1. Ejecuta la celda
1. Aparecerá tu URL pública: `https://xxxx-xxxx.ngrok-free.app`

-----

### Paso 4 — Explorar la interfaz

Abre la URL de Ngrok en tu navegador. Verás tres pestañas:

#### 🔢 Tab Tokens

- Pega cualquier texto en el cuadro
- Selecciona un modelo en el desplegable
- Haz clic en **Contar tokens**
- Verás: número de tokens, palabras, y ratio tokens/palabra

#### 📊 Tab Embedding

- Pega un texto
- Haz clic en **Generar embedding**
- Verás: dimensiones del vector, primeros 10 valores, y un gráfico de barras con las primeras 50 dimensiones

#### 🔍 Tab Similitud Coseno

- Ingresa dos textos (uno en cada cuadro)
- Haz clic en **Calcular similitud**
- Verás: score numérico entre -1 y 1, e interpretación en lenguaje natural

-----

## 🧮 Conceptos clave

### ¿Qué es un token?

Un token es la unidad mínima de texto que procesa un modelo. No es igual a una palabra: los modelos usan vocabularios propios donde las palabras poco comunes se dividen en partes.

```
"transformers"  →  ["transform", "ers"]     = 2 tokens
"gato"          →  ["gato"]                 = 1 token
"Hola mundo"    →  ["Hola", " mundo"]       = 2 tokens
```

**Regla práctica:** en inglés, 1 token ≈ 0.75 palabras. En español puede ser ligeramente mayor.

-----

### ¿Qué es un embedding?

Un embedding es una representación numérica del significado de un texto. El modelo transforma el texto en un vector de cientos de números flotantes.

```
"gato"  →  [0.023, -0.412, 0.891, 0.034, ..., -0.201]  (768 números)
```

Textos con significados similares producen vectores que apuntan en direcciones parecidas en ese espacio multidimensional.

-----

### ¿Qué es la similitud coseno?

Mide el ángulo entre dos vectores. No importa cuán "grandes" sean los vectores, solo la dirección en que apuntan.

$$\cos(\theta) = \frac{\vec{A} \cdot \vec{B}}{|\vec{A}| \cdot |\vec{B}|}$$

|Score|Interpretación                         |
|-----|---------------------------------------|
|~1.0 |Textos casi idénticos semánticamente   |
|~0.75|Alta similitud — mismo tema            |
|~0.50|Similitud moderada — temas relacionados|
|~0.25|Baja similitud — poca relación         |
|~0.0 |Sin relación semántica                 |
|< 0  |Conceptos opuestos                     |

-----

## 🧪 Experimentos sugeridos

### Tab Tokens

- Pega el mismo texto usando los 3 modelos. ¿El conteo varía?
- ¿Cuántos tokens ocupa un emoji? ¿Y una URL?
- ¿Qué pasa con texto en árabe, chino o japonés?

### Tab Embedding

- Genera embeddings de `"perro"`, `"gato"` y `"automóvil"`. ¿El gráfico de barras tiene patrones visualmente distintos?
- Compara las dimensiones de `nomic-embed-text` (768) vs `all-minilm` (384)

### Tab Similitud

- `"el banco del parque"` vs `"el banco donde guardo dinero"` — ¿el modelo distingue el contexto?
- `"Hola"` vs `"Hello"` — ¿qué score obtienes?
- Un texto y su traducción directa — ¿tienen score cercano a 1.0?
- `"bueno"` vs `"malo"` — ¿el score es negativo?

-----

## 💬 Preguntas de reflexión

Responde estas preguntas después de explorar la interfaz:

1. ¿Por qué el número de tokens no es igual al número de palabras?
1. Si dos frases tienen un score de similitud de 0.95, ¿significa que son sinónimos perfectos? ¿Qué podría causar diferencias?
1. ¿En qué aplicaciones reales usarías la similitud coseno? (piensa en búsqueda, recomendaciones, detección de duplicados…)
1. ¿Qué ventaja concreta tiene `mxbai-embed-large` (1024 dim) sobre `all-minilm` (384 dim)? ¿Siempre es mejor más dimensiones?
1. ¿Por qué usamos similitud coseno y no distancia euclidiana para comparar textos?

-----

## ⚠️ Solución de problemas comunes

|Problema                                  |Posible causa                                         |Solución                                                           |
|------------------------------------------|------------------------------------------------------|-------------------------------------------------------------------|
|`❌ No se pudo conectar al servidor Ollama`|Ollama no arrancó correctamente                       |Reinicia el runtime de Colab y ejecuta desde Celda 1               |
|`❌ El modelo no devolvió conteo de tokens`|Versión de Ollama sin soporte para `prompt_eval_count`|Cambia de modelo en el desplegable                                 |
|`❌ Error al conectar con Ngrok`           |Token inválido o túnel duplicado                      |Verifica el token; si ya tienes un túnel activo, reinicia el kernel|
|La URL de Ngrok no abre                   |Sesión de Colab inactiva                              |Vuelve a Colab y verifica que las celdas siguen corriendo          |
|La descarga de modelos tarda mucho        |Conexión lenta en Colab                               |Es normal en la primera ejecución; espera hasta ver los `✅`        |

-----

## 📎 Recursos adicionales

- [Documentación de Ollama](https://github.com/ollama/ollama/blob/main/docs/api.md) — referencia de la API REST
- [Galería de modelos Ollama](https://ollama.com/library) — todos los modelos disponibles
- [Gradio Docs](https://www.gradio.app/docs) — componentes y opciones de la interfaz
- [Illustrated Word2Vec](https://jalammar.github.io/illustrated-word2vec/) — intuición visual sobre embeddings
- [Understanding Cosine Similarity](https://www.cs.cmu.edu/~quake/robust.html) — profundización matemática

-----

> 🛠️ **Notebook:** `actividad_embeddings_ollama.ipynb`  
> ✉️ Cualquier duda, compártela en el foro del curso.
