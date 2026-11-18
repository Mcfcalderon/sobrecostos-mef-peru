"""Abre la plataforma en un navegador real y la despierta si Streamlit la puso a dormir.

Un ping HTTP no basta: Streamlit Community Cloud solo cuenta como visita una sesion
de navegador que carga la app.
"""
import re
import sys

from playwright.sync_api import sync_playwright

URL = "https://sobrecostos-mef-peru.streamlit.app/"
TITULO = "Predicción de sobrecostos"


def app_cargada(page):
    for frame in page.frames:
        try:
            if frame.get_by_text(TITULO).count() > 0:
                return True
        except Exception:
            pass
    return False


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(URL, timeout=120_000)
    page.wait_for_timeout(10_000)

    boton = page.get_by_role("button", name=re.compile("get this app back up", re.I))
    if boton.count() > 0:
        print("La app estaba dormida: se pulsa el boton para despertarla.")
        boton.first.click()

    for _ in range(18):  # hasta ~3 minutos
        if app_cargada(page):
            print("OK: la app esta despierta y muestra la pagina de Inicio.")
            browser.close()
            sys.exit(0)
        page.wait_for_timeout(10_000)

    page.screenshot(path="estado_app.png", full_page=True)
    print("ERROR: la app no cargo en 3 minutos.")
    browser.close()
    sys.exit(1)
