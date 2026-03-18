from app.extensions import db
from .base import BaseModel
from app.models.membresia_permiso import membresias_permisos

class Membresia(BaseModel):

    __tablename__ = 'membresias'

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    agrupacion_id = db.Column(db.Integer, db.ForeignKey('agrupaciones.id'), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    usuario = db.relationship('Usuario', back_populates='membresias')
    agrupacion = db.relationship('Agrupacion', back_populates='membresias')
    rol = db.relationship('Rol')
    permisos = db.relationship('Permiso', secondary=membresias_permisos, back_populates='membresias')
