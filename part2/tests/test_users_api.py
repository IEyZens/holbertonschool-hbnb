# Importation du module pytest pour les tests unitaires
import pytest

# Importation de Flask pour créer l'application de test
from flask import Flask

# Importation de l'extension Flask-RESTx pour gérer l'API REST
from flask_restx import Api

# Importation du namespace utilisateur défini dans le fichier users.py (v1)
from app.api.v1.users import api as user_ns

# Importation de la couche façade pour accéder aux repositories métiers
from app.services import facade


# Définition d'une fixture pytest qui fournit un client de test Flask
@pytest.fixture
def client():
    # Création d'une instance de l'application Flask
    app = Flask(__name__)

    # Activation du mode test dans la configuration de Flask
    app.config["TESTING"] = True

    # Création de l'objet API RESTx associé à l'app Flask
    api = Api(app)

    # Enregistrement du namespace des utilisateurs à l'URL /users
    api.add_namespace(user_ns, path="/users")

    # Nettoyage du repository des utilisateurs avant chaque test
    facade.user_repo._storage.clear()

    # Création du client de test et renvoi via un générateur
    with app.test_client() as client:
        yield client


# Test de la création d'un utilisateur valide via POST /users/
def test_create_valid_user(client):
    # Définition du payload JSON représentant un nouvel utilisateur
    payload = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice@example.com"
    }

    # Envoi d'une requête POST avec le payload
    response = client.post("/users/", json=payload)

    # Vérifie que la réponse retourne un code HTTP 201 (création réussie)
    assert response.status_code == 201

    # Récupération de la réponse au format JSON
    data = response.get_json()

    # Vérification que le prénom correspond bien à ce qui a été envoyé
    assert data["first_name"] == "Alice"

    # Vérifie que l'adresse email est correcte
    assert data["email"] == "alice@example.com"


# Test de la détection d’un doublon d’utilisateur par email
def test_create_user_duplicate_email(client):
    # Définition d’un payload pour un utilisateur avec un email unique
    payload = {
        "first_name": "Bob",
        "last_name": "Jones",
        "email": "bob@example.com"
    }

    # Première création de l'utilisateur (doit réussir)
    client.post("/users/", json=payload)

    # Deuxième tentative avec la même adresse email
    response = client.post("/users/", json=payload)

    # Vérifie que la seconde tentative échoue avec un code 400
    assert response.status_code == 400

    # Vérifie que le message d'erreur est explicite sur l'email déjà utilisé
    assert response.get_json()["error"] == "Email already registered"


# Test de la récupération d’un utilisateur existant
def test_get_existing_user(client):
    # Données de l'utilisateur à créer
    payload = {
        "first_name": "Cara",
        "last_name": "Miller",
        "email": "cara@example.com"
    }

    # Création de l'utilisateur et récupération de la réponse
    res = client.post("/users/", json=payload)

    # Extraction de l'identifiant utilisateur à partir de la réponse
    user_id = res.get_json()["id"]

    # Envoi d'une requête GET pour récupérer l'utilisateur par ID
    response = client.get(f"/users/{user_id}")

    # Vérifie que l'utilisateur a bien été trouvé (code 200)
    assert response.status_code == 200

    # Récupération des données utilisateur
    data = response.get_json()

    # Vérifie que l'ID retourné correspond à l'utilisateur créé
    assert data["id"] == user_id

    # Vérifie que l'adresse email correspond à celle de l'utilisateur
    assert data["email"] == "cara@example.com"


# Test de la récupération d’un utilisateur inexistant
def test_get_nonexistent_user(client):
    # Requête GET avec un identifiant qui ne correspond à aucun utilisateur
    response = client.get("/users/unknown-id")

    # Vérifie que l'utilisateur est introuvable (code 404)
    assert response.status_code == 404

    # Vérifie que le message d'erreur est approprié
    assert response.get_json()["error"] == "User not found"
