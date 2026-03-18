from app.extensions import db
from .base import BaseModel
import uuid

class Invitacion(BaseModel):

    __tablename__ = 'invitaciones'

    email = db.Column(db.String(120), nullable=False)
    token = db.Column(db.String(200), default=lambda: str(uuid.uuid4()), nullable=False)
    __table_args__ = (db.UniqueConstraint('token', name='uix_token_invitacion'),)

    agrupacion_id = db.Column(db.Integer, db.ForeignKey('agrupaciones.id'), nullable=False)
    agrupacion = db.relationship('Agrupacion')

    rol = db.Column(db.String(50), default='miembro')
    aceptada = db.Column(db.Boolean, default=False)


