"""
Application launcher script for the HBnB API.

This module bootstraps the Flask app using the factory pattern
and runs the development server.
"""

from app import create_app

# Création de l'instance de l'application Flask via la factory
app = create_app()

if __name__ == '__main__':
    """
    Entry point for local execution.

    Launches the Flask development server with debugging enabled.
    """
    # Démarre le serveur local avec Flask en mode debug
    app.run(debug=True)
