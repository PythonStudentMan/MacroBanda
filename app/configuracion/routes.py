from flask import Blueprint, g, render_template, request, session, redirect, url_for, flash
from flask_login import login_required
from app.models import ConfiguracionAgrupacion, TipoSocio, ConfiguracionCuota
from app.extensions import db
from app.configuracion.forms import TipoSocioForm
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

        config.forma_pago_id = request.form.get('forma_pago_id')
        if config.forma_pago_id == '':
            config.forma_pago_id = None
        config.remesas_sepa = 'remesas_sepa' in request.form

        config.iban = request.form.get('iban')
        config.sufijo = request.form.get('sufijo')

        db.session.commit()

        flash('Configuración actualizada', 'success')
        return redirect(url_for('configuracion.ver'))


    return render_template('configuracion/ver.html', config=config)

@configuracion_bp.route('/tipos-socio/')
@login_required
@tenant_required
@requiere_permiso('configuracion.ver')
def listar_tipos_socio():
    tipos = TipoSocio.query.filter_by(
        agrupacion_id=g.agrupacion.id,
        activo=True
    ).all()

    return render_template('configuracion/tipos_socio_list.html', tipos=tipos)

@configuracion_bp.route('/tipos-socio/nuevo/', methods=['GET', 'POST'])
@login_required
@tenant_required
@requiere_permiso('configuracion.editar')
def crear_tipo_socio():

    form = TipoSocioForm()

    if form.validate_on_submit():

        tipo = TipoSocio(
            nombre = form.nombre.data,
            tiene_cuota = form.tiene_cuota.data,
            agrupacion_id=g.agrupacion.id
        )
        db.session.add(tipo)
        db.session.flush()

        # Si tiene cuota, se crea la configuración
        if form.tiene_cuota.data:
            cuota = ConfiguracionCuota(
                tipo_socio_id=tipo.id,
                importe=form.importe.data,
                frecuencia=form.frecuencia.data,
                agrupacion_id=g.agrupacion.id
            )
            db.session.add(cuota)

        db.session.commit()

        flash('Tipo de socio creado correctamente', 'success')
        return redirect(url_for('configuracion.listar_tipos_socio'))

    return render_template('configuracion/tipos_socio_form.html', form=form)

@configuracion_bp.route('/tipos-socio/<int:id>/editar/', methods=['GET', 'POST'])
@login_required
@tenant_required
@requiere_permiso('configuracion.editar')
def editar_tipo_socio(id):
    tipo = TipoSocio.query.filter_by(
        id=id,
        agrupacion_id=g.agrupacion.id,
        activo=True
    ).first_or_404()

    form = TipoSocioForm(obj=tipo)

    # Precargamos datos de cuota si existen
    if request.method == 'GET' and tipo.configuracion_cuota:
        form.importe.data = tipo.configuracion_cuota.importe
        form.frecuencia.data = tipo.configuracion_cuota.frecuencia

    if form.validate_on_submit():
        tipo.nombre = form.nombre.data
        tipo.tiene_cuota = form.tiene_cuota.data

        # CASO 1: Ahora tiene cuota
        if form.tiene_cuota.data:

            if tipo.configuracion_cuota:
                # Actualizar
                tipo.configuracion_cuota.importe = form.importe.data
                tipo.configuracion_cuota.frecuencia = form.frecuencia.data
            else:
                # Crear nueva
                cuota = ConfiguracionCuota(
                    tipo_socio_id=tipo.id,
                    importe=form.importe.data,
                    frecuencia=form.frecuencia.data,
                    agrupacion_id=g.agrupacion.id
                )
                db.session.adD(cuota)

        # CASO 2: ya no tiene cuota
        else:
            if tipo.configuracion_cuota:
                tipo.configuracion_cuota.activo = False

        db.session.commit()

        flash('Tipo de socio actualizado correctamente', 'success')
        return redirect(url_for('configuracion.listar_tipos_socio'))

    return render_template('configuracion/tipos_socio_form.html', form=form, tipo=tipo)

@configuracion_bp.route('/tipo-socio/<int:id>/eliminar/')
@login_required
@tenant_required
@requiere_permiso('configuracion.eliminar')
def eliminar_tipo_socio(id):
    tipo = TipoSocio.query.filter_by(
        id=id,
        agrupacion_id=g.agrupacion.id,
        activo=True
    ).first_or_404()

    tipo.soft_delete()
    db.session.commit()

    flash('Tipo de socio desactivado', 'warning')
    return redirect(url_for('configuracion.listar_tipos_socio'))