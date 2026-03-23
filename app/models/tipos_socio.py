from enum import Enum

from sqlalchemy.orm import declared_attr

from app.extensions import db
from .tenant import TenantModel
from .forma_pago import FormaPago

class FrecuenciaCuota(str, Enum):
    UNICA = 'única'
    SEMANAL = 'semanal'
    QUINCENAL = 'quincenal'
    MENSUAL = 'mensual'
    BIMENSUAL = 'bimensual'
    TRIMESTRAL = 'trimestral'
    CUATRIMESTRAL = 'cuatrimestral'
    SEMESTRAL = 'semestral'
    ANUAL = 'anual'

class TipoSocio(TenantModel):

    __tablename__ = 'tipos_socio'

    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(200), nullable=True)
    orden = db.Column(db.Integer, default=0, nullable=False)

    requiere_cuota = db.Column(db.Boolean, default=True, nullable=False)
    frecuencia = db.Column(db.Enum(FrecuenciaCuota), nullable=True)
    importe = db.Column(db.Numeric(10, 2), nullable=True)

    color_hex = db.Column(db.String(7), nullable=True)
    icono = db.Column(db.String(50), nullable=True)

    @declared_attr
    def formas_pago(cls):
        return db.relationship(
            FormaPago,
            secondary='tipos_socio_formas_pago',
            back_populates='tipos_socio',
            lazy='dynamic',
            cascade='all, delete-orphan',
        )

    __table_args__ = (db.UniqueConstraint('agrupacion_id', 'nombre', name='uix_tipos_socio_agrupacion_nombre'),)

    def __repr__(self):
        return f'<TipoSocio {self.nombre} ({self.frecuencia or "Sin Cuota"})>'