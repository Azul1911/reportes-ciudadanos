import os
import time
from datetime import datetime, timezone
import requests
from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient
from supabase import create_client

load_dotenv()

ESTATUS = ("recibido", "en_revision", "resuelto")
_sin_resultado = set()  # reportes cuya dirección no se encontró (evita reintentar en cada carga)


class ErrorApp(Exception):
    """Error con un mensaje seguro para mostrarle a la persona usuaria."""


def _secret(nombre, requerido=True):
    """Lee de .env (local) o de st.secrets (Streamlit Cloud)."""
    valor = os.getenv(nombre)
    if valor:
        return valor
    try:
        import streamlit as st
        return st.secrets[nombre]
    except Exception:
        if requerido:
            raise
        return None


SUPABASE_URL = _secret("SUPABASE_URL")
SUPABASE_KEY = _secret("SUPABASE_KEY")
sb = create_client(SUPABASE_URL, SUPABASE_KEY)
mongo = MongoClient(_secret("MONGO_URI"))["reportes_ciudadanos"]


def _ahora():
    return datetime.now(timezone.utc)


def _texto(valor, campo, maximo, obligatorio=False):
    valor = (valor or "").strip()
    if obligatorio and not valor:
        raise ErrorApp(f"{campo} es obligatorio.")
    if len(valor) > maximo:
        raise ErrorApp(f"{campo} no puede pasar de {maximo} caracteres.")
    return valor


def _perfil(uid):
    datos = sb.table("usuarios").select("id,nombre,rol").eq("id", uid).limit(1).execute().data
    if not datos:
        raise ErrorApp("Tu sesión ya no es válida. Vuelve a iniciar sesión.")
    return datos[0]


def _es_admin(uid):
    return _perfil(uid)["rol"] == "admin"


def _reporte(reporte_id):
    datos = sb.table("reportes").select("id,usuario_id,direccion").eq("id", reporte_id).limit(1).execute().data
    if not datos:
        raise ErrorApp("El reporte ya no existe.")
    return datos[0]


# ====================== MAPA: dirección -> punto ======================
def geocodificar(direccion):
    """Convierte una dirección en (latitud, longitud) con OpenStreetMap Nominatim. None si no la encuentra."""
    consulta = (direccion or "").strip()
    if not consulta:
        return None
    if "juárez" not in consulta.lower() and "juarez" not in consulta.lower():
        consulta += ", Ciudad Juárez, Chihuahua, México"
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": consulta, "format": "json", "limit": 1, "countrycodes": "mx"},
            headers={"User-Agent": "ReportaBaches-UTCJ/1.0 (proyecto escolar)"},
            timeout=8,
        )
        datos = resp.json()
        if datos:
            return float(datos[0]["lat"]), float(datos[0]["lon"])
    except Exception:
        pass
    return None


def completar_coordenadas(intentos_max=5):
    """Ubica en el mapa los reportes que aún no tienen punto. Devuelve cuántos ubicó."""
    pendientes = (sb.table("reportes").select("id,direccion").is_("latitud", "null")
                  .order("id", desc=True).limit(40).execute().data)
    intentos = ubicados = 0
    for r in pendientes:
        if intentos >= intentos_max:
            break
        if r["id"] in _sin_resultado:
            continue
        intentos += 1
        punto = geocodificar(r["direccion"])
        if punto:
            sb.table("reportes").update({"latitud": punto[0], "longitud": punto[1]}).eq("id", r["id"]).execute()
            ubicados += 1
        else:
            _sin_resultado.add(r["id"])
        time.sleep(1.1)  # Nominatim pide máximo 1 consulta por segundo
    return ubicados


# ====================== CUENTAS (Supabase Auth + tabla usuarios) ======================
def _cliente_auth():
    # Cliente aparte para iniciar sesión: nunca se mezcla con el cliente principal.
    clave = _secret("SUPABASE_ANON_KEY", requerido=False) or SUPABASE_KEY
    return create_client(SUPABASE_URL, clave)


def perfil_por_auth(auth_id):
    datos = sb.table("usuarios").select("*").eq("auth_id", str(auth_id)).limit(1).execute().data
    return datos[0] if datos else None


def registrar(nombre, correo, telefono, password):
    nombre = _texto(nombre, "El nombre", 80, True)
    correo = _texto(correo, "El correo", 120, True).lower()
    telefono = _texto(telefono, "El teléfono", 20)
    if "@" not in correo or "." not in correo.split("@")[-1]:
        raise ErrorApp("Escribe un correo válido.")
    if len(password or "") < 8:
        raise ErrorApp("La contraseña debe tener al menos 8 caracteres.")
    try:
        resp = sb.auth.admin.create_user(
            {"email": correo, "password": password, "email_confirm": True})
        auth_id = resp.user.id
    except Exception as e:
        texto = str(e).lower()
        if "already" in texto or "registered" in texto or "exists" in texto:
            raise ErrorApp("Ya existe una cuenta con ese correo.")
        raise ErrorApp("No se pudo crear la cuenta. Intenta de nuevo.")
    try:
        sb.table("usuarios").insert({"auth_id": auth_id, "nombre": nombre, "correo": correo,
                                     "telefono": telefono or None}).execute()
    except Exception as e:
        try:
            sb.auth.admin.delete_user(auth_id)
        except Exception:
            pass
        if "23505" in str(e) or "duplicate" in str(e).lower():
            raise ErrorApp("Ya existe un usuario con ese correo.")
        raise ErrorApp("No se pudo crear el perfil. Intenta de nuevo.")
    return perfil_por_auth(auth_id)


def iniciar_sesion(correo, password):
    try:
        resp = _cliente_auth().auth.sign_in_with_password(
            {"email": (correo or "").strip().lower(), "password": password or ""})
        perfil = perfil_por_auth(resp.user.id)
    except Exception:
        raise ErrorApp("Correo o contraseña incorrectos.")
    if not perfil:
        raise ErrorApp("Tu cuenta no tiene un perfil asociado.")
    return perfil


def actualizar_perfil(actor_id, nombre, telefono):
    nombre = _texto(nombre, "El nombre", 80, True)
    telefono = _texto(telefono, "El teléfono", 20)
    sb.table("usuarios").update({"nombre": nombre, "telefono": telefono or None}).eq("id", actor_id).execute()
    return sb.table("usuarios").select("*").eq("id", actor_id).limit(1).execute().data[0]


def eliminar_cuenta(actor_id, password):
    perfil = sb.table("usuarios").select("*").eq("id", actor_id).limit(1).execute().data
    if not perfil:
        raise ErrorApp("Tu sesión ya no es válida.")
    perfil = perfil[0]
    if perfil.get("auth_id"):
        try:
            iniciar_sesion(perfil["correo"], password)
        except ErrorApp:
            raise ErrorApp("La contraseña no es correcta.")
    ids = [r["id"] for r in sb.table("reportes").select("id").eq("usuario_id", actor_id).execute().data]
    if perfil.get("auth_id"):
        sb.auth.admin.delete_user(perfil["auth_id"])  # borra el perfil y sus reportes en cascada
    sb.table("usuarios").delete().eq("id", actor_id).execute()
    mongo.comentarios.delete_many({"$or": [{"reporte_id": {"$in": ids}}, {"autor_id": actor_id}]})
    mongo.seguimiento.delete_many({"reporte_id": {"$in": ids}})


# ====================== REPORTES (Supabase) ======================
def listar_categorias():
    return sb.table("categorias").select("*").order("id").execute().data


def listar_reportes():
    return (sb.table("reportes")
            .select("*, usuarios(nombre), categorias(nombre, dependencia)")
            .order("id").execute().data)


def crear_reporte(actor_id, categoria_id, titulo, descripcion, direccion, latitud=None, longitud=None):
    datos = {
        "usuario_id": actor_id,  # siempre la persona con sesión iniciada
        "categoria_id": categoria_id,
        "titulo": _texto(titulo, "El título", 120, True),
        "descripcion": _texto(descripcion, "La descripción", 1000),
        "direccion": _texto(direccion, "La dirección", 200, True),
    }
    if latitud is None and longitud is None:
        punto = geocodificar(datos["direccion"])  # el punto del mapa sale de la dirección
        if punto:
            datos["latitud"], datos["longitud"] = punto
    else:
        if latitud is None or longitud is None or not (-90 <= latitud <= 90) or not (-180 <= longitud <= 180):
            raise ErrorApp("Revisa la latitud y la longitud.")
        datos["latitud"], datos["longitud"] = latitud, longitud
    nuevo = sb.table("reportes").insert(datos).execute().data[0]
    mongo.seguimiento.insert_one({
        "reporte_id": nuevo["id"],
        "historial": [{"estatus": "recibido", "fecha": _ahora(), "nota": "Reporte registrado"}],
    })
    return nuevo


def editar_reporte(actor_id, reporte_id, titulo, descripcion, direccion):
    actual = _reporte(reporte_id)
    if actual["usuario_id"] != actor_id:
        raise ErrorApp("Solo la persona que creó el reporte puede modificarlo.")
    nueva = _texto(direccion, "La dirección", 200, True)
    cambios = {
        "titulo": _texto(titulo, "El título", 120, True),
        "descripcion": _texto(descripcion, "La descripción", 1000),
        "direccion": nueva,
    }
    if nueva != actual["direccion"]:  # si cambió la dirección, se actualiza el punto del mapa
        punto = geocodificar(nueva)
        cambios["latitud"], cambios["longitud"] = punto if punto else (None, None)
        _sin_resultado.discard(reporte_id)
    sb.table("reportes").update(cambios).eq("id", reporte_id).execute()


def cambiar_estatus(actor_id, reporte_id, estatus):
    admin = _perfil(actor_id)
    if admin["rol"] != "admin":
        raise ErrorApp("Solo un administrador puede cambiar el estatus.")
    if estatus not in ESTATUS:
        raise ErrorApp("Estatus no válido.")
    _reporte(reporte_id)
    sb.table("reportes").update({"estatus": estatus}).eq("id", reporte_id).execute()
    mongo.seguimiento.update_one(
        {"reporte_id": reporte_id},
        {"$push": {"historial": {"estatus": estatus, "fecha": _ahora(),
                                 "nota": "Cambio de estatus", "responsable": admin["nombre"]}}},
        upsert=True,
    )


def eliminar_reporte(actor_id, reporte_id):
    if _reporte(reporte_id)["usuario_id"] != actor_id and not _es_admin(actor_id):
        raise ErrorApp("Solo la persona que creó el reporte puede eliminarlo.")
    sb.table("reportes").delete().eq("id", reporte_id).execute()
    mongo.comentarios.delete_many({"reporte_id": reporte_id})
    mongo.seguimiento.delete_many({"reporte_id": reporte_id})


# ====================== COMENTARIOS Y SEGUIMIENTO (MongoDB) ======================
def listar_comentarios(reporte_id):
    docs = list(mongo.comentarios.find({"reporte_id": reporte_id}).sort("fecha", 1))
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs


def comentarios_por_reporte(ids):
    agrupados = {i: [] for i in ids}
    for d in mongo.comentarios.find({"reporte_id": {"$in": list(ids)}}).sort("fecha", 1):
        d["_id"] = str(d["_id"])
        agrupados.setdefault(d["reporte_id"], []).append(d)
    return agrupados


def agregar_comentario(actor_id, reporte_id, texto, etiquetas):
    texto = _texto(texto, "El comentario", 1000, True)
    _reporte(reporte_id)
    etiquetas = [e.strip()[:30] for e in etiquetas if e.strip()][:8]
    mongo.comentarios.insert_one({
        "reporte_id": reporte_id, "autor": _perfil(actor_id)["nombre"], "autor_id": actor_id,
        "texto": texto, "etiquetas": etiquetas, "fecha": _ahora(),
    })


def editar_comentario(actor_id, comentario_id, texto):
    texto = _texto(texto, "El comentario", 1000, True)
    doc = mongo.comentarios.find_one({"_id": ObjectId(comentario_id)})
    if not doc:
        raise ErrorApp("El comentario ya no existe.")
    if doc.get("autor_id") != actor_id:
        raise ErrorApp("Solo puedes editar tus propios comentarios.")
    mongo.comentarios.update_one({"_id": doc["_id"]}, {"$set": {"texto": texto}})


def eliminar_comentario(actor_id, comentario_id):
    doc = mongo.comentarios.find_one({"_id": ObjectId(comentario_id)})
    if not doc:
        raise ErrorApp("El comentario ya no existe.")
    if doc.get("autor_id") != actor_id and not _es_admin(actor_id):
        raise ErrorApp("Solo puedes borrar tus propios comentarios.")
    mongo.comentarios.delete_one({"_id": doc["_id"]})


def obtener_seguimiento(reporte_id):
    doc = mongo.seguimiento.find_one({"reporte_id": reporte_id})
    return doc["historial"] if doc else []
