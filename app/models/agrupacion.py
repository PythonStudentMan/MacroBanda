from app.extensions import db
from .base import BaseModel

class Agrupacion(BaseModel):

    __tablename__ = 'agrupaciones'

    nombre = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    __table_args__ = (db.UniqueConstraint('slug', name='uix_agrupacion_slug'),)
    cif = db.Column(db.String(20))

    direccion = db.Column(db.String(200))
    cp = db.Column(db.String(10))
    poblacion = db.Column(db.String(40))
    provincia = db.Column(db.String(40))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    web = db.Column(db.String(120))

    configuracion = db.relationship('ConfiguracionAgrupacion', back_populates='agrupacion', uselist=False)
    subagrupaciones = db.relationship('Subagrupacion', back_populates='agrupacion')
    membresias = db.relationship('Membresia', back_populates='agrupacion')
    roles = db.relationship('Rol', back_populates='agrupacion')
