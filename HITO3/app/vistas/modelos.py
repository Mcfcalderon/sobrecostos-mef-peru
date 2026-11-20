import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import (COLOR_ESC, COLOR_MODELO, ESC_B, ESC_C, NOMBRE_ESC, ORDEN_MODELOS, encabezado, grafico, leer_json,
                   nota, seccion, siguiente)

RUTA = 'vistas/modelos.py'
encabezado(RUTA, 'Qué modelo ayudó más, con qué criterio se eligió y qué tan robusto es.')

meta = leer_json('meta')
test = pd.DataFrame(leer_json('metricas_test'))
cv = pd.DataFrame(leer_json('metricas_cv'))
radar = {k: pd.DataFrame(v).set_index('Modelo') for k, v in leer_json('radar').items()}
NOMBRE_CORTO = {'Regresion Lineal': 'Reg. lineal', 'Arbol de Decision': 'Árbol', 'Baseline (media)': 'Baseline'}

esc = st.segmented_control('Momento de decisión', [ESC_B, ESC_C], default=ESC_C, format_func=lambda e: NOMBRE_ESC[e],
                           label_visibility='collapsed') or ESC_C
mejor = meta['mejor_modelo'][esc]
d = test[test['Escenario'] == esc].set_index('Modelo').loc[ORDEN_MODELOS].reset_index()
g = d.set_index('Modelo').loc[mejor]
base = d.set_index('Modelo').loc['Baseline (media)']

c1, c2, c3, c4 = st.columns(4)
c1.metric('Modelo elegido', 'G. Boosting' if mejor == 'Gradient Boosting' else mejor)
c2.metric('R² en prueba', f"{g['R2_test']:.3f}")
c3.metric('MAE en prueba', f"{g['MAE_test']:.1f} pp", delta=f"{g['MAE_test'] - base['MAE_test']:.1f} pp vs baseline",
          delta_color='inverse')
c4.metric('Entrenamiento', f"{g['Tiempo entrenamiento (s)']:.0f} s")

t_eleccion, t_radar, t_metricas, t_temporal, t_fuga, t_et = st.tabs(
    ['🏆 Elección', '🕸️ Radar', '📊 Métricas', '⏳ Validación temporal', '🚫 Fuga de información', '📄 Revisión del expediente'])

with t_eleccion:
    e = d[d['Modelo'] != 'Baseline (media)'].copy()
    mejor_rmse = e['RMSE_test'].min()
    e['dif'] = (e['RMSE_test'] / mejor_rmse - 1) * 100
    empatados = e[e['dif'] < 1]
    nota('Regla fijada <b>antes</b> de ver resultados: menor RMSE → si varios quedan a menos de 1% (empate práctico), '
         'gana el de <b>menor sobreajuste</b> → luego el más rápido.', '⚖️')
    fig = go.Figure()
    fig.add_vrect(x0=-0.3, x1=1, fillcolor='#14806F', opacity=0.10, line_width=0,
                  annotation_text='Empate práctico (< 1%)', annotation_position='top left',
                  annotation_font=dict(color='#14806F', size=12))
    lejos = e[e['dif'] > 10]
    for _, r in e[e['dif'] <= 10].iterrows():
        es = r['Modelo'] == mejor
        fig.add_trace(go.Scatter(
            x=[r['dif']], y=[r['Brecha sobreajuste']], mode='markers+text', name=r['Modelo'],
            text=[NOMBRE_CORTO.get(r['Modelo'], r['Modelo'])],
            textposition={'Gradient Boosting': 'bottom right', 'Stacking': 'top center'}.get(r['Modelo'], 'top center'),
            textfont=dict(color='#D9572B' if es else '#1B2733', size=13 if es else 12),
            marker=dict(size=28 if es else 18, color=COLOR_MODELO[r['Modelo']], line=dict(color='#FFFFFF', width=2),
                        symbol='star' if es else 'circle'),
            hovertemplate=f"<b>{r['Modelo']}</b><br>RMSE {r['RMSE_test']:.2f} (+{r['dif']:.2f}%)<br>"
                          f"Brecha {r['Brecha sobreajuste']:.3f}<br>{r['Tiempo entrenamiento (s)']:.0f} s<extra></extra>"))
    fig.update_layout(showlegend=False, xaxis_title='Diferencia frente al mejor RMSE (%)',
                      yaxis_title='Brecha de sobreajuste (R² train − prueba)',
                      title='Abajo a la izquierda es mejor: preciso y sin sobreajuste')
    fig.update_xaxes(range=[-0.3, e.loc[e['dif'] <= 10, 'dif'].max() + 1])
    grafico(fig, alto=430)
    if len(lejos):
        st.caption('Fuera del gráfico por estar lejos en precisión: ' +
                   ', '.join(f"{m} (+{x:.0f}%)" for m, x in zip(lejos['Modelo'], lejos['dif'])) + '.')
    st.markdown(f"Empatan **{', '.join(empatados['Modelo'])}**. **{mejor}** ⭐ tiene la menor brecha "
                f"({g['Brecha sobreajuste']:.3f}) y pierde solo {g['RMSE_test'] - mejor_rmse:.2f} pp de RMSE.")
    with st.expander('Ver la tabla de la decisión'):
        st.dataframe(e[['Modelo', 'RMSE_test', 'dif', 'R2_train', 'R2_test', 'Brecha sobreajuste',
                        'Tiempo entrenamiento (s)']].sort_values('RMSE_test'),
                     hide_index=True, width='stretch', column_config={
                         'RMSE_test': st.column_config.NumberColumn('RMSE prueba', format='%.2f'),
                         'dif': st.column_config.NumberColumn('Dif. vs mejor (%)', format='%.2f'),
                         'R2_train': st.column_config.NumberColumn('R² train', format='%.3f'),
                         'R2_test': st.column_config.NumberColumn('R² prueba', format='%.3f'),
                         'Brecha sobreajuste': st.column_config.NumberColumn('Brecha', format='%.3f'),
                         'Tiempo entrenamiento (s)': st.column_config.NumberColumn('Entrenamiento (s)', format='%.0f')})

with t_radar:
    p = radar[esc]
    ejes = [x.replace('\n', ' ') for x in p.columns]
    elegidos = st.multiselect('Modelos', list(p.index), default=['Gradient Boosting', 'Random Forest', 'Stacking',
                                                                 'Arbol de Decision', 'Ridge'])
    izq, der = st.columns([3, 2])
    fig = go.Figure()
    for modelo in elegidos:
        v = p.loc[modelo].tolist()
        es = modelo == mejor
        fig.add_trace(go.Scatterpolar(r=v + v[:1], theta=ejes + ejes[:1], name=modelo, fill='toself',
                                      line=dict(color=COLOR_MODELO[modelo], width=4 if es else 1.6),
                                      opacity=0.9 if es else 0.5))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 1.05], showticklabels=False, gridcolor='#E6ECF2'),
                                 angularaxis=dict(gridcolor='#E6ECF2'), bgcolor='rgba(0,0,0,0)'),
                      legend=dict(orientation='h', y=-0.12))
    grafico(fig, izq, 520)
    puntaje = p.mean(axis=1).sort_values().rename('Puntaje').reset_index()
    fig = px.bar(puntaje, x='Puntaje', y='Modelo', orientation='h', text_auto='.2f', color='Modelo',
                 color_discrete_map=COLOR_MODELO, title='Puntaje promedio del radar')
    grafico(fig.update_layout(showlegend=False, yaxis_title='', xaxis_range=[0, 1]), der, 520)
    st.caption('1 = el mejor modelo en cada eje (en error, brecha y tiempo la escala está invertida: más afuera es mejor).')

with t_metricas:
    a, b = st.columns(2)
    for col, campo, titulo, fmt in [(a, 'R2_test', 'R² en prueba (mayor es mejor)', '.3f'),
                                    (b, 'MAE_test', 'MAE en prueba, pp (menor es mejor)', '.1f')]:
        fig = px.bar(d, x=campo, y='Modelo', orientation='h', color='Modelo', color_discrete_map=COLOR_MODELO,
                     text_auto=fmt, title=titulo)
        grafico(fig.update_layout(showlegend=False, yaxis_title='', xaxis_title=''), col, 380)
    c = cv[cv['Escenario'] == esc].merge(d[['Modelo', 'R2_test']], on='Modelo')
    c = c[c['Modelo'] != 'Baseline (media)']
    fig = go.Figure()
    for campo, nombre, color in [('R2_train', 'Entrenamiento (CV)', '#C3CEDA'), ('R2_cv', 'Validación cruzada', '#6391C4'),
                                 ('R2_test', 'Prueba', COLOR_ESC[esc])]:
        fig.add_trace(go.Bar(x=c['Modelo'], y=c[campo], name=nombre, marker_color=color))
    fig.update_layout(barmode='group', title='Sobreajuste: R² en entrenamiento, validación cruzada y prueba',
                      legend=dict(orientation='h', y=1.12, x=1, xanchor='right'))
    grafico(fig, alto=400)
    with st.expander('Tabla completa de métricas'):
        cols = ['Modelo', 'RMSE_test', 'MAE_test', 'R2_test', 'R2_ajustado_test', 'Brecha sobreajuste',
                'MAE_original_test', 'MedAE_original_test', 'MAE_obras_recortadas', 'Tiempo entrenamiento (s)']
        st.dataframe(d[cols].round(3), hide_index=True, width='stretch')
        st.caption('MAE y MedAE "original" = medidos contra el sobrecosto real, sin winsorizar.')

with t_temporal:
    tmp = pd.DataFrame(leer_json('temporal')['resumen'])
    tmp = tmp[tmp['Escenario'] == esc].melt(id_vars=['Escenario', 'Modelo'], var_name='Prueba', value_name='R²')
    nombres = {'R2 particion aleatoria': 'Partición aleatoria', '2022 (un anio adelante)': 'Obras de 2022',
               '2023-2026 (obras en curso)': 'Obras 2023-2026 (en curso)'}
    tmp['Prueba'] = tmp['Prueba'].map(nombres)
    fig = px.bar(tmp, x='Modelo', y='R²', color='Prueba', barmode='group', text_auto='.2f',
                 color_discrete_sequence=['#C3CEDA', COLOR_ESC[esc], '#9CC3E6'],
                 title='Entrenando hasta 2021 y prediciendo años posteriores')
    grafico(fig.update_layout(legend=dict(orientation='h', y=1.12, x=1, xanchor='right')), alto=420)
    nota('La validación temporal simula el uso real: predecir obras <b>nuevas</b>. Las de 2023-2026 aún están en '
         'ejecución, así que su sobrecosto todavía no termina de registrarse.', '⏳')

with t_fuga:
    fuga = pd.DataFrame(leer_json('fuga'))
    fuga['Escenario'] = fuga['Escenario'].replace({'B - Viabilidad': 'B sin fuga', 'B + 17 fuga': 'B + 17 variables',
                                                   'B + 18 fuga': 'B + 18 variables'})
    fig = px.bar(fuga, x='Escenario', y='R2_cv', color='Modelo', barmode='group', text_auto='.2f',
                 color_discrete_sequence=['#9CC3E6', '#D9572B'], labels={'R2_cv': 'R² (validación cruzada)', 'Escenario': ''},
                 title='Lo que pasaría si se usaran datos de la ejecución')
    grafico(fig.update_layout(yaxis_range=[0, 1.1], legend=dict(orientation='h', y=1.12, x=1, xanchor='right')), alto=400)
    nota('Con devengados y saldos el R² salta a 0.90 (0.99 con el costo actualizado): el modelo <b>reconstruye</b> el '
         'costo final en vez de anticiparlo. Por eso esas variables se excluyen.', '🚫')

with t_et:
    rev = leer_json('revision_et')
    p1, p2 = pd.DataFrame(rev['prueba1']), pd.DataFrame(rev['prueba2'])
    nota('¿<code>MONTO_ET_F8</code> se actualiza durante la obra? Si fuera así, parte del desempeño de C sería fuga.', '❓')
    a, b = st.columns(2)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=p1['etapa'], y=p1['pct_costo_igual_ET'], mode='lines+markers', name='Costo = expediente',
                             line=dict(color='#2F6FB0', width=3)))
    fig.add_trace(go.Scatter(x=p1['etapa'], y=p1['pct_costo_mayor_ET'], mode='lines+markers', name='Costo > expediente',
                             line=dict(color='#F28C28', width=3)))
    fig.update_layout(title='Prueba 1: al avanzar la obra, el costo se separa del expediente',
                      xaxis_title='Avance financiero', yaxis_title='% de obras',
                      legend=dict(orientation='h', y=-0.25))
    grafico(fig, a, 420)
    fig = px.bar(p2.melt(id_vars='Subconjunto de prueba', value_vars=['R² B', 'R² C'], var_name='Modelo', value_name='R²'),
                 x='R²', y='Subconjunto de prueba', color='Modelo', barmode='group', orientation='h', text_auto='.2f',
                 color_discrete_sequence=[COLOR_ESC[ESC_B], COLOR_ESC[ESC_C]],
                 title='Prueba 2: C se mantiene donde la fuga no es posible')
    grafico(fig.update_layout(yaxis_title='', legend=dict(orientation='h', y=-0.25)), b, 420)
    st.markdown('**Conclusión:** no hay evidencia de fuga. Sin los casos espejo, C mantiene un R² de 0.57 (cifra conservadora).')

siguiente(RUTA)
