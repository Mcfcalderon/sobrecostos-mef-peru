"""Genera una version HTML estatica (sin internet) de la plataforma web, a partir de app/datos.

Uso: python generar_respaldo.py   ->  crea Plataforma_sobrecostos_respaldo.html en esta carpeta
"""
import json
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from plotly.offline import get_plotlyjs

AQUI = Path(__file__).parent
DATOS = AQUI.parent / 'app' / 'datos'
SALIDA = AQUI / 'Plataforma_sobrecostos_respaldo.html'
URL_APP = 'https://sobrecostos-mef-peru.streamlit.app/'

ESC_B, ESC_C = 'B - Viabilidad', 'C - Expediente tecnico'
NOMBRE = {ESC_B: 'B · Al declarar la viabilidad', ESC_C: 'C · Al aprobar el expediente técnico'}
COLOR_ESC = {ESC_B: '#1f77b4', ESC_C: '#ff7f0e'}
ORDEN = ['Baseline (media)', 'Regresion Lineal', 'Ridge', 'Arbol de Decision', 'Bagging', 'Random Forest',
         'Gradient Boosting', 'Stacking']
COLOR_MOD = dict(zip(ORDEN, ['#9aa5a8', '#6baed6', '#3182bd', '#74c476', '#fdae6b', '#ff6b6b', '#4ecdc4', '#9e9ac8']))
pio.templates.default = 'plotly_white'


def j(nombre):
    return json.loads((DATOS / f'{nombre}.json').read_text(encoding='utf-8'))


meta, captura = j('meta'), j('captura')
test, cv = pd.DataFrame(j('metricas_test')), pd.DataFrame(j('metricas_cv'))
base = pd.read_parquet(DATOS / 'obras_modelo.parquet')
obras = pd.read_parquet(DATOS / 'obras_prueba.parquet')
mejor = meta['mejor_modelo']

_n = [0]


def fig_html(fig, alto=450):
    _n[0] += 1
    fig.update_layout(height=alto, margin=dict(l=10, r=10, t=50, b=10), font=dict(family='Segoe UI, Arial', size=12))
    return pio.to_html(fig, include_plotlyjs=False, full_html=False, div_id=f'g{_n[0]}',
                       config={'displaylogo': False, 'responsive': True})


def tarjetas(items):
    return '<div class="tarjetas">' + ''.join(
        f'<div class="tarjeta"><div class="valor">{escape(v)}</div><div class="etiqueta">{escape(k)}</div></div>'
        for k, v in items) + '</div>'


def resumen(df, col, minimo=30):
    return (df.groupby(col)['desviacion'].agg(obras='size', mediana='median', severo=lambda s: (s > 50).mean() * 100)
            .query('obras >= @minimo').reset_index())


# ------------------------------------------------------------------ 1. Inicio
mB = test[(test['Escenario'] == ESC_B) & (test['Modelo'] == mejor[ESC_B])].iloc[0]
mC = test[(test['Escenario'] == ESC_C) & (test['Modelo'] == mejor[ESC_C])].iloc[0]
capt = {f['Escenario']: f for f in captura['tabla']}
inicio = f"""
<p class="lead">Al aprobar una obra pública, el Estado no sabe cuánto terminará costando. Este proyecto usa
<b>Machine Learning</b> sobre los datos abiertos del MEF (Invierte.pe) para <b>estimar el sobrecosto esperado de cada
obra antes de construirla</b> y decidir cuáles supervisar primero.</p>
{tarjetas([('Obras analizadas', f"{meta['obras_modelo']:,}"),
           ('Con sobrecosto', f"{(base['desviacion'] > 0).mean() * 100:.0f}%"),
           ('Sobrecosto mediano', f"{base['desviacion'].median():.1f}%"),
           ('Con sobrecosto severo (> 50%)', f"{(base['desviacion'] > 50).mean() * 100:.0f}%")])}
<h3>Dos momentos para anticipar el sobrecosto</h3>
<div class="dos">
 <div class="caja azul"><h4>Modelo B · Al declarar la viabilidad</h4>
  <p>Usa solo lo que se sabe al aprobar la inversión: monto viable, plazo programado, ubicación, función, tipología,
  modalidad y nivel de gobierno.</p>
  {tarjetas([('R² en prueba', f"{mB['R2_test']:.2f}"), ('Error medio (MAE)', f"{mB['MAE_test']:.1f} pp"),
             ('Detecta revisando el 20%', f"{capt[ESC_B]['Captura revisando el 20%']:.0f}%")])}</div>
 <div class="caja naranja"><h4>Modelo C · Al aprobar el expediente técnico</h4>
  <p>Agrega el monto del expediente técnico: el momento previo a licitar, cuando todavía se puede corregir el
  diseño o el presupuesto.</p>
  {tarjetas([('R² en prueba', f"{mC['R2_test']:.2f}"), ('Error medio (MAE)', f"{mC['MAE_test']:.1f} pp"),
             ('Detecta revisando el 20%', f"{capt[ESC_C]['Captura revisando el 20%']:.0f}%")])}</div>
</div>
<div class="aviso">Revisando al azar el 20% de las obras se detecta solo el 20% de los sobrecostos severos. Con el
modelo C se detecta el {capt[ESC_C]['Captura revisando el 20%']:.0f}%: <b>{capt[ESC_C]['Captura revisando el 20%'] / 20:.1f}
veces más</b> con el mismo esfuerzo de supervisión.</div>
<h3>¿Qué encontramos?</h3>
<ul>
 <li><b>El sobrecosto se origina sobre todo al elaborar el expediente técnico.</b> La diferencia entre el expediente y el
 monto viable es la variable más importante del modelo C.</li>
 <li><b>La información disponible pesa más que el algoritmo.</b> Cambiar de modelo mejora el R² en centésimas;
 incorporar el expediente técnico lo triplica.</li>
 <li><b>El mejor modelo en ambos momentos es Gradient Boosting</b>: empata en precisión con Random Forest y Stacking,
 pero sobreajusta menos y entrena más rápido.</li>
 <li><b>Los modelos con fuga de información engañan:</b> con devengados y saldos el R² sube a 0.90, pero esa
 información no existe cuando hay que decidir.</li>
</ul>
"""

# ------------------------------------------------------------------ 2. Explorar
dep = resumen(base, 'DEPARTAMENTO')
coords = (base.dropna(subset=['LATITUD', 'LONGITUD']).query('-18.5 <= LATITUD <= 0 and -82 <= LONGITUD <= -68')
          .groupby('DEPARTAMENTO')[['LATITUD', 'LONGITUD']].median())
dep = dep.merge(coords, left_on='DEPARTAMENTO', right_index=True)
f_mapa = px.scatter(dep, x='LONGITUD', y='LATITUD', size='obras', color='severo', text='DEPARTAMENTO', size_max=48,
                    color_continuous_scale='RdYlGn_r', hover_data={'obras': ':,', 'mediana': ':.1f', 'severo': ':.1f'},
                    labels={'severo': '% severo'}, title='Mapa esquemático: % de obras con sobrecosto severo por departamento')
f_mapa.update_traces(textposition='top center', textfont_size=9)
f_mapa.update_yaxes(scaleanchor='x', scaleratio=1, showgrid=False, visible=False)
f_mapa.update_xaxes(showgrid=False, visible=False)
o = dep.sort_values('severo')
f_dep = px.bar(o, x='severo', y='DEPARTAMENTO', orientation='h', color='severo', color_continuous_scale='RdYlGn_r',
               hover_data={'obras': ':,', 'mediana': ':.1f'}, labels={'severo': '% con sobrecosto severo', 'DEPARTAMENTO': ''},
               title='% con sobrecosto severo por departamento')
f_dep.update_layout(coloraxis_showscale=False)
fu = resumen(base, 'FUNCION', 100).sort_values('severo')
f_fun = px.bar(fu, x='severo', y='FUNCION', orientation='h', color='severo', color_continuous_scale='RdYlGn_r',
               hover_data={'obras': ':,', 'mediana': ':.1f'}, labels={'severo': '% con sobrecosto severo', 'FUNCION': ''},
               title='Por función')
f_fun.update_layout(coloraxis_showscale=False)
ni = resumen(base, 'NIVEL').replace({'NIVEL': {'GL': 'Gobierno local', 'GR': 'Gobierno regional', 'GN': 'Gobierno nacional'}})
f_niv = px.bar(ni, x='NIVEL', y=['mediana', 'severo'], barmode='group', text_auto='.1f',
               labels={'value': '%', 'NIVEL': '', 'variable': ''}, title='Por nivel de gobierno (mediana y % severo)')
ti = resumen(base, 'anio_viabilidad').query('anio_viabilidad >= 2008')
f_tie = px.line(ti, x='anio_viabilidad', y=['mediana', 'severo'], markers=True,
                labels={'value': '%', 'anio_viabilidad': 'Año de viabilidad', 'variable': ''},
                title='En el tiempo (las obras desde 2023 aún están en curso)')
f_tie.add_vrect(x0=2022.5, x1=ti['anio_viabilidad'].max() + 0.5, fillcolor='gray', opacity=0.12, line_width=0)
f_his = px.histogram(base['desviacion'].clip(-100, 300), nbins=80, title='Distribución del sobrecosto (acotado entre -100% y 300%)',
                     labels={'value': 'Desviación presupuestal (%)'})
f_his.add_vline(x=0, line_dash='dash'); f_his.add_vline(x=50, line_dash='dot', line_color='crimson')
f_his.update_layout(showlegend=False, yaxis_title='Obras')
explorar = ('<p>Desviación presupuestal = (costo actualizado − monto viable) / monto viable. Se usan las obras con costo '
            'ya actualizado.</p>'
            + '<div class="dos">' + f'<div>{fig_html(f_mapa, 640)}</div><div>{fig_html(f_dep, 640)}</div>' + '</div>'
            + fig_html(f_fun, 520)
            + '<div class="dos">' + f'<div>{fig_html(f_niv, 400)}</div><div>{fig_html(f_tie, 400)}</div>' + '</div>'
            + fig_html(f_his, 380))

# ------------------------------------------------------------------ 3. Comparar modelos
bloques = []
radar = j('radar')
for esc in [ESC_B, ESC_C]:
    p = pd.DataFrame(radar[esc]).set_index('Modelo')
    ejes = [e.replace('\n', ' ') for e in p.columns]
    f = go.Figure()
    for m in p.index:
        v = p.loc[m].tolist()
        f.add_trace(go.Scatterpolar(r=v + v[:1], theta=ejes + ejes[:1], name=m, fill='toself',
                                    line=dict(color=COLOR_MOD[m], width=4 if m == mejor[esc] else 1.5),
                                    opacity=0.85 if m == mejor[esc] else 0.4))
    f.update_layout(title=f'Radar multi-métrica — {NOMBRE[esc]}', polar=dict(radialaxis=dict(range=[0, 1.05], showticklabels=False)),
                    legend=dict(orientation='h', y=-0.12))
    bloques.append(fig_html(f, 560))
radar_html = '<div class="dos">' + ''.join(f'<div>{b}</div>' for b in bloques) + '</div>'
radar_html += ('<p class="nota">Cada eje está escalado entre 0 y 1 dentro del escenario: 1 = el mejor modelo en esa métrica '
               '(en error, sobreajuste y tiempo la escala está invertida). Gradient Boosting, resaltado, es el más equilibrado.</p>')

d = test.copy(); d['Escenario'] = d['Escenario'].map(NOMBRE)
f_r2 = px.bar(d, x='R2_test', y='Modelo', color='Escenario', barmode='group', orientation='h', text_auto='.2f',
              category_orders={'Modelo': ORDEN}, color_discrete_sequence=['#1f77b4', '#ff7f0e'],
              title='R² en prueba (mayor es mejor)')
f_r2.update_layout(legend=dict(orientation='h', y=-0.15, title=''))
f_mae = px.bar(d, x='MAE_test', y='Modelo', color='Escenario', barmode='group', orientation='h', text_auto='.1f',
               category_orders={'Modelo': ORDEN}, color_discrete_sequence=['#1f77b4', '#ff7f0e'],
               title='MAE en prueba, puntos porcentuales (menor es mejor)')
f_mae.update_layout(legend=dict(orientation='h', y=-0.15, title=''))
c = cv.merge(test[['Escenario', 'Modelo', 'R2_test']], on=['Escenario', 'Modelo'])
c = c[c['Modelo'] != 'Baseline (media)']
graf_sobre = []
for esc in [ESC_B, ESC_C]:
    x = c[c['Escenario'] == esc]
    f = go.Figure()
    f.add_trace(go.Bar(x=x['Modelo'], y=x['R2_train'], name='R² train', marker_color='#c6dbef'))
    f.add_trace(go.Bar(x=x['Modelo'], y=x['R2_cv'], name='R² validación cruzada', marker_color='#6baed6'))
    f.add_trace(go.Bar(x=x['Modelo'], y=x['R2_test'], name='R² prueba', marker_color=COLOR_ESC[esc]))
    f.update_layout(barmode='group', title=f'Sobreajuste — {NOMBRE[esc]}', legend=dict(orientation='h', y=-0.25))
    graf_sobre.append(fig_html(f, 420))
cols = ['Escenario', 'Modelo', 'RMSE_test', 'MAE_test', 'R2_test', 'Brecha sobreajuste', 'MedAE_original_test',
        'Tiempo entrenamiento (s)']
tabla = test[cols].copy()
tabla['Escenario'] = tabla['Escenario'].map(NOMBRE)
tabla_html = tabla.round(3).to_html(index=False, classes='tabla', border=0)

tmp = pd.DataFrame(j('temporal')['resumen']).melt(id_vars=['Escenario', 'Modelo'], var_name='Prueba', value_name='R²')
tmp['Prueba'] = tmp['Prueba'].map({'R2 particion aleatoria': 'Partición aleatoria', '2022 (un anio adelante)': 'Temporal: 2022',
                                   '2023-2026 (obras en curso)': 'Temporal: 2023-2026'})
tmp['Escenario'] = tmp['Escenario'].map(NOMBRE)
f_tmp = px.bar(tmp, x='Modelo', y='R²', color='Prueba', barmode='group', facet_col='Escenario', text_auto='.2f',
               color_discrete_sequence=['#bdbdbd', '#3182bd', '#9ecae1'],
               title='Validación temporal: entrenar con obras hasta 2021 y predecir años posteriores')
f_tmp.for_each_annotation(lambda a: a.update(text=a.text.split('=')[-1]))
fuga = pd.DataFrame(j('fuga'))
f_fuga = px.bar(fuga, x='Escenario', y='R2_cv', color='Modelo', barmode='group', text_auto='.2f',
                color_discrete_sequence=['#9ecae1', '#1f77b4'], title='Fuga de información: R² si se usaran datos de la ejecución')
f_fuga.update_yaxes(range=[0, 1.1])
rev = j('revision_et')
p1, p2 = pd.DataFrame(rev['prueba1']), pd.DataFrame(rev['prueba2'])
f_p1 = go.Figure()
f_p1.add_trace(go.Scatter(x=p1['etapa'], y=p1['pct_costo_igual_ET'], mode='lines+markers', name='Costo = expediente'))
f_p1.add_trace(go.Scatter(x=p1['etapa'], y=p1['pct_costo_mayor_ET'], mode='lines+markers', name='Costo > expediente'))
f_p1.update_layout(title='Revisión de MONTO_ET_F8: el costo se separa del expediente al avanzar la obra',
                   xaxis_title='Avance financiero', yaxis_title='% de obras', legend=dict(orientation='h', y=-0.25))
f_p2 = px.bar(p2.melt(id_vars='Subconjunto de prueba', value_vars=['R² B', 'R² C'], var_name='Modelo', value_name='R²'),
              x='R²', y='Subconjunto de prueba', color='Modelo', barmode='group', orientation='h', text_auto='.2f',
              color_discrete_sequence=['#1f77b4', '#ff7f0e'], title='C se mantiene muy por encima de B aun sin posible fuga')
f_p2.update_layout(yaxis_title='')

comparar = (f"<p>Se compararon <b>7 modelos más un baseline</b> en los dos momentos de decisión, con validación cruzada de "
            f"5 folds, ajuste de hiperparámetros y una única evaluación en prueba. <b>Mejor modelo en ambos escenarios: "
            f"{mejor[ESC_B]}</b>.</p>" + radar_html
            + '<div class="dos">' + f'<div>{fig_html(f_r2, 480)}</div><div>{fig_html(f_mae, 480)}</div>' + '</div>'
            + '<div class="dos">' + ''.join(f'<div>{g}</div>' for g in graf_sobre) + '</div>'
            + '<h4>Tabla de métricas en prueba</h4>' + tabla_html
            + fig_html(f_tmp, 460)
            + '<div class="dos">' + f'<div>{fig_html(f_p1, 420)}</div><div>{fig_html(f_p2, 420)}</div>' + '</div>'
            + fig_html(f_fuga, 420))

# ------------------------------------------------------------------ 4. Priorizar obras
curvas = captura['curvas']
f_cap = go.Figure()
for esc in [ESC_B, ESC_C]:
    f_cap.add_trace(go.Scatter(x=curvas[esc]['revisado'], y=curvas[esc]['capturado'], name=NOMBRE[esc],
                               line=dict(color=COLOR_ESC[esc], width=3)))
f_cap.add_trace(go.Scatter(x=[0, 100], y=[0, 100], name='Revisión al azar', line=dict(color='black', dash='dash')))
f_cap.add_vline(x=20, line_dash='dot', line_color='gray')
f_cap.update_layout(title='Curva de captura de sobrecostos severos', xaxis_title='% de obras revisadas',
                    yaxis_title='% de sobrecostos severos detectados', legend=dict(orientation='h', y=-0.2))
dec = obras.assign(severo=obras['desviacion_real'] > 50)
dec['decil'] = pd.qcut(dec['pred_C'].rank(method='first'), 10, labels=[f'D{i}' for i in range(1, 11)])
dd = dec.groupby('decil', observed=True)['severo'].mean().mul(100).reset_index()
f_dec = px.bar(dd, x='decil', y='severo', text_auto='.0f', labels={'severo': '% con sobrecosto severo real', 'decil': 'Decil de riesgo predicho (modelo C)'},
               title='Obras agrupadas por riesgo predicho (D10 = mayor riesgo)', color_discrete_sequence=['#ff7f0e'])
top = obras.sort_values('pred_C', ascending=False).head(50)[
    ['CODIGO_UNICO', 'NOMBRE_INVERSION', 'DEPARTAMENTO', 'FUNCION', 'anio_viabilidad', 'MONTO_VIABLE', 'pred_B', 'pred_C', 'desviacion_real']].copy()
top['MONTO_VIABLE'] = (top['MONTO_VIABLE'] / 1e6).round(2)
top['NOMBRE_INVERSION'] = top['NOMBRE_INVERSION'].str.slice(0, 90)
top = top.round(1).rename(columns={'CODIGO_UNICO': 'CUI', 'NOMBRE_INVERSION': 'Obra', 'DEPARTAMENTO': 'Departamento',
                                    'FUNCION': 'Función', 'anio_viabilidad': 'Año', 'MONTO_VIABLE': 'Monto viable (S/ M)',
                                    'pred_B': 'Predicho B (%)', 'pred_C': 'Predicho C (%)', 'desviacion_real': 'Real (%)'})
priorizar = ('<p>Con recursos de supervisión limitados, lo importante es <b>qué obras revisar primero</b>. Se usan las '
             f'{meta["obras_test"]:,} obras del conjunto de prueba, que el modelo nunca vio al entrenar.</p>'
             + '<div class="dos">' + f'<div>{fig_html(f_cap, 460)}</div><div>{fig_html(f_dec, 460)}</div>' + '</div>'
             + '<h4>Las 50 obras con mayor sobrecosto predicho por el modelo C</h4>'
             + f'<p class="nota">{(top["Real (%)"] > 50).sum()} de estas 50 obras tuvieron realmente un sobrecosto severo (> 50%).</p>'
             + '<div class="scroll">' + top.to_html(index=False, classes='tabla', border=0) + '</div>')

simulador = (f'<div class="aviso">El simulador necesita ejecutar el modelo, así que solo está disponible en la versión web: '
             f'<a href="{URL_APP}">{URL_APP}</a>. También se puede correr localmente con <code>streamlit run Inicio.py</code> '
             'desde la carpeta <code>HITO3/app</code>.</div>')

# ------------------------------------------------------------------ armado
secciones = [('inicio', 'Inicio', inicio), ('explorar', 'Explorar sobrecostos', explorar),
             ('comparar', 'Comparar modelos', comparar), ('priorizar', 'Priorizar obras', priorizar),
             ('simulador', 'Simulador', simulador)]
botones = ''.join(f'<button class="tab{" activo" if i == 0 else ""}" onclick="mostrar(\'{k}\', this)">{t}</button>'
                  for i, (k, t, _) in enumerate(secciones))
cuerpos = ''.join(f'<section id="{k}" class="panel"{"" if i == 0 else " hidden"}><h2>{t}</h2>{h}</section>'
                  for i, (k, t, h) in enumerate(secciones))

html = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sobrecostos MEF · Plataforma (respaldo)</title>
<script>{get_plotlyjs()}</script>
<style>
 body {{ margin:0; font-family:'Segoe UI', Arial, sans-serif; color:#262730; background:#ffffff; }}
 header {{ background:#f0f2f6; padding:18px 32px; border-bottom:1px solid #e0e3ea; }}
 header h1 {{ margin:0; font-size:24px; }} header p {{ margin:4px 0 0; color:#555; font-size:13px; }}
 nav {{ display:flex; gap:6px; padding:10px 32px; border-bottom:1px solid #e0e3ea; position:sticky; top:0; background:#fff; z-index:9; flex-wrap:wrap; }}
 .tab {{ border:1px solid #d0d4dc; background:#fff; padding:8px 16px; border-radius:8px; cursor:pointer; font-size:14px; }}
 .tab.activo {{ background:#ff4b4b; color:#fff; border-color:#ff4b4b; }}
 main {{ padding:8px 32px 40px; max-width:1400px; margin:auto; }}
 .lead {{ font-size:16px; line-height:1.5; }}
 .tarjetas {{ display:flex; gap:12px; flex-wrap:wrap; margin:12px 0; }}
 .tarjeta {{ flex:1; min-width:150px; background:#f7f8fa; border:1px solid #e6e8ee; border-radius:10px; padding:12px 16px; }}
 .valor {{ font-size:26px; font-weight:600; }} .etiqueta {{ font-size:13px; color:#555; }}
 .dos {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:16px; }}
 .dos > div {{ min-width:0; overflow:hidden; }}
 @media (max-width: 900px) {{ .dos {{ grid-template-columns:1fr; }} }}
 .caja {{ border-radius:10px; padding:4px 16px 8px; border:1px solid #e6e8ee; }}
 .azul {{ border-left:6px solid #1f77b4; }} .naranja {{ border-left:6px solid #ff7f0e; }}
 .aviso {{ background:#e8f1fb; border:1px solid #bcd6f2; border-radius:8px; padding:12px 16px; margin:14px 0; }}
 .nota {{ color:#555; font-size:13px; }}
 .tabla {{ border-collapse:collapse; width:100%; font-size:12.5px; }}
 .tabla th {{ background:#f0f2f6; text-align:left; padding:6px 8px; position:sticky; top:0; }}
 .tabla td {{ padding:5px 8px; border-bottom:1px solid #eee; }}
 .scroll {{ max-height:520px; overflow:auto; border:1px solid #eee; border-radius:8px; }}
 footer {{ color:#777; font-size:12px; padding:16px 32px; border-top:1px solid #e0e3ea; }}
</style></head>
<body>
<header><h1>Predicción de sobrecostos en la inversión pública del Perú</h1>
<p>Versión de respaldo sin conexión · Plataforma web: <a href="{URL_APP}">{URL_APP}</a></p></header>
<nav>{botones}</nav>
<main>{cuerpos}</main>
<footer>Proyecto final IN5306 Applied Machine Learning · UTEC · Datos: MEF, Detalle de Inversiones (snapshot de
{meta['fecha_snapshot']}) · {meta['obras_modelo']:,} obras con costo actualizado.</footer>
<script>
function mostrar(id, boton) {{
  document.querySelectorAll('.panel').forEach(p => p.hidden = (p.id !== id));
  document.querySelectorAll('.tab').forEach(b => b.classList.remove('activo'));
  boton.classList.add('activo');
  document.querySelectorAll('#' + id + ' .js-plotly-plot').forEach(g => Plotly.Plots.resize(g));
  window.scrollTo(0, 0);
}}
</script>
</body></html>"""

SALIDA.write_text(html, encoding='utf-8')
print(f'{SALIDA.name}: {SALIDA.stat().st_size / 1e6:.1f} MB, {_n[0]} graficos')
