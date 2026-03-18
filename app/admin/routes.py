from flask import Blueprint, render_template, abort, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Usuario, Agrupacion, Membresia, Invitacion
from app.utils.slug import generar_slug

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

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
            usuario = Usuario(
                nombre = email_admin.split("@")[0],
                email=email_admin
            )
            db.session.add(usuario)
            db.session.flush()

        # Crear agrupación
        agrupacion = Agrupacion(nombre=nombre, slug=slug)
        db.session.add(agrupacion)
        db.session.flush()

        # Crear membresía del usuario como SuperAdmin
        membresia = Membresia(
            usuario_id = usuario.id,
            agrupacion_id = agrupacion.id,
            rol='superadmin'
        )
        db.session.add(membresia)

        db.session.commit()

        flash('Agrupación creada correctamente', 'success')
        return redirect(url_for('admin.listar_agrupaciones'))

    return render_template('admin/crear.html')

@admin_bp.route('/agrupaciones/')
@login_required
def listar_agrupaciones():
    if not current_user.es_root:
        abort(403)

    agrupaciones = Agrupacion.query.all()
    return render_template('admin/listar.html', agrupaciones=agrupaciones)

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
