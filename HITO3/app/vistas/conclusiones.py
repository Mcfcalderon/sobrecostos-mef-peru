import pandas as pd
import streamlit as st

from utils import ESC_B, ESC_C, encabezado, flujo, leer_json, seccion, siguiente
from visual import COLORES, svg

RUTA = 'vistas/conclusiones.py'
encabezado(RUTA, 'Qué responde el proyecto, hasta dónde llega y cómo recomendamos usarlo.')

meta = leer_json('meta')
test = {(m['Escenario'], m['Modelo']): m for m in leer_json('metricas_test')}
captura = {f['Escenario']: f for f in leer_json('captura')['tabla']}
temporal = {(r['Escenario'], r['Modelo']): r for r in leer_json('temporal')['resumen']}
gb = 'Gradient Boosting'
capC = captura[ESC_C]['Captura revisando el 20%']

# ------------------------------------------------------------------ hallazgos como cifras grandes
hallazgos = [
    ('bandera', 'naranja', f'{capC / 20:.1f}×', 'más casos graves que revisar al azar', 'El modelo C ordena bien el riesgo.'),
    ('barras', 'turquesa', f"{test[(ESC_B, gb)]['R2_test']:.2f} → {test[(ESC_C, gb)]['R2_test']:.2f}",
     'R² al sumar el expediente', 'La información pesa más que el algoritmo.'),
    ('check', 'azul', 'GB', 'Gradient Boosting gana', 'Empata en precisión, sobreajusta menos y es rápido.'),
    ('lupa', 'coral', '0.99', 'R² falso con datos de ejecución', 'Métricas altas pueden engañar: fuga excluida.'),
]
html = ''
for k, (ic, col, num, tit, txt) in enumerate(hallazgos):
    c1, c2 = COLORES[col]
    html += (f"<div style='animation:voEntrar .6s ease both;animation-delay:{k * 100}ms'>"
             f"<div style='display:inline-flex;width:46px;height:46px;border-radius:14px;align-items:center;"
             f"justify-content:center;background:linear-gradient(135deg,{c1},{c2})'>{svg(ic, 24)}</div>"
             f"<div style='font-size:2.3rem;font-weight:800;color:{c1};line-height:1.15;margin-top:8px'>{num}</div>"
             f"<div style='font-weight:700;color:#0F3B66'>{tit}</div>"
             f"<div style='color:#5B6B7C;font-size:.9rem'>{txt}</div></div>")
st.markdown(f"<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:22px;"
            f"margin:6px 0 10px 0'>{html}</div>", unsafe_allow_html=True)

seccion('Resultado final', ruta=RUTA)
filas = []
for esc, momento, extra in [(ESC_B, '🟦 B · Viabilidad', f"{temporal[(ESC_B, gb)]['2022 (un anio adelante)']:.2f} temporal"),
                            (ESC_C, '🟧 C · Expediente técnico', '0.57 sin casos espejo')]:
    m = test[(esc, meta['mejor_modelo'][esc])]
    filas.append((momento, f"{m['R2_test']:.3f} ({extra})", m['MAE_test'], m['MedAE_original_test'],
                  captura[esc]['Captura revisando el 20%']))
b = test[(ESC_B, 'Baseline (media)')]
filas.append(('⚪ Referencia (media)', '0.000', b['MAE_test'], b['MedAE_original_test'], 20.0))
st.dataframe(pd.DataFrame(filas, columns=['Momento', 'R² en prueba', 'MAE (pp)', 'MedAE (pp)', 'Captura al 20%']),
             hide_index=True, width='stretch', column_config={
                 'MAE (pp)': st.column_config.NumberColumn(format='%.1f'),
                 'MedAE (pp)': st.column_config.NumberColumn(format='%.1f'),
                 'Captura al 20%': st.column_config.ProgressColumn(format='%.1f%%', min_value=0, max_value=100)})
st.caption('MedAE = error de la obra típica sobre el sobrecosto real · Captura = % de casos graves (> 50%) detectados '
           'al revisar el 20% de obras de mayor riesgo.')

seccion('Recomendación: dos filtros', ruta=RUTA)
a, flecha, b = st.columns([5, 1, 5])
for col, color, titulo, texto in [
        (a, 'azul', 'Filtro 1 · Viabilidad (modelo B)', 'Marca las obras de mayor riesgo para seguirlas desde el inicio.'),
        (b, 'naranja', 'Filtro 2 · Expediente técnico (modelo C)',
         'Las de mayor riesgo se revisan antes de licitar, cuando aún se puede corregir.')]:
    c1, c2 = COLORES[color]
    col.markdown(f"<div style='background:linear-gradient(135deg,{c1},{c2});color:#fff;border-radius:16px;"
                 f"padding:16px 18px;animation:voEntrar .6s ease both'><div style='font-weight:800;font-size:1.05rem'>"
                 f"{titulo}</div><div style='opacity:.93'>{texto}</div></div>", unsafe_allow_html=True)
flecha.markdown("<div style='font-size:2.4rem;text-align:center;color:#F28C28;padding-top:14px'>➜</div>",
                unsafe_allow_html=True)

seccion('Limitaciones', ruta=RUTA)
st.markdown("""
- 📏 **No anticipa la magnitud de los extremos:** en el 8.8% de obras sobre 141.9% el error ronda 533 pp (C), aunque sí las ubica entre las de mayor riesgo.
- 📉 **B pierde fuerza con el tiempo:** R² de 0.22 a 0.14 al predecir 2022. Hay que reentrenarlo cada año.
- ⏳ **Obras recientes aún en curso:** su sobrecosto todavía no es definitivo.
- 🧩 **Un solo snapshot** y faltan variables como contratista, postores o precios de insumos.
""")

seccion('Trabajo futuro', ruta=RUTA)
flujo(['Cruzar con SEACE e INFOBRAS', 'Historial de snapshots', 'Clasificación severo sí/no para B', 'Reentrenar cada año'])

st.markdown("<div style='text-align:center;margin-top:26px;animation:voEntrar .8s ease both'>"
            "<div style='font-size:2rem;font-weight:800;color:#0F3B66'>¡Gracias!</div>"
            "<div style='color:#5B6B7C'>Calderón Flores, Marvin Andy · Chavez Arias, Cristihan David · Lapa Zuñiga, Melissa · "
            "Lopez Contreras, Aldair Mauricio<br>Docente: Jorge Villavicencio Antúnez · IN5306 Applied Machine Learning · "
            "UTEC 2026-2</div></div>", unsafe_allow_html=True)

siguiente(RUTA)
