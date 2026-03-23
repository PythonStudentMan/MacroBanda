from sqlalchemy.orm import declared_attr

from app.extensions import db
from .base import BaseModel

class TenantModel(BaseModel):

    __abstract__ = True

    agrupacion_id = db.Column(db.Integer, db.ForeignKey('agrupaciones.id'), nullable=False)

    @declared_attr
    def agrucacion(cls):
        return db.relationship('Agrupacion')