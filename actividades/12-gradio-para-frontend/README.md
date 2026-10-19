# 🎨 Actividad: Gradio para Desarrolladores Frontend

## Resumen

Actividad introductoria, sencilla y pedagógica para personas con perfil **frontend**. El estudiante aprende Gradio comparándolo con lo que ya conoce (HTML, CSS, eventos de JavaScript, React) y construye una app web con tarjeta de presentación y contador de texto escrita solo en Python. Al final la publica en Internet con Ngrok.

-----

## 📋 Ficha Técnica

|Campo                |Detalle                         |
|---------------------|--------------------------------|
|**Archivo**          |`GradioParaFrontend.ipynb`      |
|**Entorno**          |Google Colab (GPU **no** necesaria)|
|**Duración estimada**|60 – 90 minutos                 |
|**Nivel**            |Básico                          |
|**Partes**           |10 partes + limpieza + rúbrica  |

-----

## 🎯 Objetivo de Aprendizaje

1. Entender que en Gradio **una función de Python es el backend** y los componentes son sus entradas y salidas
1. Relacionar componentes Gradio con elementos HTML (`Textbox`, `Slider`, `Dropdown`, `Checkbox`)
1. Organizar la vista con `gr.Blocks`, `Row`, `Column` y `Tab` (equivalentes a flexbox y pestañas)
1. Conectar eventos `click`, `submit` y `change` (equivalentes a `addEventListener`)
1. Personalizar la interfaz con temas y CSS propio, y renderizar HTML con `gr.HTML`
1. Publicar la app en Internet con un túnel Ngrok

-----

## ✅ Prerrequisitos

- Conocimientos básicos de HTML, CSS y JavaScript (eventos, formularios)
- **No** se requiere experiencia previa en Python ni en IA: el notebook comenta cada línea
- Cuenta de Google (para Colab)
- Cuenta gratuita en [ngrok.com](https://ngrok.com) con token generado
- Token guardado en Colab Secrets como `NGROK_TOKEN` (con *Notebook access* activado)

-----

## 🛠️ Stack Tecnológico

|Componente  |Herramienta         |Detalle                                    |
|------------|--------------------|-------------------------------------------|
|Entorno     |Google Colab        |CPU es suficiente, no se usan modelos      |
|Interfaz    |Gradio 5.x          |`gr.Interface` y `gr.Blocks` (versión fijada a `>=5,<6`)|
|Publicación |Ngrok vía pyngrok   |Token desde Colab Secrets                  |

-----

## 🗺️ Estructura de la Actividad

|Parte|Contenido                                                          |
|-----|-------------------------------------------------------------------|
|1    |Instalación de Gradio y verificación de versión                    |
|2    |Primera app con `gr.Interface` (función → prueba → interfaz)       |
|3    |Componentes de entrada/salida: generador de tarjeta                |
|4    |Layout con `gr.Blocks`, `Row`, `Column`, `Tab`                     |
|5    |Eventos `click`, `submit` y `change`                               |
|6    |Temas, CSS propio, `elem_classes` y `gr.HTML`                      |
|7    |App final integrada con dos pestañas                               |
|8    |Reflexión (4 preguntas)                                            |
|9    |Retos opcionales: color por rol, `gr.State`, conectar una IA       |
|10   |Publicación con Ngrok (5 celdas) + limpieza + rúbrica              |

-----

## ▶️ Instrucciones de Ejecución

1. Abre `GradioParaFrontend.ipynb` en [Google Colab](https://colab.research.google.com)
1. Guarda `NGROK_TOKEN` en 🔑 **Secrets** y activa el acceso desde el notebook
1. Ejecuta las celdas **de arriba a abajo**, una por una, leyendo los comentarios
1. Responde las preguntas de la Parte 8 en su celda markdown
1. Prueba al menos un reto de la Parte 9
1. Publica con Ngrok (Parte 10), abre la URL desde tu celular y ejecuta la celda de limpieza

> Si ves un error de puerto ocupado, ejecuta la celda de cierre (`demo.close()`) de la parte anterior y reintenta.

-----

## 📊 Rúbrica

|Criterio                   |Excelente (5)                        |Satisfactorio (3)               |En desarrollo (1)              |
|---------------------------|-------------------------------------|--------------------------------|-------------------------------|
|Instalación y configuración|Parte 1 sin errores                  |Funciona tras algún reintento   |No logra importar Gradio       |
|Componentes y eventos      |`click`, `submit` y `change` funcionan y explica la diferencia|Funcionan 2 de 3|Los eventos no responden       |
|Layout y estilos           |`Row`/`Column`/`Tab` y CSS aplicado  |Layout correcto sin CSS visible |Todo apilado sin estructura    |
|Publicación con Ngrok      |URL pública abierta desde otro dispositivo|Ngrok conecta sin verificar|No intenta la publicación      |
|Reflexión escrita          |4 respuestas detalladas con ejemplos |Respuestas incompletas          |Sin respuestas                 |
|Reto opcional              |Implementa y explica al menos uno    |Intenta uno parcialmente        |No intenta los retos           |

-----

## 📎 Entrega

1. El notebook `.ipynb` con todas las celdas ejecutadas
1. Las preguntas de reflexión respondidas en la Parte 8
1. Captura de pantalla de la URL de Ngrok funcionando en el navegador

-----

## 🔧 Regenerar el notebook

El notebook se genera con `build_notebook.py` (ejecutar dentro de esta carpeta):

```bash
python build_notebook.py
```
