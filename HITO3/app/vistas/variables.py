import pandas as pd
import plotly.express as px
import streamlit as st

from utils import COLOR_ESC, ESC_B, ESC_C, NOMBRE_ESC, encabezado, leer_json, siguiente

RUTA = 'vistas/variables.py'
encabezado(RUTA, 'Qué variables usa más el modelo para anticipar el sobrecosto y qué perfiles de obra existen.')

NOMBRES = {
    'ratio_et_viable': 'Cambio del expediente vs. monto viable', 'TIPO_INVERSION': 'Tipo de inversión',
    'anio_viabilidad': 'Año de viabilidad', 'plazo_dias': 'Plazo programado (días)',
    'monto_viable_log': 'Monto viable (tamaño)', 'DEPARTAMENTO': 'Departamento', 'MARCO': 'Marco normativo',
    'SECTOR': 'Sector', 'DES_MODALIDAD': 'Modalidad de ejecución', 'NIVEL': 'Nivel de gobierno',
    'LATITUD': 'Latitud', 'LONGITUD': 'Longitud', 'FUNCION': 'Función', 'PROGRAMA': 'Programa',
    'SUBPROGRAMA': 'Subprograma', 'DES_TIPOLOGIA': 'Tipología', 'IND_IOARR_EMERG': 'IOARR de emergencia',
    'MONTO_ET_F8': 'Monto del expediente técnico', 'EXPEDIENTE_TECNICO': 'Tiene expediente técnico',
}

imp = leer_json('importancias')

st.subheader('Importancia de las variables')
st.caption('Importancia por permutación de Gradient Boosting: cuánto cae el R² en prueba si se desordena esa variable. '
           'Mientras más cae, más depende el modelo de ella.')
izq, der = st.columns(2)
for col, esc in [(izq, ESC_B), (der, ESC_C)]:
    d = pd.DataFrame(imp[esc]).head(6)
    d['Variable'] = d['variable'].map(NOMBRES).fillna(d['variable'])
    fig = px.bar(d.sort_values('importancia'), x='importancia', y='Variable', orientation='h', text_auto='.3f',
                 color_discrete_sequence=[COLOR_ESC[esc]], title=NOMBRE_ESC[esc],
                 labels={'importancia': 'Caída del R² al permutar', 'Variable': ''})
    col.plotly_chart(fig.update_layout(height=420), width='stretch')

i, d = st.columns(2)
i.markdown("""
**Escenario B.** La señal está repartida entre muchas variables débiles: el **tamaño** de la obra, el **plazo** y el
**año** son las más útiles, seguidas de la modalidad y la ubicación. Por eso su R² es moderado.
""")
d.markdown("""
**Escenario C.** Una sola variable domina: **cuánto cambió el expediente técnico respecto del monto viable**. Es la razón
por la que el R² se triplica al pasar de B a C: buena parte del sobrecosto ya se ve al aprobar el expediente.
""")
st.info('Es una asociación, no una prueba de causa: durante la obra también aparecen adicionales y ampliaciones.')

st.subheader('Perfiles de obra con K-Means')
st.caption('Complemento no supervisado: se agruparon las obras de entrenamiento con K-Means (K = 3) usando monto, plazo, '
           'año y ubicación, y se proyectaron con PCA para interpretarlas.')
km = pd.DataFrame(leer_json('kmeans'))
perfiles = {0: 'Chicas y recientes (sur)', 1: 'Chicas y recientes (norte)', 2: 'Grandes, largas y antiguas'}
km['Perfil'] = km['grupo'].map(perfiles)

a, b = st.columns([3, 2])
with a:
    tabla = km[['grupo', 'Perfil', 'obras', '% de obras', 'monto_mediano_millones', 'plazo_mediano_dias', 'anio_mediano',
                'departamento_mas_frecuente', 'desviacion_mediana', 'pct_sobrecosto_severo']]
    st.dataframe(tabla, hide_index=True, width='stretch', column_config={
        'grupo': 'Grupo', 'obras': st.column_config.NumberColumn('Obras', format='%d'),
        '% de obras': st.column_config.NumberColumn('% de obras', format='%.1f%%'),
        'monto_mediano_millones': st.column_config.NumberColumn('Monto mediano (S/ M)', format='%.1f'),
        'plazo_mediano_dias': st.column_config.NumberColumn('Plazo mediano (días)', format='%d'),
        'anio_mediano': st.column_config.NumberColumn('Año mediano', format='%d'),
        'departamento_mas_frecuente': 'Depto. más frecuente',
        'desviacion_mediana': st.column_config.NumberColumn('Sobrecosto mediano (%)', format='%.1f'),
        'pct_sobrecosto_severo': st.column_config.NumberColumn('% con sobrecosto severo', format='%.1f'),
    })
with b:
    fig = px.bar(km, x='Perfil', y='pct_sobrecosto_severo', text_auto='.1f', color='Perfil',
                 color_discrete_sequence=['#9ecae1', '#6baed6', '#F28C28'],
                 labels={'pct_sobrecosto_severo': '% con sobrecosto severo', 'Perfil': ''},
                 title='¿Qué grupo tiene más sobrecostos graves?')
    st.plotly_chart(fig.update_layout(showlegend=False, height=360), width='stretch')

st.markdown("""
- Las obras **grandes, de plazo largo y antiguas** (grupo 2) son las más riesgosas: 32.7% tiene sobrecosto severo.
- Al agregar el grupo de K-Means como variable, el R² de Gradient Boosting en B no mejora (0.209 frente a 0.208), porque
  los árboles ya capturan esas combinaciones. Su aporte es **descriptivo**: ayuda a comunicar perfiles de riesgo.
""")

siguiente(RUTA)
