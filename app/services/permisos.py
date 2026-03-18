from flask import session
from flask_login import current_user
from app.models import Membresia

def obtener_membresia_actual():
    agrupacion_id = session.get('agrupacion_activa')
    if not agrupacion_id:
        return None
    return Membresia.query.filter_by(
        usuario_id=current_user.id,
        agrupacion_id=agrupacion_id
    ).first()

def tiene_permiso(codigo_permiso):

    membresia = obtener_membresia_actual()
    if not membresia:
        return False

    # Permisos del Rol
    permisos_rol = {p.codigo for p in membresia.rol.permisos} if membresia.rol else set()

    # Permisos individuales
    permisos_individuales = {p.codigo for p in membresia.permisos}

    # Unión de ambos
    permisos_totales = permisos_rol.union(permisos_individuales)

    return codigo_permiso in permisos_totales
