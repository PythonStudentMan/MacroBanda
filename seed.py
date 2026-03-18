from app import create_app
from app.extensions import db
from app.models.usuario import Usuario
from app.models.auth import Rol, Permiso

app = create_app()

with app.app_context():
    roles = ['superadmin', 'admin', 'basico']
    for r in roles:
        if not Rol.query.filter_by(nombre=r).first():
            db.session.add(Rol(nombre=r))

    perms = [
        ('Gestionar Agrupación', 'agrupacion.config', 'Configurar Agrupación'),
        ('Gestionar Usuarios', 'usuario.config', 'Gestión de Usuarios'),
        ('Dashboard', 'dashboard.ver', 'Ver el Dashboard General'),
        ('Editar Ajustes', 'ajustes.config', 'Editar Ajustes Generales'),
    ]

    for nombre, codigo, descripcion in perms:
        if not Permiso.query.filter_by(codigo=codigo).first():
            db.session.add(Permiso(nombre=nombre, codigo=codigo, descripcion=descripcion))

    db.session.commit()

    # Crear usuario root si no existe

    if not Usuario.query.filter_by(email='root@test.com').first():
        u = Usuario(email="root@test.com", is_root=True)
        u.set_password('rootpass')
        db.session.add(u)
        db.session.commit()
        print('Usuario root creado: root@test.com / rootpass')
    else:
        print('Usuario root ya existe.')
