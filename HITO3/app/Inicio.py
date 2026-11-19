"""Vigía Obras: punto de entrada de la plataforma.

Define el logo, el estilo y el orden de las páginas (el mismo orden de la presentación).
"""
import streamlit as st

from utils import ASSETS, LEMA, NOMBRE_APP, PAGINAS, aplicar_estilo, pie_de_pagina

st.set_page_config(page_title=f'{NOMBRE_APP} · {LEMA}', page_icon=str(ASSETS / 'icono.png'), layout='wide')
st.logo(str(ASSETS / 'logo.svg'), icon_image=str(ASSETS / 'icono.svg'), size='large')
aplicar_estilo()

secciones = {}
for i, (ruta, titulo, icono, seccion) in enumerate(PAGINAS):
    secciones.setdefault(seccion, []).append(
        st.Page(ruta, title=f'{i + 1}. {titulo}', icon=icono, default=(i == 0)))

pagina = st.navigation(secciones)
pagina.run()
pie_de_pagina()
