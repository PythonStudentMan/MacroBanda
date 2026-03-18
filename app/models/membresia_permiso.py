from app.extensions import db

membresias_permisos = db.Table(
    'membresias_permisos',
    db.Column('membresia_id', db.Integer, db.ForeignKey('membresias.id'), primary_key=True),
    db.Column('permiso_id', db.Integer, db.ForeignKey('permisos.id'), primary_key=True)
)
