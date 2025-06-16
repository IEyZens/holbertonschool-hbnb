from flask import Flask
from app.api import api_bp  # ← importe le blueprint complet avec tous les namespaces

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')  # si tu as un fichier de conf

    # ✅ Enregistrement unique du Blueprint complet
    app.register_blueprint(api_bp)

    return app
