# ReportaBaches Ciudad Juárez

Aplicación web para que la ciudadanía registre reportes urbanos (baches, fugas de agua y fallas de alumbrado) y consulte su estatus con un folio. Proyecto de la Unidad 3, Integración de aplicaciones y bases de datos.

**App desplegada:** [URL de tu app .streamlit.app]
**Repositorio:** https://github.com/Azul1911/reportes-ciudadanos

## Problema que resuelve

Reportar un problema urbano suele ser un trámite lento, sin folio ni seguimiento. Esta app permite registrar usuarios y reportes, dar seguimiento a cada caso y consultar su estatus en cualquier momento.

## Tecnologías

- Python y Streamlit (interfaz y lógica)
- Supabase, PostgreSQL (datos relacionales)
- MongoDB Atlas (datos flexibles)
- supabase-py, pymongo, pandas, altair y pydeck
- GitHub y Streamlit Community Cloud (despliegue)

## Qué guarda cada base de datos

| Base | Qué guarda | Por qué |
|---|---|---|
| Supabase (SQL) | `usuarios`, `categorias`, `reportes` | Datos estructurados con llaves foráneas e integridad |
| MongoDB Atlas (NoSQL) | `comentarios`, `seguimiento` | Datos con estructura variable (evidencia, etiquetas, historial anidado) |

Las dos se relacionan con el campo `reporte_id`, que es el `id` del reporte en Supabase. La vista combinada de la app muestra un mismo reporte con datos de ambas.

## Funciones

- Usuarios: registrar, editar y eliminar (Supabase).
- Reportes: crear, consultar, cambiar estatus y eliminar (Supabase, con historial en MongoDB).
- Comentarios: agregar, editar y borrar (MongoDB).
- Consulta por folio, métricas, gráfica y mapa.
- Vista combinada de Supabase y MongoDB.

## Conexión y seguridad

Las credenciales no están en el repositorio. Se leen de variables de entorno (`.env` en local, Secrets en Streamlit Cloud), y `.env` está en `.gitignore`.

Archivo `.env` de ejemplo (valores falsos):

```
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_secret_key
MONGO_URI=mongodb+srv://usuario:contraseña@cluster0.xxxxx.mongodb.net/
```

- **Supabase:** URL del proyecto y secret key, usadas solo del lado del servidor. Las tablas tienen seguridad por filas (RLS) activada.
- **MongoDB Atlas:** cadena `mongodb+srv` con un usuario de base de datos limitado a `reportes_ciudadanos`, y acceso por red configurado en Network Access.

## Ejecutar en local

```
pip install -r requirements.txt
python -m streamlit run app.py
```

## Despliegue

1. Subir el código a GitHub (sin `.env`).
2. En share.streamlit.io crear la app con el repo, la rama `main` y el archivo `app.py`.
3. En Settings, Secrets, pegar `SUPABASE_URL`, `SUPABASE_KEY` y `MONGO_URI` entre comillas.

## Estructura

```
app.py            interfaz Streamlit
db.py             conexiones y CRUD de ambas bases
requirements.txt  dependencias
logo.png          logo de la app
```

## Autora

Ámbar Azul Ronquillo López · Universidad Tecnológica de Ciudad Juárez
