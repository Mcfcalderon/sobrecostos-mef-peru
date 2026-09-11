# Guía de trabajo — Proyecto Final Applied Machine Learning (IN5306)

**Curso:** IN5306 Applied Machine Learning — Ciclo 9 (UTEC)
**Docente:** Villavicencio Antunez, Jorge
**Tema:** Predicción de sobrecostos en inversión pública del Perú (MEF)

**Integrantes:**

| Nombre | Código | GitHub |
|---|---|---|
| Calderón Flores, Marvin Andy | [Código] | @Mcfcalderon |
| Chavez Arias, Cristihan David | [Código] | @cristihanchavez-code |
| Lapa Zuñiga, Melissa | 202220147 | @MeliDant |
| Lopez Contreras, Aldair Mauricio | [Código] | _(pendiente)_ |

## Objetivo y alcance
Desarrollar y comparar modelos de Machine Learning que predigan el porcentaje de desviación presupuestal (sobrecosto) de un proyecto de inversión pública a partir de sus características iniciales, usando datos del MEF (Invierte.pe).

## Distribución de roles
El proyecto ya completó Business Understanding, Data Understanding y Data Preparation (EDA, verificación de calidad de datos, feature engineering, selección de 33 variables). Falta Modelado, Evaluación e Informe final:

| Integrante | Rol | Responsabilidad |
|---|---|---|
| Marvin Calderón | Datos y EDA (ya avanzado) | Mantiene el notebook fuente y la calidad de datos; apoya con el dataset ya preparado |
| [Integrante 2] | Modelado | Implementar y comparar los 4 modelos de regresión (Hito 2): Lineal, Árbol, Random Forest, Gradient Boosting |
| [Integrante 3] | Evaluación | Validación cruzada, métricas (MAE/RMSE/R²), gráficos de resultados |
| [Integrante 4] | Informe y entrega | Consolidar el informe Word/APA, checklist de entrega, presentación final |

## Plan por fases (CRISP-DM)
- **Fase 0 — Setup:** repositorio, roles, calendario (esta guía) — ✅ hecho
- **Fase 1 — Business + Data Understanding:** ✅ hecho
- **Fase 2 — Data Preparation:** ✅ hecho (incluye verificación de calidad de datos)
- **Fase 3 — Modeling (Hito 2):** ⬜ pendiente
- **Fase 4 — Evaluation:** ⬜ pendiente
- **Fase 5 — Informe final y cierre:** ⬜ pendiente

## Calendario sugerido
_(completar con fechas de Canvas)_

## Herramientas
Google Colab (notebook compartido) · GitHub (seguimiento y versionado) · Word/APA (informe) · Google Drive (snapshot fijo de datos vía gdown)

## Buenas prácticas de coordinación
- Reunión semanal corta para revisar el tablero
- **Tablero GitHub Project**, columnas: `Por hacer` / `En curso` / `En revisión` / `Hecho`
- **Convención de ramas:** `feature/modelado-rf`, `feature/evaluacion-metricas`, `feature/informe-final`
- Commits descriptivos; Pull Request antes de fusionar a `main`
- El notebook de Colab es la única fuente de verdad — evitar copias divergentes entre integrantes

## Checklist de entrega
- [ ] 4 modelos comparados con las mismas métricas y el mismo split
- [ ] Evaluación final en test (una sola vez)
- [ ] Informe Word en formato APA actualizado con resultados de modelado
- [ ] Revisión cruzada entre los 4 integrantes antes de entregar

## Riesgos y mitigación
- Dataset con inconsistencias (fechas invertidas, coordenadas fuera de Perú, montos extremos) → **ya mitigado** en la sección de Preparación de Datos
- Coordinar un notebook entre 4 personas → mitigación: issues por sección, ramas cortas, un responsable por commit al notebook compartido

## Estructura del repositorio
Por ahora los archivos están en la raíz (migrar a subcarpetas es opcional, no urgente):
- `Guia_Proyecto_MEF.md` — este documento
- `README.md`
- `Proyecto_Inversion_Publica.ipynb` — notebook principal
- `Proyecto_Inversion_Publica.ipynb - Colab(ejecucion).pdf` — versión ejecutada de referencia
- `Informe_Sobrecostos_Inversion_Publica_MEF.docx` — informe en APA
- `inversiones_mef_snapshot.csv` — **no se sube al repositorio** (ver `.gitignore`); el notebook lo descarga automáticamente vía gdown

## Seguimiento del trabajo
GitHub Project con columnas `Por hacer / En curso / En revisión / Hecho`, un milestone por fase CRISP-DM pendiente (Modeling, Evaluation, Informe), issues por tarea asignados a cada integrante.
