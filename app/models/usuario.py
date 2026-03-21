from .base import BaseModel
from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Usuario(UserMixin, BaseModel):

    __tablename__ = 'usuarios'

    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    nombre = db.Column(db.String(120), nullable=True)

    es_root = db.Column(db.Boolean, default=False)

    __table_args__ = (db.UniqueConstraint ('email', name='uix_email_usuario'),)

    membresias = db.relationship('Membresia', back_populates='usuario')
    auditorias = db.relationship('Auditoria', back_populates='usuario')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
