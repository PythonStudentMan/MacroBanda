from flask import session
from flask_login import current_user
from app.models import Agrupacion, Membresia

def inject_agrupacion():
    agrupacion_id = session.get('agrupacion_activa')

    if not agrupacion_id:
        return dict(agrupacion=None)

    agrupacion = Agrupacion.query.get(agrupacion_id)

    return dict(agrupacion=agrupacion)

def inject_membresias():
    if not current_user.is_authenticated or current_user.es_root:
        return dict(membresias=[])

    membresias = Membresia.query.filter_by(usuario_id=current_user.id).all()

    return dict(membresias=membresias)