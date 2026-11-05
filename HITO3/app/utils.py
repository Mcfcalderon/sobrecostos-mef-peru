import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

DATOS = Path(__file__).parent / 'datos'

ESC_B = 'B - Viabilidad'
ESC_C = 'C - Expediente tecnico'
COLOR_ESC = {ESC_B: '#1f77b4', ESC_C: '#ff7f0e'}
NOMBRE_ESC = {ESC_B: 'B · Al declarar la viabilidad', ESC_C: 'C · Al aprobar el expediente técnico'}
ORDEN_MODELOS = ['Baseline (media)', 'Regresion Lineal', 'Ridge', 'Arbol de Decision',
                 'Bagging', 'Random Forest', 'Gradient Boosting', 'Stacking']
COLOR_MODELO = dict(zip(ORDEN_MODELOS, ['#9aa5a8', '#6baed6', '#3182bd', '#74c476',
                                        '#fdae6b', '#ff6b6b', '#4ecdc4', '#9e9ac8']))


def configurar_pagina(titulo, icono='🏗️'):
    st.set_page_config(page_title=f'{titulo} · Sobrecostos MEF', page_icon=icono, layout='wide')


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
    st.divider()
    st.caption(f"Proyecto final IN5306 Applied Machine Learning · UTEC · Datos: MEF, Detalle de Inversiones "
               f"(snapshot de {meta['fecha_snapshot']}) · {meta['obras_modelo']:,} obras con costo actualizado.")
