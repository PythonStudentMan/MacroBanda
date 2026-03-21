from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from flask_login import login_required
from app.models import ConfiguracionAgrupacion, Agrupacion
from app.extensions import db
from app.utils.decorators import tenant_required, requiere_permiso
import os
from werkzeug.utils import secure_filename

configuracion_bp = Blueprint('configuracion', __name__, url_prefix='/configuracion')

UPLOAD_FOLDER = 'app/static/logos'

@configuracion_bp.route('/', methods=['GET', 'POST'])
@login_required
@tenant_required
@requiere_permiso('configuracion.ver')
def ver():
    agrupacion_id = session.get('agrupacion_activa')

    config = ConfiguracionAgrupacion.query.filter_by(
        agrupacion_id=agrupacion_id,
        activo=True
    ).first()

    if not config:
        config = ConfiguracionAgrupacion(agrupacion_id=agrupacion_id)
        db.session.add(config)
        db.session.commit()

    if request.method == 'POST':

        config.color_primario = request.form.get('color_primario')
        config.color_secundario = request.form.get('color_secundario')
        config.color_fondo = request.form.get('color_fondo')
        config.color_texto = request.form.get('color_texto')

        file = request.files.get('logo')

        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            file.save(filepath)
            config.logo = filename

        config.agrupacion.direccion = request.form.get('direccion')
        config.agrupacion.cp = request.form.get('cp')
        config.agrupacion.poblacion = request.form.get('poblacion')
        config.agrupacion.provincia = request.form.get('provincia')
        config.agrupacion.cif = request.form.get('cif')

        config.agrupacion.telefono = request.form.get('telefono')
        config.agrupacion.email = request.form.get('email')
        config.agrupacion.web = request.form.get('web')

        config.iban = request.form.get('iban')
        config.sufijo = request.form.get('sufijo')

        db.session.commit()

        flash('Configuración actualizada', 'success')
        return redirect(url_for('configuracion.ver'))

    return render_template('configuracion/ver.html', config=config)