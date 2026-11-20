import pandas as pd
import plotly.express as px
import streamlit as st

from utils import ESCALA_RIESGO, encabezado, grafico, leer_tabla, nota, seccion, siguiente

RUTA = 'vistas/explorar.py'
encabezado(RUTA, 'Dónde, en qué tipo de obras y desde cuándo hay más sobrecosto.')

base = leer_tabla('obras_modelo')

with st.sidebar:
    st.markdown('**Filtros**')
    anios = st.slider('Año de viabilidad', int(base['anio_viabilidad'].min()), int(base['anio_viabilidad'].max()),
                      (2010, int(base['anio_viabilidad'].max())))
    niveles = st.multiselect('Nivel de gobierno', sorted(base['NIVEL'].dropna().unique()),
                             default=sorted(base['NIVEL'].dropna().unique()), help='GL = local, GR = regional, GN = nacional')
    funciones = st.multiselect('Función', sorted(base['FUNCION'].dropna().unique()))

d = base[base['anio_viabilidad'].between(*anios) & base['NIVEL'].isin(niveles)]
d = d[~d['DEPARTAMENTO'].astype(str).str.startswith('-')]  # quita registros multidepartamentales
if funciones:
    d = d[d['FUNCION'].isin(funciones)]
if d.empty:
    st.warning('No hay obras con esos filtros.')
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric('Obras', f'{len(d):,}')
c2.metric('Sobrecosto mediano', f"{d['desviacion'].median():.1f}%")
c3.metric('Con sobrecosto severo', f"{(d['desviacion'] > 50).mean() * 100:.1f}%", help='Desviación mayor a 50%')
c4.metric('Monto viable (S/ mil M)', f"{d['MONTO_VIABLE'].sum() / 1e9:,.0f}")


def resumen(df, cols, minimo=30):
    return (df.groupby(cols)['desviacion']
            .agg(obras='size', mediana='median', severo=lambda s: (s > 50).mean() * 100)
            .query('obras >= @minimo').reset_index())


metrica = st.segmented_control('Indicador', ['% de obras con sobrecosto severo', 'Sobrecosto mediano'],
                               default='% de obras con sobrecosto severo', label_visibility='collapsed')
col_ind = 'mediana' if metrica == 'Sobrecosto mediano' else 'severo'
etiqueta = 'Sobrecosto mediano (%)' if col_ind == 'mediana' else '% con sobrecosto severo'

coords = (d.dropna(subset=['LATITUD', 'LONGITUD']).query('-18.5 <= LATITUD <= 0 and -82 <= LONGITUD <= -68')
          .groupby('DEPARTAMENTO')[['LATITUD', 'LONGITUD']].median())

seccion('Mapa del sobrecosto', 'Cada burbuja es un departamento; el tamaño indica cuántas obras tiene.', RUTA)
modo = st.segmented_control('Vista del mapa', ['Todo el periodo', 'Animado por año ▶'], default='Todo el periodo',
                            label_visibility='collapsed')
izq, der = st.columns([3, 2])
if modo == 'Animado por año ▶':
    anual = resumen(d[d['anio_viabilidad'] <= 2022], ['anio_viabilidad', 'DEPARTAMENTO'], 15)
    anual = anual.merge(coords, left_on='DEPARTAMENTO', right_index=True).sort_values('anio_viabilidad')
    lim = anual[col_ind].quantile(0.95)
    fig = px.scatter_map(anual, lat='LATITUD', lon='LONGITUD', size='obras', color=col_ind, hover_name='DEPARTAMENTO',
                         animation_frame='anio_viabilidad', color_continuous_scale=ESCALA_RIESGO,
                         range_color=[0, lim], size_max=40, zoom=4.1, center={'lat': -9.3, 'lon': -75.0},
                         labels={col_ind: etiqueta, 'obras': 'Obras', 'anio_viabilidad': 'Año'},
                         hover_data={'obras': ':,', 'LATITUD': False, 'LONGITUD': False})
    fig.update_layout(map_style='carto-positron', margin=dict(l=0, r=0, t=0, b=0))
    grafico(fig, izq, 620)
    izq.caption('Presiona ▶ para ver cómo cambia el sobrecosto por año de viabilidad (hasta 2022, obras ya avanzadas).')
else:
    dep = resumen(d, 'DEPARTAMENTO').merge(coords, left_on='DEPARTAMENTO', right_index=True)
    fig = px.scatter_map(dep, lat='LATITUD', lon='LONGITUD', size='obras', color=col_ind, hover_name='DEPARTAMENTO',
                         color_continuous_scale=ESCALA_RIESGO, size_max=45, zoom=4.1, center={'lat': -9.3, 'lon': -75.0},
                         hover_data={'obras': ':,', 'mediana': ':.1f', 'severo': ':.1f', 'LATITUD': False, 'LONGITUD': False},
                         labels={'severo': '% severo', 'mediana': 'Mediana (%)', 'obras': 'Obras'})
    fig.update_layout(map_style='carto-positron', margin=dict(l=0, r=0, t=0, b=0), coloraxis_colorbar=dict(title=''))
    grafico(fig, izq, 620)

dep = resumen(d, 'DEPARTAMENTO').sort_values(col_ind)
fig = px.bar(dep, x=col_ind, y='DEPARTAMENTO', orientation='h', color=col_ind, color_continuous_scale=ESCALA_RIESGO,
             labels={col_ind: etiqueta, 'DEPARTAMENTO': ''}, hover_data={'obras': ':,'})
fig.update_layout(coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0))
grafico(fig, der, 620)

seccion('¿En qué tipo de obras?', ruta=RUTA)
t1, t2, t3 = st.tabs(['Por función', 'Por nivel y modalidad', 'En el tiempo'])
with t1:
    f = resumen(d, 'FUNCION', 100).sort_values(col_ind)
    fig = px.bar(f, x=col_ind, y='FUNCION', orientation='h', color=col_ind, color_continuous_scale=ESCALA_RIESGO,
                 labels={col_ind: etiqueta, 'FUNCION': ''}, hover_data={'obras': ':,'}, text_auto='.0f')
    fig.update_layout(coloraxis_showscale=False)
    grafico(fig, alto=540)
with t2:
    a, b = st.columns(2)
    n = resumen(d, 'NIVEL').replace({'NIVEL': {'GL': 'Gobierno local', 'GR': 'Gobierno regional', 'GN': 'Gobierno nacional'}})
    fig = px.bar(n, x='NIVEL', y=col_ind, color='NIVEL', text_auto='.1f', labels={col_ind: etiqueta, 'NIVEL': ''},
                 color_discrete_sequence=['#2F6FB0', '#14806F', '#F28C28'], title='Nivel de gobierno')
    grafico(fig.update_layout(showlegend=False), a, 420)
    m = resumen(d, 'DES_MODALIDAD', 200).sort_values(col_ind)
    m['DES_MODALIDAD'] = m['DES_MODALIDAD'].str.replace('ADMINISTRACIÓN ', 'ADM. ').str.slice(0, 45)
    fig = px.bar(m, x=col_ind, y='DES_MODALIDAD', orientation='h', text_auto='.1f', title='Modalidad de ejecución',
                 labels={col_ind: etiqueta, 'DES_MODALIDAD': ''}, color_discrete_sequence=['#2F4FB8'])
    grafico(fig, b, 420)
with t3:
    tiempo = resumen(d, 'anio_viabilidad')
    fig = px.area(tiempo, x='anio_viabilidad', y=col_ind, markers=True, color_discrete_sequence=['#1479A3'],
                  labels={'anio_viabilidad': 'Año de viabilidad', col_ind: etiqueta}, hover_data={'obras': ':,'})
    fig.add_vrect(x0=2022.5, x1=tiempo['anio_viabilidad'].max() + 0.5, fillcolor='#F28C28', opacity=0.12, line_width=0,
                  annotation_text='obras aún en curso', annotation_position='top left')
    grafico(fig, alto=420)
    nota('Las obras viabilizadas desde 2023 muestran menos sobrecosto en parte porque todavía no terminan: su costo '
         'puede seguir subiendo.', '⏳')

seccion('Distribución del sobrecosto', 'Acotada entre −100% y 300% para que se vea la forma.', RUTA)
fig = px.histogram(d['desviacion'].clip(-100, 300), nbins=80, color_discrete_sequence=['#2F6FB0'],
                   labels={'value': 'Desviación presupuestal (%)'})
fig.add_vline(x=0, line_dash='dash', line_color='#0F3B66')
fig.add_vline(x=50, line_dash='dot', line_color='#D9572B', annotation_text='sobrecosto severo (50%)')
fig.update_layout(showlegend=False, yaxis_title='Obras', bargap=0.05)
grafico(fig, alto=380)

siguiente(RUTA)
