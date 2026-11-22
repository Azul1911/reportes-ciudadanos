import glob
import re
import altair as alt
import pandas as pd
import pydeck as pdk
import streamlit as st
import db

st.set_page_config(page_title="ReportaBaches Ciudad Juárez", page_icon="📍", layout="wide")

st.markdown("""
<style>
:root {color-scheme: light;}
.stApp {background:#FFFFFF;}
header[data-testid="stHeader"], [data-testid="stElementToolbar"] {display:none;}
.block-container {padding:0 1.5rem 3rem; max-width:1180px;}

/* ---------- Texto siempre legible ---------- */
.stApp p, .stApp li, .stApp label, .stApp span, .stApp div[data-testid="stMarkdownContainer"],
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {color:#1B2430;}
.stApp h2, .stApp h3, .stApp h4 {color:#0B2F6B;}
.stApp [data-testid="stCaptionContainer"], .stApp [data-testid="stCaptionContainer"] p {color:#5B6B80;}
input, textarea {background:#FFFFFF !important; color:#1B2430 !important;}
input::placeholder, textarea::placeholder {color:#8A98AD !important; opacity:1;}
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div {
    background:#FFFFFF !important; border-color:#B9C7DA !important; border-radius:10px !important;}
[data-baseweb="select"] span, [data-baseweb="select"] div {color:#1B2430 !important;}
[data-baseweb="popover"] > div, [data-baseweb="menu"], ul[role="listbox"] {background:#FFFFFF !important;}
ul[role="listbox"] li, [data-baseweb="menu"] li {color:#1B2430 !important; background:#FFFFFF !important;}
ul[role="listbox"] li:hover {background:#E8F1FB !important;}
span[data-baseweb="tag"] {background:#123F7A !important;}
span[data-baseweb="tag"] span, span[data-baseweb="tag"] svg {color:#FFFFFF !important; fill:#FFFFFF !important;}
[data-testid="stExpander"] {background:#FFFFFF; border:1px solid #E3EAF3; border-radius:12px;}
[data-testid="stExpander"] summary p {color:#0B2F6B; font-weight:700;}
[data-testid="stForm"] {background:#FFFFFF; border:1px solid #E3EAF3; border-radius:12px;}

/* ---------- Botones ---------- */
.stButton > button, .stFormSubmitButton > button {background:#FFFFFF; color:#0B2F6B;
    border:1.5px solid #0B2F6B; border-radius:10px; font-weight:700;}
.stButton > button p, .stFormSubmitButton > button p {color:#0B2F6B;}
.stButton > button:hover {background:#E8F1FB; border-color:#0B2F6B;}
.stButton > button:disabled {background:#F1F4F8; border-color:#C9D3E0;}
.stButton > button:disabled p {color:#8A98AD;}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"],
button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primaryFormSubmit"] {
    background:#0B2F6B !important; border:1.5px solid #0B2F6B !important;}
button[kind="primary"] p, button[data-testid="stBaseButton-primary"] p,
button[data-testid="stBaseButton-primaryFormSubmit"] p {color:#FFFFFF !important;}

/* ---------- Barra superior y franja del logo (mismo ancho) ---------- */
.topbar {background:#123F7A; padding:.85rem 1.5rem; display:flex; justify-content:space-between;
         align-items:center; gap:1rem; flex-wrap:wrap; border-radius:0 0 14px 14px;}
.topbar span {color:#FFFFFF !important; font-size:.92rem; font-weight:500;}
.st-key-navband {background:#DCEBFB; border-radius:16px; padding:.6rem 1.2rem; margin:.9rem 0 0;}
.st-key-navband .stButton > button {width:100%; background:transparent; border:none; box-shadow:none;
    color:#123F7A; padding:.55rem .3rem; white-space:nowrap;}
.st-key-navband .stButton > button p {color:#123F7A !important; font-weight:800; font-size:.74rem;
    text-transform:uppercase; letter-spacing:.02em; white-space:nowrap;}
.st-key-navband .stButton > button:hover {background:#C5DDF6;}
.st-key-navband .stButton > button[kind="primary"],
.st-key-navband button[data-testid="stBaseButton-primary"] {background:#123F7A !important;}
.st-key-navband button[kind="primary"] p,
.st-key-navband button[data-testid="stBaseButton-primary"] p {color:#FFFFFF !important;}

/* ---------- Títulos ---------- */
.ttl {text-align:center; margin:2.2rem 0 1.4rem; position:relative;}
.ttl .marca {position:absolute; left:0; right:0; top:-1.6rem; font-size:5rem; font-weight:800;
             color:#F0F5FB; line-height:1; z-index:0; user-select:none; white-space:nowrap; overflow:hidden;}
.ttl small, .ttl h1, .ttl p {position:relative; z-index:1;}
.ttl small {color:#0B6FA8 !important; font-weight:700; letter-spacing:.14em; text-transform:uppercase;}
.ttl h1 {color:#0B2F6B !important; font-size:2.6rem; font-weight:800; margin:.3rem 0; padding:0;}
.ttl p {color:#5B6B80 !important; margin:0; font-size:1.02rem;}

/* ---------- Tarjetas ---------- */
div[data-testid="stVerticalBlockBorderWrapper"] {background:#FFFFFF; border:1px solid #E3EAF3;
    border-top:4px solid #0B6FA8; border-radius:14px; box-shadow:0 6px 18px rgba(18,63,122,.10);}
.circ {width:76px; height:76px; border-radius:50%; margin:-3.2rem auto .8rem; font-size:1.9rem;
       background:linear-gradient(135deg,#0B3C7A,#0A9BD3); display:flex; align-items:center;
       justify-content:center; box-shadow:0 6px 14px rgba(10,111,168,.35);}
.cardtit {text-align:center; color:#0B2F6B !important; font-size:1.5rem; font-weight:800; margin:.2rem 0;}
.cardsub {text-align:center; color:#5B6B80 !important; margin-bottom:1rem;}
div[data-testid="stMetric"] {background:#FFFFFF; border:1px solid #E3EAF3; border-top:4px solid #0B6FA8;
    border-radius:14px; padding:.9rem 1.1rem; box-shadow:0 6px 18px rgba(18,63,122,.10);}
div[data-testid="stMetricLabel"] p {color:#5B6B80 !important; font-weight:600;}
div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] div {color:#0B2F6B !important; font-weight:800;}

/* ---------- Avisos, etiquetas y línea de tiempo ---------- */
.aviso {border-radius:10px; padding:.75rem 1rem; margin:.6rem 0; font-weight:600; border:1px solid;}
.badge {padding:.2rem .8rem; border-radius:999px; font-size:.8rem; font-weight:700; display:inline-block;}
.tl {border-left:3px solid #0B6FA8; padding:.1rem 0 .1rem .8rem; margin-bottom:.6rem; color:#1B2430;}
</style>
<div class="topbar"><span>📍 Ciudad Juárez, Chihuahua</span>
<span>Reporta · Transforma · Mejora</span>
<span>🗄️ Supabase + 🍃 MongoDB Atlas</span></div>
""", unsafe_allow_html=True)

ESTATUS = ["recibido", "en_revision", "resuelto"]
ETIQ = {"recibido": "Recibido", "en_revision": "En revisión", "resuelto": "Resuelto"}
COLORES = {"recibido": ("#FEF3C7", "#92400E"), "en_revision": ("#DBEAFE", "#1E40AF"),
           "resuelto": ("#DCFCE7", "#166534")}
AVISOS = {"info": ("#EAF3FF", "#9CC4F0", "#123F7A"), "warn": ("#FFF4D6", "#F2C94C", "#6B4B00"),
          "ok": ("#E3F7EA", "#86D3A0", "#14532D")}
PAGINAS = ["Usuarios", "Nuevo reporte", "Consulta", "Reportes", "Comentarios", "Vista combinada"]
folio = lambda i: f"RB-{i:04d}"

def aviso(texto, tipo="info"):
    bg, borde, fg = AVISOS[tipo]
    st.markdown(f'<div class="aviso" style="background:{bg};border-color:{borde};color:{fg}">{texto}</div>',
                unsafe_allow_html=True)

def badge(e):
    bg, fg = COLORES[e]
    return f'<span class="badge" style="background:{bg};color:{fg}">{ETIQ[e]}</span>'

def titulo(arriba, grande, sub):
    st.markdown(f'<div class="ttl"><div class="marca">{arriba}</div><small>{arriba}</small>'
                f'<h1>{grande}</h1><p>{sub}</p></div>', unsafe_allow_html=True)

def historial(reporte_id):
    for h in db.obtener_seguimiento(reporte_id):
        st.markdown(f"<div class='tl'><b>{ETIQ.get(h['estatus'], h['estatus'])}</b> · "
                    f"{h['fecha']:%d/%m/%Y %H:%M}<br>{h['nota']}</div>", unsafe_allow_html=True)

def buscar_logo():
    for patron in ("logo.*", "Logo.*", "*logo*.*"):
        for f in glob.glob(patron):
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                return f
    return None

def grafica_categorias(reportes):
    conteo = pd.Series([r["categorias"]["nombre"] for r in reportes]).value_counts().reset_index()
    conteo.columns = ["categoria", "reportes"]
    chart = (alt.Chart(conteo)
             .mark_bar(color="#0B6FA8", cornerRadiusTopLeft=6, cornerRadiusTopRight=6, size=48)
             .encode(x=alt.X("categoria:N", title=None, axis=alt.Axis(labelAngle=0)),
                     y=alt.Y("reportes:Q", title=None, axis=alt.Axis(tickMinStep=1)),
                     tooltip=["categoria", "reportes"])
             .properties(height=300, width="container", background="#FFFFFF")
             .configure_axis(labelColor="#1B2430", gridColor="#E3EAF3", domainColor="#B9C7DA", tickColor="#B9C7DA")
             .configure_view(strokeWidth=0))
    st.altair_chart(chart, theme=None)

def mapa(reportes):
    pts = [{"latitude": float(r["latitud"]), "longitude": float(r["longitud"]), "titulo": r["titulo"]}
           for r in reportes if r.get("latitud") is not None and r.get("longitud") is not None]
    if not pts:
        aviso("Los reportes aún no tienen coordenadas.")
        return
    df = pd.DataFrame(pts)
    capa = pdk.Layer("ScatterplotLayer", df, get_position="[longitude, latitude]", get_radius=140,
                     get_fill_color=[56, 189, 248, 230], get_line_color=[255, 255, 255], line_width_min_pixels=2,
                     stroked=True, pickable=True)
    vista = pdk.ViewState(latitude=float(df.latitude.mean()), longitude=float(df.longitude.mean()), zoom=11)
    st.pydeck_chart(pdk.Deck(layers=[capa], initial_view_state=vista, map_style="dark",
                             tooltip={"text": "{titulo}"}))

reportes = db.listar_reportes()
fmt = lambda r: f"{folio(r['id'])} · {r['titulo']}"
if "pagina" not in st.session_state:
    st.session_state.pagina = "Usuarios"

# ---------- Encabezado: logo a la izquierda y menú en una sola línea ----------
with st.container(key="navband"):
    cols = st.columns([2.0, 1.1, 1.4, 1.1, 1.1, 1.4, 1.7], vertical_alignment="center")
    with cols[0]:
        logo = buscar_logo()
        if logo:
            st.image(logo, width=190)
        else:
            st.markdown("### ReportaBaches")
    for col, nombre in zip(cols[1:], PAGINAS):
        activo = st.session_state.pagina == nombre
        if col.button(nombre, key=f"nav_{nombre}", type="primary" if activo else "secondary"):
            st.session_state.pagina = nombre
            st.rerun()
pagina = st.session_state.pagina

# ---------- USUARIOS (Supabase) ----------
if pagina == "Usuarios":
    titulo("Registro", "Usuarios", "Personas que levantan reportes · guardados en Supabase")
    with st.expander("➕ Registrar nuevo usuario"):
        with st.form("nuevo_usuario", clear_on_submit=True):
            a, b, c = st.columns(3)
            nom = a.text_input("Nombre completo")
            cor = b.text_input("Correo")
            tel = c.text_input("Teléfono (opcional)")
            guardar = st.form_submit_button("Registrar usuario", type="primary")
        if guardar:
            if not nom.strip() or not cor.strip():
                aviso("Nombre y correo son obligatorios.", "warn")
            elif "@" not in cor:
                aviso("Escribe un correo válido.", "warn")
            else:
                try:
                    db.crear_usuario(nom.strip(), cor.strip().lower(), tel.strip())
                    aviso(f"Usuario {nom.strip()} registrado.", "ok")
                except Exception as e:
                    if "23505" in str(e) or "duplicate" in str(e).lower():
                        aviso("Ya existe un usuario con ese correo.", "warn")
                    else:
                        aviso("No se pudo registrar el usuario. Intenta de nuevo.", "warn")

    usuarios = db.listar_usuarios()
    conteo = {}
    for r in reportes:
        conteo[r["usuario_id"]] = conteo.get(r["usuario_id"], 0) + 1
    st.markdown(f"**{len(usuarios)} usuarios registrados**")
    for u in usuarios:
        with st.container(border=True):
            st.caption(f"ID {u['id']} · {conteo.get(u['id'], 0)} reporte(s)")
            a, b, c = st.columns(3)
            n = a.text_input("Nombre", u["nombre"], key=f"un{u['id']}")
            e = b.text_input("Correo", u["correo"], key=f"ue{u['id']}")
            t = c.text_input("Teléfono", u.get("telefono") or "", key=f"ut{u['id']}")
            x1, x2, x3 = st.columns([1, 1, 3])
            if x1.button("Guardar", key=f"ug{u['id']}"):
                db.actualizar_usuario(u["id"], n.strip(), e.strip().lower(), t.strip())
                st.rerun()
            ok = x3.checkbox("Confirmo que quiero eliminarlo junto con sus reportes", key=f"uc{u['id']}")
            if x2.button("Eliminar", key=f"ud{u['id']}", disabled=not ok):
                db.eliminar_usuario(u["id"])
                st.rerun()

# ---------- NUEVO REPORTE ----------
elif pagina == "Nuevo reporte":
    titulo("Ciudadanía", "Levanta un reporte", "Cuéntanos qué problema hay en tu colonia")
    _, centro, _ = st.columns([1, 3, 1])
    with centro:
        with st.form("nuevo_reporte", clear_on_submit=True):
            a, b = st.columns(2)
            usuario = a.selectbox("Usuario", db.listar_usuarios(), format_func=lambda u: u["nombre"])
            categoria = b.selectbox("Categoría", db.listar_categorias(), format_func=lambda c: c["nombre"])
            t = st.text_input("Título")
            d = st.text_area("Descripción")
            dire = st.text_input("Dirección")
            enviar = st.form_submit_button("Enviar reporte", type="primary")
        if enviar:
            if t and dire:
                nuevo = db.crear_reporte({"usuario_id": usuario["id"], "categoria_id": categoria["id"],
                                          "titulo": t, "descripcion": d, "direccion": dire})
                aviso(f"Reporte registrado. Tu folio es {folio(nuevo['id'])}", "ok")
            else:
                aviso("Título y dirección son obligatorios.", "warn")

# ---------- CONSULTA (búsqueda por folio + resumen) ----------
elif pagina == "Consulta":
    titulo("Reportes", "Consulta de reportes", "Ingresa tu número de folio para consultar el estatus de tu reporte")
    st.markdown("<div style='height:2.6rem'></div>", unsafe_allow_html=True)
    _, centro, _ = st.columns([1, 2, 1])
    with centro:
        with st.container(border=True):
            st.markdown('<div class="circ">🔍</div><div class="cardtit">Búsqueda de reporte</div>'
                        '<div class="cardsub">Ingresa tu número de folio</div>', unsafe_allow_html=True)
            entrada = st.text_input("Número de folio", placeholder="Ejemplo: RB-0001 o 1")
            if st.button("Buscar reporte", type="primary"):
                digitos = re.sub(r"\D", "", entrada)
                r = next((x for x in reportes if digitos and x["id"] == int(digitos)), None)
                if not r:
                    aviso("No encontramos un reporte con ese folio.", "warn")
                else:
                    st.markdown(f"**{folio(r['id'])} · {r['titulo']}**  " + badge(r["estatus"]),
                                unsafe_allow_html=True)
                    st.caption(f"{r['categorias']['nombre']} · {r['direccion']}")
                    st.write("**Seguimiento**")
                    historial(r["id"])

    st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)
    m = st.columns(4)
    m[0].metric("Total de reportes", len(reportes))
    for col, e in zip(m[1:], ESTATUS):
        col.metric(ETIQ[e], sum(r["estatus"] == e for r in reportes))
    st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)
    izq, der = st.columns(2)
    with izq:
        with st.container(border=True):
            st.subheader("Reportes por categoría")
            if reportes:
                grafica_categorias(reportes)
            else:
                aviso("Aún no hay reportes.")
    with der:
        with st.container(border=True):
            st.subheader("Mapa de reportes")
            mapa(reportes)

# ---------- REPORTES (Supabase) ----------
elif pagina == "Reportes":
    titulo("Administración", "Reportes registrados", "Datos estructurados guardados en Supabase")
    filtro = st.multiselect("Filtrar por estatus", ESTATUS, default=ESTATUS, format_func=ETIQ.get)
    for r in [x for x in reportes if x["estatus"] in filtro]:
        with st.container(border=True):
            a, b = st.columns([4, 1])
            a.markdown(f"**{folio(r['id'])} · {r['titulo']}**")
            b.markdown(badge(r["estatus"]), unsafe_allow_html=True)
            st.caption(f"{r['categorias']['nombre']} · {r['direccion']} · Reportó: {r['usuarios']['nombre']}")
            if r.get("descripcion"):
                st.write(r["descripcion"])
            c1, c2, c3 = st.columns([2, 1, 1])
            nuevo = c1.selectbox("Estatus", ESTATUS, index=ESTATUS.index(r["estatus"]), key=f"s{r['id']}",
                                 format_func=ETIQ.get, label_visibility="collapsed")
            if c2.button("Actualizar", key=f"u{r['id']}"):
                db.actualizar_estatus(r["id"], nuevo)
                st.rerun()
            if c3.button("Eliminar", key=f"d{r['id']}"):
                db.eliminar_reporte(r["id"])
                st.rerun()
    if not reportes:
        aviso("Aún no hay reportes.")

# ---------- COMENTARIOS (MongoDB) ----------
elif pagina == "Comentarios":
    titulo("Seguimiento", "Comentarios", "Datos flexibles guardados en MongoDB Atlas")
    if not reportes:
        aviso("Primero crea un reporte.")
    else:
        rep = st.selectbox("Reporte", reportes, format_func=fmt)
        for c in db.listar_comentarios(rep["id"]):
            with st.container(border=True):
                st.markdown(f"💬 **{c['autor']}** · {c['fecha']:%d/%m/%Y %H:%M}")
                if c.get("etiquetas"):
                    st.caption(" ".join(f"`{e}`" for e in c["etiquetas"]))
                texto = st.text_input("Comentario", c["texto"], key=f"t{c['_id']}", label_visibility="collapsed")
                b1, b2, _ = st.columns([1, 1, 4])
                if b1.button("Guardar", key=f"g{c['_id']}"):
                    db.editar_comentario(c["_id"], texto)
                    st.rerun()
                if b2.button("Borrar", key=f"b{c['_id']}"):
                    db.eliminar_comentario(c["_id"])
                    st.rerun()
        with st.expander("➕ Agregar comentario"):
            with st.form("nuevo_com", clear_on_submit=True):
                autor = st.text_input("Autor")
                texto = st.text_area("Comentario")
                etiquetas = st.text_input("Etiquetas (separadas por coma)")
                publicar = st.form_submit_button("Publicar", type="primary")
            if publicar and autor and texto:
                db.agregar_comentario(rep["id"], autor, texto,
                                      [e.strip() for e in etiquetas.split(",") if e.strip()])
                st.rerun()

# ---------- VISTA COMBINADA ----------
else:
    titulo("Integración", "Vista combinada", "Un mismo reporte con datos de las dos bases")
    if not reportes:
        aviso("Aún no hay reportes.")
    else:
        rep = st.selectbox("Reporte", reportes, format_func=fmt)
        izq, der = st.columns(2)
        with izq:
            with st.container(border=True):
                st.markdown("### 🗄️ Supabase (SQL)")
                st.caption("Tablas: reportes, usuarios, categorias")
                st.markdown(badge(rep["estatus"]), unsafe_allow_html=True)
                st.write(f"**{rep['titulo']}**")
                st.write(f"Categoría: {rep['categorias']['nombre']} ({rep['categorias']['dependencia']})")
                st.write(f"Reportó: {rep['usuarios']['nombre']}")
                st.write(f"Dirección: {rep['direccion']}")
        with der:
            with st.container(border=True):
                st.markdown("### 🍃 MongoDB (NoSQL)")
                st.caption("Colecciones: seguimiento, comentarios")
                st.write("**Historial de seguimiento**")
                historial(rep["id"])
                st.write("**Comentarios**")
                for c in db.listar_comentarios(rep["id"]):
                    st.write(f"💬 {c['autor']}: {c['texto']}")