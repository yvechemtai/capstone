import os
from secrets import token_hex
from decouple import config
from ..utils.base_dir import BASE_DIR

class Config:
    """Base configuration with common settings."""
    
    SQLALCHEMY_TRACK_MODIFICATIONS = config('SQLALCHEMY_TRACK_MODIFICATIONS', default=False, cast=bool)
    SECRET_KEY = config('SECRET_KEY', default=token_hex(16))

    HOST = '0.0.0.0'
    
    SESSION_COOKIE_SECURE = True
    BCRYPT_LOG_ROUNDS = 12

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    ALLOWED_DOCS_EXTENSIONS = {'pdf', 'docx', 'csv', 'txt', 'xls', 'xlsx'}
    DOCS_FOLDER = 'app/static/uploads/docs'
    UPLOAD_FOLDER = 'app/static/uploads/profiles'
    TEMP_FOLDER = 'app/static/uploads/temp'
    
    @staticmethod
    def init_app(app):
        os.makedirs(Config.DOCS_FOLDER, exist_ok=True)
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.TEMP_FOLDER, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration settings."""
    
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, 'database', 'dev.sqlite3')
    SQLALCHEMY_ECHO = True
    
    DEBUG = True
    PORT = 7070


class ProductionConfig(Config):
    """Production configuration settings."""
    
    SQLALCHEMY_DATABASE_URI = config('PROD_DATABASE_URI')
    SQLALCHEMY_ECHO = False
    
    DEBUG = False
    PORT = 8080
    SESSION_COOKIE_SECURE = True


class TestConfig(Config):
    """Test configuration settings."""

    pass


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestConfig,
    'default': Config
}
