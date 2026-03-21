import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "dev-secret"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SERVER_NAME = 'local.test'  # en desarrollo
    # tuapp.com (en producción)

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True

    MAIL_USERNAME = 'amvf.losgarres@gmail.com'
    MAIL_PASSWORD = 'ghp_jbJfla8n4Sd2xDv8mmWqfvG7KGJrz51tLL9k'

    MAIL_DEFAULT_SENDER = 'amvf.losgarres@gmail.com'