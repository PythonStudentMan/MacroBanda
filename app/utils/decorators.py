from functools import wraps
from flask import g, abort, flash, redirect, url_for
from flask_login import current_user

from app.services.permisos import tiene_permiso


def tenant_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.get('agrupacion'):
            flash('Debes seleccionar una agrupación primero', 'warning')
            return redirect(url_for('panel.panel_inicio'))
        return f(*args, **kwargs)
    return decorated_function

def requiere_permiso(permiso):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.es_root:
                return f(*args, **kwargs)
            if not g.get('agrupacion'):
                abort(403)
            if not tiene_permiso(permiso):
                flash('No tienes permiso para esta acción', 'danger')
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
