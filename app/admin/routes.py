import secrets
from flask import Blueprint, render_template, abort, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Usuario, Agrupacion, Membresia, Invitacion, Rol, Permiso
from app.utils.slug import generar_slug
from app.services.auditoria import registrar_accion

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

print ('IMPORTANDO ADMIN ROUTES')

@admin_bp.route('/dashboard/')
@login_required
def dashboard():
    if not current_user.es_root:
        abort(403)

    return render_template('admin/dashboard.html')

@admin_bp.route('/agrupaciones/crear/', methods=['GET', 'POST'])
@login_required
def crear_agrupacion():
    if not current_user.es_root:
        abort(403)

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email_admin = request.form.get('email').lower().strip()

        if not nombre or not email_admin:
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(request.url)

        slug = generar_slug(nombre)

        # Evitar duplicados
        if Agrupacion.query.filter_by(slug=slug).first():
            flash('Ya existe una agrupación con ese nombre', 'warning')
            return redirect(request.url)

        # Buscar o crear usuario
        usuario = Usuario.query.filter_by(email=email_admin).first()

        if not usuario:
            password_temp = secrets.token_urlsafe(12)
            usuario = Usuario(
                nombre = email_admin.split("@")[0],
                email=email_admin
            )
            usuario.set_password(password_temp)
            db.session.add(usuario)
            db.session.flush()

        # Crear agrupación
        agrupacion = Agrupacion(nombre=nombre, slug=slug, subdominio=slug)
        db.session.add(agrupacion)
        db.session.flush()

        # Crear roles propios de la agrupación
        rol_superadmin = crear_roles_base(agrupacion)

        # Crear membresía del usuario como SuperAdmin
        membresia = Membresia(
            usuario_id = usuario.id,
            agrupacion_id = agrupacion.id,
            rol=rol_superadmin
        )
        db.session.add(membresia)

        db.session.commit()


        registrar_accion(
            accion='agrupacion.creada',
            entidad='agrupacion',
            entidad_id=agrupacion.id,
            descripcion=f"Agrupacion {agrupacion.nombre}"
        )

        flash('Agrupación creada correctamente', 'success')
        return redirect(url_for('admin.listar_agrupaciones'))

    return render_template('admin/crear_agrupaciones.html')

@admin_bp.route('/agrupaciones/')
@login_required
def listar_agrupaciones():
    if not current_user.es_root:
        abort(403)

    agrupaciones = Agrupacion.query.all()
    return render_template('admin/listar_agrupaciones.html', agrupaciones=agrupaciones)

@admin_bp.route('/agrupaciones/<int:id>/invitar/', methods=['GET', 'POST'])
@login_required
def invitar_usuario(id):
    if not current_user.es_root:
        abort(403)

    agrupacion = Agrupacion.query.get_or_404(id)

    if request.method == 'POST':
        email = request.form.get('email').lower().strip()

        invitacion = Invitacion(email=email, agrupacion_id=agrupacion.id)
        db.session.add(invitacion)
        db.session.commit()

        flash('Invitación creada (simulada)', 'success')

    return render_template('admin/invitar.html', agrupacion=agrupacion)

def crear_roles_base(agrupacion):

    permisos = Permiso.query.all()
    permisos_dict = {p.codigo: p for p in permisos}

    # SUPERADMIN
    rol_superadmin = Rol(
        nombre='superadmin',
        agrupacion_id=agrupacion.id
    )
    rol_superadmin.permisos = permisos

    # ADMIN
    rol_admin = Rol(
        nombre='admin',
        agrupacion_id=agrupacion.id
    )
    rol_admin.permisos = [
        p for p in permisos if not p.codigo.startswith('configuracion')
    ]

    # MIEMBRO
    rol_miembro = Rol(
        nombre='miembro',
        agrupacion_id=agrupacion.id
    )
    rol_miembro.permisos = [
        permisos_dict['dashboard.ver']
    ]

    db.session.add_all([rol_superadmin, rol_admin, rol_miembro])
    db.session.flush()

    return rol_superadmin
