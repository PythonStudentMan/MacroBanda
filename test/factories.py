import factory
from werkzeug.security import generate_password_hash
from app.extensions import db as _db

class UsuarioFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = None
        sqlalchemy_session = _db.session
        sqlalchemy_session_persistence = 'flush'

    email = factory.LazyAttribute(lambda o: f"user+{factory.Faker('uuid4').generate({})[:8]}@test.local")
    password_hash = factory.LazyFunction(lambda: generate_password_hash('pass1'))
    role = 'usuario'