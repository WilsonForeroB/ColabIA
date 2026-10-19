"""Script para generar PythonColabBasico.ipynb"""
import json


def code(source):
    return {"cell_type": "code", "execution_count": None, "id": "", "metadata": {},
            "outputs": [], "source": source.strip("\n") + "\n"}


def md(source):
    return {"cell_type": "markdown", "id": "", "metadata": {}, "source": source.strip("\n") + "\n"}


cells = []

# ─── HEADER ──────────────────────────────────────────────────────────────────
cells.append(md(r"""
# 🐍 Actividad 13 — Python y Google Colab desde Cero

## ¿Para quién es?

Para quien **nunca ha programado** o nunca ha usado Google Colab. No necesitas saber nada previo.
Al terminar podrás ejecutar y entender todas las demás actividades del curso.

## ¿Qué es Google Colab?

Colab es un **editor de código en el navegador**. Escribes Python en "celdas", pulsas ▶ y ves el resultado justo debajo.
No instalas nada en tu computadora: el código corre en un computador de Google.

```
  Tu navegador                     Computador de Google
  ┌──────────────────┐   ▶ ejecutar  ┌───────────────────────┐
  │ Celda de código  │ ────────────► │ Python corre aquí     │
  │ print('Hola')    │               │                       │
  │ Hola             │ ◄──────────── │ Devuelve el resultado │
  └──────────────────┘   resultado   └───────────────────────┘
```

## ¿Qué es Python?

Python es un lenguaje de programación: una forma de **darle instrucciones a la computadora** con texto casi legible.
Es el lenguaje que usa todo el curso de IA.

## Cómo funciona esta actividad

> **Tú solo ejecutas. El notebook explica.**

Pulsa ▶ en cada celda **en orden**, de arriba a abajo, y lee los comentarios (las líneas que empiezan con `#`).

## Mapa de la actividad

| Parte | Tema |
|-------|------|
| 1 | Conoce Colab: celdas, ejecución y orden |
| 2 | Variables y tipos de datos |
| 3 | Listas y diccionarios |
| 4 | Decisiones (`if`) y repeticiones (`for`) |
| 5 | Funciones |
| 6 | Librerías y datos de Internet |
| 7 | Leer errores sin miedo |
| 8 | Tu primera mini-app con Gradio |
| 9 | Reflexión |
| 10 | Retos opcionales |
| 11 | Publicación con Ngrok + limpieza + rúbrica |

**⏱️ Duración:** 90–120 minutos · **GPU:** no es necesaria
"""))

# ─── PARTE 1 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🧭 PARTE 1 — Conoce Colab y configura el entorno

Un notebook tiene dos tipos de celda:

| Tipo | Para qué sirve | Cómo se ejecuta |
|------|----------------|-----------------|
| **Texto** (como esta) | Explicaciones | Se lee, no se ejecuta |
| **Código** (con ▶ a la izquierda) | Instrucciones de Python | Pulsa ▶ o `Shift + Enter` |

**Reglas que debes recordar:**
1. Ejecuta las celdas **en orden**, de arriba a abajo.
2. Si algo sale raro, usa el menú **Entorno de ejecución → Reiniciar sesión** y empieza de nuevo desde la primera celda.
3. Las líneas que empiezan con `#` son **comentarios**: Python las ignora, son notas para ti.
4. Cuando una celda termina bien, verás un mensaje con ✅.
"""))

cells.append(code(r'''
# ============================================================
# CELDA 1.1 — Tu primera celda de código
# ============================================================
# Pulsa el botón ▶ a la izquierda de esta celda (o Shift + Enter).
# Debajo aparecerá el resultado.

# print() muestra un texto en pantalla. El texto va entre comillas.
print('¡Hola! Esta es tu primera celda ejecutada 🎉')

print('✅ Ejecutaste tu primera celda')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 1.2 — Ver qué versión de Python está corriendo
# ============================================================
# "import" trae herramientas extra que Python no carga por defecto.
# "sys" es una herramienta que guarda información del sistema.

import sys   # Herramienta con información sobre Python

# sys.version es un texto con la versión instalada en el computador de Google.
print(f'Python que estás usando: {sys.version}')

print('✅ Python funciona correctamente en Colab')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 1.3 — Crear una "memoria": la celda que define un dato
# ============================================================
# Colab recuerda lo que crean las celdas ejecutadas antes.
# Aquí guardamos un texto con el nombre "mensaje".

mensaje = 'Colab recuerda lo que definiste antes'   # El signo = guarda el texto en "mensaje"

print('✅ Dato "mensaje" guardado en la memoria de Colab')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 1.4 — Usar el dato guardado en la celda anterior
# ============================================================
# Esta celda funciona SOLO si ejecutaste antes la celda 1.3.
# Si ves "NameError: name 'mensaje' is not defined", significa que
# te saltaste la 1.3: ejecútala y vuelve a esta.

print(mensaje)   # Muestra el contenido guardado en "mensaje"

print('✅ Las celdas comparten memoria, por eso el orden importa')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 1.5 — Ejecutar un comando del sistema con "!"
# ============================================================
# Cuando una línea empieza con "!", Colab NO la trata como Python:
# la manda a la terminal del computador de Google.
# Así se instalan programas y se consultan cosas del sistema.

# "echo" es un comando de terminal que repite un texto.
!echo "Esto lo ejecutó la terminal, no Python"

print('✅ Ya sabes que "!" ejecuta comandos de terminal')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 1.6 — Instalar una librería con pip
# ============================================================
# "pip" es el instalador de librerías de Python (como una tienda de apps).
# Instalaremos Gradio, que usaremos en la Parte 8 para crear una interfaz web.
# gradio>=5,<6 fija la versión para que todo se comporte igual siempre.
# -q = quiet: muestra menos mensajes.

!pip install -q 'gradio>=5,<6'

print('✅ Gradio instalado')
'''))

# ─── PARTE 2 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 📦 PARTE 2 — Variables y tipos de datos

Una **variable** es una caja con nombre donde guardas un dato.

```
   nombre = 'Ana'
     │        │
     │        └── el dato que guardas
     └── el nombre de la caja
```

Los cuatro tipos de datos más comunes:

| Tipo | Qué guarda | Ejemplo |
|------|-----------|---------|
| `str` | Texto (siempre entre comillas) | `'Hola'` |
| `int` | Número entero | `25` |
| `float` | Número con decimales | `1.75` |
| `bool` | Verdadero o falso | `True` / `False` |
"""))

cells.append(code(r'''
# ============================================================
# CELDA 2.1 — Crear variables de los cuatro tipos
# ============================================================
# Cada línea guarda un dato en una variable. Los nombres no llevan espacios ni tildes.

nombre = 'Ana'         # str: texto, va entre comillas
edad = 28              # int: número entero, sin comillas
altura = 1.68          # float: número con decimales (usa punto, no coma)
es_estudiante = True   # bool: solo puede ser True o False (con mayúscula inicial)

print('✅ Cuatro variables creadas')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 2.2 — Mostrar variables y su tipo
# ============================================================
# type() responde "¿de qué tipo es este dato?".

print(nombre, type(nombre))                 # Texto
print(edad, type(edad))                     # Entero
print(altura, type(altura))                 # Decimal
print(es_estudiante, type(es_estudiante))   # Verdadero/falso

print('✅ Ahora sabes ver el tipo de cada dato')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 2.3 — Mezclar variables en una frase con f-strings
# ============================================================
# Una f-string es un texto con una "f" antes de las comillas.
# Lo que va dentro de llaves { } se reemplaza por el valor de la variable.
# Es la forma más cómoda de armar frases con datos.

frase = f'Me llamo {nombre}, tengo {edad} años y mido {altura} m.'

print(frase)

print('✅ Frase construida con f-string')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 2.4 — Hacer cálculos con números
# ============================================================
# Python funciona como una calculadora: + suma, - resta, * multiplica, / divide.

edad_en_diez_anios = edad + 10   # Suma 10 a la edad guardada
mitad_de_edad = edad / 2         # La división siempre devuelve un float

print(f'Dentro de 10 años tendré {edad_en_diez_anios}')
print(f'La mitad de mi edad es {mitad_de_edad}')

print('✅ Cálculos básicos hechos')
'''))

# ─── PARTE 3 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🗂️ PARTE 3 — Listas y diccionarios

Cuando tienes **muchos datos**, no creas una variable para cada uno. Usas colecciones:

| Colección | Qué es | Se escribe con | Ejemplo |
|-----------|--------|----------------|---------|
| **Lista** | Una fila ordenada de datos | `[ ]` | `['rojo', 'verde', 'azul']` |
| **Diccionario** | Pares "etiqueta → valor" | `{ }` | `{'nombre': 'Ana', 'edad': 28}` |

```
Lista:                         Diccionario:
 posición  0      1      2      etiqueta   valor
          ┌─────┬──────┬─────┐   'nombre' → 'Ana'
          │rojo │verde │azul │   'edad'   → 28
          └─────┴──────┴─────┘
```

> 💡 Los diccionarios tienen el mismo aspecto que el **JSON** que verás en las APIs y en las respuestas de los modelos de IA.
> Ojo: Python empieza a contar desde **0**, no desde 1.
"""))

cells.append(code(r'''
# ============================================================
# CELDA 3.1 — Crear y leer una lista
# ============================================================

colores = ['rojo', 'verde', 'azul']   # Una lista con tres textos

print(colores[0])    # El primero está en la posición 0 (¡no en la 1!)
print(colores[2])    # El tercero está en la posición 2
print(len(colores))  # len() cuenta cuántos elementos hay

print('✅ Lista creada y leída')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 3.2 — Agregar elementos a una lista
# ============================================================
# .append() agrega un elemento al final de la lista.

colores.append('amarillo')   # Ahora la lista tiene 4 elementos

print(colores)

print('✅ Elemento agregado')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 3.3 — Crear y leer un diccionario
# ============================================================
# Cada elemento es "etiqueta: valor". Para leer un valor, escribes la etiqueta entre corchetes.

persona = {
    'nombre': 'Ana',        # Etiqueta 'nombre' → valor 'Ana'
    'edad': 28,             # Etiqueta 'edad' → valor 28
    'ciudad': 'Bogotá'      # Etiqueta 'ciudad' → valor 'Bogotá'
}

print(persona['nombre'])    # Lee el valor de la etiqueta 'nombre'
print(persona['ciudad'])    # Lee el valor de la etiqueta 'ciudad'

print('✅ Diccionario creado y leído')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 3.4 — Modificar y agregar datos en un diccionario
# ============================================================

persona['edad'] = 29            # Cambia un valor que ya existía
persona['profesion'] = 'Diseño' # Si la etiqueta no existe, la crea

print(persona)

print('✅ Diccionario actualizado')
'''))

# ─── PARTE 4 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🔀 PARTE 4 — Decisiones (`if`) y repeticiones (`for`)

Hasta ahora el código se ejecuta línea por línea. Con estas dos herramientas puedes:

| Herramienta | Qué hace | Se lee como |
|-------------|----------|-------------|
| `if` / `else` | Elige un camino según una condición | "**Si** pasa esto, haz A; **si no**, haz B" |
| `for` | Repite algo para cada elemento | "**Para cada** elemento de la lista, haz esto" |

> ⚠️ **La sangría importa.** Python usa los espacios al inicio de la línea (4 espacios) para saber qué está "dentro" del `if` o del `for`.
> Colab los pone solo cuando pulsas Enter después de los dos puntos `:`.
"""))

cells.append(code(r'''
# ============================================================
# CELDA 4.1 — Tomar una decisión con if / else
# ============================================================
# Los dos puntos ":" al final abren un bloque.
# Las líneas con 4 espacios de sangría pertenecen a ese bloque.

edad_usuario = 17

if edad_usuario >= 18:                       # ">=" significa "mayor o igual que"
    print('Eres mayor de edad')              # Se ejecuta SOLO si la condición es verdadera
else:                                        # "else" = en cualquier otro caso
    print('Eres menor de edad')              # Se ejecuta SOLO si la condición es falsa

print('✅ Decisión tomada')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 4.2 — Repetir con for
# ============================================================
# "for color in colores" significa: para cada elemento de la lista,
# guárdalo en la variable "color" y ejecuta el bloque con sangría.

for color in colores:                        # Recorre la lista de la Parte 3
    print(f'Me gusta el color {color}')      # Se ejecuta una vez por cada color

print('✅ Bucle completado')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 4.3 — Combinar for e if
# ============================================================
# Podemos poner un if DENTRO de un for (nota la doble sangría: 8 espacios).

numeros = [3, 8, 15, 22, 7]   # Lista de números enteros

for numero in numeros:                       # Para cada número...
    if numero % 2 == 0:                      # "%" da el resto de dividir; resto 0 = es par
        print(f'{numero} es par')
    else:
        print(f'{numero} es impar')

print('✅ Combinaste bucle y decisión')
'''))

# ─── PARTE 5 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🔧 PARTE 5 — Funciones

Una **función** es una receta con nombre: la defines una vez y la usas las veces que quieras.

```
        datos de entrada                 resultado
   ┌──► (parámetros) ──► def función ──► return ──►┐
   │                                                │
 precio=100, descuento=20                      80.0
```

| Palabra | Significado |
|---------|-------------|
| `def` | "Voy a definir una función" |
| **parámetros** | Los datos que la función recibe (van entre paréntesis) |
| `return` | El resultado que la función devuelve |

> 🔑 **Esta idea es la base de las demás actividades:** en Gradio, una función de Python es el "motor" de tu app.
> **Definir** una función no la ejecuta: solo la guarda. Para ejecutarla hay que **llamarla**.
"""))

cells.append(code(r'''
# ============================================================
# CELDA 5.1 — Definir una función
# ============================================================
# Esta celda SOLO guarda la receta. No imprime nada todavía.

def aplicar_descuento(precio, porcentaje):    # Recibe 2 datos: precio y porcentaje
    ahorro = precio * porcentaje / 100        # Calcula cuánto se ahorra
    precio_final = precio - ahorro            # Resta el ahorro al precio original
    return precio_final                       # Devuelve el resultado a quien la llamó

print('✅ Función aplicar_descuento() definida (aún no se ha usado)')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 5.2 — Llamar (usar) la función
# ============================================================
# Para ejecutar la función escribimos su nombre y los datos entre paréntesis.
# El resultado se guarda en una variable para poder usarlo.

resultado = aplicar_descuento(100, 20)   # precio=100, porcentaje=20

print(f'Un producto de 100 con 20% de descuento cuesta {resultado}')

print('✅ La función devolvió 80.0 (si ves otro valor, revisa la celda 5.1)')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 5.3 — Reutilizar la misma función con otros datos
# ============================================================
# La ventaja de las funciones: no repites código, solo cambias los datos.

print(aplicar_descuento(250, 10))   # 250 con 10% de descuento
print(aplicar_descuento(80, 50))    # 80 con 50% de descuento

print('✅ Una función, muchos usos')
'''))

# ─── PARTE 6 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 📚 PARTE 6 — Librerías y datos de Internet

Nadie programa todo desde cero. Una **librería** es código que otras personas ya escribieron y tú reutilizas con `import`.

```
  Tu código ──import──► Librería (random, datetime, requests, gradio...)
```

| Librería | Para qué sirve |
|----------|----------------|
| `random` | Números y elecciones al azar |
| `datetime` | Fechas y horas |
| `requests` | Pedir datos a páginas y servicios de Internet (APIs) |
| `gradio` | Crear interfaces web (Parte 8) |

Una **API** es un servicio de Internet al que le pides datos y te los devuelve en un formato como JSON (un diccionario).
Las actividades con IA funcionan exactamente así: tu código le pide texto a un modelo.
"""))

cells.append(code(r'''
# ============================================================
# CELDA 6.1 — Usar random y datetime
# ============================================================

import random                  # Librería para el azar
from datetime import datetime  # De la librería datetime, traemos solo "datetime"

fruta = random.choice(['mango', 'fresa', 'piña'])   # Elige un elemento al azar de la lista
ahora = datetime.now()                              # Fecha y hora actuales del servidor de Google

print(f'Fruta al azar: {fruta}')
print(f'Fecha y hora del servidor: {ahora:%Y-%m-%d %H:%M}')   # %Y-%m-%d %H:%M da formato legible

print('✅ Librerías estándar usadas')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 6.2 — Pedir un dato a una API de Internet
# ============================================================
# requests viene preinstalada en Colab. Hacemos una petición GET (pedir datos)
# a un servicio público que devuelve una frase de sabiduría.
# timeout=10: si en 10 segundos no responde, abandonamos en vez de quedarnos esperando.

import requests   # Librería para hablar con servicios de Internet

try:   # "try" intenta ejecutar el bloque; si algo falla, salta a "except" sin romper el notebook
    respuesta = requests.get('https://api.github.com/zen', timeout=10)
    print(f'Código de estado: {respuesta.status_code}')   # 200 significa "todo salió bien"
    if respuesta.status_code == 200:                      # Solo celebramos si el servicio respondió bien
        print(f'Frase recibida: {respuesta.text}')        # .text es el contenido de la respuesta
        print('✅ Pediste datos a Internet con éxito')
    else:
        print('⚠️ El servicio respondió con un código distinto de 200. Espera un momento y reintenta.')
except requests.RequestException as error:
    print(f'⚠️ No se pudo conectar: {error}')
    print('   Revisa tu conexión y vuelve a ejecutar la celda.')
'''))

# ─── PARTE 7 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🩺 PARTE 7 — Leer errores sin miedo

Todas las personas que programan ven errores **todos los días**. Un error no es un fracaso: es Python diciéndote qué falló.

Cómo leer un error:

```
Traceback (most recent call last):         ← "rastro del error"
  File "...", line 3, in <module>          ← ¿DÓNDE ocurrió? (línea 3)
NameError: name 'precio' is not defined    ← ¿QUÉ pasó? (LEER SIEMPRE LA ÚLTIMA LÍNEA)
```

**Truco:** la **última línea** es la más importante. Dice el tipo de error y la causa.

Para no romper el notebook, provocaremos errores **de forma controlada** con `try/except`:
capturamos el error y lo mostramos.
"""))

cells.append(code(r'''
# ============================================================
# CELDA 7.1 — Error 1: NameError (usar una variable que no existe)
# ============================================================
# Causa típica: te saltaste una celda o escribiste mal el nombre.
# Solución: ejecuta la celda que define la variable, o revisa la ortografía.

try:
    print(variable_que_no_existe)   # Esta variable nunca fue creada → error
except NameError as error:
    print(f'❌ NameError: {error}')
    print('👉 Solución: ejecuta antes la celda que crea esa variable.')

print('✅ Error 1 entendido')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 7.2 — Error 2: TypeError (mezclar tipos que no se pueden mezclar)
# ============================================================
# Causa típica: sumar un texto con un número.
# Solución: convertir con str() o int(), o usar una f-string.

try:
    resultado = 'Tengo ' + 25 + ' años'   # No se puede sumar texto (str) con número (int)
except TypeError as error:
    print(f'❌ TypeError: {error}')
    print('👉 Solución: usa una f-string →', f'Tengo {25} años')

print('✅ Error 2 entendido')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 7.3 — Error 3: IndentationError (sangría incorrecta)
# ============================================================
# Causa típica: faltan los 4 espacios dentro de un if, for o def.
# Usamos compile() para revisar un texto de código sin ejecutarlo.

codigo_malo = 'if True:\nprint("hola")'   # La línea del print no tiene sangría

try:
    compile(codigo_malo, '<ejemplo>', 'exec')   # Python revisa el código y detecta el problema
except IndentationError as error:
    print(f'❌ IndentationError: {error}')
    print('👉 Solución: agrega 4 espacios al inicio de la línea que va dentro del bloque.')

print('✅ Error 3 entendido')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 7.4 — Error 4: KeyError (etiqueta que no existe en un diccionario)
# ============================================================
# Causa típica: escribir mal la etiqueta o pedir una que no se creó.
# Solución: revisa las etiquetas disponibles con .keys().

try:
    print(persona['telefono'])   # El diccionario "persona" no tiene la etiqueta 'telefono'
except KeyError as error:
    print(f'❌ KeyError: falta la etiqueta {error}')
    print(f'👉 Etiquetas disponibles: {list(persona.keys())}')

print('✅ Error 4 entendido')
'''))

# ─── PARTE 8 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🖥️ PARTE 8 — Tu primera mini-app con Gradio

Ahora juntamos todo: usarás la función `aplicar_descuento` de la Parte 5 para crear **una app web real**.

**Gradio** convierte una función de Python en una página web con formulario:

```
  Navegador                    Python
  ┌─────────────────┐ datos   ┌──────────────────────────┐
  │ Precio: [100]   │ ──────► │ aplicar_descuento(100,20)│
  │ Descuento: [20] │         │                          │
  │ Resultado: 80.0 │ ◄────── │ return 80.0              │
  └─────────────────┘         └──────────────────────────┘
```

El orden de los componentes de entrada = el orden de los parámetros de la función.
"""))

cells.append(code(r'''
# ============================================================
# CELDA 8.1 — Importar Gradio
# ============================================================

import gradio as gr   # "gr" es el apodo corto con el que se usa Gradio

print(f'✅ Gradio {gr.__version__} listo')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 8.2 — Probar la función SOLA antes de crear la interfaz
# ============================================================
# Siempre probamos la lógica primero. Si falla aquí, el problema no es Gradio.

print(aplicar_descuento(200, 25))   # Esperado: 150.0

print('✅ La función responde bien (esperado: 150.0)')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 8.3 — Crear la interfaz
# ============================================================
# gr.Interface conecta la función con los componentes de entrada y salida.

demo = gr.Interface(
    fn=aplicar_descuento,                      # La función que creaste en la Parte 5
    inputs=[
        gr.Number(label='Precio', value=100),                                    # 1.er parámetro: precio
        gr.Slider(minimum=0, maximum=100, value=20, label='Descuento (%)'),      # 2.º parámetro: porcentaje
    ],
    outputs=gr.Number(label='Precio final'),   # Aquí aparece lo que devuelve "return"
    title='Calculadora de descuentos',         # Título de la página
    flagging_mode='never'                      # Oculta el botón "Flag" que no necesitamos
)

print('✅ Interfaz creada (todavía no se ve)')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 8.4 — Lanzar la app
# ============================================================
# launch() abre la app aquí mismo. Cambia el precio, mueve el slider y pulsa "Submit".
# quiet=True evita mensajes largos. Si hay error de puerto ocupado, reinicia la sesión.

demo.launch(quiet=True)

print('✅ App lanzada: pruébala arriba 👆')
'''))

# ─── PARTE 9 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🤔 PARTE 9 — Reflexión

Responde en esta misma celda (doble clic para editarla). Entre 2 y 4 líneas por pregunta.

1. **Conceptual:** ¿Qué diferencia hay entre una **lista** y un **diccionario**? Da un ejemplo de dato que guardarías en cada uno.

   *Tu respuesta:*

2. **Código:** En la Parte 5 definiste la función y en otra celda la llamaste. ¿Por qué la celda donde solo se define no muestra ningún resultado?

   *Tu respuesta:*

3. **Implicaciones:** Los errores de la Parte 7 no rompieron el notebook gracias a `try/except`. ¿Cuándo crees que es buena idea capturar un error y cuándo es mejor dejar que el programa falle y se vea?

   *Tu respuesta:*

4. **Comparativa:** ¿Qué ventajas y desventajas tiene programar en Colab frente a instalar Python en tu propio computador?

   *Tu respuesta:*
"""))

# ─── PARTE 10 ────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🏆 PARTE 10 — Retos opcionales

Cada reto tiene una celda vacía debajo. **No están resueltos**: solo tienes una pista de dónde empezar.

- **Reto A — Tu propia función:** crea una función `saludar(nombre, edad)` que devuelva una frase con una f-string.
  *Pista:* copia la estructura de `aplicar_descuento` (Parte 5) y usa la f-string de la Parte 2.

- **Reto B — Lista de precios:** recorre una lista de precios con `for` y muestra cada uno con 15 % de descuento.
  *Pista:* combina la lista de la Parte 3, el `for` de la Parte 4 y tu función de la Parte 5.

- **Reto C — Otra API:** pide datos a `https://api.github.com/users/octocat` y muestra el nombre del usuario.
  *Pista:* usa `requests.get(...)` como en la celda 6.2 y `.json()` para convertir la respuesta en un diccionario; luego lee la etiqueta `'name'`.
"""))

cells.append(code(r'''
# ============================================================
# CELDA 10.1 — Reto A: tu espacio para experimentar
# ============================================================
# (celda vacía a propósito)
'''))

cells.append(code(r'''
# ============================================================
# CELDA 10.2 — Reto B: tu espacio para experimentar
# ============================================================
# (celda vacía a propósito)
'''))

cells.append(code(r'''
# ============================================================
# CELDA 10.3 — Reto C: tu espacio para experimentar
# ============================================================
# (celda vacía a propósito)
'''))

# ─── PARTE 11 ────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🌐 PARTE 11 — Publicación con Ngrok

Tu app solo vive dentro de Colab. Con **Ngrok** abrimos un **túnel** hacia Internet para que otras personas la usen desde su navegador.

```
  Persona (navegador)
        │  https://xxxx.ngrok-free.app
        ▼
  Servidor de Ngrok  ───túnel───►  Colab (localhost:7860)
                                          │
                                          ▼
                                   Tu app Gradio
```

### Paso previo: guardar tu token en Secrets

El token de Ngrok es como una **contraseña**. Nunca se pega dentro del notebook; se guarda en los **Secrets** de Colab:

1. Crea una cuenta gratuita en [ngrok.com](https://ngrok.com) y copia tu *Authtoken* (menú **Your Authtoken**).
2. En Colab, pulsa el icono de la llave 🔑 **Secrets** en la barra izquierda.
3. Pulsa **Add new secret**, nombre `NGROK_TOKEN`, valor: tu token.
4. Activa el interruptor **Notebook access**.
"""))

cells.append(code(r'''
# ============================================================
# CELDA 11.1 — Instalar pyngrok
# ============================================================
# pyngrok es la librería de Python para crear túneles Ngrok.

!pip install -q pyngrok

print('✅ pyngrok instalado')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 11.2 — Autenticar con el token de Ngrok
# ============================================================
# Leemos el token desde Colab Secrets para no dejarlo escrito en el notebook.

from pyngrok import ngrok   # Librería para crear el túnel

try:
    from google.colab import userdata                 # Acceso a los Secrets de Colab
    NGROK_TOKEN = userdata.get('NGROK_TOKEN')         # Lee el secreto llamado NGROK_TOKEN
except Exception as error:
    # Si Secrets falla, usamos una variable manual como último recurso.
    print(f'⚠️ No se pudo leer el Secret: {error}')
    print('⚠️ SEGURIDAD: si pegas el token aquí, bórralo antes de compartir el notebook.')
    NGROK_TOKEN = 'PEGA_TU_TOKEN_AQUI'

# Validamos que no quedó el texto de ejemplo
if NGROK_TOKEN == 'PEGA_TU_TOKEN_AQUI':
    raise ValueError('❌ Falta el token. Guárdalo en Secrets como NGROK_TOKEN (con Notebook access) y reintenta.')

ngrok.set_auth_token(NGROK_TOKEN)   # Registra el token para esta sesión

print('✅ Token de Ngrok configurado')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 11.3 — Abrir el túnel y relanzar la app
# ============================================================
# Orden importante: cerrar lo anterior → abrir túnel → lanzar la app.

demo.close()    # Cierra la app de la Parte 8 para liberar el puerto 7860
ngrok.kill()    # Cierra túneles anteriores (el plan gratuito permite uno a la vez)

tunel = ngrok.connect(7860)   # Crea un túnel público hacia el puerto local 7860
print(f'🌍 URL pública: {tunel.public_url}')
print('   Compártela y ábrela en tu celular para comprobarla.')

# server_name='0.0.0.0' = acepta conexiones externas (las que llegan por el túnel)
# server_port=7860       = el mismo puerto que expusimos con Ngrok
# share=False            = no usamos el enlace temporal de Gradio; Ngrok es más estable
demo.launch(server_name='0.0.0.0', server_port=7860, share=False, quiet=True)

print('✅ App publicada con Ngrok')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 11.4 — Verificar los túneles activos
# ============================================================

tuneles = ngrok.get_tunnels()   # Lista de túneles abiertos en esta sesión

if tuneles:
    print(f'✅ {len(tuneles)} túnel(es) activo(s):')
    for t in tuneles:
        print(f'   {t.public_url}  →  {t.config["addr"]}')
else:
    print('❌ No hay túneles activos. Ejecuta de nuevo la celda 11.3.')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 11.5 — (Opcional) Dominio estático
# ============================================================
# El plan gratuito permite UN dominio fijo: dashboard.ngrok.com → Domains.
# Así la URL no cambia entre sesiones. Si no tienes uno, sáltate esta celda.

DOMINIO_ESTATICO = ''   # Ej: 'mi-app.ngrok-free.app'

if DOMINIO_ESTATICO:
    ngrok.kill()                                              # Cierra el túnel aleatorio
    tunel = ngrok.connect(7860, domain=DOMINIO_ESTATICO)      # Abre el túnel con tu dominio
    print(f'✅ URL fija: {tunel.public_url}')
else:
    print('ℹ️ Sin dominio estático: se mantiene la URL aleatoria.')
'''))

cells.append(code(r'''
# ============================================================
# CELDA LIMPIEZA — Liberar todos los recursos al terminar
# ============================================================
# Orden: túnel → interfaz. (Esta actividad no usa procesos externos ni GPU.)

ngrok.kill()    # 1. Cierra el túnel Ngrok
print('✅ Túnel Ngrok cerrado')

demo.close()    # 2. Cierra la interfaz Gradio
print('✅ Interfaz Gradio cerrada')

print('\n✅ Recursos liberados. ¡Ya estás listo para las demás actividades del curso!')
'''))

cells.append(md(r"""
## 📊 Rúbrica de Evaluación

| Criterio | Excelente (5) | Satisfactorio (3) | En desarrollo (1) |
|----------|---------------|-------------------|-------------------|
| **Manejo de Colab** | Ejecuta todo en orden, sin errores, y sabe reiniciar la sesión | Completa la actividad con algún reintento | No logra ejecutar las celdas |
| **Fundamentos de Python** | Explica variables, listas, diccionarios, `if`, `for` y funciones con sus palabras | Explica la mitad de los conceptos | No distingue los conceptos |
| **Lectura de errores** | Identifica el tipo de error y su solución en los 4 casos | Identifica 2 de los 4 errores | No interpreta los mensajes de error |
| **Mini-app Gradio** | La app funciona y entiende la relación función ↔ componentes | La app funciona pero sin entender el vínculo | La app no carga |
| **Publicación con Ngrok** | URL pública funcionando y abierta desde otro dispositivo | Ngrok conecta pero sin verificar | No intenta la publicación |
| **Reflexión y retos** | 4 respuestas detalladas y al menos un reto resuelto | Respuestas incompletas o reto parcial | Sin respuestas ni retos |
"""))

for i, cell in enumerate(cells):
    cell["id"] = f"cell-{i:02d}"

notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"},
        "colab": {"provenance": []}
    },
    "cells": cells
}

with open("PythonColabBasico.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)

print("✅ PythonColabBasico.ipynb generado correctamente")
print(f"   Total de celdas: {len(cells)}")
