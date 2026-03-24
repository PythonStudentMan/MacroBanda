from app.extensions import db
from .tenant import TenantModel

class ConfiguracionCuota(TenantModel):

    __tablename__ = 'configuraciones_cuotas'

    tipo_socio_id = db.Column(db.Integer, db.ForeignKey('tipos_socio.id'), nullable=False)
    importe = db.Column(db.Numeric(10, 2), nullable=False)
    frecuencia = db.Column(db.String(20), nullable=False)

    tipo_socio = db.relationship('TipoSocio', back_populates='configuracion_cuota')