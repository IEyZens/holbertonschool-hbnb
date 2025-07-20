"""
Application launcher script for the HBnB API.

This module bootstraps the Flask app using the factory pattern
and runs the development server.
"""

import os
from app import create_app
from app.extensions import db

# Création de l'instance de l'application Flask via la factory
app = create_app()


def init_database():
    """Initialize the database with all tables and default data"""
    with app.app_context():
        try:
            # Créer toutes les tables basées sur les modèles SQLAlchemy
            db.create_all()
            print("✅ Database tables created successfully!")

            # Ajouter des données par défaut si la base est vide
            from app.models.user import User
            from app.models.amenity import Amenity

            # Vérifier si l'admin existe déjà
            admin_exists = User.query.filter_by(email="admin@hbnb.io").first()
            if not admin_exists:
                # Créer un utilisateur admin par défaut
                admin_user = User(
                    first_name="Admin",
                    last_name="HBnB",
                    email="admin@hbnb.io",
                    password="admin1234",  # Sera hashé automatiquement dans le modèle
                    is_admin=True
                )
                db.session.add(admin_user)
                print("✅ Admin user created!")

            # Vérifier si des amenities existent déjà
            amenity_count = Amenity.query.count()
            if amenity_count == 0:
                # Créer quelques amenities par défaut
                default_amenities = [
                    Amenity(name="WiFi"),
                    Amenity(name="Parking"),
                    Amenity(name="Swimming Pool"),
                    Amenity(name="Air Conditioning"),
                    Amenity(name="Kitchen"),
                    Amenity(name="Gym")
                ]
                db.session.add_all(default_amenities)
                print("✅ Default amenities created!")

            db.session.commit()
            print("✅ Database initialization completed!")

        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            db.session.rollback()


if __name__ == '__main__':
    """
    Entry point for local execution.

    Launches the Flask development server with debugging enabled.
    """

    # Initialiser la base de données au démarrage
    print("🔧 Initializing database...")
    init_database()

    print("🚀 Starting HBnB application...")
    # Démarre le serveur local avec Flask en mode debug
    app.run(debug=True)
