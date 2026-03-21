from app.extensions import db
from .base import BaseModel

class Auditoria(BaseModel):

    __tablename__ = 'auditorias'

    agrupacion_id = db.Column(db.Integer, db.ForeignKey('agrupaciones.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    accion = db.Column(db.String(100), nullable=False)
    entidad = db.Column(db.String(100))
    entidad_id = db.Column(db.Integer)

    descripcion = db.Column(db.Text)

    usuario = db.relationship('Usuario', back_populates='auditorias')
    agrupacion = db.relationship('Agrupacion', back_populates='auditorias')