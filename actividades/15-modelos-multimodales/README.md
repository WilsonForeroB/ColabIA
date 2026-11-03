# 🎨🔊🎬 Actividad: Modelos Multimodales — imagen, audio y vídeo

## Resumen

Actividad para entender **cómo un modelo de IA convierte imágenes, audio y vídeo en tokens**. Se abre la "caja negra" del tokenizador visual de un Vision Transformer (CLIP ViT-B/32): la imagen se preprocesa, se trocea en parches de 32×32 px y **cada parche se convierte en un vector** con una multiplicación de matrices que se reproduce a mano. Luego se mide cuántos tokens ocupa una imagen dentro de un LLM multimodal (`gemma3:4b`), se transcribe audio con **Whisper** mostrando su espectrograma y sus tokens de audio, y se analiza un vídeo eligiendo fotogramas clave para reducir el coste en tokens. Termina con una interfaz Gradio de tres pestañas publicada con Ngrok.

Todos los datos de ejemplo son **públicos y salen de librerías que ya trae Colab**: no hay que subir archivos.

-----

## 📋 Ficha Técnica

|Campo                |Detalle                            |
|---------------------|-----------------------------------|
|**Archivo**          |`ModelosMultimodales.ipynb`        |
|**Entorno**          |Google Colab con GPU **T4**        |
|**Duración estimada**|100 – 130 minutos                  |
|**Nivel**            |Intermedio – Avanzado              |
|**Partes**           |9 partes + limpieza + rúbrica      |

-----

## 🎯 Objetivos de Aprendizaje

1. Entender que imagen, audio y vídeo se convierten en **secuencias de vectores**, igual que el texto
1. Seguir paso a paso el tokenizador visual de un ViT: preprocesado, parches, proyección a vector y embeddings de posición
1. Comprobar que la `Conv2d` de un ViT equivale a "aplanar el parche y multiplicarlo por una matriz"
1. Relacionar imágenes y texto en un espacio común con CLIP (clasificación *zero-shot*)
1. Medir cuántos tokens ocupa una imagen en un LLM multimodal (`gemma3:4b`)
1. Explicar cómo Whisper convierte audio en espectrograma log-mel y en 1500 tokens de audio, y transcribirlo con marcas de tiempo
1. Calcular el coste en tokens de un vídeo y reducirlo eligiendo fotogramas clave con CLIP
1. Integrar las tres modalidades en una app Gradio publicada con Ngrok

-----

## ✅ Prerrequisitos

- Haber hecho la actividad [03 — Embeddings, tokens y similitud](../03-embeddings-tokens-similitud/) (recomendado): qué es un token, un embedding y la similitud coseno
- Python básico (ver [actividad 13](../13-python-colab-basico/))
- Cuenta de Google (para Colab) con GPU T4 disponible
- Cuenta gratuita en [ngrok.com](https://ngrok.com) y su token guardado en Colab Secrets como `NGROK_TOKEN` (con *Notebook access* activado)

-----

## 🛠️ Stack Tecnológico

|Componente            |Herramienta                              |Detalle                                                     |
|----------------------|-----------------------------------------|------------------------------------------------------------|
|Entorno               |Google Colab                             |GPU T4                                                      |
|Tokenizador visual    |`openai/clip-vit-base-patch32` (transformers)|224 px, parches de 32 px → 49 parches + [CLS] (~600 MB) |
|LLM multimodal        |Ollama + `gemma3:4b`                     |Texto + imágenes, ~256 tokens por imagen (~3.3 GB)          |
|Audio                 |`openai/whisper-small` (transformers)    |float16 en GPU, ventanas de 30 s (~1 GB)                    |
|Vídeo                 |OpenCV (`cv2`)                           |Muestreo de fotogramas + selección de fotogramas clave con CLIP|
|Datos de ejemplo      |`skimage.data`, `librosa.ex('libri1')`, `cockatoo.mp4` de imageio|Públicos; librerías preinstaladas en Colab |
|Interfaz              |Gradio 5.x (`gr.Blocks`)                 |3 pestañas · versión fijada a `>=5,<6`                      |
|Publicación           |Ngrok vía pyngrok                        |Token desde Colab Secrets                                   |

Solo se instalan aparte Ollama, Gradio y pyngrok (lo estándar del curso); `transformers`, `torch`, `scikit-image`, `librosa`, `opencv`, `imageio` y `matplotlib` ya vienen en Colab.

-----

## 🗺️ Estructura de la Actividad

|Parte|Contenido                                                                                   |
|-----|--------------------------------------------------------------------------------------------|
|1    |GPU, verificación de librerías de Colab, Ollama, Gradio/pyngrok, descarga de `gemma3:4b`    |
|2    |**Imagen I:** imagen como matriz, preprocesado 224×224, cuadrícula 7×7, parches como secuencia, parche → vector a mano, comprobación con la `Conv2d`, posición y [CLS], similitud entre parches tras el ViT|
|3    |**Imagen II:** CLIP *zero-shot*, descripción con `gemma3:4b`, medición de tokens por imagen  |
|4    |**Audio:** onda, espectrograma log-mel, 1500 tokens de audio del encoder, tokens del decoder (idioma detectado), transcripción con tiempos, resumen con el LLM|
|5    |**Vídeo:** metadatos, coste en tokens, muestreo uniforme, similitud entre fotogramas con CLIP, fotogramas clave y resumen del vídeo|
|6    |Interfaz Gradio con pestañas Imagen / Audio / Vídeo                                         |
|7    |Reflexión (5 preguntas)                                                                     |
|8    |Retos: parches de 16 px, Whisper en español, vídeo con audio                                |
|9    |Publicación con Ngrok (5 celdas) + limpieza + rúbrica                                       |

```
TEXTO   → tokens de palabras        ┐
IMAGEN  → 49 parches → 49 vectores  ├─► secuencia de vectores ─► Transformer / LLM
AUDIO   → espectrograma → 1500 vec. │
VÍDEO   → fotogramas clave → imágenes┘
```

-----

## ▶️ Instrucciones de Ejecución

1. Abre `ModelosMultimodales.ipynb` en [Google Colab](https://colab.research.google.com) (*Archivo → Subir cuaderno*, o desde GitHub)
1. Activa la GPU: *Entorno de ejecución → Cambiar tipo de entorno → T4 GPU*
1. Ejecuta las celdas **de arriba a abajo**, una por una, leyendo los comentarios. La Parte 1 tarda 4-6 minutos (descarga de `gemma3:4b`); CLIP y Whisper se descargan en sus celdas (1-2 min cada uno)
1. En la Parte 2 detente en cada gráfico: es el núcleo de la actividad
1. En la Parte 6 prueba cada pestaña con su ejemplo y después con tus propios archivos (foto, nota de voz, vídeo corto)
1. Responde la reflexión (Parte 7), intenta al menos un reto (Parte 8) y publica con Ngrok (Parte 9). Ejecuta la celda de limpieza al terminar

-----

## ⚠️ Solución de Problemas

|Problema                                         |Solución                                                                  |
|-------------------------------------------------|--------------------------------------------------------------------------|
|`nvidia-smi` falla o PyTorch usa CPU             |Activa la GPU T4 y reinicia la sesión; ejecuta desde la celda 1.1         |
|`❌ Ollama no arrancó`                            |*Entorno de ejecución → Reiniciar sesión* y vuelve a la celda 1.3         |
|Error al descargar `gemma3:4b`                   |Repite la celda 1.6; las descargas grandes a veces se cortan              |
|`ConnectionError` al preguntar a gemma3          |El servidor Ollama se detuvo: vuelve a ejecutar la celda 1.5              |
|Falla la descarga de `librosa.ex` o del vídeo    |Problema puntual de red: repite la celda                                  |
|`CUDA out of memory`                             |Reinicia la sesión; no cargues CLIP o Whisper más de una vez              |
|El micrófono no funciona en la pestaña Audio     |El navegador solo permite el micrófono en HTTPS: usa la URL de Ngrok      |
|`❌ Falta el token` en la celda 9.2               |Guarda el token en Secrets como `NGROK_TOKEN` y activa *Notebook access*  |

-----

## 📎 Recursos

- [An Image is Worth 16x16 Words (ViT, Dosovitskiy et al.)](https://arxiv.org/abs/2010.11929)
- [CLIP: Learning Transferable Visual Models From Natural Language Supervision](https://arxiv.org/abs/2103.00020)
- [Whisper: Robust Speech Recognition via Large-Scale Weak Supervision](https://arxiv.org/abs/2212.04356)
- [Gemma 3 Technical Report](https://arxiv.org/abs/2503.19786) · [gemma3 en Ollama](https://ollama.com/library/gemma3)
- [scikit-image `data`](https://scikit-image.org/docs/stable/api/skimage.data.html) · [librosa ejemplos](https://librosa.org/doc/latest/recordings.html) · [imageio imágenes estándar](https://imageio.readthedocs.io/en/stable/user_guide/standardimages.html)
