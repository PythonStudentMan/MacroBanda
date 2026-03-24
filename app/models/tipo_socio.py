from app.extensions import db
from .tenant import TenantModel

class TipoSocio(TenantModel):

    __tablename__ = 'tipos_socio'

    nombre = db.Column(db.String(50), nullable=False)
    tiene_cuota = db.Column(db.Boolean, default=False)

    configuracion_cuota = db.relationship(
        'ConfiguracionCuota',
        back_populates='tipo_socio',
        uselist=False,
        cascade='all, delete-orphan'
    )