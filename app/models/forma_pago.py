from app.extensions import db
from .tenant import TenantModel

class FormaPago(TenantModel):

    __tablename__ = 'formas_pago'

    nombre = db.Column(db.String(80), nullable=False, unique=False)
    descripcion = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<FormaPago {self.nombre}>'