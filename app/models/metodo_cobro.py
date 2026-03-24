from app.extensions import db
from .tenant import TenantModel

class MetodoCobro(TenantModel):

    __tablename__ = 'metodos_cobro'

    nombre = db.Column(db.String(50), nullable=False)
