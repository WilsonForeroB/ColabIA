"""Script para generar GradioParaFrontend.ipynb"""
import json


def code(source):
    return {"cell_type": "code", "execution_count": None, "id": "", "metadata": {},
            "outputs": [], "source": source.strip("\n") + "\n"}


def md(source):
    return {"cell_type": "markdown", "id": "", "metadata": {}, "source": source.strip("\n") + "\n"}


cells = []

# ─── HEADER ──────────────────────────────────────────────────────────────────
cells.append(md(r"""
# 🎨 Actividad 12 — Gradio para Desarrolladores Frontend

## ¿Qué construirás?

Una **app web interactiva** escrita solo en Python, sin HTML, sin JavaScript y sin `npm install`.
Aprenderás Gradio comparándolo con lo que ya sabes de frontend:

| Lo que ya conoces (Frontend) | Su equivalente en Gradio |
|------------------------------|--------------------------|
| `<input>`, `<select>`, `<input type="range">` | `gr.Textbox`, `gr.Dropdown`, `gr.Slider` |
| `<div style="display:flex">` | `gr.Row()` y `gr.Column()` |
| Pestañas / tabs | `gr.Tab()` |
| `button.addEventListener('click', fn)` | `boton.click(fn, inputs, outputs)` |
| `input.addEventListener('input', fn)` | `componente.change(fn, inputs, outputs)` |
| `element.innerHTML = ...` | `gr.HTML` |
| Archivo `.css` | `gr.Blocks(css=...)` |
| `fetch()` a un backend | No hace falta: la función de Python **es** el backend |

## La idea central

> En Gradio **una función de Python es tu backend**.
> Los componentes son sus entradas y salidas. Gradio genera el frontend por ti.

```
  Navegador (componentes)           Servidor Python
  ┌───────────────────┐   inputs   ┌─────────────────────┐
  │ Textbox / Slider  │ ─────────► │  def mi_funcion(..) │
  │ Dropdown ...      │            │      return ...     │
  │                   │ ◄───────── │                     │
  │ Salida (texto/HTML)│  outputs  └─────────────────────┘
  └───────────────────┘
```

## Mapa de la actividad

| Parte | Tema |
|-------|------|
| 1 | Instalación y configuración |
| 2 | Tu primera app con `gr.Interface` |
| 3 | Componentes de entrada y salida |
| 4 | Layout con `gr.Blocks`, `Row`, `Column` y `Tab` |
| 5 | Eventos: `click`, `change` y `submit` |
| 6 | Estilos: temas y CSS propio |
| 7 | App final integrada |
| 8 | Reflexión |
| 9 | Retos opcionales |
| 10 | Publicación con Ngrok + limpieza + rúbrica |

**⏱️ Duración:** 60–90 minutos · **GPU:** no es necesaria (no usamos modelos de IA pesados)
"""))

# ─── PARTE 1 ─────────────────────────────────────────────────────────────────
cells.append(md("## ⚙️ PARTE 1 — Instalación y configuración del entorno"))

cells.append(code(r'''
# ============================================================
# CELDA 1.1 — Instalar Gradio
# ============================================================
# Fijamos gradio>=5,<6 para que el notebook se comporte igual aunque salgan versiones nuevas
# (en Gradio 6 los parámetros theme y css se movieron de Blocks a launch()).
# Gradio es una librería de Python que crea interfaces web a partir de funciones.
# Es el equivalente a "instalar el framework" en un proyecto frontend,
# pero aquí es un solo comando y no hay bundler ni configuración.

# -q = quiet: reduce el ruido de la salida de pip
!pip install -q 'gradio>=5,<6'

print('✅ Gradio instalado')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 1.2 — Importar Gradio y verificar la versión
# ============================================================
# Por convención, Gradio se importa con el alias "gr" (como "$" en jQuery o "React" en React).

import gradio as gr   # Librería principal para construir la interfaz

# gr.__version__ nos dice qué versión quedó instalada.
# Es útil si alguna vez la documentación no coincide con lo que ves.
print(f'✅ Gradio {gr.__version__} listo para usar')
'''))

# ─── PARTE 2 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 👋 PARTE 2 — Tu primera app con `gr.Interface`

`gr.Interface` es la forma **más corta** de crear una app. Solo necesita tres cosas:

```
gr.Interface(
    fn      = tu_funcion,     ← el "backend": una función de Python normal
    inputs  = "textbox",      ← qué componente recoge los datos
    outputs = "textbox",      ← qué componente muestra el resultado
)
```

Piensa en él como un **componente "todo en uno"**: formulario + botón + resultado.

**Orden que seguiremos (siempre igual):**
1. Escribimos la función y la **probamos sola** (sin interfaz)
2. Recién entonces la conectamos a Gradio
"""))

cells.append(code(r'''
# ============================================================
# CELDA 2.1 — Definir una función normal de Python
# ============================================================
# Esta función NO sabe nada de Gradio. Es Python puro.
# Eso es lo bonito: puedes probarla, reutilizarla o llevarla a otro proyecto.

def saludar(nombre):
    # f-string: inserta la variable "nombre" dentro del texto
    # (igual que los template literals `Hola ${nombre}` de JavaScript)
    return f'¡Hola, {nombre}! 👋 Bienvenido a Gradio.'

print('✅ Función saludar() definida')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 2.2 — Probar la función SOLA, antes de crear la interfaz
# ============================================================
# Siempre probamos primero la lógica. Si falla aquí, sabemos que el problema
# está en la función y no en Gradio.

print(saludar('Ada'))   # Debe imprimir el saludo con el nombre "Ada"

print('✅ La función responde correctamente')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 2.3 — Conectar la función a una interfaz Gradio
# ============================================================
# Interface recibe la función y los tipos de entrada y salida.
# Gradio mira la función, crea los componentes y conecta todo automáticamente.

demo_saludo = gr.Interface(
    fn=saludar,              # Función que se ejecuta cuando el usuario envía el formulario
    inputs='textbox',        # Atajo en texto para gr.Textbox(): una caja de texto de entrada
    outputs='textbox',       # Una caja de texto (de solo lectura) para mostrar el resultado
    title='Mi primera app',  # Título que aparece arriba (como un <h1>)
    flagging_mode='never'    # Oculta el botón "Flag" que no necesitamos en esta actividad
)

print('✅ Interfaz creada (todavía no se muestra)')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 2.4 — Lanzar la app dentro del notebook
# ============================================================
# launch() levanta un servidor web local y muestra la app aquí mismo en Colab.
# Escribe tu nombre en la caja y pulsa "Submit".
#
# quiet=True evita mensajes largos de arranque.
# Si ves un error de "puerto ocupado", ejecuta la celda 2.5 y vuelve a intentar.

demo_saludo.launch(quiet=True)

print('✅ App lanzada: pruébala arriba 👆')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 2.5 — Cerrar la app de esta parte
# ============================================================
# close() apaga el servidor de esta app y libera su puerto.
# Es buena costumbre cerrar cada demo antes de pasar a la siguiente.

demo_saludo.close()

print('✅ App de la Parte 2 cerrada')
'''))

# ─── PARTE 3 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🧩 PARTE 3 — Componentes de entrada y salida

Cada componente de Gradio se parece a un elemento de formulario HTML:

| Gradio | HTML equivalente | Valor que recibe tu función |
|--------|------------------|-----------------------------|
| `gr.Textbox()` | `<input type="text">` / `<textarea>` | `str` |
| `gr.Slider(0, 10)` | `<input type="range">` | `int` o `float` |
| `gr.Checkbox()` | `<input type="checkbox">` | `bool` |
| `gr.Dropdown([...])` | `<select>` | `str` (la opción elegida) |

**La regla de oro:** el orden de la lista `inputs` = el orden de los parámetros de tu función.

```
inputs=[nombre_box, edad_slider]   ──►   def mi_funcion(nombre, edad): ...
          1º            2º                                1º       2º
```

Construiremos un **generador de tarjeta de presentación** que usaremos hasta el final.
"""))

cells.append(code(r'''
# ============================================================
# CELDA 3.1 — Definir la función que genera la tarjeta
# ============================================================
# Recibe 4 valores (uno por cada componente) y devuelve un texto.
# Cada parámetro llega con el tipo de dato de su componente.

def crear_tarjeta(nombre, rol, experiencia, disponible):
    # nombre: str (Textbox) | rol: str (Dropdown)
    # experiencia: int (Slider) | disponible: bool (Checkbox)

    # Expresión condicional de una línea (como el operador ternario "? :" de JavaScript)
    estado = 'Disponible para proyectos ✅' if disponible else 'Ocupado por ahora ⏳'

    # Triple comilla = texto de varias líneas. El resultado se mostrará en un Textbox.
    return f"""{nombre}
{rol} · {experiencia} años de experiencia
{estado}"""

print('✅ Función crear_tarjeta() definida')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 3.2 — Probar crear_tarjeta() sola
# ============================================================
# Pasamos los valores a mano, exactamente como los enviaría Gradio.

print(crear_tarjeta('Ada Lovelace', 'Frontend', 5, True))

print('✅ La función devuelve la tarjeta esperada')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 3.3 — Crear la interfaz con 4 componentes de entrada
# ============================================================
# Ahora pasamos objetos de componente (no atajos de texto) para poder
# configurar cada uno: etiqueta, valor inicial, rango, opciones, etc.

demo_tarjeta = gr.Interface(
    fn=crear_tarjeta,   # La función de la celda 3.1
    inputs=[
        # label = texto de la etiqueta | placeholder = texto gris de ayuda (como en HTML)
        gr.Textbox(label='Nombre', placeholder='Ej: Ada Lovelace'),
        # choices = las <option> del <select> | value = opción seleccionada al inicio
        gr.Dropdown(choices=['Frontend', 'Backend', 'Diseño UX', 'DevOps'], value='Frontend', label='Rol'),
        # minimum / maximum / step = atributos min, max y step del <input type="range">
        gr.Slider(minimum=0, maximum=30, step=1, value=3, label='Años de experiencia'),
        # value=True deja la casilla marcada al inicio
        gr.Checkbox(value=True, label='¿Disponible para proyectos?'),
    ],
    outputs=gr.Textbox(label='Tu tarjeta', lines=3),   # lines=3: altura de la caja
    title='Generador de tarjeta',
    flagging_mode='never'
)

print('✅ Interfaz con 4 componentes creada')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 3.4 — Lanzar y probar los 4 componentes
# ============================================================
# Mueve el slider, cambia el rol, marca/desmarca la casilla y pulsa "Submit".
# Observa cómo el valor de cada componente llega a la función en el orden correcto.

demo_tarjeta.launch(quiet=True)

print('✅ App lanzada: juega con los componentes arriba 👆')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 3.5 — Cerrar la app de esta parte
# ============================================================
demo_tarjeta.close()   # Libera el puerto

print('✅ App de la Parte 3 cerrada')
'''))

# ─── PARTE 4 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 📐 PARTE 4 — Layout con `gr.Blocks`

`gr.Interface` es rápido pero rígido. Para controlar el diseño usamos **`gr.Blocks`**:
aquí tú decides qué va dónde, igual que armas un layout con `div`s.

| Gradio | Equivalente CSS / HTML |
|--------|------------------------|
| `with gr.Blocks() as demo:` | El `<body>` / componente raíz |
| `with gr.Row():` | `display: flex; flex-direction: row` |
| `with gr.Column():` | `display: flex; flex-direction: column` |
| `with gr.Tab("Nombre"):` | Un panel de pestañas |

El bloque `with` funciona como el anidamiento de etiquetas HTML:
todo lo que escribas **indentado dentro** queda **dentro** del contenedor.

```
with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():  ← columna izquierda (entradas)
        with gr.Column():  ← columna derecha (salidas)
```

> ⚠️ Con `Blocks` los componentes **no están conectados todavía**.
> Eso lo hacemos con eventos en la Parte 5. Aquí solo organizamos la vista.
"""))

cells.append(code(r'''
# ============================================================
# CELDA 4.1 — Construir un layout de dos columnas con pestañas
# ============================================================
# Solo dibujamos la estructura. Los botones aún no hacen nada (eso es la Parte 5).

with gr.Blocks() as demo_layout:                      # Contenedor raíz de toda la app
    gr.Markdown('# 🧱 Mi primer layout')              # Markdown = texto con formato (títulos, negritas...)

    with gr.Tab('Formulario'):                        # Primera pestaña
        with gr.Row():                                # Fila: sus hijos quedan lado a lado
            with gr.Column():                         # Columna izquierda
                gr.Textbox(label='Nombre')            # Un campo de entrada
                gr.Slider(0, 30, label='Años')        # Otro campo (0 = mínimo, 30 = máximo)
            with gr.Column():                         # Columna derecha
                gr.Textbox(label='Resultado')         # Una salida

    with gr.Tab('Ayuda'):                             # Segunda pestaña
        gr.Markdown('Aquí podría ir la documentación de tu app.')

print('✅ Layout creado')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 4.2 — Ver el layout
# ============================================================
# Cambia entre las pestañas y observa que las dos columnas quedan lado a lado.
# Prueba reducir el ancho del navegador: Gradio es responsive, como un buen CSS.

demo_layout.launch(quiet=True)

print('✅ Layout visible arriba 👆')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 4.3 — Cerrar la app de esta parte
# ============================================================
demo_layout.close()   # Libera el puerto

print('✅ App de la Parte 4 cerrada')
'''))

# ─── PARTE 5 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## ⚡ PARTE 5 — Eventos: dar vida a la interfaz

Aquí está lo más parecido a tu día a día como frontend. En Gradio los eventos se escriben así:

```
componente.evento( fn,  inputs=[...],  outputs=[...] )
```

| JavaScript | Gradio |
|------------|--------|
| `btn.addEventListener('click', handler)` | `btn.click(fn, inputs, outputs)` |
| `input.addEventListener('input', handler)` | `caja.change(fn, inputs, outputs)` (se dispara al cambiar el valor) |
| `form.addEventListener('submit', handler)` | `caja.submit(fn, inputs, outputs)` (al pulsar Enter) |

**Diferencia clave con JS:** no lees valores con `document.getElementById(...).value`.
Gradio **te entrega** los valores de `inputs` como argumentos y **escribe** lo que devuelvas en `outputs`.

Reutilizaremos `crear_tarjeta()` de la Parte 3 y la conectaremos de **tres formas distintas**.
"""))

cells.append(code(r'''
# ============================================================
# CELDA 5.1 — Conectar eventos click, submit y change
# ============================================================
# Una misma función puede dispararse desde varios eventos.

with gr.Blocks() as demo_eventos:
    gr.Markdown('# ⚡ Eventos en Gradio')

    with gr.Row():
        with gr.Column():
            nombre = gr.Textbox(label='Nombre', placeholder='Escribe y pulsa Enter')
            rol = gr.Dropdown(['Frontend', 'Backend', 'Diseño UX', 'DevOps'], value='Frontend', label='Rol')
            experiencia = gr.Slider(0, 30, step=1, value=3, label='Años de experiencia')
            disponible = gr.Checkbox(value=True, label='¿Disponible?')
            boton = gr.Button('Crear tarjeta', variant='primary')   # variant='primary' = botón destacado
        with gr.Column():
            salida = gr.Textbox(label='Tu tarjeta', lines=3)

    # Guardamos las entradas en una lista para no repetirla en cada evento.
    entradas = [nombre, rol, experiencia, disponible]

    # EVENTO 1 — click: se ejecuta al pulsar el botón
    boton.click(crear_tarjeta, inputs=entradas, outputs=salida)

    # EVENTO 2 — submit: se ejecuta al pulsar Enter dentro de la caja de nombre
    nombre.submit(crear_tarjeta, inputs=entradas, outputs=salida)

    # EVENTO 3 — change: se ejecuta cada vez que mueves el slider (actualización "en vivo")
    experiencia.change(crear_tarjeta, inputs=entradas, outputs=salida)

print('✅ Eventos conectados')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 5.2 — Probar los tres eventos
# ============================================================
# 1) Escribe un nombre y pulsa Enter        → evento submit
# 2) Pulsa el botón "Crear tarjeta"          → evento click
# 3) Mueve el slider                         → evento change (la tarjeta cambia sola)

demo_eventos.launch(quiet=True)

print('✅ Prueba los tres eventos arriba 👆')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 5.3 — Cerrar la app de esta parte
# ============================================================
demo_eventos.close()   # Libera el puerto

print('✅ App de la Parte 5 cerrada')
'''))

# ─── PARTE 6 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🎨 PARTE 6 — Estilos: temas y CSS propio

Como frontend, aquí te sentirás en casa. Gradio ofrece dos niveles de personalización:

| Nivel | Cómo | Equivalente |
|-------|------|-------------|
| **Tema** | `gr.Blocks(theme=gr.themes.Soft())` | Un design system ya hecho |
| **CSS propio** | `gr.Blocks(css="...")` + `elem_classes=["mi-clase"]` | Tu hoja de estilos y tus clases |

`elem_classes` es el equivalente a `class="..."` en HTML: le pone una clase CSS al componente.

Además usaremos **`gr.HTML`**, que dibuja HTML crudo (como `innerHTML`),
para mostrar la tarjeta con un diseño real en lugar de texto plano.
"""))

cells.append(code(r'''
# ============================================================
# CELDA 6.1 — Función que devuelve HTML en lugar de texto
# ============================================================
# Misma información que crear_tarjeta(), pero con etiquetas HTML y clases CSS.
# Las clases ("tarjeta", "estado-on"...) se definirán en el CSS de la siguiente celda.

def crear_tarjeta_html(nombre, rol, experiencia, disponible):
    # Si el usuario no escribió nombre, usamos un texto por defecto
    nombre = nombre or 'Tu nombre aquí'

    # Elegimos la clase CSS y el texto según la disponibilidad
    clase_estado = 'estado-on' if disponible else 'estado-off'
    texto_estado = 'Disponible' if disponible else 'Ocupado'

    # f-string con HTML. Las llaves {} insertan variables de Python en el HTML.
    return f"""
    <div class="tarjeta">
        <h2>{nombre}</h2>
        <p class="rol">{rol} · {experiencia} años</p>
        <span class="{clase_estado}">{texto_estado}</span>
    </div>
    """

print('✅ Función crear_tarjeta_html() definida')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 6.2 — Probar la función HTML sola
# ============================================================
# Veremos el HTML como texto. Debe contener las etiquetas <div>, <h2> y <span>.

print(crear_tarjeta_html('Ada', 'Frontend', 5, True))

print('✅ La función genera HTML correctamente')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 6.3 — Definir el CSS de la tarjeta
# ============================================================
# Es una cadena de texto con CSS normal. Se la pasaremos a gr.Blocks(css=...).
# Guardarla en una variable la mantiene ordenada y reutilizable.

css_tarjeta = """
.tarjeta {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);  /* Degradado morado */
    color: white;
    padding: 24px;
    border-radius: 16px;                                    /* Esquinas redondeadas */
    box-shadow: 0 8px 24px rgba(99, 102, 241, 0.35);        /* Sombra suave */
}
.tarjeta h2 { margin: 0 0 8px 0; color: white; }
.tarjeta .rol { margin: 0 0 16px 0; opacity: 0.9; }
.estado-on, .estado-off {
    padding: 4px 12px;
    border-radius: 999px;                                   /* Forma de píldora */
    font-size: 0.85rem;
    font-weight: 600;
}
.estado-on  { background: #22c55e; }                        /* Verde */
.estado-off { background: #f59e0b; }                        /* Ámbar */
"""

print('✅ CSS definido')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 6.4 — Construir la app con tema + CSS propio
# ============================================================
# theme=gr.themes.Soft() aplica un tema prediseñado (colores y bordes suaves).
# css=css_tarjeta inyecta nuestra hoja de estilos para la tarjeta.

with gr.Blocks(theme=gr.themes.Soft(), css=css_tarjeta) as demo_estilos:
    gr.Markdown('# 🎨 Tarjeta con estilo')

    with gr.Row():
        with gr.Column():
            nombre = gr.Textbox(label='Nombre')
            rol = gr.Dropdown(['Frontend', 'Backend', 'Diseño UX', 'DevOps'], value='Frontend', label='Rol')
            experiencia = gr.Slider(0, 30, step=1, value=3, label='Años de experiencia')
            disponible = gr.Checkbox(value=True, label='¿Disponible?')
            boton = gr.Button('Crear tarjeta', variant='primary')
        with gr.Column():
            # gr.HTML dibuja el HTML que devuelva la función (como asignar a innerHTML)
            salida = gr.HTML(label='Tarjeta')

    # Mismo patrón de evento que en la Parte 5, pero con la función que devuelve HTML
    boton.click(crear_tarjeta_html, inputs=[nombre, rol, experiencia, disponible], outputs=salida)

print('✅ App con estilos creada')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 6.5 — Ver la app con estilos
# ============================================================
# Rellena los campos y pulsa "Crear tarjeta". Verás la tarjeta con degradado.

demo_estilos.launch(quiet=True)

print('✅ App con estilos visible arriba 👆')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 6.6 — Cerrar la app de esta parte
# ============================================================
demo_estilos.close()   # Libera el puerto

print('✅ App de la Parte 6 cerrada')
'''))

# ─── PARTE 7 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🧪 PARTE 7 — App final integrada

Juntamos todo lo aprendido en **una sola app con dos pestañas**:

| Pestaña | Qué demuestra |
|---------|---------------|
| 🪪 Tarjeta | Componentes + eventos + CSS (Partes 3, 5 y 6) |
| 🔢 Contador de texto | Un evento `change` "en vivo" mientras escribes |

Esta es la app (`demo`) que publicaremos en Internet en la Parte 10.
"""))

cells.append(code(r'''
# ============================================================
# CELDA 7.1 — Función del contador de texto
# ============================================================
# Se ejecutará cada vez que el usuario escriba una letra (evento change).

def contar_texto(texto):
    # len(texto) = número de caracteres; texto.split() separa por espacios para contar palabras
    caracteres = len(texto)
    palabras = len(texto.split())

    # Devolvemos DOS valores: Gradio los repartirá en los DOS outputs, en el mismo orden.
    return caracteres, palabras

print('✅ Función contar_texto() definida')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 7.2 — Probar contar_texto() sola
# ============================================================
# "Hola mundo Gradio" tiene 17 caracteres y 3 palabras.

caracteres, palabras = contar_texto('Hola mundo Gradio')
print(f'Caracteres: {caracteres} | Palabras: {palabras}')

print('✅ El contador funciona (esperado: 17 caracteres, 3 palabras)')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 7.3 — Construir la app final con dos pestañas
# ============================================================
# Reutilizamos crear_tarjeta_html (Parte 6), contar_texto (7.1) y css_tarjeta (6.3).

with gr.Blocks(theme=gr.themes.Soft(), css=css_tarjeta, title='Gradio para Frontend') as demo:
    gr.Markdown('# 🚀 Mi app Gradio\nConstruida solo con Python.')

    # ---------- Pestaña 1: tarjeta ----------
    with gr.Tab('🪪 Tarjeta'):
        with gr.Row():
            with gr.Column():
                t_nombre = gr.Textbox(label='Nombre')
                t_rol = gr.Dropdown(['Frontend', 'Backend', 'Diseño UX', 'DevOps'], value='Frontend', label='Rol')
                t_exp = gr.Slider(0, 30, step=1, value=3, label='Años de experiencia')
                t_disp = gr.Checkbox(value=True, label='¿Disponible?')
                t_boton = gr.Button('Crear tarjeta', variant='primary')
            with gr.Column():
                t_salida = gr.HTML()

        # Evento click: llama a la función con los 4 valores y pinta el HTML resultante
        t_boton.click(crear_tarjeta_html, inputs=[t_nombre, t_rol, t_exp, t_disp], outputs=t_salida)

    # ---------- Pestaña 2: contador ----------
    with gr.Tab('🔢 Contador de texto'):
        c_texto = gr.Textbox(label='Escribe algo', lines=4)
        with gr.Row():
            c_caracteres = gr.Number(label='Caracteres')   # gr.Number = salida numérica
            c_palabras = gr.Number(label='Palabras')

        # Evento change: se dispara con cada letra. Una entrada, DOS salidas (en orden).
        c_texto.change(contar_texto, inputs=c_texto, outputs=[c_caracteres, c_palabras])

print('✅ App final construida')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 7.4 — Probar la app final
# ============================================================
# Crea una tarjeta en la primera pestaña y escribe en la segunda para ver el conteo en vivo.

demo.launch(quiet=True)

print('✅ App final visible arriba 👆')
'''))

# ─── PARTE 8 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🤔 PARTE 8 — Reflexión

Responde en esta misma celda (haz doble clic para editarla). Entre 2 y 4 líneas por pregunta.

1. **Conceptual:** ¿Qué diferencia hay entre `gr.Interface` y `gr.Blocks`? ¿En qué casos usarías cada uno?

   *Tu respuesta:*

2. **Código:** En `c_texto.change(contar_texto, inputs=c_texto, outputs=[c_caracteres, c_palabras])`, ¿por qué la función devuelve dos valores y qué determina a cuál componente va cada uno?

   *Tu respuesta:*

3. **Implicaciones:** Gradio permite que alguien sin conocimientos de frontend publique una interfaz en minutos. ¿Qué ventajas y qué riesgos trae esto (por ejemplo, seguridad, accesibilidad o consistencia visual)?

   *Tu respuesta:*

4. **Comparativa:** ¿Qué ventajas y desventajas tiene Gradio frente a construir la misma app con React + una API en FastAPI?

   *Tu respuesta:*
"""))

# ─── PARTE 9 ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🏆 PARTE 9 — Retos opcionales

Cada reto tiene una celda vacía debajo. Usa `demo` o crea tu propio `gr.Blocks`.
Los retos **no están resueltos**: solo tienes una pista de dónde empezar.

- **Reto A — Modo oscuro:** haz que la tarjeta cambie de color según el rol elegido.
  *Pista:* en `crear_tarjeta_html` elige una clase CSS distinta según `rol` y defínela en el CSS.

- **Reto B — Galería de tarjetas:** guarda cada tarjeta creada y muéstralas todas juntas.
  *Pista:* investiga `gr.State()`, que guarda datos entre eventos (como el `useState` de React).

- **Reto C — Conecta una IA:** reemplaza `contar_texto` por una función que llame a un modelo (Ollama o la API de Claude) y muestre su respuesta.
  *Pista:* tu función solo tiene que recibir un `str` y devolver un `str`; Gradio no necesita saber nada más.
"""))

cells.append(code(r'''
# ============================================================
# CELDA 9.1 — Reto A: tu espacio para experimentar
# ============================================================
# (celda vacía a propósito)
'''))

cells.append(code(r'''
# ============================================================
# CELDA 9.2 — Reto B: tu espacio para experimentar
# ============================================================
# (celda vacía a propósito)
'''))

cells.append(code(r'''
# ============================================================
# CELDA 9.3 — Reto C: tu espacio para experimentar
# ============================================================
# (celda vacía a propósito)
'''))

# ─── PARTE 10 ────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 🌐 PARTE 10 — Publicación con Ngrok

Hasta ahora tu app solo vive dentro de Colab. Con **Ngrok** creamos un **túnel** hacia Internet
para que tus compañeros la abran desde su navegador.

```
  Compañero (navegador)
        │  https://xxxx.ngrok-free.app
        ▼
  Servidor de Ngrok  ───túnel───►  Colab (localhost:7860)
                                          │
                                          ▼
                                   Tu app Gradio
```

**Antes de empezar:** crea una cuenta gratuita en [ngrok.com](https://ngrok.com), copia tu *Authtoken*
y guárdalo en Colab: icono 🔑 **Secrets** → *Add new secret* → nombre `NGROK_TOKEN` → pega el token → activa *Notebook access*.
"""))

cells.append(code(r'''
# ============================================================
# CELDA 10.1 — Instalar pyngrok
# ============================================================
# pyngrok es el cliente de Python para manejar túneles Ngrok desde el notebook.

!pip install -q pyngrok

print('✅ pyngrok instalado')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 10.2 — Autenticar con el token de Ngrok
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
'''))

cells.append(code(r'''
# ============================================================
# CELDA 10.3 — Abrir el túnel y relanzar la app
# ============================================================
# Orden importante: cerrar lo anterior → abrir túnel → lanzar la app.

demo.close()    # Cierra la app lanzada en la Parte 7 para liberar el puerto 7860
ngrok.kill()    # Cierra túneles anteriores (el plan gratuito solo permite uno a la vez)

# connect(7860) crea un túnel público hacia el puerto local 7860
tunel = ngrok.connect(7860)
print(f'🌍 URL pública: {tunel.public_url}')
print('   Compártela con tus compañeros y ábrela en tu celular para comprobarla.')

# server_name='0.0.0.0' = acepta conexiones externas (las que llegan por el túnel)
# server_port=7860       = el mismo puerto que expusimos con Ngrok
# share=False            = no usamos el enlace temporal de Gradio; Ngrok es más estable
demo.launch(server_name='0.0.0.0', server_port=7860, share=False, quiet=True)

print('✅ App publicada con Ngrok')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 10.4 — Verificar los túneles activos
# ============================================================
# get_tunnels() lista los túneles abiertos en esta sesión.

tuneles = ngrok.get_tunnels()

if tuneles:
    print(f'✅ {len(tuneles)} túnel(es) activo(s):')
    for t in tuneles:
        print(f'   {t.public_url}  →  {t.config["addr"]}')
else:
    print('❌ No hay túneles activos. Ejecuta de nuevo la celda 10.3.')
'''))

cells.append(code(r'''
# ============================================================
# CELDA 10.5 — (Opcional) Dominio estático
# ============================================================
# Con el plan gratuito puedes reclamar UN dominio fijo en dashboard.ngrok.com → Domains.
# Así la URL no cambia entre sesiones. Si no tienes uno, sáltate esta celda.

DOMINIO_ESTATICO = ''   # Ej: 'mi-app-gradio.ngrok-free.app'

if DOMINIO_ESTATICO:
    ngrok.kill()                                                    # Cierra el túnel aleatorio
    tunel = ngrok.connect(7860, domain=DOMINIO_ESTATICO)            # Abre el túnel con tu dominio
    print(f'✅ URL fija: {tunel.public_url}')
else:
    print('ℹ️ Sin dominio estático configurado: se mantiene la URL aleatoria.')
'''))

# ─── LIMPIEZA ────────────────────────────────────────────────────────────────
cells.append(code(r'''
# ============================================================
# CELDA LIMPIEZA — Liberar todos los recursos al terminar
# ============================================================
# Orden: túnel → interfaz. (Esta actividad no usa procesos externos ni GPU.)

# 1. Cerrar el túnel Ngrok
ngrok.kill()
print('✅ Túnel Ngrok cerrado')

# 2. Cerrar la interfaz Gradio
demo.close()
print('✅ Interfaz Gradio cerrada')

print('\n✅ Todos los recursos liberados. Puedes cerrar el notebook.')
'''))

# ─── RÚBRICA ─────────────────────────────────────────────────────────────────
cells.append(md(r"""
## 📊 Rúbrica de Evaluación

| Criterio | Excelente (5) | Satisfactorio (3) | En desarrollo (1) |
|----------|---------------|-------------------|-------------------|
| **Instalación y configuración** | Gradio instalado y todas las celdas de la Parte 1 sin errores | Gradio funciona tras algún reintento | No logra importar Gradio |
| **Componentes y eventos** | Los 3 eventos (`click`, `submit`, `change`) funcionan y sabe explicar la diferencia | Funcionan 2 de los 3 eventos | La app carga pero los eventos no responden |
| **Layout y estilos** | Usa `Row`/`Column`/`Tab` y el CSS se ve aplicado en la tarjeta | Layout correcto pero sin CSS visible | Todo apilado sin estructura |
| **Publicación con Ngrok** | URL pública funcionando y abierta desde otro dispositivo | Ngrok conecta pero sin verificar desde otro dispositivo | No intenta la publicación |
| **Reflexión escrita** | Las 4 respuestas son detalladas y usan ejemplos de frontend | Respuestas incompletas o genéricas | Sin respuestas |
| **Reto opcional** | Implementa y explica al menos uno | Intenta uno parcialmente | No intenta los retos |
"""))

# ─── Asignar IDs únicos ──────────────────────────────────────────────────────
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

with open("GradioParaFrontend.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)

print("✅ GradioParaFrontend.ipynb generado correctamente")
print(f"   Total de celdas: {len(cells)}")
