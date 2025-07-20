"""
Flask application factory for the HBnB RESTful API.

This module serves as the main entry point for the HBnB application, implementing the
Application Factory pattern to create and configure Flask app instances. It handles
the initialization of all extensions, API namespaces, and configuration settings
required for the RESTful API to function properly.

The factory pattern allows for flexible configuration management, easier testing,
and better separation of concerns by deferring application creation until runtime.
This approach enables multiple app instances with different configurations and
facilitates unit testing with isolated application contexts.

Key Components:
- Flask-RESTX API configuration with Swagger documentation
- JWT authentication setup for secure API access
- Database initialization through SQLAlchemy
- Password hashing configuration via bcrypt
- Namespace registration for all API endpoints
- Authorization schema definition for API documentation

API Structure:
- Version 1 endpoints under /api/v1/ prefix
- Separate namespaces for regular and admin operations
- JWT Bearer token authentication for protected endpoints
- Comprehensive Swagger documentation with security schemas

Supported Entity Operations:
- Users: Registration, authentication, profile management
- Places: Property listings, search, and management
- Amenities: Feature management and associations
- Reviews: User feedback and rating system
- Admin: Administrative operations for all entities
"""

# Import Flask core components for application creation
from flask import Flask
from flask_restx import Api

# Import application extensions for database, authentication, and security
from app.extensions import db, bcrypt, jwt

# Import API namespace modules for different entity types
# Regular user-facing endpoints
from app.api.v1.users import api as users_ns
from app.api.v1.places import api as places_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.reviews import api as reviews_ns
from app.api.v1.auth import api as auth_ns

# Administrative endpoints requiring elevated privileges
from app.api.v1.admin_users import api as admin_users_ns
from app.api.v1.admin_places import api as admin_places_ns
from app.api.v1.admin_amenities import api as admin_amenities_ns
from app.api.v1.admin_reviews import api as admin_reviews_ns


def create_app(config_class="config.DevelopmentConfig"):
    """
    Application factory function for creating and configuring Flask app instances.

    This function implements the Application Factory pattern, allowing for the creation
    of Flask applications with different configurations. It initializes all necessary
    extensions, configures API documentation, sets up authentication, and registers
    all API namespaces for the HBnB application.

    The factory pattern provides several benefits:
    - Multiple app instances can be created with different configurations
    - Easier unit testing with isolated application contexts
    - Deferred configuration loading based on environment
    - Better separation between application creation and configuration
    - Support for different deployment environments (dev, test, production)

    Configuration Loading:
    - Loads configuration from the specified config class
    - Supports different environments through config inheritance
    - Configuration includes database URLs, JWT secrets, and feature flags

    Extension Initialization:
    - SQLAlchemy for database ORM operations
    - bcrypt for secure password hashing
    - JWT for stateless authentication tokens
    - Flask-RESTX for API documentation and validation

    Args:
        config_class (str): The import path to the configuration class to use.
                           Defaults to "config.DevelopmentConfig" for local development.
                           Common options include:
                           - "config.DevelopmentConfig": Local development settings
                           - "config.TestingConfig": Unit testing configuration
                           - "config.ProductionConfig": Production deployment settings

    Returns:
        Flask: A fully configured Flask application instance ready for deployment.
               The app includes:
               - All extensions initialized and configured
               - API namespaces registered with proper routing
               - Swagger documentation configured with authentication
               - Database models and relationships established
               - JWT authentication and authorization setup

    Example:
        # Create development app
        app = create_app()

        # Create testing app
        test_app = create_app("config.TestingConfig")

        # Create production app
        prod_app = create_app("config.ProductionConfig")

    Security Configuration:
        - JWT Bearer token authentication for protected endpoints
        - bcrypt password hashing with automatic salt generation
        - Swagger UI integration with authentication support
        - CORS handling for cross-origin requests (if configured)

    API Documentation:
        - Automatic Swagger/OpenAPI documentation generation
        - Interactive API testing interface
        - Request/response schema validation
        - Authentication flow documentation
    """
    # Initialize Flask application instance
    app = Flask(__name__)

    # Load configuration from the specified config class
    # This allows environment-specific settings (database URLs, secrets, etc.)
    app.config.from_object(config_class)

    # Define authorization configuration for Swagger documentation
    # This enables the "Authorize" button in Swagger UI for JWT token input
    authorizations = {
        'Bearer': {
            'type': 'apiKey',            # Type of authentication (API key)
            'in': 'header',              # Location of the token (HTTP header)
            'name': 'Authorization',     # Header name for the token
            'description': 'Just paste your token — Swagger will send it as: Authorization: Bearer <token>'
        }
    }

    # Initialize Flask-RESTX API with comprehensive configuration
    api = Api(
        app,                            # Flask app instance to attach API to
        version='1.0',                  # API version for documentation
        title='HBnB API',              # API title displayed in Swagger UI
        description='HBnB Application API',  # API description for documentation
        authorizations=authorizations,   # JWT authorization configuration
        security='Bearer'               # Default security scheme for endpoints
    )

    # Initialize Flask extensions with the application instance
    # bcrypt: Secure password hashing for user authentication
    bcrypt.init_app(app)

    # JWT: JSON Web Token handling for stateless authentication
    jwt.init_app(app)

    # SQLAlchemy: Database ORM for data persistence and relationships
    db.init_app(app)

    # Register API namespaces for user-facing endpoints
    # Users namespace: Registration, profile management, authentication
    api.add_namespace(users_ns, path='/api/v1/users')

    # Places namespace: Property listings, search, and basic management
    api.add_namespace(places_ns, path="/api/v1/places")

    # Amenities namespace: Feature listings and basic operations
    api.add_namespace(amenities_ns, path="/api/v1/amenities")

    # Reviews namespace: User feedback and rating operations
    api.add_namespace(reviews_ns, path="/api/v1/reviews")

    # Authentication namespace: Login, token management, protected resource testing
    api.add_namespace(auth_ns, path="/api/v1/auth")

    # Register API namespaces for administrative endpoints
    # Admin Users namespace: User management, role assignment, account administration
    api.add_namespace(admin_users_ns, path='/api/v1/admin/users')

    # Admin Places namespace: Property management, owner verification, place administration
    api.add_namespace(admin_places_ns, path="/api/v1/admin/places")

    # Admin Amenities namespace: Feature management, system-wide amenity operations
    api.add_namespace(admin_amenities_ns, path="/api/v1/admin/amenities")

    # Admin Reviews namespace: Review moderation, content management, user feedback oversight
    api.add_namespace(admin_reviews_ns, path="/api/v1/admin/reviews")

    # Return the fully configured Flask application instance
    # The app is now ready for deployment or testing with all components initialized
    return app
