import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_default_secret_key')  # Default secret key for sessions
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///instance/Checkpoint3.db')  # SQLite database
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable unnecessary signals

class DevelopmentConfig(Config):
    DEBUG = True  # Enable debug mode for development

class ProductionConfig(Config):
    DEBUG = False  # Disable debug mode for production
