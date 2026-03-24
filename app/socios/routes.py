from flask import Blueprint, g, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required
from app.extensions import db
from app.utils.decorators import tenant_required, requiere_permiso
from app.models import Socio, TipoSocio, Cuota
from app.cuotas.generador import generar_cuotas_socio
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
    # Cargamos tipos de socio
    tipos_socio = TipoSocio.query.filter_by(
        agrupacion_id=g.agrupacion.id,
        activo=True
    ).all()

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellidos = request.form.get('apellidos')
        documento_identidad = request.form.get('documento_identidad')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        direccion = request.form.get('direccion')
        cp = request.form.get('cp')
        poblacion = request.form.get('poblacion')
        provincia = request.form.get('provincia')
        fecha_alta = request.form.get('fecha_alta')
        tipo_id = request.form.get('tipo_socio_id')
        metodo_cobro = request.form.get('metodo_cobro')
        observaciones = request.form.get('observaciones')

        tipo = TipoSocio.query.filter_by(
            id=tipo_id,
            agrupacion_id=g.agrupacion.id,
            activo=True
        ).first()
        if not tipo:
            flash('Tipo de socio no válido', 'warning')
            return redirect(url_for('socios.crear_socio'))

        socio = Socio(
            nombre=nombre,
            apellidos=apellidos,
            documento_identidad=documento_identidad,
            email=email,
            telefono=telefono,
            direccion=direccion,
            cp=cp,
            poblacion=poblacion,
            provincia=provincia,
            fecha_alta=fecha_alta,
            tipo_socio_id=tipo.id,
            metodo_cobro=metodo_cobro,
            agrupacion_id=g.agrupacion.id,
            observaciones=observaciones
        )
        db.session.add(socio)
        db.session.commit()

        # Generar cuotas iniciales
        generar_cuotas_socio(socio, hasta_fecha=None)

        flash(f'Socio {nombre} {apellidos} creado correctamente', 'success')
        return redirect(url_for('socios.listar_socios'))

    return render_template('socios/socios_form.html', tipos_socio=tipos_socio, socio=None)

@socios_bp.route('/<int:id_socio>/editar/', methods=['GET', 'POST'])
@login_required
@tenant_required
@requiere_permiso('socios.editar')
def editar_socio(id_socio):
    socio = Socio.query.filter_by(
        id=id_socio,
        agrupacion_id=g.agrupacion.id,
        activo=True
    ).first()
    if not socio:
        abort(404)

    tipos_socio = TipoSocio.query.filter_by(
        agrupacion_id=g.agrupacion.id,
        activo=True
    ).all()

    if request.method == 'POST':
        socio.nombre = request.form.get('nombre')
        socio.apellidos = request.form.get('apellidos')
        socio.documento_identidad = request.form.get('documento_identidad')
        socio.email = request.form.get('email')
        socio.telefono = request.form.get('telefono')
        socio.direccion = request.form.get('direccion')
        socio.cp = request.form.get('cp')
        socio.poblacion = request.form.get('poblacion')
        socio.provincia = request.form.get('provincia')
        tipo_id = request.form.get('tipo_socio_id')
        tipo = TipoSocio.query.filter_by(
            id=tipo_id,
            agrupacion_id=g.agrupacion.id,
            activo=True
        ).first()
        if tipo:
            socio.tipo_socio_id = tipo.id
        socio.fecha_alta = request.form.get('fecha_alta')
        socio.observaciones = request.form.get('observaciones')

        db.session.commit()

        flash(f'Socio {socio.nombre} {socio.apellido} actualizado correctamente', 'success')
        return redirect(url_for('socios.listar_socios'))

    return render_template('socios/socios_form.html',
                           socio=socio, tipos_socio=tipos_socio)

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