import pandas as pd
import plotly.express as px
import streamlit as st

from utils import COLOR_ESC, ESC_B, ESC_C, NOMBRE_ESC, encabezado, grafico, leer_json, nota, seccion, siguiente

RUTA = 'vistas/variables.py'
encabezado(RUTA, 'Qué variables usa más el modelo y qué perfiles de obra existen.')

NOMBRES = {
    'ratio_et_viable': 'Cambio del expediente vs. monto viable', 'TIPO_INVERSION': 'Tipo de inversión',
    'anio_viabilidad': 'Año de viabilidad', 'plazo_dias': 'Plazo programado', 'monto_viable_log': 'Monto viable (tamaño)',
    'DEPARTAMENTO': 'Departamento', 'MARCO': 'Marco normativo', 'SECTOR': 'Sector', 'DES_MODALIDAD': 'Modalidad',
    'NIVEL': 'Nivel de gobierno', 'LATITUD': 'Latitud', 'LONGITUD': 'Longitud', 'FUNCION': 'Función',
}
imp = leer_json('importancias')

seccion('Importancia de las variables', 'Cuánto cae el R² si se desordena cada variable (Gradient Boosting).', RUTA)
izq, der = st.columns(2)
for col, esc, escala in [(izq, ESC_B, ['#D6E4F3', COLOR_ESC[ESC_B]]), (der, ESC_C, ['#FCE3C6', COLOR_ESC[ESC_C]])]:
    d = pd.DataFrame(imp[esc]).head(6)
    d['Variable'] = d['variable'].map(NOMBRES).fillna(d['variable'])
    fig = px.bar(d.sort_values('importancia'), x='importancia', y='Variable', orientation='h', text_auto='.3f',
                 color='importancia', color_continuous_scale=escala, title=NOMBRE_ESC[esc],
                 labels={'importancia': 'Caída del R²', 'Variable': ''})
    grafico(fig.update_layout(coloraxis_showscale=False), col, 360)

a, b = st.columns(2)
a.markdown('🟦 **B:** la señal está repartida — tamaño, plazo y año pesan más, pero ninguna domina.')
b.markdown('🟧 **C:** una variable domina — **cuánto cambió el expediente** frente al monto viable.')
nota('Por eso el R² se triplica de B a C: gran parte del sobrecosto ya se ve al aprobar el expediente técnico. '
     'Es una asociación, no una prueba de causa.', '🔎')

seccion('Perfiles de obra con K-Means', 'K = 3 grupos según monto, plazo, año y ubicación.', RUTA)
km = pd.DataFrame(leer_json('kmeans'))
perfiles = {0: ('Chicas y recientes', 'sur · Cusco', '#2F6FB0', '🏘️'),
            1: ('Chicas y recientes', 'norte · Áncash', '#14806F', '🏡'),
            2: ('Grandes y largas', 'antiguas · Lima', '#F28C28', '🏗️')}
cols = st.columns(3)
for col, (_, r) in zip(cols, km.iterrows()):
    nombre, zona, color, emoji = perfiles[int(r['grupo'])]
    col.markdown(
        f"<div style='border-top:5px solid {color};padding:12px 4px 4px 4px;animation:voAparecer .5s ease both'>"
        f"<div style='font-size:1.8rem'>{emoji}</div>"
        f"<div style='font-weight:800;font-size:1.1rem;color:#0F3B66'>{nombre}</div>"
        f"<div style='color:#5B6B7C;font-size:.9rem'>{zona} · {r['% de obras']:.0f}% de las obras</div>"
        f"<div style='font-size:2.2rem;font-weight:800;color:{color};margin-top:6px'>{r['pct_sobrecosto_severo']:.1f}%</div>"
        f"<div style='color:#5B6B7C;font-size:.85rem'>con sobrecosto severo</div>"
        f"<div style='color:#1B2733;font-size:.88rem;margin-top:8px'>Monto mediano S/ {r['monto_mediano_millones']:.1f} M · "
        f"{r['plazo_mediano_dias']:.0f} días · año {r['anio_mediano']:.0f}</div></div>", unsafe_allow_html=True)

nota('Las obras <b>grandes, largas y antiguas</b> son las más riesgosas. Como variable extra, el grupo no mejora el '
     'modelo (R² 0.209 vs 0.208): su aporte es <b>descriptivo</b>, para comunicar perfiles de riesgo.', '🧩')

siguiente(RUTA)
