from app import create_app
from app.extensions import db
from app.models import Usuario

app = create_app()

with app.app_context():
    usuario = Usuario.query.filter_by(
        email='root@root.com'
    ).first()

    if not usuario:
        root = Usuario(
            email='root@root.com',
            es_root=True
        )

        root.set_password('root123')

        db.session.add(root)
        db.session.commit()

        print('Usuario root creado')

    else:

        print('El usuario root ya existe')