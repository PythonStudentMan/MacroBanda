from datetime import datetime, timezone
from app.extensions import db

class BaseModel(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    created_by = db.Column(db.Integer, nullable=True)

    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc), nullable=False
    )
    update_by = db.Column(db.Integer, nullable=True)

    activo = db.Column(db.Boolean, default=True)

    def soft_delete(self):
        self.activo = False
