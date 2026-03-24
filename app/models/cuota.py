from app.extensions import db
from .tenant import TenantModel

class Cuota(TenantModel):

    __tablename__ = 'cuotas'

    # A quién pertenece (si es socio)
    socio_id = db.Column(db.Integer, db.ForeignKey('socios.id'), nullable=True)
    socio = db.relationship('Socio')

    # Tipo de cuota (Clave)
    tipo = db.Column(db.String(50), nullable=False) # 'Socio', 'Educando', 'Evento', 'Fianza'

    # Referencia al origen
    referencia_id = db.Column(db.Integer, nullable=True) # id de actividad, evento, etc.

    # Datos económicos
    fecha = db.Column(db.Date, nullable=False)
    importe = db.Column(db.Numeric(10, 2), nullable=False)

    estado = db.Column(db.String(20), default='pendiente')
    descripcion = db.Column(db.String(255), nullable=True)