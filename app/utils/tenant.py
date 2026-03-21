from flask import request, g, session
from app.models import Agrupacion

def cargar_tenant():

    host = request.host

    partes = host.split('.')

    # Localhost o sin subdominio
    if len(partes) < 3:
        g.agrupacion = None
        return

    subdominio = partes[0]

    agrupacion = Agrupacion.query.filter_by(
        subdominio=subdominio
    ).first()

    g.agrupacion = agrupacion

    print("HOST:", request.host)
    print("SUBDOMINIO DETECTADO:", subdominio)

def get_agrupacion_id():
    if g.get('agrupacion'):
        return g.agrupacion.id

    return session.get('agrupacion_activa')