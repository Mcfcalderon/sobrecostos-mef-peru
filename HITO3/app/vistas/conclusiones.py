import pandas as pd
import streamlit as st

from utils import ESC_B, ESC_C, encabezado, leer_json, siguiente, tarjeta

RUTA = 'vistas/conclusiones.py'
encabezado(RUTA, 'Qué responde el proyecto, hasta dónde llega y cómo recomendamos usarlo.')

meta = leer_json('meta')
test = {(m['Escenario'], m['Modelo']): m for m in leer_json('metricas_test')}
captura = {f['Escenario']: f for f in leer_json('captura')['tabla']}
temporal = {(r['Escenario'], r['Modelo']): r for r in leer_json('temporal')['resumen']}
gb = 'Gradient Boosting'

st.subheader('Resultado final')
filas = []
for esc, momento, extra in [(ESC_B, 'B · Al declarar la viabilidad',
                             f"{temporal[(ESC_B, gb)]['2022 (un anio adelante)']:.2f} en validación temporal"),
                            (ESC_C, 'C · Al aprobar el expediente técnico', '0.57 sin casos espejo')]:
    m = test[(esc, meta['mejor_modelo'][esc])]
    filas.append((momento, meta['mejor_modelo'][esc], f"{m['R2_test']:.3f} ({extra})", f"{m['MAE_test']:.1f}",
                  f"{m['MedAE_original_test']:.1f}", f"{captura[esc]['Captura revisando el 20%']:.1f}%"))
base = test[(ESC_B, 'Baseline (media)')]
filas.append(('Referencia (predice la media)', '—', '0.000', f"{base['MAE_test']:.1f}",
              f"{base['MedAE_original_test']:.1f}", '20% (azar)'))
st.dataframe(pd.DataFrame(filas, columns=['Momento de decisión', 'Mejor modelo', 'R² en prueba', 'MAE (pp)',
                                          'MedAE (pp)', 'Captura revisando el 20%']),
             hide_index=True, width='stretch')
st.caption('pp = puntos porcentuales. MedAE = error de la obra típica, sobre el sobrecosto real sin winsorizar. '
           'Captura = % de sobrecostos severos (más de 50%) detectados al revisar el 20% de obras de mayor riesgo.')

st.subheader('Hallazgos principales')
a, b, c = st.columns(3)
with a:
    tarjeta('Es posible anticipar el riesgo', 'Con datos abiertos del MEF se puede estimar el riesgo de sobrecosto '
            '<b>antes de ejecutar</b> la obra y ordenar la supervisión: el modelo C encuentra 3.3 veces más casos '
            'graves que revisar al azar.', '3.3×')
with b:
    tarjeta('La información pesa más que el algoritmo', 'Cambiar de modelo mueve el R² unas centésimas; sumar el '
            'expediente técnico lo triplica. El sobrecosto se origina sobre todo al elaborar el expediente.', '0.22 → 0.67')
with c:
    tarjeta('Gradient Boosting es el mejor', 'Empata en precisión con Random Forest y Stacking, pero sobreajusta menos '
            'y es el ensamble que entrena más rápido, algo clave para reentrenarlo cada año.', 'GB')
st.write('')
a, b = st.columns(2)
with a:
    tarjeta('Las métricas altas pueden engañar', 'Con devengados y saldos el R² llega a 0.99, pero esa información solo '
            'existe cuando la obra ya avanzó. Por eso se excluyeron 18 variables de fuga.', '0.99')
with b:
    tarjeta('El escenario C es robusto', 'Predice obras de 2022 con R² 0.68 (igual que con partición aleatoria) y '
            'mantiene 0.57 a 0.64 donde la fuga del expediente no es posible.', '0.68')

st.subheader('Limitaciones')
st.markdown("""
- **No anticipa la magnitud de los sobrecostos extremos.** El 8.8% de las obras de prueba superó el 141.9%; en ellas el
  error medio ronda los 533 puntos con C y 583 con B. Sí las ubica entre las de mayor riesgo.
- **El modelo B pierde fuerza con el tiempo:** su R² baja de 0.22 a 0.14 al predecir obras de 2022.
- **El sobrecosto de las obras recientes aún no es definitivo,** porque muchas siguen en ejecución.
- **Un solo snapshot del MEF** y faltan variables que probablemente influyen (contratista, número de postores, precios
  de insumos).
""")

st.subheader('Recomendación de uso: dos filtros')
i, d = st.columns(2)
with i.container(border=True):
    st.markdown('#### 🟦 Filtro 1 · Viabilidad (modelo B)')
    st.markdown('Marca las obras de mayor riesgo para **seguirlas desde el inicio**. Reentrenarlo cada año.')
with d.container(border=True):
    st.markdown('#### 🟧 Filtro 2 · Expediente técnico (modelo C)')
    st.markdown('Vuelve a ordenar las obras y las de mayor riesgo se **revisan antes de licitar**, cuando todavía se '
                'puede corregir el diseño o el presupuesto.')

st.subheader('Trabajo futuro')
st.markdown("""
- Cruzar con **SEACE** e **INFOBRAS** (contratistas, postores, avance físico).
- Construir un **historial de snapshots** para validar con obras ya cerradas.
- Probar un enfoque de **clasificación** (sobrecosto severo sí/no) para el escenario B.
""")

st.success('**Gracias.** Equipo: Calderón Flores, Marvin Andy · Chavez Arias, Cristihan David · Lapa Zuñiga, Melissa · '
           'Lopez Contreras, Aldair Mauricio. Docente: Jorge Villavicencio Antúnez · IN5306 Applied Machine Learning, '
           'UTEC 2026-2.')

siguiente(RUTA)
