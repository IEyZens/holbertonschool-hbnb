"""
Flask application factory for the HBnB RESTful API.

This module defines the main entry point for initializing the Flask app and
registering versioned namespaces for user, place, amenity, and review resources.
"""

from flask import Flask
from flask_restx import Api
from app.api.v1.users import api as users_ns
from app.api.v1.places import api as places_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.reviews import api as reviews_ns


def create_app():
    """
    Application factory function.

    Creates and configures the Flask app instance, sets up Flask-RESTx,
    and registers all API namespaces under versioned routes.

    Returns:
        Flask: A configured Flask application instance.
    """
    # Initialisation de l'application Flask
    app = Flask(__name__)

    # Configuration de la documentation Swagger via Flask-RESTx
    api = Api(app, version='1.0', title='HBnB API',
              description='HBnB Application API')

    # Enregistrement du namespace utilisateurs (v1)
    api.add_namespace(users_ns, path='/api/v1/users')
    # Enregistrement du namespace lieux (v1)
    api.add_namespace(places_ns, path="/api/v1/places")
    # Enregistrement du namespace commodités (v1)
    api.add_namespace(amenities_ns, path="/api/v1/amenities")
    # Enregistrement du namespace avis (v1)
    api.add_namespace(reviews_ns, path="/api/v1/reviews")

    # Retourne l’instance configurée de l'application
    return app
