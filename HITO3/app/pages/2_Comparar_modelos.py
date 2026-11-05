import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import (COLOR_ESC, COLOR_MODELO, ESC_B, ESC_C, NOMBRE_ESC, ORDEN_MODELOS, configurar_pagina,
                   leer_json, pie_de_pagina)

configurar_pagina('Comparar modelos', '📊')
st.title('Comparar modelos')

meta = leer_json('meta')
test = pd.DataFrame(leer_json('metricas_test'))
cv = pd.DataFrame(leer_json('metricas_cv'))
radar = {k: pd.DataFrame(v).set_index('Modelo') for k, v in leer_json('radar').items()}

st.markdown(
    'Se compararon **7 modelos de regresión más un baseline** en los dos momentos de decisión. Todos usan el mismo '
    'preprocesamiento, la misma partición train/test (80/20) y validación cruzada de 5 folds. La regla para elegir '
    'el mejor modelo se fijó **antes** de ver los resultados: menor RMSE en prueba; si hay empate práctico '
    '(diferencia menor al 1%), gana el que menos sobreajusta y, después, el más rápido.'
)

esc = st.radio('Momento de decisión', [ESC_B, ESC_C], format_func=lambda e: NOMBRE_ESC[e], horizontal=True)
mejor = meta['mejor_modelo'][esc]
st.success(f'**Mejor modelo en {NOMBRE_ESC[esc]}: {mejor}**')

t_radar, t_metricas, t_temporal, t_fuga, t_et = st.tabs(
    ['Radar multi-métrica', 'Métricas en prueba y CV', 'Validación temporal', 'Fuga de información',
     'Revisión del expediente técnico'])

with t_radar:
    p = radar[esc]
    ejes = list(p.columns)
    elegidos = st.multiselect('Modelos', list(p.index), default=list(p.index))
    fig = go.Figure()
    for modelo in elegidos:
        valores = p.loc[modelo].tolist()
        fig.add_trace(go.Scatterpolar(r=valores + valores[:1], theta=[e.replace('\n', ' ') for e in ejes + ejes[:1]],
                                      name=modelo, line=dict(color=COLOR_MODELO[modelo], width=4 if modelo == mejor else 1.5),
                                      fill='toself', opacity=0.85 if modelo == mejor else 0.45))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 1.05], showticklabels=False)), height=560,
                      legend=dict(orientation='h', y=-0.1))
    st.plotly_chart(fig, width='stretch')
    st.caption('Cada eje está escalado entre 0 y 1 dentro del escenario: 1 = el mejor modelo en esa métrica. '
               'En error, brecha de sobreajuste y tiempo la escala está invertida, así que más afuera siempre es mejor.')
    puntaje = p.mean(axis=1).sort_values(ascending=False).rename('Puntaje promedio').reset_index()
    st.dataframe(puntaje, hide_index=True, width='stretch',
                 column_config={'Puntaje promedio': st.column_config.ProgressColumn(min_value=0, max_value=1, format='%.2f')})

with t_metricas:
    d = test[test['Escenario'] == esc].set_index('Modelo').loc[ORDEN_MODELOS].reset_index()
    a, b = st.columns(2)
    fig = px.bar(d, x='R2_test', y='Modelo', orientation='h', color='Modelo', color_discrete_map=COLOR_MODELO,
                 text_auto='.3f', title='R² en prueba (mayor es mejor)')
    a.plotly_chart(fig.update_layout(showlegend=False, yaxis_title=''), width='stretch')
    fig = px.bar(d, x='MAE_test', y='Modelo', orientation='h', color='Modelo', color_discrete_map=COLOR_MODELO,
                 text_auto='.1f', title='MAE en prueba, puntos porcentuales (menor es mejor)')
    b.plotly_chart(fig.update_layout(showlegend=False, yaxis_title=''), width='stretch')

    c = cv[cv['Escenario'] == esc].merge(d[['Modelo', 'R2_test']], on='Modelo')
    c = c[c['Modelo'] != 'Baseline (media)']
    fig = go.Figure()
    fig.add_trace(go.Bar(x=c['Modelo'], y=c['R2_train'], name='R² train (CV)', marker_color='#c6dbef'))
    fig.add_trace(go.Bar(x=c['Modelo'], y=c['R2_cv'], name='R² validación cruzada', marker_color='#6baed6'))
    fig.add_trace(go.Bar(x=c['Modelo'], y=c['R2_test'], name='R² prueba', marker_color=COLOR_ESC[esc]))
    fig.update_layout(barmode='group', title='Sobreajuste: R² en train vs validación vs prueba', height=420)
    st.plotly_chart(fig, width='stretch')

    fig = px.scatter(d[d['Modelo'] != 'Baseline (media)'], x='Tiempo entrenamiento (s)', y='RMSE_test', color='Modelo',
                     color_discrete_map=COLOR_MODELO, size=[18] * 7, text='Modelo', log_x=True,
                     title='Precisión vs costo computacional (abajo a la izquierda es mejor)')
    fig.update_traces(textposition='top center')
    st.plotly_chart(fig.update_layout(showlegend=False, height=430), width='stretch')

    cols = ['Modelo', 'RMSE_test', 'MAE_test', 'R2_test', 'R2_ajustado_test', 'Brecha sobreajuste',
            'MAE_original_test', 'MedAE_original_test', 'MAE_obras_recortadas', 'Tiempo entrenamiento (s)']
    st.markdown('**Tabla completa** (MAE/MedAE "original" = contra el sobrecosto real sin winsorizar)')
    st.dataframe(d[cols].round(3), hide_index=True, width='stretch')

with t_temporal:
    tmp = pd.DataFrame(leer_json('temporal')['resumen'])
    tmp = tmp[tmp['Escenario'] == esc].melt(id_vars=['Escenario', 'Modelo'], var_name='Prueba', value_name='R²')
    nombres = {'R2 particion aleatoria': 'Partición aleatoria (Hito 2)', '2022 (un anio adelante)': 'Temporal: prueba 2022',
               '2023-2026 (obras en curso)': 'Temporal: prueba 2023-2026'}
    tmp['Prueba'] = tmp['Prueba'].map(nombres)
    fig = px.bar(tmp, x='Modelo', y='R²', color='Prueba', barmode='group', text_auto='.2f',
                 color_discrete_sequence=['#bdbdbd', '#3182bd', '#9ecae1'],
                 title='Entrenando con obras viabilizadas hasta 2021 y prediciendo años posteriores')
    st.plotly_chart(fig.update_layout(height=450), width='stretch')
    st.markdown(
        '- La partición aleatoria mezcla obras de todos los años; la temporal simula el uso real: predecir obras **nuevas**.\n'
        '- Las obras de **2023 a 2026** todavía están en ejecución y su sobrecosto aún no termina de registrarse, '
        'por eso el modelo tiende a sobreestimarlas respecto de lo registrado hasta hoy.')

with t_fuga:
    fuga = pd.DataFrame(leer_json('fuga'))
    fig = px.bar(fuga, x='Escenario', y='R2_cv', color='Modelo', barmode='group', text_auto='.2f',
                 color_discrete_sequence=['#9ecae1', '#1f77b4'],
                 title='R² si se agregaran las variables que solo existen durante la ejecución')
    st.plotly_chart(fig.update_layout(height=430, yaxis_range=[0, 1.1]), width='stretch')
    st.markdown('Con devengados, saldos y avances el R² de Gradient Boosting salta a 0.90 (0.99 con el costo actualizado): '
                'el modelo **reconstruye** el costo final en vez de anticiparlo. Luce excelente, pero esa información '
                'no existe cuando se aprueba la obra, por eso se excluye.')

with t_et:
    rev = leer_json('revision_et')
    p1, p2 = pd.DataFrame(rev['prueba1']), pd.DataFrame(rev['prueba2'])
    st.markdown('**Pregunta:** ¿`MONTO_ET_F8` es el monto original del expediente o se actualiza durante la obra? '
                'Si se actualizara, parte del buen desempeño del modelo C sería fuga.')
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=p1['etapa'], y=p1['pct_costo_igual_ET'], mode='lines+markers', name='Costo actualizado = expediente'))
    fig.add_trace(go.Scatter(x=p1['etapa'], y=p1['pct_costo_mayor_ET'], mode='lines+markers', name='Costo actualizado > expediente'))
    fig.update_layout(title='Prueba 1: a medida que avanza la obra, el costo se separa del expediente',
                      xaxis_title='Avance financiero (devengado / costo actualizado)', yaxis_title='% de obras', height=420)
    st.plotly_chart(fig, width='stretch')
    fig = px.bar(p2.melt(id_vars='Subconjunto de prueba', value_vars=['R² B', 'R² C'], var_name='Modelo', value_name='R²'),
                 x='R²', y='Subconjunto de prueba', color='Modelo', barmode='group', orientation='h', text_auto='.2f',
                 color_discrete_sequence=[COLOR_ESC[ESC_B], COLOR_ESC[ESC_C]],
                 title='Prueba 2: el modelo C se mantiene muy por encima de B aun donde la fuga no es posible')
    st.plotly_chart(fig.update_layout(height=430, yaxis_title=''), width='stretch')

pie_de_pagina()
