import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import COLOR_ESC, ESC_B, ESC_C, NOMBRE_ESC, configurar_pagina, leer_json, leer_tabla, pie_de_pagina

configurar_pagina('Priorizar obras', '🎯')
st.title('Priorizar obras para supervisión')
st.markdown(
    'Con recursos de supervisión limitados, lo importante no es el valor exacto del sobrecosto sino **qué obras revisar '
    'primero**. Aquí se usan las obras del conjunto de prueba (que el modelo nunca vio al entrenar), se ordenan por el '
    'sobrecosto que predice el modelo y se compara con lo que realmente pasó.'
)

obras = leer_tabla('obras_prueba')
captura = leer_json('captura')

esc = st.radio('Modelo usado para ordenar', [ESC_C, ESC_B], format_func=lambda e: NOMBRE_ESC[e], horizontal=True)
col_pred = 'pred_C' if esc == ESC_C else 'pred_B'

with st.sidebar:
    st.header('Filtros')
    deps = st.multiselect('Departamento', sorted(obras['DEPARTAMENTO'].dropna().unique()))
    funcs = st.multiselect('Función', sorted(obras['FUNCION'].dropna().unique()))
    nivel = st.multiselect('Nivel de gobierno', sorted(obras['NIVEL'].dropna().unique()))
    monto_min = st.number_input('Monto viable mínimo (S/)', min_value=0, value=0, step=500_000)
    pct_revisar = st.slider('% de obras que se pueden revisar', 5, 50, 20, step=5)

d = obras.copy()
if deps:
    d = d[d['DEPARTAMENTO'].isin(deps)]
if funcs:
    d = d[d['FUNCION'].isin(funcs)]
if nivel:
    d = d[d['NIVEL'].isin(nivel)]
d = d[d['MONTO_VIABLE'] >= monto_min]
if len(d) < 20:
    st.warning('Muy pocas obras con esos filtros.')
    st.stop()

d = d.sort_values(col_pred, ascending=False).reset_index(drop=True)
d['severo'] = d['desviacion_real'] > 50
n_rev = max(1, int(len(d) * pct_revisar / 100))
revisadas = d.head(n_rev)
capt = revisadas['severo'].sum() / max(1, d['severo'].sum()) * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric('Obras en el filtro', f'{len(d):,}')
c2.metric(f'Se revisan ({pct_revisar}%)', f'{n_rev:,}')
c3.metric('Sobrecostos severos detectados', f'{capt:.0f}%',
          delta=f'{capt - pct_revisar:+.0f} pp vs revisar al azar')
c4.metric('Monto viable en obras revisadas', f"S/ {revisadas['MONTO_VIABLE'].sum() / 1e6:,.0f} M")

izq, der = st.columns([2, 3])
with izq:
    orden = np.argsort(-d[col_pred].to_numpy())
    cap = np.cumsum(d['severo'].to_numpy()[orden]) / max(1, d['severo'].sum()) * 100
    rev = np.arange(1, len(d) + 1) / len(d) * 100
    paso = max(1, len(d) // 300)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rev[::paso], y=cap[::paso], name='Ordenando con el modelo',
                             line=dict(color=COLOR_ESC[esc], width=3)))
    fig.add_trace(go.Scatter(x=[0, 100], y=[0, 100], name='Revisión al azar', line=dict(color='black', dash='dash')))
    fig.add_vline(x=pct_revisar, line_dash='dot', line_color='gray')
    fig.update_layout(title='Curva de captura de sobrecostos severos', xaxis_title='% de obras revisadas',
                      yaxis_title='% de sobrecostos severos detectados', height=440, legend=dict(orientation='h', y=-0.2))
    st.plotly_chart(fig, width='stretch')
with der:
    decil = pd.qcut(d[col_pred].rank(method='first'), 10, labels=[f'D{i}' for i in range(1, 11)]).rename('decil')
    dec = d.groupby(decil, observed=True).agg(severo=('severo', 'mean')).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=dec['decil'], y=dec['severo'] * 100, name='% con sobrecosto severo (real)',
                         marker_color=COLOR_ESC[esc], text=(dec['severo'] * 100).round(0), textposition='outside'))
    fig.add_hline(y=d['severo'].mean() * 100, line_dash='dash', annotation_text='promedio')
    fig.update_layout(title='Obras agrupadas en deciles de riesgo predicho (D10 = mayor riesgo)',
                      xaxis_title='Decil de riesgo predicho', yaxis_title='% con sobrecosto severo real', height=440)
    st.plotly_chart(fig, width='stretch')

st.subheader(f'Las {min(n_rev, 200)} obras de mayor riesgo predicho')
tabla = revisadas.head(200)[['CODIGO_UNICO', 'NOMBRE_INVERSION', 'DEPARTAMENTO', 'FUNCION', 'NIVEL',
                             'anio_viabilidad', 'MONTO_VIABLE', col_pred, 'desviacion_real']].copy()
tabla['MONTO_VIABLE'] = tabla['MONTO_VIABLE'] / 1e6
st.dataframe(tabla, hide_index=True, width='stretch', height=480,
             column_config={
                 'CODIGO_UNICO': 'CUI', 'NOMBRE_INVERSION': st.column_config.TextColumn('Obra', width='large'),
                 'anio_viabilidad': st.column_config.NumberColumn('Año', format='%d'),
                 'MONTO_VIABLE': st.column_config.NumberColumn('Monto viable (S/ M)', format='%.2f'),
                 col_pred: st.column_config.NumberColumn('Sobrecosto predicho (%)', format='%.1f'),
                 'desviacion_real': st.column_config.NumberColumn('Sobrecosto real (%)', format='%.1f'),
             })
st.caption('El sobrecosto real es el registrado en el snapshot del MEF; en obras aún en ejecución todavía puede cambiar. '
           'Se puede buscar cada obra por su CUI en el portal de consulta de inversiones del MEF.')

pie_de_pagina()
