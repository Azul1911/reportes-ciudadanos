import glob
import re
from datetime import datetime, timezone
from html import escape
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
input:disabled {color:#5B6B80 !important; -webkit-text-fill-color:#5B6B80 !important;}
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
    background:#0B6FA8 !important; border:1.5px solid #0B2F6B !important;}
button[kind="primary"] p, button[data-testid="stBaseButton-primary"] p,
button[data-testid="stBaseButton-primaryFormSubmit"] p {color:#FFFFFF !important;}

/* ---------- Barra superior y franja del logo ---------- */
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
.st-key-navband button[data-testid="stBaseButton-primary"] p,
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

/* ---------- Muro tipo red social ---------- */
.post-head {display:flex; align-items:center; gap:.7rem; margin-bottom:.4rem;}
.post-head .quien {flex:1; min-width:0;}
.post-head .autor {font-weight:700; color:#0B2F6B; line-height:1.2;}
.post-head .meta {font-size:.8rem; color:#5B6B80;}
.avatar {width:42px; height:42px; border-radius:50%; flex:0 0 auto; display:flex; align-items:center;
         justify-content:center; color:#FFFFFF; font-weight:800;
         background:linear-gradient(135deg,#0B3C7A,#0A9BD3);}
.avatar.sm {width:30px; height:30px; font-size:.8rem;}
.post-titulo {font-size:1.15rem; font-weight:800; color:#0B2F6B; margin:.3rem 0 .1rem;}
.post-texto {color:#1B2430; margin-bottom:.6rem; line-height:1.45; word-wrap:break-word;}
.stApp .chip {display:inline-block; background:#EAF3FF; color:#123F7A; border-radius:999px;
              padding:.15rem .7rem; font-size:.78rem; font-weight:700; margin:0 .3rem .2rem 0;}
.com-tit {font-weight:700; color:#0B2F6B; margin:.7rem 0 .2rem; border-top:1px solid #E3EAF3; padding-top:.6rem;}
.com {display:flex; gap:.5rem; margin:.45rem 0 .1rem;}
.burbuja {background:#F1F5FA; border-radius:14px; padding:.5rem .8rem; flex:1; min-width:0;
          word-wrap:break-word; color:#1B2430;}
.burbuja b {color:#0B2F6B;}
.stApp .tiempo {font-size:.74rem; color:#8A98AD;}
.stApp .tag {color:#0B6FA8; font-weight:600; margin-right:.4rem; font-size:.85rem;}

/* ---------- Responsivo: tablet ---------- */
@media (max-width: 900px) {
  .block-container {padding:0 .9rem 2rem;}
  .ttl h1 {font-size:2rem;}
  .ttl .marca {font-size:3.2rem; top:-1rem;}
  .st-key-navband .stButton > button p {font-size:.68rem;}
}
/* ---------- Responsivo: celular ---------- */
@media (max-width: 640px) {
  .block-container {padding:0 .6rem 2rem;}
  .topbar {flex-direction:column; align-items:flex-start; gap:.25rem; padding:.7rem 1rem;}
  .topbar span {font-size:.82rem;}
  .ttl {margin:1.4rem 0 1rem;}
  .ttl h1 {font-size:1.6rem;}
  .ttl .marca {display:none;}
  .ttl p {font-size:.92rem;}
  .st-key-navband {padding:.5rem .6rem;}
  .st-key-navband [data-testid="stHorizontalBlock"] {flex-wrap:wrap !important; gap:.3rem !important;}
  .st-key-navband [data-testid="stColumn"] {flex:1 1 calc(50% - .4rem) !important;
      min-width:calc(50% - .4rem) !important; width:auto !important;}
  .st-key-navband [data-testid="stColumn"]:first-child {flex:1 1 100% !important;
      min-width:100% !important; text-align:center;}
  .st-key-navband [data-testid="stColumn"]:first-child img {margin:0 auto;}
  .st-key-metricas [data-testid="stHorizontalBlock"] {flex-wrap:wrap !important; gap:.5rem !important;}
  .st-key-metricas [data-testid="stColumn"] {flex:1 1 calc(50% - .5rem) !important;
      min-width:calc(50% - .5rem) !important;}
  div[data-testid="stMetric"] {padding:.6rem .8rem;}
  .circ {width:64px; height:64px; font-size:1.5rem; margin-top:-2.8rem;}
  .cardtit {font-size:1.25rem;}
  .post-titulo {font-size:1.05rem;}
}
</style>
""", unsafe_allow_html=True)

ESTATUS = list(db.ESTATUS)
ETIQ = {"recibido": "Recibido", "en_revision": "En revisión", "resuelto": "Resuelto"}
COLORES = {"recibido": ("#FEF3C7", "#92400E"), "en_revision": ("#DBEAFE", "#1E40AF"),
           "resuelto": ("#DCFCE7", "#166534")}
AVISOS = {"info": ("#EAF3FF", "#9CC4F0", "#123F7A"), "warn": ("#FFF4D6", "#F2C94C", "#6B4B00"),
          "ok": ("#E3F7EA", "#86D3A0", "#14532D")}
folio = lambda i: f"RB-{i:04d}"


def aviso(texto, tipo="info"):
    bg, borde, fg = AVISOS[tipo]
    st.markdown(f'<div class="aviso" style="background:{bg};border-color:{borde};color:{fg}">'
                f'{escape(str(texto))}</div>', unsafe_allow_html=True)


def flash(texto, tipo="ok"):
    st.session_state["flash"] = (texto, tipo)


def ejecutar(fn, mensaje, *args):
    """Ejecuta una operación con permisos y deja un aviso para la siguiente pantalla."""
    try:
        fn(*args)
        flash(mensaje, "ok")
    except db.ErrorApp as e:
        flash(str(e), "warn")
    st.rerun()


def badge(e):
    bg, fg = COLORES[e]
    return f'<span class="badge" style="background:{bg};color:{fg}">{ETIQ[e]}</span>'


def titulo(arriba, grande, sub):
    st.markdown(f'<div class="ttl"><div class="marca">{arriba}</div><small>{arriba}</small>'
                f'<h1>{grande}</h1><p>{sub}</p></div>', unsafe_allow_html=True)


def texto_html(texto):
    return escape(texto or "").replace("\n", "<br>")


def hace(valor):
    """'hace 5 min', 'hace 2 h'... a partir de un texto ISO o un datetime."""
    try:
        if isinstance(valor, str):
            f = datetime.fromisoformat(valor.replace("Z", "+00:00"))
        else:
            f = valor
        if f.tzinfo is None:
            f = f.replace(tzinfo=timezone.utc)
        s = (datetime.now(timezone.utc) - f).total_seconds()
    except Exception:
        return ""
    if s < 60:
        return "hace un momento"
    if s < 3600:
        return f"hace {int(s // 60)} min"
    if s < 86400:
        return f"hace {int(s // 3600)} h"
    if s < 604800:
        return f"hace {int(s // 86400)} d"
    return f.strftime("%d/%m/%Y")


def historial(reporte_id):
    for h in db.obtener_seguimiento(reporte_id):
        quien = f" · por {escape(h['responsable'])}" if h.get("responsable") else ""
        st.markdown(f"<div class='tl'><b>{ETIQ.get(h['estatus'], h['estatus'])}</b> · "
                    f"{h['fecha']:%d/%m/%Y %H:%M}{quien}<br>{escape(h.get('nota', ''))}</div>",
                    unsafe_allow_html=True)


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


def numero(texto):
    texto = (texto or "").strip()
    if not texto:
        return None
    try:
        return float(texto)
    except ValueError:
        raise db.ErrorApp("La latitud y la longitud deben ser números.")


# ---------- Sesión y barra superior ----------
usuario = st.session_state.get("usuario")
es_admin = bool(usuario and usuario.get("rol") == "admin")


def requiere_sesion():
    if not usuario:
        aviso("Inicia sesión para usar esta sección.", "warn")
        st.stop()


def burbuja(c):
    ini = escape((c.get("autor") or "?")[:1].upper())
    tags = "".join(f'<span class="tag">#{escape(e)}</span>' for e in c.get("etiquetas", []))
    st.markdown(f'<div class="com"><div class="avatar sm">{ini}</div><div class="burbuja">'
                f'<b>{escape(c.get("autor") or "")}</b> <span class="tiempo">{hace(c.get("fecha"))}</span>'
                f'<div>{texto_html(c["texto"])}</div>{tags}</div></div>', unsafe_allow_html=True)


def tarjeta(r, comentarios):
    """Una publicación del muro: el reporte arriba y sus comentarios abajo."""
    dueno = r["usuario_id"] == usuario["id"]
    autor = r["usuarios"]["nombre"]
    with st.container(border=True):
        st.markdown(
            f'<div class="post-head"><div class="avatar">{escape(autor[:1].upper())}</div>'
            f'<div class="quien"><div class="autor">{escape(autor)}{" · tú" if dueno else ""}</div>'
            f'<div class="meta">{hace(r.get("creado_en"))} · 📍 {escape(r["direccion"])}</div></div></div>'
            f'<div class="post-titulo">{escape(r["titulo"])}</div>'
            f'<div class="post-texto">{texto_html(r.get("descripcion"))}</div>'
            f'<div><span class="chip">{escape(r["categorias"]["nombre"])}</span>'
            f'<span class="chip">{escape(r["categorias"]["dependencia"])}</span>'
            f'<span class="chip">{folio(r["id"])}</span> {badge(r["estatus"])}</div>',
            unsafe_allow_html=True)

        st.markdown(f'<div class="com-tit">💬 {len(comentarios)} comentario(s)</div>', unsafe_allow_html=True)
        for c in comentarios:
            burbuja(c)
            if c.get("autor_id") == usuario["id"]:
                with st.popover("⋯ Mi comentario"):
                    nuevo = st.text_input("Editar", c["texto"], key=f"t{c['_id']}")
                    b1, b2 = st.columns(2)
                    if b1.button("Guardar", key=f"g{c['_id']}"):
                        ejecutar(db.editar_comentario, "Comentario actualizado.", usuario["id"], c["_id"], nuevo)
                    if b2.button("Borrar", key=f"b{c['_id']}"):
                        ejecutar(db.eliminar_comentario, "Comentario borrado.", usuario["id"], c["_id"])
            elif es_admin:
                with st.popover("⋯ Moderar"):
                    if st.button("Borrar comentario", key=f"m{c['_id']}"):
                        ejecutar(db.eliminar_comentario, "Comentario borrado.", usuario["id"], c["_id"])

        with st.form(f"cm{r['id']}", clear_on_submit=True):
            a, b = st.columns([5, 1], vertical_alignment="bottom")
            texto = a.text_input("Comentario", placeholder="Escribe un comentario… usa #etiquetas",
                                 label_visibility="collapsed")
            enviar = b.form_submit_button("Comentar", type="primary")
        if enviar:
            ejecutar(db.agregar_comentario, "Comentario publicado.", usuario["id"], r["id"], texto,
                     re.findall(r"#(\w{1,30})", texto))

        if dueno or es_admin:
            with st.popover("⚙️ Administrar publicación"):
                if es_admin:
                    nuevo_est = st.selectbox("Estatus", ESTATUS, index=ESTATUS.index(r["estatus"]),
                                             key=f"s{r['id']}", format_func=ETIQ.get)
                    if st.button("Actualizar estatus", key=f"u{r['id']}"):
                        ejecutar(db.cambiar_estatus, "Estatus actualizado.", usuario["id"], r["id"], nuevo_est)
                if dueno:
                    with st.form(f"ed{r['id']}"):
                        et = st.text_input("Título", r["titulo"])
                        ed = st.text_area("Descripción", r.get("descripcion") or "")
                        edi = st.text_input("Dirección", r["direccion"])
                        guardar = st.form_submit_button("Guardar cambios", type="primary")
                    if guardar:
                        ejecutar(db.editar_reporte, "Reporte actualizado.", usuario["id"], r["id"], et, ed, edi)
                ok = st.checkbox("Confirmo que quiero eliminar este reporte", key=f"dc{r['id']}")
                if st.button("Eliminar reporte", key=f"d{r['id']}", disabled=not ok):
                    ejecutar(db.eliminar_reporte, "Reporte eliminado.", usuario["id"], r["id"])


derecha = (f"👤 {escape(usuario['nombre'])}" + (" · Admin" if es_admin else "")) if usuario \
    else "🗄️ Supabase + 🍃 MongoDB Atlas"
st.markdown(f'<div class="topbar"><span>📍 Ciudad Juárez, Chihuahua</span>'
            f'<span>Reporta · Transforma · Mejora</span><span>{derecha}</span></div>',
            unsafe_allow_html=True)

reportes = db.listar_reportes()
fmt = lambda r: f"{folio(r['id'])} · {r['titulo']}"

# ---------- Menú según la sesión ----------
if usuario:
    MENU = [("Muro", 0.9), ("Nuevo reporte", 1.35), ("Consulta", 1.05),
            ("Vista combinada", 1.55), ("Mi perfil", 1.05)]
else:
    MENU = [("Consulta", 1.0), ("Iniciar sesión", 1.4), ("Crear cuenta", 1.3)]
nombres = [n for n, _ in MENU] + ["Iniciar sesión", "Crear cuenta"]
if st.session_state.get("pagina") not in nombres:
    st.session_state.pagina = "Muro" if usuario else "Iniciar sesión"

with st.container(key="navband"):
    pesos = [2.0 if usuario else 4.0] + [w for _, w in MENU] + ([0.8] if usuario else [])
    cols = st.columns(pesos, vertical_alignment="center")
    with cols[0]:
        logo = buscar_logo()
        if logo:
            st.image(logo, width=190)
        else:
            st.markdown("### ReportaBaches")
    for col, (nombre, _) in zip(cols[1:], MENU):
        activo = st.session_state.pagina == nombre
        if col.button(nombre, key=f"nav_{nombre}", type="primary" if activo else "secondary"):
            st.session_state.pagina = nombre
            st.rerun()
    if usuario and cols[-1].button("Salir", key="nav_salir"):
        st.session_state.pop("usuario", None)
        st.session_state.pagina = "Iniciar sesión"
        flash("Cerraste sesión.", "info")
        st.rerun()
pagina = st.session_state.pagina

if "flash" in st.session_state:
    _texto, _tipo = st.session_state.pop("flash")
    aviso(_texto, _tipo)

# ---------- INICIAR SESIÓN ----------
if pagina == "Iniciar sesión":
    titulo("Acceso", "Iniciar sesión", "Entra con tu cuenta para levantar y dar seguimiento a tus reportes")
    st.markdown("<div style='height:2.4rem'></div>", unsafe_allow_html=True)
    _, centro, _ = st.columns([1, 2, 1])
    with centro:
        with st.container(border=True):
            st.markdown('<div class="circ">👤</div><div class="cardtit">Bienvenida/o</div>'
                        '<div class="cardsub">Ingresa tu correo y contraseña</div>', unsafe_allow_html=True)
            with st.form("login"):
                correo = st.text_input("Correo", placeholder="tu@correo.com")
                pwd = st.text_input("Contraseña", type="password")
                entrar = st.form_submit_button("Entrar", type="primary")
            if entrar:
                try:
                    st.session_state.usuario = db.iniciar_sesion(correo, pwd)
                    st.session_state.pagina = "Muro"
                    st.rerun()
                except db.ErrorApp as e:
                    aviso(str(e), "warn")
            st.caption("¿Aún no tienes cuenta?")
            if st.button("Crear cuenta nueva"):
                st.session_state.pagina = "Crear cuenta"
                st.rerun()

# ---------- CREAR CUENTA ----------
elif pagina == "Crear cuenta":
    titulo("Registro", "Crear cuenta", "Regístrate para levantar reportes y comentar")
    st.markdown("<div style='height:2.4rem'></div>", unsafe_allow_html=True)
    _, centro, _ = st.columns([1, 2, 1])
    with centro:
        with st.container(border=True):
            st.markdown('<div class="circ">✨</div><div class="cardtit">Nueva cuenta</div>'
                        '<div class="cardsub">Solo tú podrás modificar tus reportes</div>', unsafe_allow_html=True)
            with st.form("registro"):
                nom = st.text_input("Nombre completo")
                cor = st.text_input("Correo", placeholder="tu@correo.com")
                tel = st.text_input("Teléfono (opcional)")
                p1 = st.text_input("Contraseña (mínimo 8 caracteres)", type="password")
                p2 = st.text_input("Confirma tu contraseña", type="password")
                crear = st.form_submit_button("Crear cuenta", type="primary")
            if crear:
                if p1 != p2:
                    aviso("Las contraseñas no coinciden.", "warn")
                else:
                    try:
                        st.session_state.usuario = db.registrar(nom, cor, tel, p1)
                        st.session_state.pagina = "Muro"
                        flash("Cuenta creada. ¡Bienvenida/o!", "ok")
                        st.rerun()
                    except db.ErrorApp as e:
                        aviso(str(e), "warn")
            st.caption("¿Ya tienes cuenta?")
            if st.button("Iniciar sesión"):
                st.session_state.pagina = "Iniciar sesión"
                st.rerun()

# ---------- MURO (feed de reportes y comentarios) ----------
elif pagina == "Muro":
    requiere_sesion()
    titulo("Comunidad", "Muro de reportes",
           "Lo que reporta la gente de Ciudad Juárez · solo tú puedes modificar lo tuyo")
    _, centro, _ = st.columns([1, 3, 1])
    with centro:
        f1, f2 = st.columns(2, vertical_alignment="bottom")
        ver = f1.radio("Ver", ["Todos", "Mis reportes"], horizontal=True)
        est = f2.selectbox("Estatus", ["Todos"] + ESTATUS,
                           format_func=lambda e: "Todos" if e == "Todos" else ETIQ[e])
        lista = sorted([x for x in reportes
                        if (est == "Todos" or x["estatus"] == est)
                        and (ver == "Todos" or x["usuario_id"] == usuario["id"])],
                       key=lambda x: x["id"], reverse=True)
        if not lista:
            aviso("No hay reportes con esos filtros.")
        limite = st.session_state.get("limite", 10)
        visibles = lista[:limite]
        coms = db.comentarios_por_reporte([r["id"] for r in visibles])
        for r in visibles:
            tarjeta(r, coms.get(r["id"], []))
        if len(lista) > limite and st.button("Ver más reportes"):
            st.session_state.limite = limite + 10
            st.rerun()

# ---------- CONSULTA (pública) ----------
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
                digitos = re.sub(r"\D", "", entrada)[:9]
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
    with st.container(key="metricas"):
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
            with st.spinner("Ubicando reportes en el mapa…"):
                if db.completar_coordenadas():
                    reportes = db.listar_reportes()
            mapa(reportes)

# ---------- NUEVO REPORTE ----------
elif pagina == "Nuevo reporte":
    requiere_sesion()
    titulo("Ciudadanía", "Levanta un reporte", "Cuéntanos qué problema hay en tu colonia")
    _, centro, _ = st.columns([1, 3, 1])
    with centro:
        with st.form("nuevo_reporte", clear_on_submit=True):
            categoria = st.selectbox("Categoría", db.listar_categorias(), format_func=lambda c: c["nombre"])
            t = st.text_input("Título")
            d = st.text_area("Descripción")
            dire = st.text_input("Dirección", placeholder="Calle y número, colonia · Ej. Av. de las Torres 1234, Col. Partido Romero")
            enviar = st.form_submit_button("Publicar reporte", type="primary")
        if enviar:
            try:
                with st.spinner("Ubicando la dirección en el mapa…"):
                    nuevo = db.crear_reporte(usuario["id"], categoria["id"], t, d, dire)
                if nuevo.get("latitud") is None:
                    aviso(f"Reporte publicado (folio {folio(nuevo['id'])}), pero no pudimos ubicar la dirección en el mapa. "
                          "Prueba a editarla con calle, número y colonia.", "warn")
                else:
                    aviso(f"Reporte publicado. Tu folio es {folio(nuevo['id'])}. Ya aparece en el muro y en el mapa.", "ok")
            except db.ErrorApp as e:
                aviso(str(e), "warn")

# ---------- VISTA COMBINADA ----------
elif pagina == "Vista combinada":
    requiere_sesion()
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

# ---------- MI PERFIL ----------
else:
    requiere_sesion()
    titulo("Cuenta", "Mi perfil", "Solo tú puedes modificar estos datos")
    _, centro, _ = st.columns([1, 2, 1])
    with centro:
        with st.container(border=True):
            st.caption(f"ID {usuario['id']} · " + ("Administrador" if es_admin else "Ciudadano"))
            with st.form("perfil"):
                nom = st.text_input("Nombre", usuario["nombre"])
                st.text_input("Correo", usuario["correo"], disabled=True)
                tel = st.text_input("Teléfono", usuario.get("telefono") or "")
                guardar = st.form_submit_button("Guardar cambios", type="primary")
            if guardar:
                try:
                    st.session_state.usuario = db.actualizar_perfil(usuario["id"], nom, tel)
                    flash("Perfil actualizado.", "ok")
                except db.ErrorApp as e:
                    flash(str(e), "warn")
                st.rerun()
        with st.expander("🗑️ Eliminar mi cuenta"):
            aviso("Se borrarán tu cuenta, tus reportes y tus comentarios. No se puede deshacer.", "warn")
            pwd = st.text_input("Confirma tu contraseña", type="password", key="pwd_del")
            ok = st.checkbox("Entiendo que es definitivo", key="ok_del")
            if st.button("Eliminar mi cuenta definitivamente", disabled=not ok):
                try:
                    db.eliminar_cuenta(usuario["id"], pwd)
                    st.session_state.pop("usuario", None)
                    st.session_state.pagina = "Iniciar sesión"
                    flash("Tu cuenta fue eliminada.", "ok")
                except db.ErrorApp as e:
                    flash(str(e), "warn")
                st.rerun()
