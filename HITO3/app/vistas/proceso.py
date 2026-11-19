import pandas as pd
import streamlit as st

from utils import encabezado, flujo, leer_json, siguiente, tarjeta

RUTA = 'vistas/proceso.py'
encabezado(RUTA, 'El proyecto siguió las etapas de CRISP-DM. Aquí está cada paso, con las decisiones que tomamos y por qué.')

meta = leer_json('meta')

flujo(['1 · Negocio', '2 · Datos', '3 · Calidad y EDA', '4 · Preparación', '5 · Modelado', '6 · Evaluación',
       '7 · Despliegue'])

a, b, c, d = st.columns(4)
with a:
    tarjeta('obras en el dataset del MEF', '68 columnas, descargadas con la API del Portal de Datos Abiertos.',
            f"{meta['obras_total']:,}")
with b:
    tarjeta('obras usadas para modelar', 'Las que ya tienen su costo actualizado registrado.', f"{meta['obras_modelo']:,}")
with c:
    tarjeta('modelos comparados', 'Siete modelos de regresión más un baseline, en dos escenarios.', '7 + 1')
with d:
    tarjeta('variables excluidas por fuga', 'Solo existen durante o después de la obra: no sirven para prevenir.', '18')

st.write('')
e1, e2, e3, e4, e5, e6, e7 = st.tabs(['1 · Negocio', '2 · Datos', '3 · Calidad y EDA', '4 · Preparación',
                                      '5 · Modelado', '6 · Evaluación', '7 · Despliegue'])

with e1:
    st.markdown("""
**Problema.** El Estado peruano no tiene una herramienta preventiva para anticipar, al aprobar una obra, cuánto podría
desviarse su costo final. Según la Contraloría, el costo de las obras paralizadas pasó de S/ 21,595 millones (2022) a
S/ 67,139 millones (2025).

**Objetivo.** Desarrollar y comparar modelos que predigan el porcentaje de sobrecosto con las características
iniciales de la obra, para priorizar la supervisión.

**Variable objetivo.**
""")
    st.latex(r'\text{Sobrecosto (\%)} = \frac{\text{Costo actualizado} - \text{Monto viable}}{\text{Monto viable}} \times 100')
    st.caption('Ejemplo: una obra viabilizada en S/ 1,000,000 que hoy cuesta S/ 1,300,000 tiene +30%. '
               'Se predice en % y no en soles para comparar obras de cualquier tamaño.')

with e2:
    st.markdown(f"""
- **Fuente:** Portal de Datos Abiertos del MEF, dataset *Detalle de Inversiones* (Invierte.pe). Un solo dataset.
- **Descarga:** API `datastore_search`, paginada de 10,000 en 10,000 registros, con reintentos.
- **Tamaño:** {meta['obras_total']:,} inversiones × 68 columnas (montos, ubicación, función, modalidad, fechas y avances).
- **Reproducibilidad:** se guardó un *snapshot* fijo en Google Drive; el notebook siempre usa los mismos datos.
- La API entrega todo como texto, así que se convirtieron montos, avances, fechas y coordenadas a su tipo correcto.
""")

with e3:
    st.markdown('**Chequeos de coherencia** (más allá de los valores vacíos):')
    st.dataframe(pd.DataFrame([
        ('Fecha de fin antes que la de inicio', '108', 'Fechas a vacío'),
        ('Viabilidad declarada después de iniciar la obra', '17,755', 'Documentado'),
        ('Monto viable mayor a S/ 2,958 millones', '16', 'Acotado'),
        ('Código único duplicado', '1', 'Eliminado'),
        ('Coordenadas fuera del Perú', '23,120', 'A vacío'),
    ], columns=['Caso', 'Obras', 'Tratamiento']), hide_index=True, width='stretch')
    st.markdown("""
**Hallazgos clave del EDA**
- El sobrecosto es **muy desigual**: media de 38.9% frente a una mediana de 0% (asimetría de 189.6). Por eso se comparan
  grupos con la mediana y se usan pruebas robustas (Spearman y Kruskal-Wallis + η²).
- Hay **22,349 outliers** (14.9%). No se eliminan, porque son justamente los casos graves.
- **55,308 obras** muestran 0% porque su costo todavía no se actualiza. Su 0% es falso y enseñaría algo incorrecto al
  modelo, así que se excluyeron. Quedan **94,469 obras**.
""")

with e4:
    st.markdown('**Orden del flujo** (todo lo que aprende de los datos se ajusta solo con el entrenamiento):')
    flujo(['Quitar duplicados', 'Winsorizar el target', 'Crear variables', 'Partir 80/20', 'Imputar vacíos',
           'Escalar + One-Hot', 'Entrenar'])
    i, d = st.columns(2)
    with i:
        st.markdown(f"""
- **Winsorización del target:** límites de {meta['lim_inf']:.1f}% y {meta['lim_sup']:.1f}%, calculados solo con train.
  Se ajusta el 9.1% de las obras y ninguna se borra.
- **División:** {meta['obras_train']:,} obras de entrenamiento y {meta['obras_test']:,} de prueba (semilla 3791).
- **Imputación:** mediana, moda o 0 según lo que significa cada vacío.
- **Codificación:** One-Hot con `min_frequency = 50` para agrupar categorías raras.
""")
    with d:
        st.dataframe(pd.DataFrame([
            ('plazo_dias', 'Duración programada de la obra'),
            ('anio_viabilidad', 'Año de aprobación'),
            ('monto_viable_log', 'Tamaño de la obra (logaritmo)'),
            ('ratio_et_viable', 'Cambio del expediente técnico frente al monto viable (solo en C)'),
        ], columns=['Variable creada', 'Qué mide']), hide_index=True, width='stretch')
    st.warning('**Fuga de información:** se excluyeron 18 variables (avances, devengados, saldos, certificaciones, '
               'estado y fechas reales de ejecución). Con ellas el R² sube a 0.99, pero esa información no existe al '
               'aprobar la obra.')

with e5:
    i, d = st.columns(2)
    with i:
        st.markdown("""
**Dos escenarios según el momento de decisión de Invierte.pe**
- **B · Viabilidad (16 variables):** monto, plazo, año, ubicación, nivel, sector, función, modalidad, tipología…
- **C · Expediente técnico (19 variables):** las de B + monto del expediente, `ratio_et_viable` y si tiene expediente.

Mismas obras, misma partición y mismo target: la diferencia entre B y C mide solo el valor de la información.
""")
    with d:
        st.markdown("""
**Modelos (escalera de complejidad)**
- Baseline (media) → Regresión lineal → Ridge → Árbol de decisión
- Ensambles: Bagging, Random Forest, Gradient Boosting y Stacking

**Validación:** KFold de 5 partes con el preprocesamiento dentro del pipeline.
**Ajuste:** GridSearchCV y RandomizedSearchCV (3 folds sobre el 40% de train, 30,230 obras), optimizando RMSE.
""")
    st.markdown('**Mejores hiperparámetros y mejora del RMSE (config. inicial → ajustada)**')
    st.dataframe(pd.DataFrame([
        ('Ridge', 'alpha = 10', '49.28 → 49.26', '44.17 → 44.15'),
        ('Árbol de decisión', 'max_depth = 10; min_samples_leaf = 200 (B) / 50 (C)', '49.65 → 49.25', '32.66 → 32.45'),
        ('Bagging', 'min_samples_leaf = 5; max_samples = 1.0', '47.62 → 47.59', '31.25 → 31.23'),
        ('Random Forest', 'max_features = 0.2; min_samples_leaf = 5', '47.54 → 46.94', '34.85 → 31.18'),
        ('Gradient Boosting', 'learning_rate = 0.05; 63 hojas; 300 iteraciones; L2 = 10; min_leaf = 20',
         '47.08 → 46.93', '30.85 → 30.75'),
    ], columns=['Modelo', 'Hiperparámetros elegidos', 'RMSE B', 'RMSE C']), hide_index=True, width='stretch')
    st.caption('El ajuste mejora poco: el límite del desempeño está en la información disponible, no en la configuración.')

with e6:
    st.markdown("""
- **Prueba única:** cada modelo se reentrena con todo train y se evalúa **una sola vez** en las obras de prueba.
- **Criterios fijados antes de ver resultados:** (1) menor RMSE; (2) si hay empate práctico (menos de 1% de
  diferencia), el que menos sobreajusta; (3) el más rápido; (4) el más interpretable.
- **Pruebas de robustez** (observaciones del Hito 2):
    - Error sobre el sobrecosto original, sin winsorizar.
    - Gráfico de radar con 7 métricas.
    - Revisión de `MONTO_ET_F8` para descartar fuga en el escenario C.
    - Validación temporal: entrenar hasta 2021 y probar con 2022 y 2023-2026.
""")
    st.page_link('vistas/modelos.py', label='Ver los resultados en "Comparar modelos"', icon=':material/leaderboard:')

with e7:
    st.markdown("""
- Los modelos finales (Gradient Boosting B y C) se exportaron con `joblib` **junto con su preprocesamiento**, para que
  el simulador aplique exactamente las mismas transformaciones del entrenamiento.
- La plataforma carga solo resúmenes (16 archivos, unos 8 MB), porque el dataset completo pesa 216 MB.
- Está publicada en Streamlit Community Cloud. Un flujo de GitHub Actions la visita cada 4 horas para que no se duerma.
""")

siguiente(RUTA)
