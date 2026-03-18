from flask import Flask
from .config import Config
from .extensions import db, migrate, login_manager, csrf
from app.services.permisos import tiene_permiso

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp)
    from .admin.routes import admin_bp
    app.register_blueprint(admin_bp)
    from .panel.routes import panel_bp
    app.register_blueprint(panel_bp)
    from .agrupaciones.routes import agrupaciones_bp
    app.register_blueprint(agrupaciones_bp)

    @app.context_processor
    def inject_permisos():
        return dict(tiene_permiso=tiene_permiso)

    from app.models import Usuario
    @login_manager.user_loader
    def cargar_usuario(usuario_id):
        return Usuario.query.get(int(usuario_id))

    return app