from functools import wraps
from flask import abort, session
from flask_login import current_user
from app.services.permisos import tiene_permiso, obtener_membresia_actual


def tenant_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.es_root:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def permiso_requerido(codigo_permiso):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            agrupacion_id = session.get('agrupacion_activa')
            if not agrupacion_id or not tiene_permiso(codigo_permiso):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        membresia = obtener_membresia_actual()

        if not membresia or membresia.rol != 'admin':
            abort(403)

        return f(*args, **kwargs)
    return wrapper()


def superadmin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        membresia = obtener_membresia_actual()

        if not membresia or membresia.rol != 'superadmin':
            abort(403)

        return f(*args, **kwargs)

    return wrapper()