from app.extensions import db
from .base import BaseModel

class Permiso(BaseModel):

    __tablename__ = 'permisos'

    nombre = db.Column(db.String(50), nullable=False)
    codigo = db.Column(db.String(50), nullable=False)

    roles = db.relationship('Rol', secondary='roles_permisos', back_populates='permisos')
    membresias = db.relationship('Membresia', secondary='membresias_permisos', back_populates='permisos')