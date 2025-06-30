"""
Flask application factory for the HBnB RESTful API.

This module defines the main entry point for initializing the Flask app and
registering versioned namespaces for user, place, amenity, and review resources.
"""

from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from app.api.v1.users import api as users_ns
from app.api.v1.places import api as places_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.reviews import api as reviews_ns
from app.api.v1.auth import api as auth_ns

bcrypt = Bcrypt()
jwt = JWTManager()


def create_app(config_class="config.DevelopmentConfig"):
    """
    Application factory function.

    Creates and configures the Flask app instance, sets up Flask-RESTx,
    and registers all API namespaces under versioned routes.

    Returns:
        Flask: A configured Flask application instance.
    """
    # Initialisation de l'application Flask
    app = Flask(__name__)

    authorizations = {
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Enter JWT token with **Bearer** prefix: Bearer <token>'
        }
    }

    api = Api(
        app,
        version='1.0',
        title='HBnB API',
        description='HBnB Application API',
        authorizations=authorizations,
        security='Bearer'
    )

    app.config.from_object(config_class)

    bcrypt.init_app(app)
    jwt.init_app(app)

    # Enregistrement du namespace utilisateurs (v1)
    api.add_namespace(users_ns, path='/api/v1/users')
    # Enregistrement du namespace lieux (v1)
    api.add_namespace(places_ns, path="/api/v1/places")
    # Enregistrement du namespace commodités (v1)
    api.add_namespace(amenities_ns, path="/api/v1/amenities")
    # Enregistrement du namespace avis (v1)
    api.add_namespace(reviews_ns, path="/api/v1/reviews")
    api.add_namespace(auth_ns, path="/api/v1/auth")

    # Retourne l’instance configurée de l'application
    return app
