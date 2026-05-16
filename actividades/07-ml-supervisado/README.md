# Actividad 07 — Modelos Supervisados con Datos de Hotel

## Objetivo de aprendizaje

Aplicar los algoritmos más importantes de aprendizaje supervisado sobre el mismo dataset de reservas de hotel de la actividad anterior, cubriendo tanto clasificación como regresión.

Al finalizar el estudiante sabrá:
- Codificar variables categóricas con One-Hot Encoding para usarlas en ML
- Separar correctamente los datos en train/test y aplicar StandardScaler
- Entrenar y comparar Regresión Logística, Árbol de Decisión y Random Forest para clasificación
- Interpretar matrices de confusión, curvas ROC y métricas de clasificación (Accuracy, F1, AUC)
- Entrenar modelos de regresión y evaluar con MAE, RMSE y R²
- Identificar overfitting y ajustar `max_depth` en árboles de decisión
- Distinguir cuándo usar aprendizaje supervisado vs no supervisado

## Prerrequisitos

- Haber completado la **Actividad 06** (ML no supervisado) — se usa el mismo dataset y contexto
- Conocimientos básicos de Python (funciones, listas, diccionarios)
- No se requiere GPU — el notebook corre en CPU estándar de Colab

## Stack tecnológico

| Rol | Herramienta |
|-----|-------------|
| Entorno | Google Colab (CPU) |
| Manipulación de datos | pandas + NumPy |
| Clasificación | scikit-learn: LogisticRegression, DecisionTreeClassifier, RandomForestClassifier |
| Regresión | scikit-learn: LinearRegression, DecisionTreeRegressor, RandomForestRegressor |
| Preprocesamiento | scikit-learn: StandardScaler, train_test_split |
| Métricas | scikit-learn: classification_report, roc_curve, auc, MAE, RMSE, R² |
| Visualización | Matplotlib + Seaborn |

## Estructura del notebook

```
ml_supervisado_hoteles.ipynb
│
├── Parte 1 — Generar el dataset (mismo hotel, + columna cancelado)
├── Parte 2 — Preprocesamiento: One-Hot Encoding, split 80/20, StandardScaler
├── Parte 3 — Regresión Logística (clasificar cancelaciones)
├── Parte 4 — Árbol de Decisión (reglas interpretables + control de overfitting)
├── Parte 5 — Random Forest (clasificación robusta + importancia de features)
├── Parte 6 — Comparación de clasificadores (ROC, AUC, tabla de métricas)
├── Parte 7 — Regresión: predecir precio por noche (Lineal, Árbol, Random Forest)
├── Parte 8 — Comparación final supervisado vs no supervisado
└── Retos opcionales — umbral de decisión, cross-validation, GridSearchCV
```

## Instrucciones de ejecución

1. Descarga el archivo `ml_supervisado_hoteles.ipynb`
2. Ve a [colab.research.google.com](https://colab.research.google.com)
3. Haz clic en **Archivo → Subir notebook** y selecciona el archivo
4. No es necesario activar GPU — el tipo de entorno por defecto (CPU) es suficiente
5. Ejecuta las celdas **de arriba a abajo** con `Shift + Enter`

> Esta actividad no usa Ngrok ni Gradio. El resultado es el análisis completo con gráficos y tablas de métricas dentro del propio notebook.
