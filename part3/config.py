"""
Configuration module for the HBnB Flask application.

Defines environment-specific settings using class-based configuration.
Supports development mode and default fallback configuration.
"""

import os

class Config:
    """
    Base configuration class.

    Attributes:
        SECRET_KEY (str): Secret used for cryptographic operations.
        DEBUG (bool): Debug mode flag.
    """
    # Clé secrète utilisée pour les sessions et la sécurité (JWT, cookies, etc.)
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    # Mode debug désactivé par défaut
    DEBUG = False

class DevelopmentConfig(Config):
    """
    Configuration for development environment.

    Extends base configuration and enables Flask debug mode.
    """
    # Active le mode debug pour le développement
    DEBUG = True

# Dictionnaire d'association des environnements à leurs configurations
config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
