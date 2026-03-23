from flask import Blueprint, session, render_template, redirect, url_for, flash, g, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from app.extensions import db
from app.models import Agrupacion, Membresia, Auditoria, Rol
from app.utils.decorators import tenant_required, requiere_permiso


panel_bp = Blueprint('panel', __name__, url_prefix='/panel')

@login_required
@panel_bp.route('/')
def panel_inicio():
    # Caso ROOT
    if current_user.es_root:
        return redirect(url_for('admin.dashboard'))

    if g.get('agrupacion'):
        session['agrupacion_activa'] = g.agrupacion.id
        return redirect(url_for('panel.dashboard'))

    # Buscamos membresías del usuario
    membresias = Membresia.query.filter_by(usuario_id=current_user.id, activo=True).all()

    if not membresias:
        flash('No perteneces a ninguna agrupación.', 'warning')
        return redirect(url_for('auth.login'))

    # Si solo tiene una agrupación, activarla automáticamente
    if len(membresias) == 1:
        session['agrupacion_activa'] = membresias[0].agrupacion_id
        return redirect(url_for('panel.dashboard'))

    return render_template('panel/seleccionar_agrupacion.html', membresias=membresias)

@login_required
@panel_bp.route('/seleccionar/<int:agrupacion_id>/')
def activar_agrupacion(agrupacion_id):
    # Validar que el usuario pertenece a esa agrupación
    membresia = Membresia.query.filter_by(
        usuario_id=current_user.id,
        agrupacion_id=agrupacion_id,
        activo=True
    ).first()

    if not membresia:
        flash('No tienes acceso a esta agrupación', 'danger')
        return redirect(url_for('panel.panel_inicio'))

    # Guardar en sesión actual
    session['agrupacion_activa'] = agrupacion_id
    flash(f'Agrupación "{membresia.agrupacion.nombre}" activada', 'success')
    return redirect(url_for('panel.dashboard'))

@panel_bp.route('/dashboard/')
@login_required
@tenant_required
def dashboard():
    agrupacion_id = g.agrupacion.id if g.get('agrupacion') else session.get('agrupacion_activa')
    agrupacion = Agrupacion.query.get_or_404(agrupacion_id)

    # Métricas
    total_usuarios = Membresia.query.filter_by(
        agrupacion_id=agrupacion_id,
        activo=True
    ).count()

    total_roles = Rol.query.filter_by(
        agrupacion_id=agrupacion_id,
        activo=True
    ).count()

    usuarios_por_mes = db.session.query(
        func.strftime('%Y-%m', Membresia.created_at),
        func.count(Membresia.id)
    ).filter(
        Membresia.agrupacion_id == agrupacion_id
    ).group_by(
        func.strftime('%Y-%m', Membresia.created_at)
    ).all()

    labels = [u[0] for u in usuarios_por_mes]
    valores = [u[1] for u in usuarios_por_mes]

    # Actividad Reciente
    actividad = Auditoria.query.filter_by(
        agrupacion_id=agrupacion_id
    ).order_by(Auditoria.created_at.desc()).limit(5).all()

    return render_template(
        'panel/dashboard.html',
        agrupacion=agrupacion,
        total_usuarios=total_usuarios,
        total_roles=total_roles,
        actividad=actividad,
        labels=labels,
        valores=valores
    )


@panel_bp.route('/auditoria/')
@login_required
@tenant_required
@requiere_permiso('auditoria.ver')
def auditoria():
    logs = Auditoria.query.filter_by(
        agrupacion_id=g.agrupacion.id
    ).order_by(Auditoria.created_at.desc()).limit(50).all()

    return render_template(
        'panel/auditoria.html', logs=logs
    )