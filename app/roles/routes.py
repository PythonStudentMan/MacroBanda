from flask import Blueprint, render_template, session, request, redirect, url_for, flash, abort
from flask_login import login_required
from app.extensions import db
from app.models import Rol, Permiso, Membresia
from app.utils.decorators import tenant_required, requiere_permiso
from app.services.auditoria import registrar_accion

roles_bp = Blueprint('roles', __name__, url_prefix='/roles')

@roles_bp.route('/')
@login_required
@tenant_required
@requiere_permiso('roles.ver')
def listar():
    agrupacion_id = session.get('agrupacion_activa')

    search = request.args.get('search', '')

    query = Rol.query.filter_by(agrupacion_id=agrupacion_id)

    if search:
        query = query.join(Membresia.rol).filter(
            Rol.nombre.ilike(f"%(search)%")
        )

    page = request.args.get('page', 1, type=int)

    pagination = query.paginate(page=page, per_page=10)

    render_template(
        'roles/listar.html',
        roles=pagination.items,
        pagination=pagination,
        search=search
    )

@roles_bp.route('/crear/', methods=['GET', 'POST'])
@login_required
@tenant_required
@requiere_permiso('roles.crear')
def crear():

    if request.method == 'POST':
        agrupacion_id = session.get('agrupacion_activa')
        nombre = request.form.get('nombre')
        rol = Rol(nombre=nombre, agrupacion_id=agrupacion_id)

        permisos_ids = request.form.getlist('permisos')
        permisos = Permiso.query.filter(Permiso.id.in_(permisos_ids)).all()
        rol.permisos = permisos

        db.session.add(rol)
        db.session.commit()

        registrar_accion(
            accion='rol.creado',
            entidad='rol',
            entidad_id=rol.id,
            descripcion=f"Rol {rol.nombre} creado"
        )

        flash('Rol creado correctamente', 'success')
        return redirect(url_for('roles.listar'))

    permisos = Permiso.query.all()

    return render_template('roles/crear.html', permisos=permisos)

@roles_bp.route('/<int:rol_id>/editar/', methods=['GET', 'POST'])
@login_required
@tenant_required
@requiere_permiso('roles.editar')
def editar(rol_id):
    rol = Rol.query.get_or_404(rol_id)

    # Seguridad
    if rol.agrupacion_id != session.get('agrupacion_activa'):
        abort(403)

    if request.method == 'POST':
        rol.nombre = request.form.get('nombre')
        permisos_ids = request.form.getlist('permisos')

        permisos = Permiso.query.filter(Permiso.id.in_(permisos_ids)).all()
        rol.permisos = permisos

        db.session.commit()

        flash('Rol actualizado', 'success')
        return redirect(url_for('roles.listar'))

    permisos = Permiso.query.all()
    return render_template('roles/editar.html', rol=rol, permisos=permisos)