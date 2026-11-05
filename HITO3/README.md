# Hito 3 — Visualización y comunicación de resultados

Proyecto final IN5306 Applied Machine Learning (UTEC, ciclo 2026-2) · Predicción de sobrecostos en inversión pública del Perú (MEF).

**Plataforma web:** https://sobrecostos-mef-peru.streamlit.app/

## Contenido

| Archivo / carpeta | Qué es |
|---|---|
| `Proyecto_Inversion_Publica_HITO3.ipynb` | Notebook completo (Hitos 1, 2 y 3), ejecutado. Incluye el levantamiento de las observaciones del Hito 2 y la sección 7 de visualización y comunicación. |
| `app/` | Plataforma web en Streamlit con los resultados del proyecto. |
| `app/datos/` | Modelos finales y tablas exportadas por la sección 7.2 del notebook (la app no necesita el dataset completo). |
| `respaldo/Plataforma_sobrecostos_respaldo.html` | Versión de respaldo **sin internet** de la plataforma (se abre con doble clic). Tiene todo menos el simulador. Se regenera con `python respaldo/generar_respaldo.py`. |

## Observaciones del Hito 2 y dónde se levantan

| Observación | Sección del notebook |
|---|---|
| No hay gráfico de radar ni vista comparativa multi-métrica | 6.5 · *Vista comparativa multi-métrica (gráfico de radar)* |
| Revisar el momento real de `MONTO_ET_F8` (posible fuga en el escenario C) | 6.5.3 |
| Reportar el MAE sobre el target original, no solo el winsorizado | 6.5 · *Error sobre la variable objetivo original* |
| Cifras desactualizadas en el markdown | Todo el notebook se volvió a ejecutar y los textos se actualizaron con las salidas |
| La partición es aleatoria: falta validación temporal | 6.5.4 |

## Cómo correr la plataforma

```bash
cd HITO3/app
pip install -r requirements.txt
streamlit run Inicio.py
```

Para publicarla en Streamlit Community Cloud: *New app* → repositorio `Mcfcalderon/sobrecostos-mef-peru` → archivo principal `HITO3/app/Inicio.py` → Python 3.12.

## Datos

Snapshot fijo del dataset *Detalle de Inversiones* del MEF (Portal de Datos Abiertos), descargable desde Google Drive con `gdown` (ID `19xYE2ppcFlMoX6g6Ni6BXBqV7hIL5EiG`); el notebook lo descarga solo.
