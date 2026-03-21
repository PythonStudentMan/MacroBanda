from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from flask_login import login_user, logout_user, login_required
from datetime import datetime, timezone
from app.extensions import db
from app.models import Usuario, Invitacion, Membresia
from app.auth.forms import FormularioLogin


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
    form = FormularioLogin()

    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(
            email=form.email.data
        ).first()

        if usuario and usuario.check_password(form.password.data):
            login_user(usuario)
            if usuario.es_root:
                return redirect(url_for('admin.dashboard'))

            return redirect(url_for('panel.panel_inicio'))

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout/')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/invitar/<token>', methods= ['GET', 'POST'])
def aceptar_invitacion(token):

    invitacion = Invitacion.query.filter_by(
        token=token,
        aceptada=False
    ).first_or_404()

    # Comprobamos expiración
    if invitacion.expira_en < datetime.now(timezone.utc):
        return "Invitación expirada"

    if request.method == 'POST':

        password = request.form.get('password')

        # Buscar usuario
        usuario = Usuario.query.filter_by(
            email=invitacion.email
        ).first()

        # Si no existe lo creamos
        if not usuario:
            usuario = Usuario(email=invitacion.email)
            usuario.set_password(password)
            db.session.add(usuario)
            db.session.flush()
        else:
            usuario.set_password(password)

        # Crear membresía
        membresia = Membresia(
            usuario_id=usuario.id,
            agrupacion_id=invitacion.agrupacion_id,
            rol=invitacion.rol
        )

        db.session.add(membresia)

        invitacion.aceptada = True

        db.session.commit()

        # Login automático
        login_user(usuario)

        flash('Cuenta creada correctamente', 'success')
        return redirect(url_for('panel.panel_inicio'))

    return render_template(
        'auth/aceptar_invitacion.html',
        token=token,
        email=invitacion.email
    )
