import streamlit as st

from utils import (ESC_B, ESC_C, configurar_pagina, leer_json, leer_tabla, pie_de_pagina)

configurar_pagina('Inicio')

meta = leer_json('meta')
captura = leer_json('captura')
metricas = {(m['Escenario'], m['Modelo']): m for m in leer_json('metricas_test')}
base = leer_tabla('obras_modelo')

st.title('Predicción de sobrecostos en la inversión pública del Perú')
st.markdown(
    'Al aprobar una obra pública, el Estado no sabe cuánto terminará costando. Esta plataforma usa '
    '**Machine Learning** sobre los datos abiertos del MEF (Invierte.pe) para **estimar el sobrecosto '
    'esperado de cada obra antes de construirla** y así decidir cuáles supervisar primero.'
)

c1, c2, c3, c4 = st.columns(4)
c1.metric('Obras analizadas', f"{meta['obras_modelo']:,}", help='Obras con monto viable y costo actualizado registrado')
c2.metric('Con sobrecosto', f"{(base['desviacion'] > 0).mean() * 100:.0f}%")
c3.metric('Sobrecosto mediano', f"{base['desviacion'].median():.1f}%")
c4.metric('Con sobrecosto severo (> 50%)', f"{(base['desviacion'] > 50).mean() * 100:.0f}%")

st.subheader('Dos momentos para anticipar el sobrecosto')
mB, mC = metricas[(ESC_B, meta['mejor_modelo'][ESC_B])], metricas[(ESC_C, meta['mejor_modelo'][ESC_C])]
filaB = next(f for f in captura['tabla'] if f['Escenario'] == ESC_B)
filaC = next(f for f in captura['tabla'] if f['Escenario'] == ESC_C)

col_b, col_c = st.columns(2)
with col_b:
    st.markdown('#### 🟦 Modelo B · Al declarar la viabilidad')
    st.markdown('Usa solo lo que se sabe cuando se aprueba la inversión: monto viable, plazo programado, '
                'ubicación, función, tipología, modalidad y nivel de gobierno.')
    a, b, c = st.columns(3)
    a.metric('R² en prueba', f"{mB['R2_test']:.2f}")
    b.metric('Error medio (MAE)', f"{mB['MAE_test']:.1f} pp")
    c.metric('Detecta revisando el 20%', f"{filaB['Captura revisando el 20%']:.0f}%",
             help='Porcentaje de obras con sobrecosto severo que se detectan revisando el 20% de obras con mayor riesgo predicho')
with col_c:
    st.markdown('#### 🟧 Modelo C · Al aprobar el expediente técnico')
    st.markdown('Agrega el monto del expediente técnico. Es el momento previo a licitar, '
                'cuando todavía se puede corregir el diseño o el presupuesto.')
    a, b, c = st.columns(3)
    a.metric('R² en prueba', f"{mC['R2_test']:.2f}")
    b.metric('Error medio (MAE)', f"{mC['MAE_test']:.1f} pp")
    c.metric('Detecta revisando el 20%', f"{filaC['Captura revisando el 20%']:.0f}%")

st.info(f"Revisando al azar el 20% de las obras se detectaría solo el 20% de los sobrecostos severos. "
        f"Con el modelo C se detecta el {filaC['Captura revisando el 20%']:.0f}%, es decir "
        f"**{filaC['Captura revisando el 20%'] / 20:.1f} veces más** con el mismo esfuerzo de supervisión.")

st.subheader('¿Qué encontramos?')
st.markdown(f"""
- **El sobrecosto se origina sobre todo al elaborar el expediente técnico.** La diferencia entre el expediente y el monto viable es la variable más importante del modelo C.
- **La información disponible pesa más que el algoritmo.** Cambiar de modelo mejora el R² en centésimas; incorporar el expediente técnico lo triplica.
- **El mejor modelo en ambos momentos es Gradient Boosting**: empata en precisión con Random Forest y Stacking, pero sobreajusta menos y entrena más rápido.
- **Los modelos con "fuga de información" engañan.** Si se usan datos de la ejecución (devengados, saldos), el R² sube a 0.90, pero esa información no existe cuando hay que decidir.
""")

st.subheader('Cómo usar esta plataforma')
st.markdown("""
| Página | Qué puedes hacer |
|---|---|
| **Explorar sobrecostos** | Ver en el mapa y en gráficos dónde y en qué tipo de obras hay más sobrecosto |
| **Comparar modelos** | Comparar los 7 modelos + baseline con radar, métricas, validación temporal y pruebas de fuga |
| **Priorizar obras** | Ordenar obras reales por riesgo predicho, filtrar por región o función y ver qué pasó realmente |
| **Simulador** | Ingresar los datos de una obra nueva y estimar su sobrecosto |
""")

pie_de_pagina()
