from datetime import date, timedelta
from flask import g
from app.extensions import db
from app.models import Cuota, Socio

# Lista de hooks para módulos adicionales
HOOKS_CUOTAS = []

def registrar_hook(func):
    """
    Permite registrar un hook que genere cuotas de otro módulo.
    Cada hook debe recibir 'hasta_fecha' como parámetro
    """
    HOOKS_CUOTAS.append(func)
    return func

def generar_cuotas_global(hasta_fecha: date = None):
    """
    Genera todas las cuotas pendientes de todos los módulos hasta una fecha determinada.
    """
    if hasta_fecha is None:
        hasta_fecha = date.today()

    # Cuotas de Socios
    socios = Socio.query.filter_by(agrupacion_id=g.agrupacion.id, activo=True).all()
    for socio in socios:
        generar_cuotas_socio(socio, hasta_fecha)

    # Ejecutar hooks de otros módulos
    for hook in HOOKS_CUOTAS:
        hook(hasta_fecha)


def generar_cuotas_socio(socio, hasta_fecha: date):
    """
    Genera cuotas tipo 'socio' para un socio concreto hasta la fecha indicada.
    """
    config = socio.tipo_socio.configuracion_cuota
    if not config or not config.tiene_cuota:
        return

    fecha_actual = socio.fecha_alta

    while fecha_actual <= hasta_fecha:
        # Evitamos duplicados
        existe = Cuota.query.filter_by(
            socio_id=socio.id,
            tipo='socio',
            fecha=fecha_actual,
            agrupacion_id=socio.agrupacion_id
        ).first()
        if not existe:
            cuota = Cuota(
                socio_id=socio.id,
                tipo='socio',
                fecha=fecha_actual,
                importe=config.importe,
                descripcion=f"Cuota {config.frecuencia}",
                agrupacion_id=socio.agrupacion_id
            )
            db.session.add(cuota)

        # Avanzar según frecuencia
        frecuencia_dias = {
            'unico': 0,
            'mensual': 30,
            'bimensual': 60,
            'trimestral': 90,
            'cuatrimestral': 120,
            'semestral': 180,
            'anual': 365,
            'quincenal': 15,
            'semanal': 7,
        }
        dias = frecuencia_dias.get(config.frecuencia.lower())
        if dias:
            fecha_actual += timedelta(days=dias)
        else:
            break

    db.session.commit()

