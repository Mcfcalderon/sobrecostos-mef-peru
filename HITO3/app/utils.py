import json
from pathlib import Path

import joblib
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

RAIZ = Path(__file__).parent
DATOS = RAIZ / 'datos'
ASSETS = RAIZ / 'assets'

NOMBRE_APP = 'Vigía Obras'
LEMA = 'Alerta temprana de sobrecostos en la inversión pública del Perú'
URL_APP = 'https://sobrecostos-mef-peru.streamlit.app/'

AZUL = '#0F3B66'
NARANJA = '#F28C28'
TEXTO_SUAVE = '#5B6B7C'

ESC_B = 'B - Viabilidad'
ESC_C = 'C - Expediente tecnico'
COLOR_ESC = {ESC_B: '#2F6FB0', ESC_C: '#F28C28'}
NOMBRE_ESC = {ESC_B: 'B · Al declarar la viabilidad', ESC_C: 'C · Al aprobar el expediente técnico'}
ORDEN_MODELOS = ['Baseline (media)', 'Regresion Lineal', 'Ridge', 'Arbol de Decision',
                 'Bagging', 'Random Forest', 'Gradient Boosting', 'Stacking']
# Tonos azules para todos y naranja para el modelo elegido (Gradient Boosting), para que resalte
COLOR_MODELO = dict(zip(ORDEN_MODELOS, ['#C3CEDA', '#A9C1DD', '#86A9D1', '#6391C4',
                                        '#4479B4', '#2A5F9E', '#F28C28', '#0F3B66']))
ESCALA_RIESGO = [[0, '#E8F1FA'], [0.35, '#9CC3E6'], [0.6, '#F7B04A'], [0.8, '#E0662E'], [1, '#9E2A1F']]

# Orden de la presentación: (ruta, título, ícono material, sección, ícono svg, color)
PAGINAS = [
    ('vistas/inicio.py', 'Inicio', ':material/home:', 'Presentación', 'ruta', 'azul'),
    ('vistas/proceso.py', 'Cómo lo hicimos', ':material/route:', 'Presentación', 'ruta', 'azul'),
    ('vistas/explorar.py', 'Explorar sobrecostos', ':material/map:', 'Resultados', 'mapa', 'cian'),
    ('vistas/modelos.py', 'Comparar modelos', ':material/leaderboard:', 'Resultados', 'barras', 'turquesa'),
    ('vistas/variables.py', 'Qué explica el sobrecosto', ':material/insights:', 'Resultados', 'lupa', 'indigo'),
    ('vistas/priorizar.py', 'Priorizar obras', ':material/flag:', 'Resultados', 'bandera', 'naranja'),
    ('vistas/simulador.py', 'Simulador', ':material/calculate:', 'Herramienta', 'calculadora', 'coral'),
    ('vistas/conclusiones.py', 'Conclusiones', ':material/task_alt:', 'Cierre', 'check', 'verde'),
]

# ---------------------------------------------------------------- plantilla de gráficos
pio.templates['vigia'] = go.layout.Template(layout=dict(
    font=dict(family='"Source Sans Pro", "Segoe UI", sans-serif', size=13, color='#1B2733'),
    colorway=['#2F6FB0', '#F28C28', '#14806F', '#2F4FB8', '#D9572B', '#24875A', '#1479A3', '#8FA9C7'],
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    title=dict(font=dict(size=15, color=AZUL), x=0, xanchor='left'),
    xaxis=dict(gridcolor='#E6ECF2', zerolinecolor='#D3DCE6', linecolor='#D3DCE6'),
    yaxis=dict(gridcolor='#E6ECF2', zerolinecolor='#D3DCE6', linecolor='#D3DCE6'),
    legend=dict(bgcolor='rgba(0,0,0,0)', title_text=''),
    hoverlabel=dict(bgcolor='#FFFFFF', bordercolor='#D3DCE6', font=dict(color='#1B2733')),
    margin=dict(l=10, r=10, t=48, b=10),
))
pio.templates.default = 'plotly_white+vigia'
CONFIG_GRAFICO = {'displayModeBar': False, 'responsive': True}


def grafico(fig, donde=None, alto=None):
    """Muestra un gráfico de Plotly con la plantilla de Vigía Obras (sin la barra de herramientas)."""
    fig.update_layout(template='plotly_white+vigia', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    if alto:
        fig.update_layout(height=alto)
    (donde or st).plotly_chart(fig, width='stretch', theme=None, config=CONFIG_GRAFICO)


CSS = f"""
<style>
.block-container {{padding-top: 2rem; max-width: 1280px;}}
@keyframes voAparecer {{from {{opacity: 0; transform: translateY(10px);}} to {{opacity: 1; transform: none;}}}}
.stMainBlockContainer .stElementContainer {{animation: voAparecer .45s ease both;}}

/* Métricas: sin caja, con una línea de acento */
[data-testid="stMetric"] {{
    background: linear-gradient(90deg, rgba(15, 59, 102, 0.05), rgba(15, 59, 102, 0));
    border-left: 4px solid var(--vo-acento, {NARANJA}); border-radius: 4px 12px 12px 4px; padding: 8px 14px;
}}
[data-testid="stMetricValue"] {{font-weight: 800; color: {AZUL}; font-size: 1.95rem;}}
[data-testid="stMetricLabel"] p {{color: {TEXTO_SUAVE}; font-weight: 600;}}

/* Pestañas como píldoras */
.stTabs [role="tablist"] {{gap: 8px; flex-wrap: wrap; border-bottom: none !important; box-shadow: none !important;}}
.stTabs [role="tablist"]::after, .stTabs [role="tablist"]::before {{display: none !important;}}
.stTabs [data-testid="stTab"] {{
    background: rgba(15, 59, 102, 0.06); border-radius: 999px !important; padding: 6px 16px !important; font-weight: 600;
    border: none !important; box-shadow: none !important; transition: background .2s ease;
}}
.stTabs [data-testid="stTab"]::after, .stTabs [data-testid="stTab"]::before {{display: none !important;}}
.stTabs [data-testid="stTab"]:hover {{background: rgba(242, 140, 40, 0.16);}}
.stTabs [data-testid="stTab"][aria-selected="true"] {{background: var(--vo-acento, {AZUL}); color: #FFFFFF;}}
.stTabs [data-testid="stTab"][aria-selected="true"] * {{color: #FFFFFF !important;}}
.stTabs [data-testid="stTab"] + div:not([data-testid="stTab"]) {{display: none;}}

/* Encabezado de página */
.vo-cab {{
    position: relative; overflow: hidden; display: flex; align-items: center; gap: 18px; padding: 22px 26px;
    border-radius: 20px; margin-bottom: 1rem; color: #FFFFFF;
    background: radial-gradient(circle at 92% 10%, rgba(255,255,255,.22) 0, rgba(255,255,255,0) 35%),
                linear-gradient(120deg, var(--c1), var(--c2));
    animation: voAparecer .5s ease both;
}}
.vo-cab .vo-ico {{width: 58px; height: 58px; flex: 0 0 58px; border-radius: 17px; background: rgba(255,255,255,.22);
                  display: flex; align-items: center; justify-content: center;}}
.vo-cab .vo-pp {{font-size: .76rem; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; opacity: .9;}}
.vo-cab .vo-tt {{font-size: 2rem; font-weight: 800; line-height: 1.15;}}
.vo-cab .vo-ss {{font-size: 1rem; opacity: .93; margin-top: 2px;}}
.vo-cab .vo-fondo {{position: absolute; right: -10px; bottom: -26px; opacity: .14;}}

/* Título de sección */
.vo-sec {{display: flex; align-items: baseline; gap: 10px; margin: 1.4rem 0 .4rem 0;}}
.vo-sec .barra {{width: 6px; height: 22px; border-radius: 4px; background: linear-gradient(180deg, var(--c1), var(--c2));
                 align-self: center;}}
.vo-sec .t {{font-size: 1.32rem; font-weight: 800; color: {AZUL};}}
.vo-sec .s {{font-size: .92rem; color: {TEXTO_SUAVE};}}

/* Mensaje destacado */
.vo-nota {{display: flex; gap: 12px; align-items: center; padding: 12px 16px; border-radius: 14px; margin: .4rem 0 .8rem 0;
           background: linear-gradient(90deg, rgba(242,140,40,.13), rgba(242,140,40,.02)); color: #1B2733;}}
.vo-nota .i {{font-size: 1.3rem;}}

.vo-flujo {{display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin: 6px 0 12px 0;}}
.vo-flujo span {{background: rgba(15, 59, 102, 0.07); border-radius: 999px; padding: 5px 12px; font-size: .86rem;
                 font-weight: 600;}}
.vo-flujo b {{color: {NARANJA};}}

/* Navegación anterior / siguiente */
[class*="st-key-vo_nav_pie"] [data-testid="stPageLink"] a {{
    border-radius: 999px; padding: 6px 14px; background: rgba(15, 59, 102, 0.06); transition: background .2s ease;
}}
[class*="st-key-vo_nav_pie"] [data-testid="stPageLink"] a:hover {{background: rgba(242, 140, 40, 0.18);}}
</style>
"""


def aplicar_estilo():
    st.markdown(CSS, unsafe_allow_html=True)


def _info_pagina(ruta):
    i = next(k for k, p in enumerate(PAGINAS) if p[0] == ruta)
    return i, PAGINAS[i]


def encabezado(ruta, subtitulo=''):
    """Banda de color con el número de paso, el título y el ícono de la página."""
    from visual import COLORES, svg
    i, (_, titulo, _, seccion, icono, color) = _info_pagina(ruta)
    c1, c2 = COLORES[color]
    st.markdown(f'<style>:root {{--vo-acento: {c1};}}</style>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="vo-cab" style="--c1:{c1};--c2:{c2}"><div class="vo-ico">{svg(icono, 30)}</div>'
        f'<div><div class="vo-pp">Paso {i + 1} de {len(PAGINAS)} · {seccion}</div><div class="vo-tt">{titulo}</div>'
        f'<div class="vo-ss">{subtitulo}</div></div><div class="vo-fondo">{svg(icono, 150)}</div></div>',
        unsafe_allow_html=True)


def seccion(titulo, subtitulo='', ruta=None):
    from visual import COLORES
    color = _info_pagina(ruta)[1][5] if ruta else 'azul'
    c1, c2 = COLORES[color]
    sub = f'<span class="s">{subtitulo}</span>' if subtitulo else ''
    st.markdown(f'<div class="vo-sec" style="--c1:{c1};--c2:{c2}"><span class="barra"></span>'
                f'<span class="t">{titulo}</span>{sub}</div>', unsafe_allow_html=True)


def nota(texto, icono='💡'):
    st.markdown(f'<div class="vo-nota"><span class="i">{icono}</span><span>{texto}</span></div>', unsafe_allow_html=True)


def siguiente(ruta):
    """Enlaces al paso anterior y al siguiente, para seguir la presentación en orden."""
    i, _ = _info_pagina(ruta)
    st.write('')
    with st.container(key='vo_nav_pie'):
        izq, _, der = st.columns([2, 3, 2])
        if i > 0:
            r, t = PAGINAS[i - 1][:2]
            izq.page_link(r, label=f'Anterior: {t}', icon=':material/arrow_back:')
        if i < len(PAGINAS) - 1:
            r, t = PAGINAS[i + 1][:2]
            der.page_link(r, label=f'Siguiente: {t}', icon=':material/arrow_forward:')


def flujo(pasos):
    html = ' <b>→</b> '.join(f'<span>{p}</span>' for p in pasos)
    st.markdown(f"<div class='vo-flujo'>{html}</div>", unsafe_allow_html=True)


@st.cache_data
def leer_json(nombre):
    return json.loads((DATOS / f'{nombre}.json').read_text(encoding='utf-8'))


@st.cache_data
def leer_tabla(nombre):
    return pd.read_parquet(DATOS / f'{nombre}.parquet')


@st.cache_resource
def leer_modelo(nombre):
    return joblib.load(DATOS / f'{nombre}.joblib')


def soles(x):
    if pd.isna(x):
        return '-'
    if abs(x) >= 1e6:
        return f'S/ {x / 1e6:,.1f} M'
    return f'S/ {x:,.0f}'


def nivel_riesgo(pred, cortes):
    # cortes: percentiles 50 y 80 de la prediccion en el conjunto de prueba
    if pred >= cortes['p80']:
        return 'Alto', '#D9572B'
    if pred >= cortes['p50']:
        return 'Medio', '#F28C28'
    return 'Bajo', '#24875A'


def pie_de_pagina():
    meta = leer_json('meta')
    st.caption(f"{NOMBRE_APP} · Proyecto final IN5306 Applied Machine Learning · UTEC 2026-2 · Datos: MEF, "
               f"Detalle de Inversiones (snapshot de {meta['fecha_snapshot']}) · "
               f"{meta['obras_modelo']:,} obras con costo actualizado.")
