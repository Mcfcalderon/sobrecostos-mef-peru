import streamlit as st

from utils import ESC_B, ESC_C, LEMA, leer_json, leer_tabla, siguiente
from visual import franja_ideas, grilla_paginas, portada

meta = leer_json('meta')
captura = {f['Escenario']: f for f in leer_json('captura')['tabla']}
metricas = {(m['Escenario'], m['Modelo']): m for m in leer_json('metricas_test')}
base = leer_tabla('obras_modelo')
mB = metricas[(ESC_B, meta['mejor_modelo'][ESC_B])]
mC = metricas[(ESC_C, meta['mejor_modelo'][ESC_C])]
capC = captura[ESC_C]['Captura revisando el 20%']

portada('Vigía', 'Obras', LEMA,
        'Machine Learning sobre los datos abiertos del MEF para saber, <b>antes de construir</b>, qué obras públicas '
        'tienen más riesgo de pasarse de su presupuesto.',
        f'Detecta {capC / 20:.1f} veces más sobrecostos graves que revisar al azar')

st.markdown('### Recorrido del proyecto')
st.caption('Haz clic en cada tarjeta para ver lo que se hizo en ese paso.')
grilla_paginas([
    dict(n=2, titulo='Cómo lo hicimos', texto='Datos, limpieza, preparación y modelado.', icono='ruta', color='azul',
         chip='CRISP-DM', ruta='vistas/proceso.py'),
    dict(n=3, titulo='Explorar sobrecostos', texto='Mapa y focos de sobrecosto en el Perú.', icono='mapa', color='cian',
         chip=f"{meta['obras_modelo']:,} obras", ruta='vistas/explorar.py'),
    dict(n=4, titulo='Comparar modelos', texto='7 modelos frente a frente y el ganador.', icono='barras', color='turquesa',
         chip=f"R² {mC['R2_test']:.2f}", ruta='vistas/modelos.py'),
    dict(n=5, titulo='Qué explica el sobrecosto', texto='Variables clave y perfiles de obra.', icono='lupa',
         color='indigo', chip='K-Means', ruta='vistas/variables.py'),
    dict(n=6, titulo='Priorizar obras', texto='Qué obras revisar primero.', icono='bandera', color='naranja',
         chip=f'{capC:.0f}% detectado', ruta='vistas/priorizar.py'),
    dict(n=7, titulo='Simulador', texto='Estima el sobrecosto de una obra nueva.', icono='calculadora', color='coral',
         chip='Modelos B y C', ruta='vistas/simulador.py'),
    dict(n=8, titulo='Conclusiones', texto='Hallazgos, límites y recomendación.', icono='check', color='verde',
         chip=f'{capC / 20:.1f}× vs azar', ruta='vistas/conclusiones.py'),
])

st.markdown('### El proyecto en cifras')
c1, c2, c3, c4 = st.columns(4)
c1.metric('Obras analizadas', f"{meta['obras_modelo']:,}", help='Obras con monto viable y costo actualizado registrado')
c2.metric('Terminan costando más', f"{(base['desviacion'] > 0).mean() * 100:.0f}%")
c3.metric('Sobrecosto mediano', f"{base['desviacion'].median():.1f}%")
c4.metric('Con sobrecosto severo (> 50%)', f"{(base['desviacion'] > 50).mean() * 100:.0f}%")

franja_ideas([
    ('maletin', 'azul', 'El problema', 'No hay alerta preventiva de sobrecostos.'),
    ('red', 'turquesa', 'Qué predecimos', 'El % de sobrecosto de cada obra.'),
    ('bandera', 'naranja', 'Para qué sirve', 'Ordenar la supervisión por riesgo.'),
])

st.markdown('### Dos momentos para anticipar el sobrecosto')
col_b, col_c = st.columns(2)
for col, titulo, sub, m, esc in [
        (col_b, '🟦 Modelo B · Al declarar la viabilidad', 'Solo datos de la aprobación (16 variables).', mB, ESC_B),
        (col_c, '🟧 Modelo C · Al aprobar el expediente', 'Suma el expediente técnico (19 variables).', mC, ESC_C)]:
    with col:
        st.markdown(f'#### {titulo}')
        st.caption(sub)
        a, b, c = st.columns(3)
        a.metric('R² en prueba', f"{m['R2_test']:.2f}")
        b.metric('Error medio (pp)', f"{m['MAE_test']:.1f}")
        c.metric('Detecta (20%)', f"{captura[esc]['Captura revisando el 20%']:.0f}%",
                 help='Sobrecostos severos detectados al revisar el 20% de obras con mayor riesgo predicho')

st.caption('Equipo: Calderón Flores, Marvin Andy · Chavez Arias, Cristihan David · Lapa Zuñiga, Melissa · '
           'Lopez Contreras, Aldair Mauricio — Docente: Jorge Villavicencio Antúnez.')

siguiente('vistas/inicio.py')
