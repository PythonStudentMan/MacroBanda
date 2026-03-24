from app import create_app
from app.extensions import db
from app.models import Rol, Permiso, roles_permisos

app = create_app()

# Definición de permisos por módulos

PERMISOS = [
    ('Ver Dashboard', 'dashboard.ver'),

    ('Ver Agrupaciones', 'agrupaciones.ver'),
    ('Crear Agrupaciones', 'agrupaciones.crear'),
    ('Editar Agrupaciones', 'agrupaciones.editar'),

    ('Ver Usuarios', 'usuarios.ver'),
    ('Crear Usuarios', 'usuarios.crear'),
    ('Editar Usuarios', 'usuarios.editar'),

    ('Ver Roles', 'roles.ver'),
    ('Editar Roles', 'roles.editar'),

    ('Ver Configuración', 'configuracion.ver'),
    ('Editar Configuración', 'configuracion.editar'),
    ('Eliminar Configuración', 'configuracion.eliminar'),
    ('Ver Formas de Pago', 'configuracion,formas_pago.ver'),
    ('Editar Formas de Pago', 'configuracion,formas_pago.editar'),
    ('Eliminar Formas de Pago', 'configuracion,formas_pago.eliminar'),

    ('Ver Socios', 'socios.ver'),
    ('Editar Socios', 'socios.editar'),
    ('Eliminar Socios', 'socios.eliminar'),

]

with app.app_context():
    print('Creando permisos...')

    permisos_obj = {}

    for nombre, codigo in PERMISOS:

        permiso = Permiso.query.filter_by(codigo=codigo).first()

        if not permiso:
            permiso = Permiso(nombre=nombre, codigo=codigo)
            db.session.add(permiso)

        permisos_obj[codigo] = permiso

    db.session.commit()


    print('Seed completaado correctamente')