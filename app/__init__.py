import requests_toolbelt.adapters.host_header_ssl
from flask import Flask, g, request, render_template
from .config import Config
from .extensions import db, migrate, login_manager, csrf, mail
from app.services.permisos import tiene_permiso
from app.utils.tenant import cargar_tenant
from app.context_processors import inject_agrupacion, inject_membresias

def create_app(config: dict | None = None):
    """
    Factory de la app. Si se pasa 'config' (dict), se aplica antes de inicializar
    las extensiones para que los tests puedan forzar settings como
    SQLALCHEMY_DATABASE_URI o TESTING
    """
    app = Flask(__name__, instance_relative_config=True)

    # Cargar configuración por defecto desde la clase Config
    app.config.from_object(Config)

    # Si nos pasan overrides (tests), aplicarlos
    if config:
        app.config.update(config)

    # Inicializar extensiones después de aplicar la configuración
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    # Detector de Tenant
    @app.before_request
    def before_request():
        cargar_tenant()

    # RUTA RAIZ
    @app.route('/')
    def home():
        if g.get('agrupacion'):
            return f"Tenant activo: {g.agrupacion.nombre}"
        return "Landing pública - MacroBandas"

    # Blueprints
    from .admin.routes import admin_bp
    from .panel.routes import panel_bp
    from .auth.routes import auth_bp
    from .configuracion.routes import configuracion_bp
    from .agrupaciones.routes import agrupaciones_bp
    from .roles.routes import roles_bp
    from .usuarios.routes import usuarios_bp
    from .errors.handlers import errors_bp
    from .socios.routes import socios_bp

    app.register_blueprint(admin_bp)
    app.register_blueprint(panel_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(configuracion_bp)
    app.register_blueprint(agrupaciones_bp)
    app.register_blueprint(roles_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(socios_bp)

    app.context_processor(inject_agrupacion)
    app.context_processor(inject_membresias)

    from app.models import Usuario
    @login_manager.user_loader
    def cargar_usuario(usuario_id):
        return Usuario.query.get(int(usuario_id))

    app.jinja_env.globals['tiene_permiso'] = tiene_permiso

    return app