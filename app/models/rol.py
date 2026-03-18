from app.extensions import db
from .base import BaseModel
from .rol_permiso import roles_permisos

class Rol(BaseModel):

    __tablename__ = 'roles'

    nombre = db.Column(db.String(50), nullable=False)
    agrupacion_id = db.Column(db.Integer, db.ForeignKey('agrupaciones.id'), nullable=False)

    agrupacion = db.relationship('Agrupacion', back_populates='roles')
    permisos = db.relationship('Permiso', secondary=roles_permisos, back_populates='roles')