from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

agrupaciones_bp = Blueprint('agrupaciones', __name__, url_prefix='/agrupaciones')

@login_required
@agrupaciones_bp.route('/listar/')
def listar():
    return "Lista de agrupaciones"