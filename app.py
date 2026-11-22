import pandas as pd
import streamlit as st
import db

st.set_page_config(page_title="Reportes Ciudadanos", page_icon="📍", layout="wide")
st.title(" Reportes Ciudadanos de Ciudad Juárez")
ESTATUS = ["recibido", "en_revision", "resuelto"]

reportes = db.listar_reportes()
fmt = lambda r: f"#{r['id']} - {r['titulo']}"
tab1, tab2, tab3 = st.tabs(["Reportes (Supabase)", "Comentarios (MongoDB)", "Vista combinada"])

# ---------- TAB 1: CRUD en Supabase ----------
with tab1:
    st.subheader("Nuevo reporte")
    with st.form("nuevo_reporte", clear_on_submit=True):
        usuario = st.selectbox("Usuario", db.listar_usuarios(), format_func=lambda u: u["nombre"])
        categoria = st.selectbox("Categoría", db.listar_categorias(), format_func=lambda c: c["nombre"])
        titulo = st.text_input("Título")
        descripcion = st.text_area("Descripción")
        direccion = st.text_input("Dirección")
        if st.form_submit_button("Guardar reporte"):
            if titulo and direccion:
                db.crear_reporte({"usuario_id": usuario["id"], "categoria_id": categoria["id"],
                                  "titulo": titulo, "descripcion": descripcion, "direccion": direccion})
                st.success("Reporte guardado en Supabase y su historial abierto en MongoDB.")
                st.rerun()
            else:
                st.warning("Título y dirección son obligatorios.")

    st.subheader("Reportes registrados")
    if reportes:
        st.dataframe(pd.DataFrame([{
            "id": r["id"], "título": r["titulo"], "categoría": r["categorias"]["nombre"],
            "usuario": r["usuarios"]["nombre"], "dirección": r["direccion"], "estatus": r["estatus"],
        } for r in reportes]), use_container_width=True, hide_index=True)

        sel = st.selectbox("Reporte a modificar", reportes, format_func=fmt, key="sel_mod")
        c1, c2 = st.columns(2)
        nuevo = c1.selectbox("Nuevo estatus", ESTATUS, index=ESTATUS.index(sel["estatus"]))
        if c1.button("Actualizar estatus"):
            db.actualizar_estatus(sel["id"], nuevo)
            st.rerun()
        if c2.button("Eliminar reporte"):
            db.eliminar_reporte(sel["id"])
            st.rerun()
    else:
        st.info("Aún no hay reportes.")

# ---------- TAB 2: CRUD en MongoDB ----------
with tab2:
    if not reportes:
        st.info("Primero crea un reporte.")
    else:
        rep = st.selectbox("Reporte", reportes, format_func=fmt, key="sel_com")
        for c in db.listar_comentarios(rep["id"]):
            st.markdown(f"**{c['autor']}** · {', '.join(c.get('etiquetas', []))}")
            a, b, d = st.columns([5, 1, 1])
            texto = a.text_input("Comentario", c["texto"], key=f"t{c['_id']}", label_visibility="collapsed")
            if b.button("Guardar", key=f"g{c['_id']}"):
                db.editar_comentario(c["_id"], texto)
                st.rerun()
            if d.button("Borrar", key=f"b{c['_id']}"):
                db.eliminar_comentario(c["_id"])
                st.rerun()

        st.subheader("Agregar comentario")
        with st.form("nuevo_com", clear_on_submit=True):
            autor = st.text_input("Autor")
            texto = st.text_area("Comentario")
            etiquetas = st.text_input("Etiquetas (separadas por coma)")
            if st.form_submit_button("Publicar") and autor and texto:
                db.agregar_comentario(rep["id"], autor, texto,
                                      [e.strip() for e in etiquetas.split(",") if e.strip()])
                st.rerun()

# ---------- TAB 3: Vista que une ambas bases ----------
with tab3:
    if reportes:
        rep = st.selectbox("Reporte", reportes, format_func=fmt, key="sel_comb")
        izq, der = st.columns(2)
        with izq:
            st.markdown("### Datos de Supabase (SQL)")
            st.caption("Origen: tablas reportes, usuarios y categorias")
            st.write(f"**Título:** {rep['titulo']}")
            st.write(f"**Categoría:** {rep['categorias']['nombre']} ({rep['categorias']['dependencia']})")
            st.write(f"**Reportó:** {rep['usuarios']['nombre']}")
            st.write(f"**Dirección:** {rep['direccion']}")
            st.write(f"**Estatus actual:** {rep['estatus']}")
        with der:
            st.markdown("### Datos de MongoDB (NoSQL)")
            st.caption("Origen: colecciones seguimiento y comentarios")
            st.write("**Historial de seguimiento**")
            for h in db.obtener_seguimiento(rep["id"]):
                st.write(f"- {h['fecha']:%d/%m/%Y %H:%M} · {h['estatus']} · {h['nota']}")
            st.write("**Comentarios**")
            for c in db.listar_comentarios(rep["id"]):
                st.write(f"- {c['autor']}: {c['texto']}")