from app.extensions import db
from .base import BaseModel

class Subagrupacion(BaseModel):

    __tablaname__ = 'subagrupaciones'

    nombre = db.Column(db.String(50), nullable=False)
    agrupacion_id = db.Column(db.Integer, db.ForeignKey('agrupaciones.id'), nullable=False)
    agrupacion = db.relationship('Agrupacion', back_populates='subagrupaciones', lazy=True)