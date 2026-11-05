import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import (COLOR_ESC, ESC_B, ESC_C, configurar_pagina, leer_json, leer_modelo, leer_tabla, nivel_riesgo,
                   pie_de_pagina, soles)

configurar_pagina('Simulador', '🧮')
st.title('Simulador: ¿cuánto sobrecosto podría tener una obra nueva?')
st.markdown('Ingresa los datos de una obra tal como se conocen **al declarar su viabilidad** (modelo B). Si además ya '
            'tiene **expediente técnico aprobado**, ingresa su monto para usar el modelo C, que es más preciso.')

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


st.subheader('1. Datos de la inversión')
a, b, c = st.columns(3)
monto = a.number_input('Monto viable (S/)', min_value=10_000, value=2_500_000, step=100_000)
plazo = b.number_input('Plazo programado de ejecución (días)', min_value=30, max_value=6000,
                       value=int(cat['mediana_plazo_dias']), step=30)
anio = c.number_input('Año de declaración de viabilidad', min_value=2005, max_value=2030, value=2026)

a, b, c = st.columns(3)
ops, i = opciones('DEPARTAMENTO', 'CUSCO')
departamento = a.selectbox('Departamento', ops, index=i)
ops, i = opciones('NIVEL', 'GL')
nivel = b.selectbox('Nivel de gobierno', ops, index=i, format_func=lambda v: {'GL': 'GL · Local', 'GR': 'GR · Regional',
                                                                                 'GN': 'GN · Nacional'}.get(v, v))
ops, i = opciones('DES_MODALIDAD', 'ADMINISTRACIÓN INDIRECTA - POR CONTRATA')
modalidad = c.selectbox('Modalidad de ejecución', ops, index=i)

st.subheader('2. Tipo de obra')
a, b = st.columns(2)
funciones = jer.groupby('FUNCION')['obras'].sum().sort_values(ascending=False).index.tolist()
funcion = a.selectbox('Función', funciones, index=funciones.index('TRANSPORTE') if 'TRANSPORTE' in funciones else 0)
j = jer[jer['FUNCION'] == funcion]
programas = j.groupby('PROGRAMA')['obras'].sum().sort_values(ascending=False).index.tolist()
programa = b.selectbox('Programa', programas)
j = j[j['PROGRAMA'] == programa]
a, b = st.columns(2)
subprogramas = j.groupby('SUBPROGRAMA')['obras'].sum().sort_values(ascending=False).index.tolist()
subprograma = a.selectbox('Subprograma', subprogramas)
j = j[j['SUBPROGRAMA'] == subprograma]
tipologias = j.groupby('DES_TIPOLOGIA')['obras'].sum().sort_values(ascending=False).index.tolist()
tipologia = b.selectbox('Tipología', tipologias)
j = j[j['DES_TIPOLOGIA'] == tipologia]
sector_def = j.sort_values('obras', ascending=False)['SECTOR'].iloc[0] if len(j) else categorias['SECTOR'][0]

a, b, c, d = st.columns(4)
ops, i = opciones('SECTOR', sector_def)
sector = a.selectbox('Sector', ops, index=i)
ops, i = opciones('TIPO_INVERSION', 'PROYECTO DE INVERSION')
tipo = b.selectbox('Tipo de inversión', ops, index=i)
ops, i = opciones('MARCO', 'INVIERTE')
marco = c.selectbox('Marco', ops, index=i)
ops, i = opciones('IND_IOARR_EMERG', 'NO')
emergencia = d.selectbox('¿IOARR de emergencia?', ops, index=i)

st.subheader('3. Expediente técnico (opcional)')
a, b = st.columns(2)
tiene_et = a.checkbox('La obra ya tiene expediente técnico aprobado')
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
cols_B = list(modelo_B.feature_names_in_)
pred_B = float(modelo_B.predict(X[cols_B])[0])
pred_C = float(modelo_C.predict(X[list(modelo_C.feature_names_in_)])[0]) if tiene_et else None

st.divider()
st.subheader('Resultado')


def tarjeta(columna, titulo, pred, esc):
    nivel_txt, color = nivel_riesgo(pred, meta['cortes_riesgo'][esc])
    col_pred = 'pred_B' if esc == ESC_B else 'pred_C'
    percentil = (obras_prueba[col_pred] < pred).mean() * 100
    fig = go.Figure(go.Indicator(mode='gauge+number', value=pred, number={'suffix': '%', 'valueformat': '.1f'},
                                 title={'text': titulo},
                                 gauge={'axis': {'range': [meta['lim_inf'], meta['lim_sup']]},
                                        'bar': {'color': color},
                                        'steps': [{'range': [meta['lim_inf'], 0], 'color': '#e5f5e0'},
                                                  {'range': [0, 50], 'color': '#fff7bc'},
                                                  {'range': [50, meta['lim_sup']], 'color': '#fee0d2'}]}))
    fig.update_layout(height=290, margin=dict(l=20, r=20, t=60, b=10))
    columna.plotly_chart(fig, width='stretch')
    columna.markdown(f"Riesgo **<span style='color:{color}'>{nivel_txt}</span>** · más alto que el "
                     f"{percentil:.0f}% de las obras evaluadas · costo final esperado ≈ **{soles(monto * (1 + pred / 100))}**",
                     unsafe_allow_html=True)


r2 = {m['Escenario']: m['R2_test'] for m in leer_json('metricas_test') if m['Modelo'] == meta['mejor_modelo'][m['Escenario']]}

izq, der = st.columns(2)
tarjeta(izq, 'Modelo B (viabilidad)', pred_B, ESC_B)
if pred_C is not None:
    tarjeta(der, 'Modelo C (expediente técnico)', pred_C, ESC_C)
    der.caption(f'El expediente ya implica una desviación de {(monto_et / monto - 1) * 100:+.1f}% respecto del monto viable.')
else:
    der.info('Marca "La obra ya tiene expediente técnico aprobado" e ingresa su monto para obtener la estimación '
             f'del modelo C (R² = {r2[ESC_C]:.2f} frente a {r2[ESC_B]:.2f} del modelo B).')

similares = base[(base['FUNCION'] == funcion) & (base['DEPARTAMENTO'] == departamento)]
if len(similares) >= 20:
    st.markdown(f"**Referencia histórica:** {len(similares):,} obras de {funcion.lower()} en {departamento.title()} "
                f"tuvieron un sobrecosto mediano de **{similares['desviacion'].median():.1f}%** y el "
                f"{(similares['desviacion'] > 50).mean() * 100:.0f}% tuvo sobrecosto severo.")

st.warning('Es una estimación estadística para **priorizar la supervisión**, no un presupuesto. El modelo B explica cerca '
           f'del {r2[ESC_B] * 100:.0f}% de la variación del sobrecosto; sirve para ordenar obras por riesgo, no para '
           'predecir el monto exacto.')

pie_de_pagina()
