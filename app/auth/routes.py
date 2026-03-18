from flask import Blueprint, render_template, redirect, url_for, session
from flask_login import login_user, logout_user, login_required
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
            return redirect(url_for('panel.panel_inicio'))

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout/')
@login_required
def logout():
    logout_user()
    session.pop('usuario')
    session.pop('current_user')
    return redirect(url_for('auth.login'))

@auth_bp.route('/invitar/<token>')
def aceptar_invitacion(token):
    invitacion = Invitacion.query.filter_by(token=token, aceptada=False).first_or_404()
    usuario = Usuario.query.filter_by(email=invitacion.email).first()

    if not usuario:
        usuario = Usuario(email=invitacion.email, nombre=invitacion.email.split('@')[0])
        db.session.add(usuario)
        db.session.flush()

    membresia = Membresia(
        usuario_id=usuario.id,
        agrupacion_id=invitacion.agrupacion_id,
        rol=invitacion.rol
    )
    db.session.add(membresia)
    invitacion.aceptada = True
    db.session.commit()

    return 'Invitación aceptada. Ahora puedes iniciar sesión.'