import os
from datetime import datetime, timezone
from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient
from supabase import create_client

load_dotenv()

def _secret(nombre):
    """Lee de .env (local) o de st.secrets (Streamlit Cloud)."""
    valor = os.getenv(nombre)
    if valor:
        return valor
    import streamlit as st
    return st.secrets[nombre]

sb = create_client(_secret("SUPABASE_URL"), _secret("SUPABASE_KEY"))
mongo = MongoClient(_secret("MONGO_URI"))["reportes_ciudadanos"]

def _ahora():
    return datetime.now(timezone.utc)

# ---------- SUPABASE (datos estructurados) ----------
def listar_usuarios():
    return sb.table("usuarios").select("*").order("id").execute().data

def listar_categorias():
    return sb.table("categorias").select("*").order("id").execute().data

def listar_reportes():
    return (sb.table("reportes")
            .select("*, usuarios(nombre), categorias(nombre, dependencia)")
            .order("id").execute().data)

def crear_reporte(datos):
    nuevo = sb.table("reportes").insert(datos).execute().data[0]
    # Al crear el reporte, se abre su historial en MongoDB
    mongo.seguimiento.insert_one({
        "reporte_id": nuevo["id"],
        "historial": [{"estatus": "recibido", "fecha": _ahora(), "nota": "Reporte registrado"}],
    })
    return nuevo

def actualizar_estatus(reporte_id, estatus):
    sb.table("reportes").update({"estatus": estatus}).eq("id", reporte_id).execute()
    mongo.seguimiento.update_one(
        {"reporte_id": reporte_id},
        {"$push": {"historial": {"estatus": estatus, "fecha": _ahora(), "nota": "Cambio de estatus"}}},
        upsert=True,
    )

def eliminar_reporte(reporte_id):
    sb.table("reportes").delete().eq("id", reporte_id).execute()
    mongo.comentarios.delete_many({"reporte_id": reporte_id})
    mongo.seguimiento.delete_many({"reporte_id": reporte_id})

# ---------- MONGODB (datos flexibles) ----------
def listar_comentarios(reporte_id):
    docs = list(mongo.comentarios.find({"reporte_id": reporte_id}).sort("fecha", 1))
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs

def agregar_comentario(reporte_id, autor, texto, etiquetas):
    mongo.comentarios.insert_one({
        "reporte_id": reporte_id, "autor": autor, "texto": texto,
        "etiquetas": etiquetas, "fecha": _ahora(),
    })

def editar_comentario(comentario_id, texto):
    mongo.comentarios.update_one({"_id": ObjectId(comentario_id)}, {"$set": {"texto": texto}})

def eliminar_comentario(comentario_id):
    mongo.comentarios.delete_one({"_id": ObjectId(comentario_id)})

def obtener_seguimiento(reporte_id):
    doc = mongo.seguimiento.find_one({"reporte_id": reporte_id})
    return doc["historial"] if doc else []