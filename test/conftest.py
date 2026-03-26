import os
import sys
import inspect
import uuid
import pkgutil
import importlib
import pytest
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError

from app.models import TenantModel

# Aseguramos que la raiz del repo está en sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Intentos de import
try:
    from app import create_app
except Exception:
    try:
        from run import create_app
    except Exception:
        create_app = None

# Intantamos importar el objeto extensión de SQLAlchemy si existe
try:
    from app.extensions import db as _db
except Exception:
    _db = None

# cargar dinámicamente el paquete app.models para inspección
_models_mod = {}
try:
    import app.models as _models_pkg
    package_path = _models_pkg.__path__
    for finder, name, ispkg in pkgutil.iter_modules(package_path):
        full_name = f"app.models.{name}"
        try:
            mod = importlib.import_module(full_name)
            _models_mod[full_name] = mod
        except Exception:
            continue
    try:
        _models_mod["app.models.__init__"] = importlib.import_module("app.models")
    except Exception:
        pass
except Exception:
    try:
        mod = importlib.import_module("app.models")
        _models_mod["app.models"] = mod
    except Exception:
        _models_mod = {}

# Heurística para encontrar clases por nombre o por atributos
def find_model_by_name(name):
    for mod in _models_mod.values():
        for _, obj in getattr(mod, "__dict__", {}).items():
            if isinstance(obj, type) and obj.__name__ == name:
                return obj
    return None

def find_model_by_attrs(*attrs):
    for mod in _models_mod.values():
        for _, obj in getattr(mod, "__dict__", {}).items():
            if isinstance(obj, type):
                if all(hasattr(obj, a) for a in attrs):
                    return obj
    return None

# Detectar usuario y TipoSocio y TenantModel subclass
Usuario = find_model_by_name('Usuario') or find_model_by_attrs('email', 'password_hash')
TipoSocio = find_model_by_name('TipoSocio') or find_model_by_attrs('nombre')
TenantModel = find_model_by_name('TenantModel')
TenantConcrete = None
if TenantModel:
    for mod in _models_mod.values():
        for _, obj in getattr(mod, "__dict__", {}).items():
            try:
                if isinstance(obj, type) and obj is not TenantModel and any(base.__name__ == 'TenantModel' for base in obj.__mro__):
                    TenantConcrete = obj
                    break
            except Exception:
                continue

def _unique_email(base):
    return f'{base}+{uuid.uuid4().hex[:8]}@test.local'

@pytest.fixture(scope='session')
def app():
    if create_app is None:
        pytest.skip('No se encontró create_app. Ajusta la importación en tests/conftest')

    test_cfg = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
    }

    # Llamar create_app con config
    try:
        sig = inspect.signature(create_app)
        accepts_arg = any(
            p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD, p.VAR_KEYWORD)
            for p in sig.parameters.values()
        )
    except Exception:
        accepts_arg = False

    if accepts_arg:
        app = create_app(test_cfg)
    else:
        app = create_app()
        app.config.update(test_cfg)

    # Inicializar db si existe y comprobar que la URL es in-memory
    if _db is not None:
        try:
            _db.init_app(app)
        except Exception:
            pass

    # Comprobación de seguridad: si el engine ya existe, asegurar in-memory
    try:
        with app.app_context():
            if _db is not None and getattr(_db, 'engine', None) is not None:
                url = str(_db.engine.url)
                if url != 'sqlite:///:memory:':
                    raise RuntimeError(
                        'La base de datos configurada para tests NO es sqlite:///:memory:.'
                        'Asegúrate de ejecutar tests con la configuración de testing.'
                    )
    except RuntimeError:
        raise
    except Exception:
        pass

    return app

@pytest.fixture(scope='session')
def db(app):
    if _db is None:
        pytest.skip('No se encontró db en app.extensions. Ajusta import en tests/conftest.')

    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
def client(app, db):
    return app.test_client()

@pytest.fixture
def seed_data(app, db):
    """
    Crea:
      - 1 TipoSocio mínimo si existe el modelo correspondiente.
      - 2 tenants (si existe clase concreta que herede de TenantModel)
      - 3 usuarios: user1, user2 y admin (emails únicos)
      - TestResource temporal con 2 filas (tenant1 y tenant2)
    """
    # Importar módulos de modelos ya cargados
    # Buscar TipoSocio y Usuario dinámicamente (re-evaluar en runtime)
    Usuario_local = Usuario
    TipoSocio_local = TipoSocio
    TenantConcrete_local = TenantConcrete

    default_tipo = None
    if TipoSocio_local:
        try:
            default_tipo = TipoSocio_local()
            if hasattr(default_tipo, 'nombre'):
                default_tipo.nombre = 'por_defecto'
            if default_agrup and hasattr(default_tipo, 'agrupacion_id'):
                default_tipo.agrupacion_id = default_agrup.id
            if hasattr(default_tipo, 'activo'):
                default_tipo.activo = True
            db.session.add(default_tipo)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            default_tipo.nombre = f'por_defecto_{uuid.uuid4().hex[:6]}'
            db.session.add(default_tipo)
            db.session.commit()
        except Exception:
            db.session.rollback()
            default_tipo = None

    # Detectar clase concreta que herede de TenantModel (si la hay)
    tenants = []
    if TenantConcrete_local:
        try:
            t1 = TenantConcrete_local()
            t2 = TenantConcrete_local()
            if hasattr(t1, 'name'):
                t1.name = 'tenant1'
                t2.name = 'tenant2'
            if hasattr(t1, 'subdomain'):
                t1.subdomain = 't1'
                t2.subsomain = 't2'
            db.session.add_all([t1, t2])
            db.session.commit()
            tenants = [t1, t2]
        except Exception:
            db.session.rollback()
            tenants = []

    # Crear Usuarios con emails únicos
    if Usuario_local is None:
        Usuario_local = find_model_by_name('Usuario') or find_model_by_attrs('email', 'password_hash')

    if Usuario_local is None:
        pytest.skip('No se detectó modelo Usuario en app.models. Ajusta tests para su uso')

    u1 = Usuario_local()
    u2 = Usuario_local()
    admin = Usuario_local()

    if hasattr(u1, 'email'):
        u1.email = _unique_email('user1')
        u2.email = _unique_email('user2')
        admin.email = _unique_email('admin')
    if hasattr(u1, 'password_hash'):
        u1.password_hash = generate_password_hash('pass1')
        u2.password_hash = generate_password_hash('pass2')
        admin.password_hash = generate_password_hash('adminpass')
    if default_tipo and hasattr(u1, 'tipo_socio_id'):
        try:
            u1.tipo_socio_id = default_tipo.id
            u2.tipo_socio_id = default_tipo.id
            admin.tipo_socio_id = default_tipo.id
        except Exception:
            pass

    if hasattr(u1, 'rol'):
        u1.rol = 'usuario'
        u2.rol = 'usuario'
        admin.rol = 'admin'
    elif hasattr(u1, 'role'):
        u1.role = 'user'
        u2.role = 'user'
        admin.role = 'admin'

    db.session.add_all([u1, u2, admin])
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        # reintentar con nuevos emails únicos
        u1.email = _unique_email('user1')
        u2.email = _unique_email('user2')
        admin.email = _unique_email('admin')
        db.session.add_all([u1, u2, admin])
        db.session.commit()

    if default_tipo and hasattr(u1, 'tipo_socio_id') and (getattr(u1, 'tipo_socio_id', None) is None):
        try:
            u1.tipo_socio_id = default_tipo.id
            u2.tipo_socio_id = default_tipo.id
            admin.tipo_socio_id = default_tipo.id
            db.session.commit()
        except Exception:
            db.session.rollback()

    # Crear TestResource temporal en la DB de pruebas
    class TestResource(db.Model):
        __tablename__ = 'test_resource'
        id = db.Column(db.Integer, primary_key=True)
        tenant_id = db.Column(db.Integer, index=True)
        owner_id = db.Column(db.Integer)
        data = db.Column(db.String(200))

    TestResource.__table__.create(bind=db.engine, checkfirst=True)
    r1 = TestResource(tenant_id=(tenants[0].id if tenants else None),
                          owner_id=getattr(u1, 'id', None),
                          data='secret t1')
    r2 = TestResource(tenant_id=(tenants[1].id if tenants else None),
                          owner_id=getattr(u2, 'id', None),
                          data='secret t2')
    db.session.add_all([r1, r2])
    db.session.commit()

    return {'tenants': tenants, 'users': {'u1': u1, 'u2': u2, 'admin': admin}, 'TestResource': TestResource}