import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import COLOR_ESC, ESC_B, ESC_C, NOMBRE_ESC, encabezado, grafico, leer_tabla, nota, seccion, siguiente

RUTA = 'vistas/priorizar.py'
encabezado(RUTA, 'Con supervisión limitada, lo importante es saber qué obras revisar primero.')

obras = leer_tabla('obras_prueba')

with st.sidebar:
    st.markdown('**Filtros**')
    deps = st.multiselect('Departamento', sorted(obras['DEPARTAMENTO'].dropna().unique()))
    funcs = st.multiselect('Función', sorted(obras['FUNCION'].dropna().unique()))
    nivel = st.multiselect('Nivel de gobierno', sorted(obras['NIVEL'].dropna().unique()))
    monto_min = st.number_input('Monto viable mínimo (S/)', min_value=0, value=0, step=500_000)

a, b = st.columns([3, 2])
esc = a.segmented_control('Modelo para ordenar', [ESC_C, ESC_B], default=ESC_C, format_func=lambda e: NOMBRE_ESC[e]) or ESC_C
pct_revisar = b.slider('% de obras que se pueden revisar', 5, 50, 20, step=5)
col_pred = 'pred_C' if esc == ESC_C else 'pred_B'
color = COLOR_ESC[esc]

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
c1.metric('Obras de prueba (nunca vistas)', f'{len(d):,}')
c2.metric(f'Se revisan ({pct_revisar}%)', f'{n_rev:,}')
c3.metric('Casos graves detectados', f'{capt:.0f}%', delta=f'{capt / pct_revisar:.1f}× vs azar')
c4.metric('Monto viable revisado', f"S/ {revisadas['MONTO_VIABLE'].sum() / 1e6:,.0f} M")

izq, der = st.columns(2)
with izq:
    cap = np.cumsum(d['severo'].to_numpy()) / max(1, d['severo'].sum()) * 100
    rev = np.arange(1, len(d) + 1) / len(d) * 100
    paso = max(1, len(d) // 300)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 100], y=[0, 100], name='Revisión al azar', line=dict(color='#9AA7B5', dash='dash')))
    fig.add_trace(go.Scatter(x=rev[::paso], y=cap[::paso], name='Ordenando con el modelo', fill='tonexty',
                             fillcolor='rgba(242,140,40,0.15)' if esc == ESC_C else 'rgba(47,111,176,0.15)',
                             line=dict(color=color, width=4)))
    fig.add_trace(go.Scatter(x=[pct_revisar], y=[capt], mode='markers+text', text=[f'{capt:.0f}%'],
                             textposition='top left', marker=dict(size=14, color=color, line=dict(color='#FFF', width=2)),
                             showlegend=False))
    fig.update_layout(title='Curva de captura de sobrecostos severos', xaxis_title='% de obras revisadas',
                      yaxis_title='% de casos graves detectados', legend=dict(orientation='h', y=-0.22))
    grafico(fig, alto=420)
with der:
    decil = pd.qcut(d[col_pred].rank(method='first'), 10, labels=[f'D{i}' for i in range(1, 11)]).rename('decil')
    dec = d.groupby(decil, observed=True).agg(severo=('severo', 'mean')).reset_index()
    fig = go.Figure(go.Bar(x=dec['decil'], y=dec['severo'] * 100, text=(dec['severo'] * 100).round(0),
                           textposition='outside', marker=dict(color=dec['severo'] * 100,
                                                               colorscale=[[0, '#D6E4F3'], [1, color]])))
    fig.add_hline(y=d['severo'].mean() * 100, line_dash='dash', line_color='#5B6B7C', annotation_text='promedio')
    fig.update_layout(title='% de casos graves por decil de riesgo (D10 = mayor riesgo)', xaxis_title='',
                      yaxis_title='% con sobrecosto severo real')
    grafico(fig, alto=420)

seccion(f'Las {min(n_rev, 200)} obras de mayor riesgo', 'Ordenadas por el sobrecosto que predice el modelo.', RUTA)
tabla = revisadas.head(200)[['CODIGO_UNICO', 'NOMBRE_INVERSION', 'DEPARTAMENTO', 'FUNCION', 'MONTO_VIABLE', col_pred,
                             'desviacion_real']].copy()
tabla['MONTO_VIABLE'] = tabla['MONTO_VIABLE'] / 1e6
tabla['Grave'] = np.where(tabla['desviacion_real'] > 50, '🔴 Sí', '⚪ No')
st.dataframe(tabla, hide_index=True, width='stretch', height=430, column_config={
    'CODIGO_UNICO': st.column_config.NumberColumn('CUI', format='%d'),
    'NOMBRE_INVERSION': st.column_config.TextColumn('Obra', width='medium'),
    'DEPARTAMENTO': 'Departamento', 'FUNCION': 'Función',
    'MONTO_VIABLE': st.column_config.NumberColumn('Monto (S/ M)', format='%.2f'),
    col_pred: st.column_config.ProgressColumn('Riesgo predicho (%)', format='%.0f%%', min_value=-100, max_value=160),
    'desviacion_real': st.column_config.NumberColumn('Sobrecosto real (%)', format='%.0f%%'),
    'Grave': 'Grave real (> 50%)',
})
nota('El sobrecosto real es el del snapshot del MEF (en obras en curso aún puede cambiar). Las predicciones salen de '
     'los modelos exportados para la plataforma y pueden diferir en décimas del informe por la aleatoriedad del '
     'entrenamiento.', 'ℹ️')

siguiente(RUTA)
