import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from utils import configurar_pagina, leer_tabla, pie_de_pagina

configurar_pagina('Explorar sobrecostos', '🗺️')
st.title('Explorar sobrecostos')
st.caption('Desviación presupuestal = (costo actualizado − monto viable) / monto viable. '
           'Se usan las obras con costo ya actualizado (las que aún no registran cambios se excluyen).')

base = leer_tabla('obras_modelo')

with st.sidebar:
    st.header('Filtros')
    anios = st.slider('Año de viabilidad', int(base['anio_viabilidad'].min()), int(base['anio_viabilidad'].max()),
                      (2010, int(base['anio_viabilidad'].max())))
    niveles = st.multiselect('Nivel de gobierno', sorted(base['NIVEL'].dropna().unique()),
                             default=sorted(base['NIVEL'].dropna().unique()),
                             help='GL = local, GR = regional, GN = nacional')
    funciones = st.multiselect('Función', sorted(base['FUNCION'].dropna().unique()))

d = base[base['anio_viabilidad'].between(*anios) & base['NIVEL'].isin(niveles)]
if funciones:
    d = d[d['FUNCION'].isin(funciones)]
if d.empty:
    st.warning('No hay obras con esos filtros.')
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric('Obras', f'{len(d):,}')
c2.metric('Sobrecosto mediano', f"{d['desviacion'].median():.1f}%")
c3.metric('Con sobrecosto severo (> 50%)', f"{(d['desviacion'] > 50).mean() * 100:.1f}%")
c4.metric('Monto viable total', f"S/ {d['MONTO_VIABLE'].sum() / 1e9:,.1f} mil M")


def resumen(df, col, minimo=30):
    r = (df.groupby(col)['desviacion']
         .agg(obras='size', mediana='median', severo=lambda s: (s > 50).mean() * 100)
         .query('obras >= @minimo').reset_index())
    return r


st.subheader('¿Dónde hay más sobrecosto?')
metrica = st.radio('Indicador', ['% de obras con sobrecosto severo', 'Sobrecosto mediano'], horizontal=True)
col_ind = 'severo' if metrica.startswith('%') else 'mediana'

dep = resumen(d, 'DEPARTAMENTO')
coords = (d.dropna(subset=['LATITUD', 'LONGITUD'])
          .query('-18.5 <= LATITUD <= 0 and -82 <= LONGITUD <= -68')
          .groupby('DEPARTAMENTO')[['LATITUD', 'LONGITUD']].median())
dep = dep.merge(coords, left_on='DEPARTAMENTO', right_index=True)

izq, der = st.columns([3, 2])
with izq:
    fig = px.scatter_map(dep, lat='LATITUD', lon='LONGITUD', size='obras', color=col_ind,
                         hover_name='DEPARTAMENTO', color_continuous_scale='RdYlGn_r', size_max=45, zoom=4.2,
                         center={'lat': -9.3, 'lon': -75.0}, height=620,
                         hover_data={'obras': ':,', 'mediana': ':.1f', 'severo': ':.1f',
                                     'LATITUD': False, 'LONGITUD': False},
                         labels={'severo': '% severo', 'mediana': 'Mediana (%)', 'obras': 'Obras'})
    fig.update_layout(map_style='carto-positron', margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, width='stretch')
    st.caption('Cada burbuja es un departamento (ubicada en la mediana de sus obras); el tamaño indica el número de obras.')
with der:
    orden = dep.sort_values(col_ind)
    fig = px.bar(orden, x=col_ind, y='DEPARTAMENTO', orientation='h', color=col_ind,
                 color_continuous_scale='RdYlGn_r', height=620,
                 labels={col_ind: metrica, 'DEPARTAMENTO': ''}, hover_data={'obras': ':,'})
    fig.update_layout(coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, width='stretch')

st.subheader('¿En qué tipo de obras?')
t1, t2, t3 = st.tabs(['Por función', 'Por nivel de gobierno y modalidad', 'En el tiempo'])
with t1:
    f = resumen(d, 'FUNCION', 100).sort_values(col_ind)
    fig = px.bar(f, x=col_ind, y='FUNCION', orientation='h', color=col_ind, color_continuous_scale='RdYlGn_r',
                 labels={col_ind: metrica, 'FUNCION': ''}, hover_data={'obras': ':,'}, height=520)
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, width='stretch')
with t2:
    a, b = st.columns(2)
    n = resumen(d, 'NIVEL').replace({'NIVEL': {'GL': 'Gobierno local', 'GR': 'Gobierno regional', 'GN': 'Gobierno nacional'}})
    a.plotly_chart(px.bar(n, x='NIVEL', y=col_ind, color='NIVEL', text_auto='.1f',
                          labels={col_ind: metrica, 'NIVEL': ''}).update_layout(showlegend=False),
                   width='stretch')
    m = resumen(d, 'DES_MODALIDAD', 200).sort_values(col_ind)
    m['DES_MODALIDAD'] = m['DES_MODALIDAD'].str.replace('ADMINISTRACIÓN ', 'ADM. ').str.slice(0, 55)
    b.plotly_chart(px.bar(m, x=col_ind, y='DES_MODALIDAD', orientation='h', text_auto='.1f',
                          labels={col_ind: metrica, 'DES_MODALIDAD': ''}), width='stretch')
with t3:
    tiempo = resumen(d, 'anio_viabilidad')
    fig = px.line(tiempo, x='anio_viabilidad', y=col_ind, markers=True,
                  labels={'anio_viabilidad': 'Año de viabilidad', col_ind: metrica}, hover_data={'obras': ':,'})
    fig.add_vrect(x0=2022.5, x1=tiempo['anio_viabilidad'].max() + 0.5, fillcolor='gray', opacity=0.12, line_width=0,
                  annotation_text='obras aún en curso', annotation_position='top left')
    st.plotly_chart(fig, width='stretch')
    st.caption('Las obras viabilizadas desde 2023 muestran menos sobrecosto en parte porque todavía no terminan: '
               'su costo actualizado puede seguir subiendo.')

st.subheader('Distribución del sobrecosto')
recorte = d['desviacion'].clip(-100, 300)
fig = px.histogram(recorte, nbins=80, labels={'value': 'Desviación presupuestal (%), acotada entre -100% y 300%'})
fig.add_vline(x=0, line_dash='dash', line_color='black')
fig.add_vline(x=50, line_dash='dot', line_color='crimson', annotation_text='sobrecosto severo (50%)')
fig.update_layout(showlegend=False, yaxis_title='Obras')
st.plotly_chart(fig, width='stretch')

pie_de_pagina()
