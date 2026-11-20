"""Componentes visuales de Vigía Obras: tarjetas de colores con íconos, animaciones y navegación."""
import streamlit as st

# Íconos SVG (trazo blanco, 24x24)
ICONOS = {
    'ruta': '<circle cx="6" cy="19" r="2"/><circle cx="18" cy="5" r="2"/><path d="M8 19h8a3 3 0 0 0 0-6H8a3 3 0 0 1 0-6h8"/>',
    'mapa': '<path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2-6-2z"/><path d="M9 4v14M15 6v14"/>',
    'barras': '<path d="M4 20h16"/><rect x="5" y="11" width="3" height="7" rx="0.5"/><rect x="10.5" y="7" width="3" height="11" rx="0.5"/><rect x="16" y="4" width="3" height="14" rx="0.5"/>',
    'lupa': '<circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.2-4.2"/><path d="M8 12.5l2-2 1.5 1.5 2.5-3"/>',
    'bandera': '<path d="M5 21V4"/><path d="M5 4h12l-2.5 4 2.5 4H5"/>',
    'calculadora': '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8"/><path d="M8.5 12h.01M12 12h.01M15.5 12h.01M8.5 16h.01M12 16h.01M15.5 16h.01"/>',
    'check': '<circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/>',
    'maletin': '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/><path d="M3 13h18"/>',
    'base': '<ellipse cx="12" cy="5" rx="7" ry="3"/><path d="M5 5v14c0 1.7 3.1 3 7 3s7-1.3 7-3V5"/><path d="M5 12c0 1.7 3.1 3 7 3s7-1.3 7-3"/>',
    'filtro': '<path d="M4 5h16l-6 7v6l-4 2v-8z"/>',
    'red': '<circle cx="6" cy="6" r="2.2"/><circle cx="18" cy="6" r="2.2"/><circle cx="12" cy="18" r="2.2"/><path d="M7.5 7.8 11 16M16.5 7.8 13 16M8.2 6h7.6"/>',
    'nube': '<path d="M7 18a4 4 0 0 1-.5-8 5.5 5.5 0 0 1 10.7-1.5A4 4 0 1 1 17 18"/><path d="M12 12v8M9 15l3-3 3 3"/>',
}

# Colores derivados del logo (azul y naranja) + tonos claros y vivos
COLORES = {
    'azul': ('#0F3B66', '#2F6FB0'), 'cian': ('#1479A3', '#3BB4DC'), 'turquesa': ('#14806F', '#38C29E'),
    'indigo': ('#2F4FB8', '#6E8BF0'), 'naranja': ('#E07812', '#F7B04A'), 'coral': ('#D9572B', '#F59A62'),
    'verde': ('#24875A', '#56C98C'),
}


def svg(nombre, tam=28):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="{tam}" height="{tam}" fill="none" '
            f'stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONOS[nombre]}</svg>')


CSS_VISUAL = """
<style>
@keyframes voEntrar {from {opacity: 0; transform: translateY(16px);} to {opacity: 1; transform: none;}}
@keyframes voCrecer {from {transform: scaleY(0.15);} to {transform: scaleY(1);}}
@keyframes voTrazo {from {stroke-dashoffset: 120;} to {stroke-dashoffset: 0;}}
@keyframes voPulso {0%, 100% {box-shadow: 0 0 0 0 rgba(242, 140, 40, 0.55);} 70% {box-shadow: 0 0 0 12px rgba(242, 140, 40, 0);}}
@keyframes voFlotar {0%, 100% {transform: translateY(0);} 50% {transform: translateY(-6px);}}

.vo-card {
  position: relative; border-radius: 18px; overflow: hidden; background: #FFFFFF;
  border: 1px solid rgba(15, 59, 102, 0.10); box-shadow: 0 4px 14px rgba(15, 59, 102, 0.08);
  transition: transform .25s ease, box-shadow .25s ease; animation: voEntrar .6s ease both;
  height: 100%;
}
.vo-card .vo-top {
  position: relative; height: 92px; display: flex; align-items: center; padding: 0 18px;
  background: linear-gradient(135deg, var(--c1), var(--c2));
}
.vo-card .vo-ico {
  width: 52px; height: 52px; border-radius: 15px; background: rgba(255, 255, 255, 0.22);
  display: flex; align-items: center; justify-content: center; transition: transform .35s ease;
  backdrop-filter: blur(2px);
}
.vo-card .vo-n {
  position: absolute; right: 14px; bottom: -16px; font-size: 4.4rem; font-weight: 800; line-height: 1;
  color: rgba(255, 255, 255, 0.30);
}
.vo-card .vo-chip {
  position: absolute; top: 12px; right: 12px; background: rgba(255, 255, 255, 0.92); color: var(--c1);
  font-size: 0.72rem; font-weight: 800; padding: 3px 9px; border-radius: 999px; letter-spacing: .02em;
}
.vo-card .vo-cuerpo {padding: 13px 18px 15px 18px; min-height: 132px; display: flex; flex-direction: column;}
.vo-card .vo-cta {margin-top: auto !important; padding-top: 9px;}
.vo-card .vo-cuerpo .vo-tt {margin: 0 0 3px 0; padding: 0; font-size: 1.04rem; color: #0F3B66; font-weight: 750;}
.vo-card .vo-cuerpo p {margin: 0; font-size: 0.87rem; color: #5B6B7C; line-height: 1.35;}
.vo-card .vo-cta {font-size: 0.8rem; font-weight: 800; color: var(--c1);}
.vo-card .vo-cta span {display: inline-block; transition: transform .25s ease;}
.vo-card:hover, [class*="st-key-vonav"]:hover .vo-card {transform: translateY(-6px); box-shadow: 0 16px 30px rgba(15, 59, 102, 0.18);}
.vo-card:hover .vo-ico, [class*="st-key-vonav"]:hover .vo-ico {transform: rotate(-8deg) scale(1.12);}
.vo-card:hover .vo-cta span, [class*="st-key-vonav"]:hover .vo-cta span {transform: translateX(6px);}

/* Tarjeta completa clickeable: el enlace de Streamlit cubre la tarjeta y queda invisible */
[class*="st-key-vonav"] {position: relative; gap: 0 !important;}
[class*="st-key-vonav"] .stElementContainer {animation: none !important; transform: none !important;}
[class*="st-key-vonav"] .stElementContainer,
[class*="st-key-vonav"] [data-testid="stPageLink"],
[class*="st-key-vonav"] [data-testid="stPageLink"] * {position: static !important;}
[class*="st-key-vonav"] .stElementContainer:has([data-testid="stPageLink"]) {height: 0; margin: 0; padding: 0;}
[class*="st-key-vonav"] a[data-testid="stPageLink-NavLink"] {
  position: absolute !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important;
  max-width: none !important; z-index: 5; opacity: 0; border-radius: 18px;
}

/* Grilla con enlaces internos (anclas) */
.vo-grid {display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 12px; margin: 6px 0 18px 0;}
@media (max-width: 1100px) {.vo-grid {grid-template-columns: repeat(4, minmax(0, 1fr));}}
@media (max-width: 640px) {.vo-grid {grid-template-columns: repeat(2, minmax(0, 1fr));}}
.vo-grid .vo-card .vo-cuerpo {min-height: 104px; padding: 11px 13px 12px 13px;}
.vo-grid .vo-card .vo-cuerpo .vo-tt {font-size: .95rem;}
.vo-grid .vo-card .vo-cuerpo p {font-size: .8rem;}
.vo-grid .vo-card .vo-top {padding: 0 13px;}
.vo-grid a {text-decoration: none !important; color: inherit !important;}
.vo-grid .vo-card .vo-top {height: 74px;}
.vo-grid .vo-card .vo-n {font-size: 3.4rem; bottom: -12px;}
.vo-grid .vo-card .vo-ico {width: 44px; height: 44px; border-radius: 13px;}

/* Portada animada */
.vo-hero2 {
  position: relative; overflow: hidden; border-radius: 22px; padding: 30px 34px; margin-bottom: 1.1rem;
  background: radial-gradient(circle at 85% 20%, rgba(242,140,40,0.35) 0, rgba(242,140,40,0) 38%),
              linear-gradient(120deg, #0F3B66 0%, #1D5C96 60%, #2F7FC0 100%);
  display: flex; align-items: center; justify-content: space-between; gap: 24px; animation: voEntrar .5s ease both;
}
.vo-hero2 h1 {color: #FFFFFF !important; font-size: 2.6rem; margin: 0; padding: 0; line-height: 1.1;}
.vo-hero2 h1 .vo-acento {color: #F7A54A;}
.vo-hero2 .vo-lema {color: #FFFFFF; font-size: 1.15rem; font-weight: 600; margin-top: 6px;}
.vo-hero2 p {color: #DCE8F4; font-size: 1rem; margin: 10px 0 0 0; max-width: 640px;}
.vo-hero2 .vo-insignia {
  display: inline-block; margin-top: 14px; background: #F28C28; color: #FFFFFF; font-weight: 800; font-size: .85rem;
  padding: 7px 14px; border-radius: 999px; animation: voPulso 2.2s infinite;
}
.vo-hero2 .vo-arte {flex: 0 0 auto; animation: voFlotar 4s ease-in-out infinite;}
.vo-hero2 .vo-arte .b {transform-box: fill-box; transform-origin: bottom; animation: voCrecer 1.1s cubic-bezier(.2,.8,.2,1) both;}
.vo-hero2 .vo-arte .b2 {animation-delay: .15s;}
.vo-hero2 .vo-arte .b3 {animation-delay: .3s;}
.vo-hero2 .vo-arte .l {stroke-dasharray: 120; animation: voTrazo 1.4s .45s ease both;}
@media (max-width: 760px) {.vo-hero2 .vo-arte {display: none;} .vo-hero2 h1 {font-size: 2rem;}}

/* Franja de ideas cortas */
.vo-franja {display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 12px; margin: 4px 0 8px 0;}
.vo-idea {display: flex; gap: 12px; align-items: center; padding: 12px 14px; border-radius: 14px;
          background: rgba(15, 59, 102, 0.045); border: 1px solid rgba(15, 59, 102, 0.10); animation: voEntrar .6s ease both;}
.vo-idea .vo-ico {width: 40px; height: 40px; border-radius: 12px; flex: 0 0 40px; display: flex; align-items: center;
                  justify-content: center; background: linear-gradient(135deg, var(--c1), var(--c2));}
.vo-idea b {display: block; color: #0F3B66; font-size: .92rem;}
.vo-idea span {color: #5B6B7C; font-size: .84rem;}

/* Encabezado de sección de etapa */
.vo-etapa {display: flex; align-items: center; gap: 14px; margin: 26px 0 8px 0; padding: 12px 16px; border-radius: 16px;
           background: linear-gradient(135deg, var(--c1), var(--c2)); color: #FFFFFF; animation: voEntrar .5s ease both;}
.vo-etapa .vo-ico {width: 44px; height: 44px; border-radius: 13px; background: rgba(255,255,255,.22); display: flex;
                   align-items: center; justify-content: center;}
.vo-etapa .t {font-size: 1.25rem; font-weight: 800;}
.vo-etapa .s {font-size: .9rem; opacity: .92;}
.vo-etapa .k {margin-left: auto; display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end;}
.vo-etapa .k span {background: rgba(255,255,255,.92); color: var(--c1); border-radius: 999px; padding: 4px 10px;
                   font-size: .8rem; font-weight: 800; white-space: nowrap;}
</style>
"""


def aplicar_estilo_visual():
    st.markdown(CSS_VISUAL, unsafe_allow_html=True)


def _tarjeta_html(n, titulo, texto, icono, color, chip='', cta='Ver', retardo=0):
    c1, c2 = COLORES[color]
    chip_html = f'<div class="vo-chip">{chip}</div>' if chip else ''
    return (f'<div class="vo-card" style="--c1:{c1};--c2:{c2};animation-delay:{retardo}ms">'
            f'<div class="vo-top"><div class="vo-ico">{svg(icono)}</div>{chip_html}<div class="vo-n">{n}</div></div>'
            f'<div class="vo-cuerpo"><div class="vo-tt">{titulo}</div><p>{texto}</p>'
            f'<div class="vo-cta">{cta} <span>→</span></div></div></div>')


def grilla_paginas(items, columnas=4):
    """Tarjetas clickeables que llevan a otras páginas de la app (navegación interna de Streamlit)."""
    for fila in range(0, len(items), columnas):
        cols = st.columns(columnas)
        for k, it in enumerate(items[fila:fila + columnas]):
            with cols[k].container(key=f'vonav_{fila + k}'):
                st.markdown(_tarjeta_html(it['n'], it['titulo'], it['texto'], it['icono'], it['color'], it.get('chip', ''),
                                          'Ver paso', retardo=(fila + k) * 90), unsafe_allow_html=True)
                st.page_link(it['ruta'], label=it['titulo'])


def grilla_anclas(items):
    """Tarjetas que saltan a una sección de la misma página."""
    html = ''.join(f'<a href="#{it["ancla"]}">' + _tarjeta_html(it['n'], it['titulo'], it['texto'], it['icono'], it['color'],
                                                               it.get('chip', ''), 'Ir', retardo=i * 70) + '</a>'
                   for i, it in enumerate(items))
    st.markdown(f'<div class="vo-grid">{html}</div>', unsafe_allow_html=True)


def franja_ideas(ideas):
    html = ''.join(f'<div class="vo-idea" style="--c1:{COLORES[c][0]};--c2:{COLORES[c][1]};animation-delay:{i * 90}ms">'
                   f'<div class="vo-ico">{svg(ic, 22)}</div><div><b>{t}</b><span>{x}</span></div></div>'
                   for i, (ic, c, t, x) in enumerate(ideas))
    st.markdown(f'<div class="vo-franja">{html}</div>', unsafe_allow_html=True)


def etapa(ancla, n, titulo, subtitulo, icono, color, cifras=()):
    c1, c2 = COLORES[color]
    k = ''.join(f'<span>{c}</span>' for c in cifras)
    st.markdown(f'<div id="{ancla}" class="vo-etapa" style="--c1:{c1};--c2:{c2}"><div class="vo-ico">{svg(icono, 24)}</div>'
                f'<div><div class="t">{n}. {titulo}</div><div class="s">{subtitulo}</div></div><div class="k">{k}</div></div>',
                unsafe_allow_html=True)


def portada(nombre_a, nombre_b, lema, texto, insignia):
    arte = ('<svg class="vo-arte" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="150" height="150">'
            '<rect x="2" y="2" width="60" height="60" rx="14" fill="rgba(255,255,255,0.10)"/>'
            '<rect class="b" x="13" y="36" width="9" height="16" rx="1.5" fill="#FFFFFF"/>'
            '<rect class="b b2" x="27.5" y="28" width="9" height="24" rx="1.5" fill="#FFFFFF"/>'
            '<rect class="b b3" x="42" y="20" width="9" height="32" rx="1.5" fill="#FFFFFF" opacity="0.6"/>'
            '<polyline class="l" points="11,31 26,23 35,26 50,12" fill="none" stroke="#F28C28" stroke-width="4" '
            'stroke-linecap="round" stroke-linejoin="round"/><circle cx="50" cy="12" r="4.5" fill="#F28C28"/></svg>')
    st.markdown(f'<div class="vo-hero2"><div><h1>{nombre_a} <span class="vo-acento">{nombre_b}</span></h1><div class="vo-lema">{lema}</div>'
                f'<p>{texto}</p><div class="vo-insignia">{insignia}</div></div>{arte}</div>', unsafe_allow_html=True)
