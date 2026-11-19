import json
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

RAIZ = Path(__file__).parent
DATOS = RAIZ / 'datos'
ASSETS = RAIZ / 'assets'

NOMBRE_APP = 'Vigía Obras'
LEMA = 'Alerta temprana de sobrecostos en la inversión pública del Perú'
URL_APP = 'https://sobrecostos-mef-peru.streamlit.app/'

AZUL = '#0F3B66'
NARANJA = '#F28C28'

ESC_B = 'B - Viabilidad'
ESC_C = 'C - Expediente tecnico'
COLOR_ESC = {ESC_B: '#1f77b4', ESC_C: '#ff7f0e'}
NOMBRE_ESC = {ESC_B: 'B · Al declarar la viabilidad', ESC_C: 'C · Al aprobar el expediente técnico'}
ORDEN_MODELOS = ['Baseline (media)', 'Regresion Lineal', 'Ridge', 'Arbol de Decision',
                 'Bagging', 'Random Forest', 'Gradient Boosting', 'Stacking']
COLOR_MODELO = dict(zip(ORDEN_MODELOS, ['#9aa5a8', '#6baed6', '#3182bd', '#74c476',
                                        '#fdae6b', '#ff6b6b', '#4ecdc4', '#9e9ac8']))

# Orden de la presentación: (ruta, título, ícono, sección)
PAGINAS = [
    ('vistas/inicio.py', 'Inicio', ':material/home:', 'Presentación'),
    ('vistas/proceso.py', 'Cómo lo hicimos', ':material/route:', 'Presentación'),
    ('vistas/explorar.py', 'Explorar sobrecostos', ':material/map:', 'Resultados'),
    ('vistas/modelos.py', 'Comparar modelos', ':material/leaderboard:', 'Resultados'),
    ('vistas/variables.py', 'Qué explica el sobrecosto', ':material/insights:', 'Resultados'),
    ('vistas/priorizar.py', 'Priorizar obras', ':material/flag:', 'Resultados'),
    ('vistas/simulador.py', 'Simulador', ':material/calculate:', 'Herramienta'),
    ('vistas/conclusiones.py', 'Conclusiones', ':material/task_alt:', 'Cierre'),
]

CSS = f"""
<style>
.block-container {{padding-top: 2.2rem; max-width: 1280px;}}
[data-testid="stMetric"] {{
    background: rgba(15, 59, 102, 0.045);
    border: 1px solid rgba(15, 59, 102, 0.14);
    border-radius: 12px; padding: 14px 16px;
}}
[data-testid="stMetricValue"] {{font-weight: 700;}}
.vo-hero {{
    background: linear-gradient(120deg, {AZUL} 0%, #1D5C96 100%);
    color: #FFFFFF; border-radius: 18px; padding: 30px 34px 26px 34px; margin-bottom: 1.2rem;
}}
.vo-hero h1 {{color: #FFFFFF; font-size: 2.3rem; margin: 0 0 4px 0; padding: 0;}}
.vo-hero h1 span {{color: {NARANJA};}}
.vo-hero p {{color: #E3ECF5; font-size: 1.08rem; margin: 6px 0 0 0;}}
.vo-hero .vo-lema {{color: #FFFFFF; font-size: 1.2rem; font-weight: 600; margin-top: 2px;}}
.vo-paso {{
    display: inline-block; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; color: {NARANJA}; margin-bottom: -6px;
}}
.vo-sub {{color: #5B6B7C; font-size: 1.05rem; margin-top: -6px; margin-bottom: 0.6rem;}}
.vo-tarjeta {{
    border: 1px solid rgba(15, 59, 102, 0.16); border-radius: 14px; padding: 16px 18px; height: 100%;
    background: rgba(15, 59, 102, 0.03);
}}
.vo-tarjeta h4 {{margin: 0 0 6px 0; padding: 0; font-size: 1.02rem;}}
.vo-tarjeta p {{margin: 0; font-size: 0.93rem; color: inherit; opacity: 0.88;}}
.vo-num {{font-size: 1.7rem; font-weight: 800; color: {NARANJA}; line-height: 1.1;}}
.vo-flujo {{display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin: 6px 0 12px 0;}}
.vo-flujo span {{
    background: rgba(15, 59, 102, 0.08); border-radius: 999px; padding: 5px 12px; font-size: 0.86rem; font-weight: 600;
}}
.vo-flujo b {{color: {NARANJA};}}
</style>
"""


def aplicar_estilo():
    st.markdown(CSS, unsafe_allow_html=True)


def encabezado(ruta, subtitulo=''):
    """Título de la página con su número de paso dentro del recorrido."""
    i = next(k for k, p in enumerate(PAGINAS) if p[0] == ruta)
    _, titulo, _, seccion = PAGINAS[i]
    st.markdown(f"<span class='vo-paso'>Paso {i + 1} de {len(PAGINAS)} · {seccion}</span>", unsafe_allow_html=True)
    st.title(titulo)
    if subtitulo:
        st.markdown(f"<p class='vo-sub'>{subtitulo}</p>", unsafe_allow_html=True)


def siguiente(ruta):
    """Enlace al paso anterior y al siguiente, para seguir la presentación en orden."""
    i = next(k for k, p in enumerate(PAGINAS) if p[0] == ruta)
    st.divider()
    izq, _, der = st.columns([2, 3, 2])
    if i > 0:
        r, t, ic, _ = PAGINAS[i - 1]
        izq.page_link(r, label=f'Anterior: {t}', icon=':material/arrow_back:')
    if i < len(PAGINAS) - 1:
        r, t, ic, _ = PAGINAS[i + 1]
        der.page_link(r, label=f'Siguiente: {t}', icon=':material/arrow_forward:')


def tarjeta(titulo, texto, numero=None):
    num = f"<div class='vo-num'>{numero}</div>" if numero else ''
    st.markdown(f"<div class='vo-tarjeta'>{num}<h4>{titulo}</h4><p>{texto}</p></div>", unsafe_allow_html=True)


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
        return 'Alto', '#d62728'
    if pred >= cortes['p50']:
        return 'Medio', '#ff7f0e'
    return 'Bajo', '#2ca02c'


def pie_de_pagina():
    meta = leer_json('meta')
    st.caption(f"{NOMBRE_APP} · Proyecto final IN5306 Applied Machine Learning · UTEC 2026-2 · Datos: MEF, "
               f"Detalle de Inversiones (snapshot de {meta['fecha_snapshot']}) · "
               f"{meta['obras_modelo']:,} obras con costo actualizado.")
