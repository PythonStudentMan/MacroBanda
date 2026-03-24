from flask import Blueprint, g, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required
from app.extensions import db
from app.socios.forms import SocioForm
from app.utils.decorators import tenant_required, requiere_permiso
from app.models import Socio, TipoSocio, Cuota
from datetime import datetime, timezone

socios_bp = Blueprint('socios', __name__, url_prefix='/socios')

@socios_bp.route('/')
@login_required
@tenant_required
@requiere_permiso('socios.ver')
def listar_socios():
    socios = Socio.query.filter_by(
        agrupacion_id=g.agrupacion.id,
        activo=True
    ).all()

    return render_template('socios/socios_list.html', socios=socios)

@socios_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@tenant_required
@requiere_permiso('socios.editar')
def crear_socio():

    form = SocioForm()

    # Cargamos tipos de socio
    tipos = TipoSocio.query.filter_by(
        agrupacion_id=g.agrupacion.id,
        activo=True
    ).all()

    form.tipo_socio_id.choices = [(t.id, t.nombre) for t in tipos]

    if form.validate_on_submit():
        socio = Socio(
            nombre=form.nombre.data,
            apellidos=form.apellidos.data,
            documento_identidad=form.documento_identidad.data,
            email=form.email.data,
            telefono=form.telefono.data,
            direccion=form.direccion.data,
            cp=form.cp.data,
            poblacion=form.poblacion.data,
            provincia=form.provincia.data,
            tipo_socio_id=form.tipo_socio_id.data,
            fecha_alta=form.fecha_alta.data,
            observaciones=form.observaciones.data,
            agrupacion_id=g.agrupacion.id
        )

        db.session.add(socio)
        db.session.commit()

        flash('Socio creado correctamente', 'success')
        return redirect(url_for('socios.listar_socios'))

    return render_template('socios/socios_form.html', form=form)

@socios_bp.route('/<int:id_socio>/editar/', methods=['GET', 'POST'])
@login_required
@tenant_required
@requiere_permiso('socios.editar')
def editar_socio(id_socio):
    socio = Socio.query.filter_by(
        id=id_socio,
        agrupacion_id=g.agrupacion.id,
        activo=True
    ).first_or_404()

    form = SocioForm(obj=socio)

    tipos = TipoSocio.query.filter_by(
        agrupacion_id=g.agrupacion.id,
        activo=True
    ).all()

    form.tipo_socio_id.choices = [(t.id, t.nombre) for t in tipos]

    if form.validate_on_submit():

        socio.nombre = form.nombre.data
        socio.apellidos = form.apellidos.data
        socio.documento_identidad = form.documento_identidad.data
        socio.email = form.email.data
        socio.telefono = form.telefono.data
        socio.direccion = form.direccion.data
        socio.cp = form.cp.data
        socio.poblacion = form.poblacion.data
        socio.provincia = form.provincia.data
        socio.tipo_socio_id = form.tipo_socio_id.data
        socio.fecha_alta = form.fecha_alta.data
        socio.observaciones = form.observaciones.data

        db.session.commit()

        flash('Socio actualizado correctamente', 'success')
        return redirect(url_for('socios.listar_socios'))

    return render_template('socios/socios_form.html', form=form, socio=socio)

@socios_bp.route('/<int:id_socio>/baja/')
@login_required
@tenant_required
@requiere_permiso('socios.eliminar')
def baja_socio(id_socio):
    socio = Socio.query.filter_by(
        id=id_socio,
        agrupacion_id=g.agrupacion.id,
        activo=True
    ).first_or_404()

    socio.fecha_baja = datetime.now(timezone.utc)
    socio.soft_delete()

    db.session.commit()

    flash('Socio dado de baja', 'warning')
    return redirect(url_for('socios.lista_socios'))

@socios_bp.route('/<int:id_socio>/cuotas/')
@login_required
@tenant_required
@requiere_permiso('socios.ver')
def ver_cuotas(id_socio):
    socio = Socio.query.filter_by(
        id=id_socio,
        agrupacion_id=g.agrupacion.id,
        activo=True
    ).first()

    if not socio:
        abort(404)

    # Filtros opcionales
    estado = request.args.get('estado')
    tipo = request.args.get('tipo')

    query = Cuota.query.filter_by(
        socio_id=socio.id,
        agrupacion_id=g.agrupacion.id,
        activo=True
    )

    if estado:
        query = query.filter_by(estado=estado)
    if tipo:
        query = query.filter_by(tipo=tipo)

    cuotas = query.order_by(Cuota.fecha.desc()).all()

    return render_template('socios/cuotas.html',
                           socio=socio, cuotas=cuotas,
                           estado_filtrado=estado, tipo_filtrado=tipo)