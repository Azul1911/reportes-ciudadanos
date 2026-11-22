import glob
import re
import pandas as pd
import streamlit as st
import db

st.set_page_config(page_title="ReportaBaches Ciudad Juárez", page_icon="📍", layout="wide")

st.markdown("""
<style>
:root {color-scheme: light;}
.stApp {background:#FFFFFF;}
header[data-testid="stHeader"] {display:none;}
.block-container {padding-top:0; max-width:1150px;}

/* Texto siempre oscuro y legible */
.stApp p, .stApp li, .stApp label, .stApp span, .stApp div[data-testid="stMarkdownContainer"],
.stApp [data-testid="stCaptionContainer"], .stApp h1, .stApp h2, .stApp h3, .stApp h4 {color:#1B2430;}
.stApp [data-testid="stCaptionContainer"] {color:#5B6B80;}
.stApp h2, .stApp h3, .stApp h4 {color:#0B2F6B;}
input, textarea, [data-baseweb="select"] > div, [data-baseweb="input"] > div {
    background:#FFFFFF !important; color:#1B2430 !important; border-color:#B9C7DA !important;}
[data-baseweb="select"] span, [data-baseweb="select"] div {color:#1B2430 !important;}
.stButton > button {background:#FFFFFF; color:#0B2F6B; border:1.5px solid #0B2F6B; border-radius:10px; font-weight:700;}
.stButton > button:hover {background:#E8F1FB; color:#0B2F6B; border-color:#0B2F6B;}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
    background:#0B2F6B; color:#FFFFFF !important; border:none;}
.stButton > button[kind="primary"] p, .stFormSubmitButton > button p {color:#FFFFFF !important;}

/* Barra superior */
.topbar {background:#123F7A; padding:.8rem 1.5rem; font-size:.92rem;
         display:flex; justify-content:space-between; gap:1rem; flex-wrap:wrap;}
.topbar span {color:#FFFFFF !important; font-weight:500;}

/* Franja con logo y menú */
.st-key-navband {background:#DCEBFB; padding:.7rem 1.5rem; margin:0 -1rem 0;}
.st-key-navband div[role="radiogroup"] {gap:.2rem; justify-content:flex-end; flex-wrap:wrap;}
.st-key-navband div[role="radiogroup"] label {padding:.5rem .95rem; border-radius:8px; cursor:pointer;}
.st-key-navband div[role="radiogroup"] label > div:first-child {display:none;}
.st-key-navband div[role="radiogroup"] label p {font-weight:700; color:#123F7A !important;
    font-size:.88rem; text-transform:uppercase; letter-spacing:.02em;}
.st-key-navband div[role="radiogroup"] label:has(input:checked) {background:#123F7A;}
.st-key-navband div[role="radiogroup"] label:has(input:checked) p {color:#FFFFFF !important;}

/* Títulos de sección */
.ttl {text-align:center; margin:2.4rem 0 1.6rem; position:relative;}
.ttl .marca {position:absolute; left:0; right:0; top:-1.4rem; font-size:5.5rem; font-weight:800;
             color:#EAF1F9; line-height:1; z-index:0; user-select:none;}
.ttl small, .ttl h1, .ttl p {position:relative; z-index:1;}
.ttl small {color:#0B2F6B !important; font-weight:700; letter-spacing:.12em; text-transform:uppercase;}
.ttl h1 {color:#0B2F6B !important; font-size:2.7rem; font-weight:800; margin:.3rem 0; padding:0;}
.ttl p {color:#5B6B80 !important; margin:0; font-size:1.02rem;}

/* Tarjetas */
div[data-testid="stVerticalBlockBorderWrapper"] {background:#FFFFFF; border:1px solid #E3EAF3;
    border-top:4px solid #0B6FA8; border-radius:14px; box-shadow:0 6px 18px rgba(18,63,122,.10);}
.circ {width:78px; height:78px; border-radius:50%; margin:-3rem auto .6rem; font-size:2rem;
       background:linear-gradient(135deg,#0B3C7A,#0A9BD3); display:flex; align-items:center;
       justify-content:center; box-shadow:0 6px 14px rgba(10,111,168,.35);}
.cardtit {text-align:center; color:#0B2F6B !important; font-size:1.5rem; font-weight:800; margin:.2rem 0;}
.cardsub {text-align:center; color:#5B6B80 !important; margin-bottom:1rem;}
div[data-testid="stMetric"] {background:#FFFFFF; border-radius:14px; border-top:4px solid #0B6FA8;
    padding:.9rem 1rem; box-shadow:0 6px 18px rgba(18,63,122,.10);}
div[data-testid="stMetricLabel"] p {color:#5B6B80 !important; font-weight:600;}
div[data-testid="stMetricValue"] {color:#0B2F6B !important; font-weight:800;}

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
folio = lambda i: f"RB-{i:04d}"

def badge(e):
    bg, fg = COLORES[e]
    return f'<span class="badge" style="background:{bg};color:{fg}">{ETIQ[e]}</span>'

def titulo(arriba, grande, sub, marca=""):
    st.markdown(f'<div class="ttl"><div class="marca">{marca or grande}</div><small>{arriba}</small>'
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

reportes = db.listar_reportes()
fmt = lambda r: f"{folio(r['id'])} · {r['titulo']}"

# ---------- Encabezado: logo en la esquina + menú ----------
with st.container(key="navband"):
    c1, c2 = st.columns([1, 3], vertical_alignment="center")
    with c1:
        logo = buscar_logo()
        if logo:
            st.image(logo, width=210)
        else:
            st.markdown("### ReportaBaches")
    with c2:
        pagina = st.radio("Menú", ["Inicio", "Nuevo reporte", "Reportes", "Comentarios", "Vista combinada"],
                          horizontal=True, label_visibility="collapsed", key="nav")

# ---------- INICIO ----------
if pagina == "Inicio":
    titulo("Reportes", "Consulta de reportes",
           "Ingresa tu número de folio para consultar el estatus de tu reporte")
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
                    st.warning("No encontramos un reporte con ese folio.")
                else:
                    st.markdown(f"**{folio(r['id'])} · {r['titulo']}**  " + badge(r["estatus"]),
                                unsafe_allow_html=True)
                    st.caption(f"{r['categorias']['nombre']} · {r['direccion']}")
                    st.write("**Seguimiento**")
                    historial(r["id"])

    st.markdown("&nbsp;")
    cols = st.columns(4)
    cols[0].metric("Total de reportes", len(reportes))
    for col, e in zip(cols[1:], ESTATUS):
        col.metric(ETIQ[e], sum(r["estatus"] == e for r in reportes))
    st.markdown("&nbsp;")
    izq, der = st.columns(2)
    with izq:
        with st.container(border=True):
            st.subheader("Reportes por categoría")
            if reportes:
                st.bar_chart(pd.Series([r["categorias"]["nombre"] for r in reportes]).value_counts())
    with der:
        with st.container(border=True):
            st.subheader("Mapa de reportes")
            pts = [{"latitude": float(r["latitud"]), "longitude": float(r["longitud"])}
                   for r in reportes if r.get("latitud") is not None and r.get("longitud") is not None]
            if pts:
                st.map(pd.DataFrame(pts))
            else:
                st.info("Los reportes aún no tienen coordenadas.")

# ---------- NUEVO REPORTE ----------
elif pagina == "Nuevo reporte":
    titulo("Ciudadanía", "Levanta un reporte", "Cuéntanos qué problema hay en tu colonia", "Nuevo")
    _, centro, _ = st.columns([1, 3, 1])
    with centro:
        with st.container(border=True):
            with st.form("nuevo_reporte", clear_on_submit=True):
                a, b = st.columns(2)
                usuario = a.selectbox("Usuario", db.listar_usuarios(), format_func=lambda u: u["nombre"])
                categoria = b.selectbox("Categoría", db.listar_categorias(), format_func=lambda c: c["nombre"])
                t = st.text_input("Título")
                d = st.text_area("Descripción")
                dire = st.text_input("Dirección")
                if st.form_submit_button("Enviar reporte", type="primary"):
                    if t and dire:
                        nuevo = db.crear_reporte({"usuario_id": usuario["id"], "categoria_id": categoria["id"],
                                                  "titulo": t, "descripcion": d, "direccion": dire})
                        st.success(f"Reporte registrado. Tu folio es {folio(nuevo['id'])}")
                    else:
                        st.warning("Título y dirección son obligatorios.")

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
        st.info("Aún no hay reportes.")

# ---------- COMENTARIOS (MongoDB) ----------
elif pagina == "Comentarios":
    titulo("Seguimiento", "Comentarios", "Datos flexibles guardados en MongoDB Atlas")
    if not reportes:
        st.info("Primero crea un reporte.")
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
                if st.form_submit_button("Publicar", type="primary") and autor and texto:
                    db.agregar_comentario(rep["id"], autor, texto,
                                          [e.strip() for e in etiquetas.split(",") if e.strip()])
                    st.rerun()

# ---------- VISTA COMBINADA ----------
else:
    titulo("Integración", "Vista combinada", "Un mismo reporte con datos de las dos bases")
    if not reportes:
        st.info("Aún no hay reportes.")
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