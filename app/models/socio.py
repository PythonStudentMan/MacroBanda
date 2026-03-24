from app.extensions import db
from .tenant import TenantModel

class Socio(TenantModel):

    __tablename__ = 'socios'

    # Identificación
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(150), nullable=True)
    documento_identidad = db.Column(db.String(20), nullable=True)

    # Contacto
    email = db.Column(db.String(120), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    direccion = db.Column(db.String(255), nullable=True)
    cp = db.Column(db.String(10), nullable=True)
    poblacion = db.Column(db.String(30), nullable=True)
    provincia = db.Column(db.String(30), nullable=True)

    # Relación con la Agrupación
    tipo_socio_id = db.Column(db.Integer, db.ForeignKey('tipos_socio.id'), nullable=False)
    tipo_socio = db.relationship('TipoSocio')

    fecha_alta = db.Column(db.Date, nullable=False)
    fecha_baja = db.Column(db.Date, nullable=True)

    # Configuración individual
    metodo_cobro = db.Column(db.String(50), nullable=True)

    # Estado
    observaciones = db.Column(db.Text, nullable=True)