from flask import Blueprint, session, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Agrupacion, Membresia
from app.utils.decorators import tenant_required

panel_bp = Blueprint('panel', __name__, url_prefix='/panel')

@login_required
@panel_bp.route('/')
def panel_inicio():

    # Caso ROOT
    if current_user.es_root:
        return redirect(url_for('admin.dashboard'))

    # Buscamos membresías del usuario
    membresias = Membresia.query.filter_by(usuario_id=current_user.id).all()

    if not membresias:
        flash('No perteneces a ninguna agrupación. Solicita una invitación.', 'warning')
        return redirect(url_for('auth.login'))

    # Si solo tiene una agrupación, activarla automáticamente
    if len(membresias) == 1:
        session['agrupacion_activa'] = membresias[0].agrupacion_id
        return redirect(url_for('panel.dashboard'))

    # Si tiene varias, seleccionar con qué agrupación quiere trabajar en esta sesión
    return render_template('panel/seleccionar_agrupacion.html', membresias=membresias)

@login_required
@tenant_required
@panel_bp.route('/seleccioanr/<int:agrupacion_id>/')
def activar_agrupacion(agrupacion_id):
    # Validar que el usuario pertenece a esa agrupación
    membresia = Membresia.query.filter_by(usuario_id=current_user.id, agrupacion_id=agrupacion_id).first()

    if not membresia:
        flash('No tienes acceso a esta agrupación', 'danger')
        return redirect(url_for('panel.panel_inicio'))

    # Guardar en sesión actual
    session['agrupacion_activa'] = agrupacion_id
    flash(f'Agrupación "{membresia.agrupacion.nombre}" activada', 'success')
    return redirect(url_for('panel.dashboard'))

@login_required
@tenant_required
@panel_bp.route('/dashboard/')
def dashboard():
    agrupacion_id = session.get('agrupacion_activa')
    if not agrupacion_id:
        flash('Debe seleccionar una agrupación activa', 'warning')
        return redirect(url_for('panel.panel_inicio'))

    agrupacion = Agrupacion.query.get(agrupacion_id)
    return render_template('panel/dashboard.html', agrupacion=agrupacion)