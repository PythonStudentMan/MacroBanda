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

    if current_user.es_root:
        return True

    membresia = obtener_membresia_actual()

    if not membresia:
        return False

    # Permisos directos (override)
    if any(p.codigo_permiso == codigo_permiso for p in membresia.permisos):
        return True

    # Permisos del rol
    if membresia.rol:
        if any(p.codigo_permiso == codigo_permiso for p in membresia.rol.permisos):
            return True

    return False
