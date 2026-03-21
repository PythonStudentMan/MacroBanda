from flask_login import current_user
from flask import session
from app.extensions import db
from app.models import Auditoria


def registrar_accion(accion, entidad=None, entidad_id=None, descripcion=None):

    auditoria = Auditoria(
        usuario_id=current_user.id if current_user.is_authenticated else None,
        agrupacion_id=session.get('agrupacion_activa'),
        accion=accion,
        entidad=entidad,
        entidad_id=entidad_id,
        descripcion=descripcion
    )
    db.session.add(auditoria)
    db.session.commit()