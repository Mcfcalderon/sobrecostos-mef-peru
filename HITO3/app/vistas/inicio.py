import streamlit as st

from utils import (ESC_B, ESC_C, LEMA, PAGINAS, leer_json, leer_tabla, siguiente, tarjeta)

meta = leer_json('meta')
captura = leer_json('captura')
metricas = {(m['Escenario'], m['Modelo']): m for m in leer_json('metricas_test')}
base = leer_tabla('obras_modelo')

st.markdown(f"""
<div class='vo-hero'>
  <h1>Vigía <span>Obras</span></h1>
  <div class='vo-lema'>{LEMA}</div>
  <p>Usamos <b>Machine Learning</b> sobre los datos abiertos del MEF (Invierte.pe) para estimar, <b>antes de construir</b>,
  cuánto podría pasarse una obra de su presupuesto, y así decidir cuáles supervisar primero.</p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric('Obras analizadas', f"{meta['obras_modelo']:,}", help='Obras con monto viable y costo actualizado registrado')
c2.metric('Terminan costando más', f"{(base['desviacion'] > 0).mean() * 100:.0f}%")
c3.metric('Sobrecosto mediano', f"{base['desviacion'].median():.1f}%")
c4.metric('Con sobrecosto severo (> 50%)', f"{(base['desviacion'] > 50).mean() * 100:.0f}%")

st.subheader('El problema y nuestra respuesta')
a, b, c = st.columns(3)
with a:
    tarjeta('El problema', 'El Estado aprueba obras con un monto, pero muchas terminan costando mucho más. Hoy no existe '
            'una herramienta preventiva que avise, al aprobar la obra, cuánto podría desviarse.')
with b:
    tarjeta('Qué predecimos', 'El <b>% de sobrecosto</b> de cada obra: (costo actualizado − monto viable) ÷ monto viable. '
            'Es un problema de <b>regresión supervisada</b> que usa solo información previa a la ejecución.')
with c:
    tarjeta('Para qué sirve', 'Con recursos de supervisión limitados, el modelo <b>ordena las obras por riesgo</b> '
            'para revisar primero las que tienen más probabilidad de un sobrecosto grave.')

st.subheader('Dos momentos para anticipar el sobrecosto')
mB, mC = metricas[(ESC_B, meta['mejor_modelo'][ESC_B])], metricas[(ESC_C, meta['mejor_modelo'][ESC_C])]
filaB = next(f for f in captura['tabla'] if f['Escenario'] == ESC_B)
filaC = next(f for f in captura['tabla'] if f['Escenario'] == ESC_C)

col_b, col_c = st.columns(2)
with col_b.container(border=True):
    st.markdown('#### 🟦 Modelo B · Al declarar la viabilidad')
    st.caption('Usa solo lo que se sabe cuando se aprueba la inversión: monto viable, plazo programado, '
               'ubicación, función, tipología, modalidad y nivel de gobierno (16 variables).')
    a, b, c = st.columns(3)
    a.metric('R² en prueba', f"{mB['R2_test']:.2f}")
    b.metric('Error medio (MAE)', f"{mB['MAE_test']:.1f} pp")
    c.metric('Detecta revisando el 20%', f"{filaB['Captura revisando el 20%']:.0f}%",
             help='Porcentaje de obras con sobrecosto severo que se detectan revisando el 20% de obras con mayor riesgo predicho')
with col_c.container(border=True):
    st.markdown('#### 🟧 Modelo C · Al aprobar el expediente técnico')
    st.caption('Agrega el monto del expediente técnico (19 variables). Es el momento previo a licitar, '
               'cuando todavía se puede corregir el diseño o el presupuesto.')
    a, b, c = st.columns(3)
    a.metric('R² en prueba', f"{mC['R2_test']:.2f}")
    b.metric('Error medio (MAE)', f"{mC['MAE_test']:.1f} pp")
    c.metric('Detecta revisando el 20%', f"{filaC['Captura revisando el 20%']:.0f}%")

st.info(f"Revisando al azar el 20% de las obras se detectaría solo el 20% de los sobrecostos severos. "
        f"Con el modelo C se detecta el {filaC['Captura revisando el 20%']:.0f}%, es decir "
        f"**{filaC['Captura revisando el 20%'] / 20:.1f} veces más** con el mismo esfuerzo de supervisión.")

st.subheader('Recorrido de la plataforma')
st.caption('Las páginas siguen el orden del proyecto: primero cómo se hizo, luego los resultados y al final la herramienta.')
descripciones = {
    'vistas/proceso.py': 'Datos, limpieza, preparación y modelado, paso a paso (CRISP-DM).',
    'vistas/explorar.py': 'Mapa y gráficos: dónde y en qué tipo de obras hay más sobrecosto.',
    'vistas/modelos.py': '7 modelos + baseline: radar, métricas, elección y pruebas de robustez.',
    'vistas/variables.py': 'Qué variables pesan más y qué perfiles de obra existen (K-Means).',
    'vistas/priorizar.py': 'Ranking de obras reales por riesgo y cuántos casos graves se detectan.',
    'vistas/simulador.py': 'Ingresa una obra nueva y estima su sobrecosto con B y C.',
    'vistas/conclusiones.py': 'Hallazgos, limitaciones y recomendación de uso.',
}
cols = st.columns(4)
for k, (ruta, titulo, icono, _) in enumerate(PAGINAS[1:]):
    with cols[k % 4].container(border=True):
        st.page_link(ruta, label=f'{k + 2}. {titulo}', icon=icono)
        st.caption(descripciones[ruta])

st.caption('Equipo: Calderón Flores, Marvin Andy · Chavez Arias, Cristihan David · Lapa Zuñiga, Melissa · '
           'Lopez Contreras, Aldair Mauricio — Docente: Jorge Villavicencio Antúnez.')

siguiente('vistas/inicio.py')
