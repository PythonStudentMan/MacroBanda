from sqlalchemy.orm import foreign

from app.extensions import db
from .base import BaseModel

class ConfiguracionAgrupacion(BaseModel):

    __tablename__ = 'configuraciones_agrupaciones'

    agrupacion_id = db.Column(db.Integer, db.ForeignKey('agrupaciones.id'), nullable=False)
    agrupacion = db.relationship('Agrupacion', back_populates='configuracion', uselist=False)
    __table_args__ = (db.UniqueConstraint('agrupacion_id', name='uix_agrupacion_configuracion'),)

    remesas_sepa = db.Column(db.Boolean, default=True, nullable=False)
    iban = db.Column(db.String(50))
    sufijo = db.Column(db.String(10))

    logo = db.Column(db.String(255))
    color_primario = db.Column(db.String(7), default="#0d6efd")
    color_secundario = db.Column(db.String(7), default="#6c757d")
    color_fondo = db.Column(db.String(7), default="#ffffff")
    color_texto = db.Column(db.String(7), default="#000000")

    forma_pago_id = db.Column(db.Integer, db.ForeignKey('formas_pago.id', name='fk_config_agrupacion_forma_pago_id'), nullable=True)
    forma_pago = db.relationship(
        'FormaPago',
        foreign_keys=[forma_pago_id],
        uselist=False,
        back_populates='configuracion'
    )



