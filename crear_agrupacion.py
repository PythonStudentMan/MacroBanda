from app import create_app
from app.extensions import db

from app.models import Usuario, Agrupacion, Membresia, Rol

app = create_app()
with app.app_context():
    usuario = Usuario.query.filter_by(email='root@root.com').first()
    agrupacion = Agrupacion(nombre="Agrupacion Demo", slug='agrupacion-demo', subdominio='banda1')
    db.session.add(agrupacion)
    db.session.commit()
    rol = Rol(nombre="Superadmin", agrupacion_id=agrupacion.id)
    db.session.add(rol)
    db.session.commit()
    membresia = Membresia(usuario_id=usuario.id, agrupacion_id=agrupacion.id, rol_id=rol.id)
    db.session.add(membresia)
    db.session.commit()
    print("Agrupación Creada")