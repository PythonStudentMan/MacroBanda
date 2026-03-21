import secrets
from flask import Blueprint, render_template, session, request, redirect, url_for, flash, abort
from flask_login import login_required
from app.models import Membresia, Rol, Invitacion, Permiso, Usuario
from app.extensions import db
from app.utils.decorators import tenant_required, requiere_permiso
from app.services.auditoria import registrar_accion
from app.services.email import enviar_invitacion
from datetime import datetime, timezone, timedelta

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@usuarios_bp.route('/')
@login_required
@tenant_required
@requiere_permiso('usuarios.ver')
def listar():
    agrupacion_id = session.get('agrupacion_activa')

    search = request.args.get('search', '')

    query = Membresia.query.filter_by(
        agrupacion_id=agrupacion_id,
        activo=True
    )

    if search:
        query = query.join(Membresia.usuario).filter(
            Usuario.email.ilike(f"%(search)%")
        )

    page = request.args.get('page', 1, type=int)

    pagination = query.paginate(page=page, per_page=10)

    return render_template(
        'usuarios/listar.html',
        membresias=pagination.items,
        pagination=pagination,
        search=search
    )

@usuarios_bp.route('/<int:membresia_id>/editar/', methods=['GET', 'POST'])
@login_required
@tenant_required
@requiere_permiso('usuarios.editar')
def editar_membresia(membresia_id):
    membresia = Membresia.query.get_or_404(membresia_id)

    if membresia.agrupacion_id != session.get('agrupacion_activa'):
        abort(403)

    if request.method == 'POST':
        rol_id = request.form.get('rol_id')
        rol = Rol.query.get(rol_id)
        membresia.rol = rol

        permisos_ids = request.form.getlist('permisos')
        permisos = Permiso.query.filter(Permiso.id.in_(permisos_ids)).all()
        membresia.permisos = permisos

        db.session.commit()
        flash('Rol actualizado', 'success')
        return redirect(url_for('usuarios.listar'))

    roles = Rol.query.filter_by(agrupacion_id=session.get('agrupacion_activa')).all()
    permisos = Permiso.query.all()
    return render_template('usuarios/editar.html', membresia=membresia, roles=roles, permisos=permisos)

@usuarios_bp.route('/<int:membresia_id>/eliminar/')
@login_required
@tenant_required
@requiere_permiso('usuarios.eliminar')
def eliminar(membresia_id):

    membresia = Membresia.query.get_or_404(membresia_id)

    if membresia.agrupacion_id != session.get('agrupacion_activa'):
        abort(403)

    membresia.soft_delete()

    db.session.commit()

    registrar_accion(
        accion='usuario.eliminado',
        entidad='membresia',
        entidad_id=membresia.id,
        descripcion=f"Usuario {membresia.usuario.email} eliminado"
    )

    flash('Usuario eliminado', 'success')

    return redirect(url_for('usuarios.listar'))

@usuarios_bp.route('/<int:membresia_id>/restaurar/')
@login_required
@tenant_required
@requiere_permiso('usuarios.editar')
def restaurar(membresia_id):

    membresia = Membresia.query.get_or_404(membresia_id)

    membresia.activo = True

    db.session.commit()

    flash('Usuario restaurado', 'success')

    return redirect(url_for('usuarios.listar'))



@usuarios_bp.route('/invitaciones/')
@login_required
@tenant_required
@requiere_permiso('usuarios.invitar')
def invitaciones():
    agrupacion_id = session.get('agrupacion_activa')

    invitaciones = Invitacion.query.filter_by(
        agrupacion_id=agrupacion_id,
        activo=True
    ).order_by(Invitacion.created_at.desc()).all()

    return render_template(
        'usuarios/invitaciones.html',
        invitaciones=invitaciones
    )


@usuarios_bp.route('/invitar/', methods=['GET', 'POST'])
@login_required
@tenant_required
@requiere_permiso('usuarios.invitar')
def invitar():
    if request.method == 'POST':
        email = request.form.get('email')
        agrupacion_id = session.get('agrupacion_activa')
        rol = Rol.query.filter_by(nombre='miembro', agrupacion_id=agrupacion_id).first()
        token = secrets.token_urlsafe(32)
        link = url_for('auth.aceptar_invitacion', token=token, _external=True)

        invitacion = Invitacion(
            email=email,
            agrupacion_id=agrupacion_id,
            rol=rol,
            token=token
        )

        db.session.add(invitacion)
        db.session.commit()
        registrar_accion(
            accion='usuario.invitado',
            entidad='usuario',
            descripcion=f"Invitado {email}"
        )

        enviar_invitacion(email, invitacion.token)

        return render_template('usuarios/invitacion_creada.html', link=link, email=email)

    return render_template('usuarios/invitar.html')


@usuarios_bp.route('/invitacion/<int:id_invitacion>/reenviar/')
@login_required
@tenant_required
@requiere_permiso('usuarios.invitar')
def reenviar_invitacion(id_invitacion):
    invitacion = Invitacion.query.get_or_404(id_invitacion)

    # Nueva expiración
    invitacion.expira_en = datetime.now(timezone.utc) + timedelta(days=2)

    db.session.commit()

    enviar_invitacion(invitacion.email, invitacion.token)
    print(f"Reenviar invitación: /auth/invitar/{invitacion.token}")

    flash('Invitación reenviada', 'success')
    return redirect(url_for('usuarios.invitacines'))