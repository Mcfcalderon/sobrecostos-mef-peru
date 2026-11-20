import pandas as pd
import streamlit as st

from utils import encabezado, flujo, leer_json, siguiente
from visual import etapa, grilla_anclas

RUTA = 'vistas/proceso.py'
encabezado(RUTA, 'Las 7 etapas de CRISP-DM. Haz clic en una etapa para ir a su detalle.')

meta = leer_json('meta')

grilla_anclas([
    dict(n=1, titulo='Negocio', texto='Problema y objetivo', icono='maletin', color='azul', ancla='negocio'),
    dict(n=2, titulo='Datos', texto='Fuente MEF y descarga', icono='base', color='cian', ancla='datos'),
    dict(n=3, titulo='Calidad y EDA', texto='Errores y hallazgos', icono='lupa', color='turquesa', ancla='eda'),
    dict(n=4, titulo='Preparación', texto='Limpieza y variables', icono='filtro', color='indigo', ancla='preparacion'),
    dict(n=5, titulo='Modelado', texto='2 escenarios, 7 modelos', icono='red', color='naranja', ancla='modelado'),
    dict(n=6, titulo='Evaluación', texto='Elección y robustez', icono='check', color='coral', ancla='evaluacion'),
    dict(n=7, titulo='Despliegue', texto='Esta plataforma', icono='nube', color='verde', ancla='despliegue'),
])

# 1 ---------------------------------------------------------------------------------------------
etapa('negocio', 1, 'Entendimiento del negocio', 'Anticipar el sobrecosto al aprobar una obra', 'maletin', 'azul',
      ['S/ 67,139 M en obras paralizadas (2025)'])
st.markdown('**Objetivo:** predecir el % de sobrecosto con las características iniciales de la obra, para '
            '**priorizar la supervisión**. Es un problema de regresión supervisada y preventiva.')
st.latex(r'\text{Sobrecosto} = \frac{\text{Costo actualizado} - \text{Monto viable}}{\text{Monto viable}} \times 100')

# 2 ---------------------------------------------------------------------------------------------
etapa('datos', 2, 'Adquisición de datos', 'Portal de Datos Abiertos del MEF · Detalle de Inversiones', 'base', 'cian',
      [f"{meta['obras_total']:,} obras", '68 columnas', '1 dataset'])
flujo(['API datastore_search', 'Páginas de 10,000', 'Snapshot fijo en Drive', 'Conversión de tipos'])

# 3 ---------------------------------------------------------------------------------------------
etapa('eda', 3, 'Calidad y análisis exploratorio', 'Más allá de los valores vacíos', 'lupa', 'turquesa',
      ['Media 38.9% vs mediana 0%', '22,349 outliers'])
i, d = st.columns([3, 2])
with i:
    st.dataframe(pd.DataFrame([
        ('Fecha de fin antes que la de inicio', '108', 'Fechas a vacío'),
        ('Viabilidad después de iniciar la obra', '17,755', 'Documentado'),
        ('Monto viable > S/ 2,958 millones', '16', 'Acotado'),
        ('Código único duplicado', '1', 'Eliminado'),
        ('Coordenadas fuera del Perú', '23,120', 'A vacío'),
    ], columns=['Chequeo de coherencia', 'Obras', 'Tratamiento']), hide_index=True, width='stretch')
with d:
    st.metric('Obras excluidas (0% falso: costo sin actualizar)', '55,308')
    st.metric('Obras que quedan para modelar', f"{meta['obras_modelo']:,}")
st.caption('El sobrecosto es muy desigual (asimetría 189.6): se usan la mediana y pruebas robustas (Spearman, '
           'Kruskal-Wallis + η²). Los outliers no se borran: son los casos graves.')

# 4 ---------------------------------------------------------------------------------------------
etapa('preparacion', 4, 'Preparación de los datos', 'Todo se ajusta solo con el entrenamiento', 'filtro', 'indigo',
      [f"Train {meta['obras_train']:,}", f"Test {meta['obras_test']:,}", '18 variables de fuga fuera'])
flujo(['Quitar duplicados', 'Winsorizar target', 'Crear variables', 'Partir 80/20', 'Imputar', 'Escalar + One-Hot',
       'Entrenar'])
a, b, c = st.columns(3)
a.metric('Límites de Winsorización', f"{meta['lim_inf']:.1f}% / {meta['lim_sup']:.1f}%", help='Calculados solo con train')
b.metric('Obras ajustadas', '9.1%', help='Ninguna se borra')
c.metric('R² si se usaran variables de fuga', '0.99', delta='inútil para prevenir', delta_color='inverse')
with st.expander('Variables creadas y codificación'):
    st.dataframe(pd.DataFrame([
        ('plazo_dias', 'Duración programada de la obra'), ('anio_viabilidad', 'Año de aprobación'),
        ('monto_viable_log', 'Tamaño de la obra (logaritmo)'),
        ('ratio_et_viable', 'Cambio del expediente frente al monto viable (solo C)'),
    ], columns=['Variable creada', 'Qué mide']), hide_index=True, width='stretch')
    st.caption('Imputación con mediana, moda o 0 según el significado del vacío · One-Hot con min_frequency = 50 · '
               'semilla 3791.')

# 5 ---------------------------------------------------------------------------------------------
etapa('modelado', 5, 'Modelamiento', 'Dos momentos de decisión de Invierte.pe', 'red', 'naranja',
      ['B: 16 variables', 'C: 19 variables', '7 modelos + baseline'])
i, d = st.columns(2)
with i:
    st.markdown('**🟦 B · Viabilidad** — monto, plazo, año, ubicación, nivel, sector, función, modalidad, tipología…')
    st.markdown('**🟧 C · Expediente técnico** — lo de B + monto del expediente y su cambio frente al monto viable.')
with d:
    flujo(['Baseline', 'Lineal', 'Ridge', 'Árbol', 'Bagging', 'Random Forest', 'Gradient Boosting', 'Stacking'])
    st.caption('KFold de 5 partes · ajuste con Grid/RandomizedSearchCV (3 folds, 30,230 obras) optimizando RMSE.')
with st.expander('Hiperparámetros elegidos y mejora del RMSE'):
    st.dataframe(pd.DataFrame([
        ('Ridge', 'alpha = 10', '49.28 → 49.26', '44.17 → 44.15'),
        ('Árbol de decisión', 'max_depth = 10; min_samples_leaf = 200 (B) / 50 (C)', '49.65 → 49.25', '32.66 → 32.45'),
        ('Bagging', 'min_samples_leaf = 5; max_samples = 1.0', '47.62 → 47.59', '31.25 → 31.23'),
        ('Random Forest', 'max_features = 0.2; min_samples_leaf = 5', '47.54 → 46.94', '34.85 → 31.18'),
        ('Gradient Boosting', 'learning_rate = 0.05; 63 hojas; 300 iteraciones; L2 = 10; min_leaf = 20',
         '47.08 → 46.93', '30.85 → 30.75'),
    ], columns=['Modelo', 'Hiperparámetros', 'RMSE B', 'RMSE C']), hide_index=True, width='stretch')

# 6 ---------------------------------------------------------------------------------------------
etapa('evaluacion', 6, 'Evaluación', 'Criterios fijados antes de ver los resultados', 'check', 'coral',
      ['Prueba única', 'Gradient Boosting'])
flujo(['Menor RMSE', 'Empate < 1%', 'Menor sobreajuste', 'Más rápido', 'Más interpretable'])
st.markdown('Pruebas de robustez: **error sin winsorizar · radar · revisión de MONTO_ET_F8 · validación temporal**.')
st.page_link('vistas/modelos.py', label='Ver los resultados en Comparar modelos', icon=':material/arrow_forward:')

# 7 ---------------------------------------------------------------------------------------------
etapa('despliegue', 7, 'Despliegue', 'Vigía Obras en Streamlit Community Cloud', 'nube', 'verde',
      ['16 archivos · 8 MB', 'Activa 24/7'])
flujo(['Modelos + preprocesamiento (joblib)', 'Resúmenes JSON/Parquet', 'Streamlit Cloud',
       'GitHub Actions la mantiene despierta'])

siguiente(RUTA)
