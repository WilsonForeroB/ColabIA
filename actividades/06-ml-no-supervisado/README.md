# Actividad 06 — Modelos No Supervisados con Datos de Hotel

## Objetivo de aprendizaje

Aplicar tres técnicas fundamentales de aprendizaje no supervisado sobre un dataset real de reservas de hotel, entendiendo cuándo y por qué usar cada algoritmo.

Al finalizar el estudiante sabrá:
- Preprocesar y normalizar datos tabulares para algoritmos de clustering
- Reducir dimensionalidad con PCA y visualizar patrones ocultos en 2D
- Segmentar clientes en perfiles de negocio con K-Means (método del codo + Silhouette Score)
- Explorar la estructura jerárquica de los datos sin definir K de antemano (dendrograma)
- Detectar reservas atípicas o sospechosas automáticamente con DBSCAN
- Comparar los tres algoritmos y justificar cuándo usar cada uno

> **En el aprendizaje no supervisado NO hay respuesta correcta.** El modelo descubre estructura a partir de los propios datos, sin etiquetas.

## Prerrequisitos

- Cuenta de Google (para usar Colab)
- Conocimientos básicos de Python (listas, funciones, variables)
- No se requiere GPU — el notebook corre en CPU estándar de Colab

## Stack tecnológico

| Rol | Herramienta |
|-----|-------------|
| Entorno | Google Colab (CPU) |
| Manipulación de datos | pandas + NumPy |
| Algoritmos de clustering | scikit-learn (KMeans, AgglomerativeClustering, DBSCAN) |
| Reducción de dimensionalidad | scikit-learn PCA |
| Clustering jerárquico + dendrograma | SciPy |
| Visualización | Matplotlib + Seaborn |

## Estructura del notebook

```
ml_no_supervisado_hoteles.ipynb
│
├── Parte 1 — Generar y explorar el dataset (500 reservas de hotel)
├── Parte 2 — Preprocesamiento y reducción de dimensionalidad (PCA)
├── Parte 3 — K-Means: segmentación de huéspedes
├── Parte 4 — Clustering Jerárquico + dendrograma
├── Parte 5 — DBSCAN: detección de anomalías
├── Parte 6 — Comparación final de los tres algoritmos
└── Reto extra — Optimización, variables categóricas o visualización 3D
```

## Instrucciones de ejecución

1. Descarga el archivo `ml_no_supervisado_hoteles.ipynb`
2. Ve a [colab.research.google.com](https://colab.research.google.com)
3. Haz clic en **Archivo → Subir notebook** y selecciona el archivo
4. No es necesario activar GPU — el tipo de entorno por defecto (CPU) es suficiente
5. Ejecuta las celdas **de arriba a abajo** con `Shift + Enter`, leyendo los bloques de texto antes de cada sección

> Esta actividad no usa Ngrok ni Gradio. El resultado es el análisis completo con gráficos dentro del propio notebook.
