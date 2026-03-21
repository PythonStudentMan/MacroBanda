from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models import Agrupacion
from app.utils.decorators import requiere_permiso

agrupaciones_bp = Blueprint('agrupaciones', __name__, url_prefix='/agrupaciones')

@agrupaciones_bp.route('/listar/')
@login_required
@requiere_permiso('agrupaciones.ver')
def listar():
    search = request.args.get('search', '')

    query = Agrupacion.query.all()

    if search:
        query = query.join(Agrupacion).filter(
            Agrupacion.nombre.ilike(f"%(search)%")
        )

    page = request.args.get('page', 1, type=int)

    pagination = query.paginate(page=page, per_page=10)

    return render_template(
        'agrupaciones/listar.html',
        agrupaciones=pagination.items,
        pagination=pagination,
        search=search
    )