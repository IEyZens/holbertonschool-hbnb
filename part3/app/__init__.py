"""
Flask application factory for the HBnB RESTful API.

This module defines the main entry point for initializing the Flask app and
registering versioned namespaces for user, place, amenity, and review resources.
"""

from flask import Flask
from flask_restx import Api
from app.extensions import db, bcrypt, jwt
from app.api.v1.users import api as users_ns
from app.api.v1.admin_users import api as admin_users_ns
from app.api.v1.places import api as places_ns
from app.api.v1.admin_places import api as admin_places_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.admin_amenities import api as admin_amenities_ns
from app.api.v1.reviews import api as reviews_ns
from app.api.v1.admin_reviews import api as admin_reviews_ns
from app.api.v1.auth import api as auth_ns


def create_app(config_class="config.DevelopmentConfig"):
    """
    Application factory function.

    Creates and configures the Flask app instance using the provided configuration class.

    Args:
        config_class (str): The import path to the configuration class to use.

    Returns:
        Flask: A configured Flask application instance.
    """
    # Initialisation de l'application Flask
    app = Flask(__name__)
    app.config.from_object(config_class)

    authorizations = {
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Just paste your token — Swagger will send it as: Authorization: Bearer <token>'
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

    bcrypt.init_app(app)
    jwt.init_app(app)
    db.init_app(app)

    # Enregistrement du namespace utilisateurs (v1)
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(admin_users_ns, path='/api/v1/admin_users')
    # Enregistrement du namespace lieux (v1)
    api.add_namespace(places_ns, path="/api/v1/places")
    api.add_namespace(admin_places_ns, path="/api/v1/admin_places")
    # Enregistrement du namespace commodités (v1)
    api.add_namespace(amenities_ns, path="/api/v1/amenities")
    api.add_namespace(admin_amenities_ns, path="/api/v1/admin_amenities")
    # Enregistrement du namespace avis (v1)
    api.add_namespace(reviews_ns, path="/api/v1/reviews")
    api.add_namespace(admin_reviews_ns, path="/api/v1/admin_reviews")
    api.add_namespace(auth_ns, path="/api/v1/auth")

    # Retourne l’instance configurée de l'application
    return app
