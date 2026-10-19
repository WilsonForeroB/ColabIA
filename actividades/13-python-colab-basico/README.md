# 🐍 Actividad: Python y Google Colab desde Cero

## Resumen

Actividad de nivelación para personas que **nunca han programado** ni usado Google Colab. Enseña, paso a paso y sin escribir código propio, lo mínimo necesario para poder ejecutar y entender el resto de actividades del curso: cómo funciona Colab, los fundamentos de Python, cómo leer errores y cómo crear y publicar una mini-app con Gradio.

> 💡 **Recomendada como primera actividad**, antes de las actividades 01 a 12.

-----

## 📋 Ficha Técnica

|Campo                |Detalle                            |
|---------------------|-----------------------------------|
|**Archivo**          |`PythonColabBasico.ipynb`          |
|**Entorno**          |Google Colab (GPU **no** necesaria)|
|**Duración estimada**|90 – 120 minutos                   |
|**Nivel**            |Básico (sin conocimientos previos) |
|**Partes**           |11 partes + limpieza + rúbrica     |

-----

## 🎯 Objetivos de Aprendizaje

1. Entender qué es Google Colab y ejecutar celdas de código y de texto en el orden correcto
1. Usar variables y los tipos de datos `str`, `int`, `float` y `bool`
1. Manejar colecciones: listas y diccionarios
1. Controlar el flujo con `if`/`else` y `for`
1. Definir y llamar funciones (la base de Gradio y de todas las actividades de IA)
1. Usar librerías con `import` y `pip install`, y pedir datos a una API
1. Leer mensajes de error comunes (`NameError`, `TypeError`, `IndentationError`, `KeyError`)
1. Crear una mini-app con Gradio y publicarla con Ngrok

-----

## ✅ Prerrequisitos

- **Ninguno de programación.** No se necesita experiencia previa
- Cuenta de Google (para Colab)
- Cuenta gratuita en [ngrok.com](https://ngrok.com) con token generado
- Token guardado en Colab Secrets como `NGROK_TOKEN` (con *Notebook access* activado; el paso a paso está en la Parte 11)

-----

## 🛠️ Stack Tecnológico

|Componente |Herramienta       |Detalle                                        |
|-----------|------------------|-----------------------------------------------|
|Entorno    |Google Colab      |CPU es suficiente, no se usan modelos          |
|Lenguaje   |Python 3          |Versión que provee Colab                       |
|Interfaz   |Gradio 5.x        |`gr.Interface` (versión fijada a `>=5,<6`)     |
|Publicación|Ngrok vía pyngrok |Token desde Colab Secrets                      |

-----

## 🗺️ Estructura de la Actividad

|Parte|Contenido                                                              |
|-----|-----------------------------------------------------------------------|
|1    |Conoce Colab: celdas, orden de ejecución, comandos con `!`, `pip`      |
|2    |Variables, tipos de datos, f-strings y cálculos                        |
|3    |Listas y diccionarios                                                  |
|4    |Decisiones (`if`) y repeticiones (`for`)                               |
|5    |Funciones: definir, llamar y reutilizar                                |
|6    |Librerías (`random`, `datetime`, `requests`) y primera API             |
|7    |Leer errores: 4 errores comunes provocados con `try/except`            |
|8    |Mini-app Gradio: calculadora de descuentos                             |
|9    |Reflexión (4 preguntas)                                                |
|10   |Retos opcionales: función propia, lista de precios, otra API           |
|11   |Publicación con Ngrok (5 celdas) + limpieza + rúbrica                  |

-----

## ▶️ Instrucciones de Ejecución

1. Abre `PythonColabBasico.ipynb` en [Google Colab](https://colab.research.google.com) (menú *Archivo → Subir cuaderno*, o desde GitHub)
1. Ejecuta las celdas **de arriba a abajo**, una por una (botón ▶ o `Shift + Enter`), leyendo los comentarios
1. Si algo sale raro, usa *Entorno de ejecución → Reiniciar sesión* y empieza otra vez desde la primera celda
1. Responde las preguntas de la Parte 9 en su celda markdown
1. Prueba al menos un reto de la Parte 10
1. Guarda `NGROK_TOKEN` en 🔑 **Secrets**, publica con Ngrok (Parte 11), abre la URL desde tu celular y ejecuta la celda de limpieza

-----

## 📊 Rúbrica

|Criterio                |Excelente (5)                                    |Satisfactorio (3)                |En desarrollo (1)               |
|------------------------|-------------------------------------------------|---------------------------------|--------------------------------|
|Manejo de Colab         |Todo en orden, sin errores, sabe reiniciar sesión|Completa con algún reintento     |No logra ejecutar las celdas    |
|Fundamentos de Python   |Explica los 6 conceptos con sus palabras         |Explica la mitad                 |No distingue los conceptos      |
|Lectura de errores      |Identifica tipo y solución en los 4 casos        |Identifica 2 de 4                |No interpreta los errores       |
|Mini-app Gradio         |Funciona y entiende la relación función ↔ componentes|Funciona sin entender el vínculo|La app no carga                 |
|Publicación con Ngrok   |URL pública abierta desde otro dispositivo       |Ngrok conecta sin verificar      |No intenta la publicación       |
|Reflexión y retos       |4 respuestas detalladas y un reto resuelto       |Respuestas incompletas o reto parcial|Sin respuestas ni retos     |

-----

## 📎 Entrega

1. El notebook `.ipynb` con todas las celdas ejecutadas
1. Las preguntas de reflexión respondidas en la Parte 9
1. Captura de pantalla de la URL de Ngrok funcionando en el navegador

-----

## 🔧 Regenerar el notebook

El notebook se genera con `build_notebook.py` (ejecutar dentro de esta carpeta):

```bash
python build_notebook.py
```
