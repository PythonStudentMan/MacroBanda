from app import create_app
from app.extensions import db
from app.models import Usuario

app = create_app()

with app.app_context():

    email = 'root@root.com'
    password = 'root123'

    usuario = Usuario.query.filter_by(email=email).first()

    if usuario:
        print('El usuario root ya existe')
    else:
        usuario = Usuario(
            email=email,
            nombre='root',
            es_root=True
        )
        usuario.set_password(password)

        db.session.add(usuario)
        db.session.commit()

        print('Usuario root creado correctamente')
