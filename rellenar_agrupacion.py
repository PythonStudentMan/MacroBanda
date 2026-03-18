from app import create_app
from app.extensions import db
from app.models import Agrupacion, Usuario

app = create_app()
with app.app_context():
    agrupacion = Agrupacion.query.first()
    usuarios = Usuario.query.all()
    for u in usuarios:
        u.agrupacion_id = agrupacion.id
    db.session.commit()
    print("Datos actualizados")