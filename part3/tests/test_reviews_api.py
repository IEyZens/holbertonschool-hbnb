# Importation de pytest pour la gestion des tests
import pytest

# Importation de Flask pour créer une application de test
from flask import Flask

# Importation de Flask-RESTx pour gérer l’API
from flask_restx import Api

# Importation du namespace des avis (reviews)
from app.api.v1.reviews import api as review_ns

# Importation de la façade métier
from app.services import facade

# Importation des modèles nécessaires aux tests
from app.models.user import User
from app.models.place import Place


# Définition d’un client de test Flask avec configuration isolée
@pytest.fixture
def client():
    # Création de l’application Flask
    app = Flask(__name__)

    # Activation du mode test pour Flask
    app.config["TESTING"] = True

    # Création de l’API et ajout du namespace "reviews"
    api = Api(app)
    api.add_namespace(review_ns, path="/reviews")

    # Réinitialisation complète des données avant chaque test
    User.existing_emails.clear()
    facade.user_repo._storage.clear()
    facade.place_repo._storage.clear()
    facade.review_repo._storage.clear()

    # Activation du client de test Flask
    with app.test_client() as client:
        yield client


# Fonction utilitaire pour créer un utilisateur et un lieu
def create_user_and_place():
    # Création d’un utilisateur
    user = User("Review", "Tester", "reviewer@example.com")

    # Création d’un lieu associé à cet utilisateur
    place = Place("Nice Spot", "Great stay", 120.0, 45.0, 2.0, user, 3)

    # Enregistrement de l’utilisateur et du lieu dans les repositories
    facade.user_repo.add(user)
    facade.place_repo.add(place)

    # Retourne les deux objets créés
    return user, place


# Test de création d’un avis valide
def test_create_valid_review(client):
    # Création des entités nécessaires
    user, place = create_user_and_place()

    # Données de l’avis à créer
    payload = {
        "text": "Loved it!",
        "rating": 5,
        "user_id": user.id,
        "place_id": place.id
    }

    # Requête POST pour créer l’avis
    response = client.post("/reviews/", json=payload)

    # Vérification du code HTTP
    assert response.status_code == 201

    # Vérification du contenu de la réponse
    data = response.get_json()
    assert data["text"] == "Loved it!"
    assert data["rating"] == 5
    assert data["user_id"] == user.id
    assert data["place_id"] == place.id


# Test d’un avis avec une note invalide
def test_create_review_invalid_rating(client):
    # Création des entités nécessaires
    user, place = create_user_and_place()

    # Note invalide (10)
    payload = {
        "text": "Meh...",
        "rating": 10,
        "user_id": user.id,
        "place_id": place.id
    }

    # Envoi de la requête POST
    response = client.post("/reviews/", json=payload)

    # Vérification que l’erreur est bien levée
    assert response.status_code == 400
    assert "error" in response.get_json()


# Test de récupération de tous les avis
def test_get_all_reviews(client):
    # Création des entités nécessaires
    user, place = create_user_and_place()

    # Création d’un avis initial
    payload = {
        "text": "Great service",
        "rating": 4,
        "user_id": user.id,
        "place_id": place.id
    }

    # Insertion dans l'API
    client.post("/reviews/", json=payload)

    # Récupération de tous les avis
    response = client.get("/reviews/")

    # Vérifications
    assert response.status_code == 200
    reviews = response.get_json()
    assert isinstance(reviews, list)
    assert any(r["text"] == "Great service" for r in reviews)


# Test de récupération d’un avis par son ID
def test_get_review_by_id(client):
    # Création des entités nécessaires
    user, place = create_user_and_place()

    # Création d’un avis
    response = client.post("/reviews/", json={
        "text": "Amazing!",
        "rating": 5,
        "user_id": user.id,
        "place_id": place.id
    })

    # Extraction de l’ID de l’avis
    review_id = response.get_json()["id"]

    # Récupération de l’avis par son ID
    res = client.get(f"/reviews/{review_id}")

    # Vérification du contenu
    assert res.status_code == 200
    assert res.get_json()["id"] == review_id


# Test de mise à jour d’un avis
def test_update_review(client):
    # Création des entités nécessaires
    user, place = create_user_and_place()

    # Création initiale de l’avis
    res = client.post("/reviews/", json={
        "text": "Initial",
        "rating": 3,
        "user_id": user.id,
        "place_id": place.id
    })

    # Récupération de l’ID
    review_id = res.get_json()["id"]

    # Données de mise à jour
    update_data = {
        "text": "Updated",
        "rating": 4,
        "user_id": user.id,
        "place_id": place.id
    }

    # Envoi de la requête PUT
    res2 = client.put(f"/reviews/{review_id}", json=update_data)

    # Vérification du résultat
    assert res2.status_code == 200
    assert res2.get_json()["text"] == "Updated"


# Test de suppression d’un avis
def test_delete_review(client):
    # Création des entités nécessaires
    user, place = create_user_and_place()

    # Création de l’avis à supprimer
    res = client.post("/reviews/", json={
        "text": "To be deleted",
        "rating": 3,
        "user_id": user.id,
        "place_id": place.id
    })

    # Récupération de l’ID de l’avis
    review_id = res.get_json()["id"]

    # Requête DELETE pour supprimer l’avis
    res2 = client.delete(f"/reviews/{review_id}")

    # Vérifications
    assert res2.status_code == 200
    assert res2.get_json()["message"] == "Review successfully deleted"


# Test de récupération des avis liés à un lieu spécifique
def test_get_reviews_by_place(client):
    # Création des entités nécessaires
    user, place = create_user_and_place()

    # Création d’un avis spécifique à un lieu
    client.post("/reviews/", json={
        "text": "Specific place",
        "rating": 4,
        "user_id": user.id,
        "place_id": place.id
    })

    # Récupération des avis pour ce lieu
    response = client.get(f"/reviews/places/{place.id}/reviews")

    # Vérifications
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any(r["place_id"] == place.id for r in data)
