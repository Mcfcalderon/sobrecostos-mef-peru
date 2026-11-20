import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import (ESC_B, ESC_C, encabezado, grafico, leer_json, leer_modelo, leer_tabla, nivel_riesgo, nota, seccion,
                   siguiente, soles)

RUTA = 'vistas/simulador.py'
encabezado(RUTA, 'Ingresa una obra nueva y estima su sobrecosto con los modelos finales B y C.')

meta = leer_json('meta')
cat = leer_json('catalogo')
jer = leer_tabla('jerarquia')
obras_prueba = leer_tabla('obras_prueba')
base = leer_tabla('obras_modelo')
categorias = cat['categorias']
centroides = pd.DataFrame(cat['centroides']).set_index('DEPARTAMENTO')


def opciones(col, preferido=None):
    ops = categorias[col]
    return ops, (ops.index(preferido) if preferido in ops else 0)


seccion('① Datos de la inversión', ruta=RUTA)
a, b, c = st.columns(3)
monto = a.number_input('Monto viable (S/)', min_value=10_000, value=2_500_000, step=100_000)
plazo = b.number_input('Plazo programado (días)', min_value=30, max_value=6000, value=int(cat['mediana_plazo_dias']), step=30)
anio = c.number_input('Año de viabilidad', min_value=2005, max_value=2030, value=2026)
a, b, c = st.columns(3)
ops, i = opciones('DEPARTAMENTO', 'CUSCO')
departamento = a.selectbox('Departamento', ops, index=i)
ops, i = opciones('NIVEL', 'GL')
nivel = b.selectbox('Nivel de gobierno', ops, index=i,
                    format_func=lambda v: {'GL': 'Local', 'GR': 'Regional', 'GN': 'Nacional'}.get(v, v))
ops, i = opciones('DES_MODALIDAD', 'ADMINISTRACIÓN INDIRECTA - POR CONTRATA')
modalidad = c.selectbox('Modalidad de ejecución', ops, index=i)

seccion('② Tipo de obra', ruta=RUTA)
a, b, c, d = st.columns(4)
funciones = jer.groupby('FUNCION')['obras'].sum().sort_values(ascending=False).index.tolist()
funcion = a.selectbox('Función', funciones, index=funciones.index('TRANSPORTE') if 'TRANSPORTE' in funciones else 0)
j = jer[jer['FUNCION'] == funcion]
programas = j.groupby('PROGRAMA')['obras'].sum().sort_values(ascending=False).index.tolist()
programa = b.selectbox('Programa', programas)
j = j[j['PROGRAMA'] == programa]
subprogramas = j.groupby('SUBPROGRAMA')['obras'].sum().sort_values(ascending=False).index.tolist()
subprograma = c.selectbox('Subprograma', subprogramas)
j = j[j['SUBPROGRAMA'] == subprograma]
tipologias = j.groupby('DES_TIPOLOGIA')['obras'].sum().sort_values(ascending=False).index.tolist()
tipologia = d.selectbox('Tipología', tipologias)
j = j[j['DES_TIPOLOGIA'] == tipologia]
sector_def = j.sort_values('obras', ascending=False)['SECTOR'].iloc[0] if len(j) else categorias['SECTOR'][0]
with st.expander('Más detalles (sector, tipo de inversión, marco)'):
    a, b, c, d = st.columns(4)
    ops, i = opciones('SECTOR', sector_def)
    sector = a.selectbox('Sector', ops, index=i)
    ops, i = opciones('TIPO_INVERSION', 'PROYECTO DE INVERSION')
    tipo = b.selectbox('Tipo de inversión', ops, index=i)
    ops, i = opciones('MARCO', 'INVIERTE')
    marco = c.selectbox('Marco', ops, index=i)
    ops, i = opciones('IND_IOARR_EMERG', 'NO')
    emergencia = d.selectbox('¿IOARR de emergencia?', ops, index=i)

seccion('③ Expediente técnico (opcional)', 'Actívalo para usar el modelo C, que es más preciso.', RUTA)
a, b = st.columns([1, 2])
tiene_et = a.toggle('Ya tiene expediente aprobado')
monto_et = b.number_input('Monto del expediente técnico (S/)', min_value=0, value=int(monto * 1.15), step=100_000,
                          disabled=not tiene_et)

lat, lon = centroides.loc[departamento, ['LATITUD', 'LONGITUD']] if departamento in centroides.index else (np.nan, np.nan)
fila = {'monto_viable_log': min(np.log1p(monto), cat['tope_monto_viable_log']), 'plazo_dias': plazo,
        'anio_viabilidad': anio, 'LATITUD': lat, 'LONGITUD': lon, 'NIVEL': nivel, 'SECTOR': sector, 'FUNCION': funcion,
        'DES_MODALIDAD': modalidad, 'TIPO_INVERSION': tipo, 'DEPARTAMENTO': departamento, 'MARCO': marco,
        'PROGRAMA': programa, 'SUBPROGRAMA': subprograma, 'DES_TIPOLOGIA': tipologia, 'IND_IOARR_EMERG': emergencia,
        'MONTO_ET_F8': monto_et if tiene_et else np.nan,
        'ratio_et_viable': np.log(monto_et / monto) if tiene_et and monto_et > 0 else np.nan,
        'EXPEDIENTE_TECNICO': 'SI' if tiene_et else 'NO'}
X = pd.DataFrame([fila])

modelo_B, modelo_C = leer_modelo('modelo_B'), leer_modelo('modelo_C')
pred_B = float(modelo_B.predict(X[list(modelo_B.feature_names_in_)])[0])
pred_C = float(modelo_C.predict(X[list(modelo_C.feature_names_in_)])[0]) if tiene_et else None
r2 = {m['Escenario']: m['R2_test'] for m in leer_json('metricas_test') if m['Modelo'] == meta['mejor_modelo'][m['Escenario']]}

seccion('Resultado', ruta=RUTA)


def resultado(columna, titulo, pred, esc):
    nivel_txt, color = nivel_riesgo(pred, meta['cortes_riesgo'][esc])
    col_pred = 'pred_B' if esc == ESC_B else 'pred_C'
    percentil = (obras_prueba[col_pred] < pred).mean() * 100
    fig = go.Figure(go.Indicator(
        mode='gauge+number', value=pred, number={'suffix': '%', 'valueformat': '.1f', 'font': {'color': color, 'size': 46}},
        title={'text': titulo, 'font': {'size': 16, 'color': '#0F3B66'}},
        gauge={'axis': {'range': [meta['lim_inf'], meta['lim_sup']], 'tickcolor': '#9AA7B5'},
               'bar': {'color': color, 'thickness': 0.28}, 'borderwidth': 0,
               'steps': [{'range': [meta['lim_inf'], 0], 'color': '#E3F2EA'}, {'range': [0, 50], 'color': '#FFF4DE'},
                         {'range': [50, meta['lim_sup']], 'color': '#FCE1D6'}]}))
    fig.update_layout(margin=dict(l=25, r=25, t=60, b=0))
    grafico(fig, columna, 270)
    columna.markdown(
        f"<div style='text-align:center'><span style='background:{color};color:#fff;font-weight:800;padding:5px 14px;"
        f"border-radius:999px'>Riesgo {nivel_txt}</span><div style='color:#5B6B7C;margin-top:8px;font-size:.92rem'>"
        f"Más alto que el {percentil:.0f}% de las obras evaluadas · costo final esperado ≈ "
        f"<b>{soles(monto * (1 + pred / 100))}</b></div></div>", unsafe_allow_html=True)


izq, der = st.columns(2)
resultado(izq, 'Modelo B · viabilidad', pred_B, ESC_B)
if pred_C is not None:
    resultado(der, 'Modelo C · expediente técnico', pred_C, ESC_C)
else:
    der.markdown(
        f"<div style='height:100%;display:flex;align-items:center;justify-content:center;text-align:center;"
        f"color:#5B6B7C;padding:40px 20px'><div><div style='font-size:2.4rem'>📄</div>Activa <b>③ Expediente técnico</b> "
        f"para ver el modelo C<br>(R² {r2[ESC_C]:.2f} frente a {r2[ESC_B]:.2f} de B).</div></div>", unsafe_allow_html=True)

similares = base[(base['FUNCION'] == funcion) & (base['DEPARTAMENTO'] == departamento)]
st.write('')
if len(similares) >= 20:
    nota(f"<b>Referencia histórica:</b> {len(similares):,} obras de {funcion.lower()} en {departamento.title()} tuvieron un "
         f"sobrecosto mediano de <b>{similares['desviacion'].median():.1f}%</b> y el "
         f"{(similares['desviacion'] > 50).mean() * 100:.0f}% tuvo sobrecosto severo.", '📚')
nota(f"Es una estimación para <b>priorizar la supervisión</b>, no un presupuesto: el modelo B explica cerca del "
     f"{r2[ESC_B] * 100:.0f}% de la variación del sobrecosto.", '⚠️')

siguiente(RUTA)
