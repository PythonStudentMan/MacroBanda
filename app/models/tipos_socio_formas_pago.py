from app.extensions import db

tipos_socio_formas_pago = db.Table(
    'tipos_socio_formas_pago',
    db.Column('tipo_socio_id', db.Integer, db.ForeignKey('tipos_socio.id'), primary_key=True),
    db.Column('forma_pago_id', db.Integer, db.ForeignKey('formas_pago.id'), primary_key=True)
)