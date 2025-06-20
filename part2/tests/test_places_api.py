# Importation des modules nécessaires pour les tests unitaires
import unittest
from unittest.mock import patch, MagicMock
from app.api.v1.places import api as places_api
from flask import Flask
from flask_restx import Api


# Définition de la classe de test pour les endpoints "places"
class PlacesAPITestCase(unittest.TestCase):
    # Configuration exécutée avant chaque test
    def setUp(self):
        # Création d'une application Flask de test
        app = Flask(__name__)
        # Initialisation de l'API Flask-RESTx
        self.api = Api(app)
        # Ajout du namespace "places" à l’API
        self.api.add_namespace(places_api, path='/places')
        # Création du client de test
        self.client = app.test_client()

        # Définition d’un payload de lieu valide
        self.valid_place = {
            "title": "Beach House",
            "description": "Relax by the sea",
            "price": 120.0,
            "latitude": 36.5,
            "longitude": -5.0,
            "owner_id": "user-123",
            "max_person": 6,
            "amenities": [],
            "owner": {
                "id": "user-123",
                "first_name": "Alice",
                "last_name": "Doe",
                "email": "alice@example.com"
            },
            "reviews": []
        }

    # Teste la récupération de tous les lieux disponibles
    @patch("app.api.v1.places.facade.get_all_places")
    def test_get_all_places(self, mock_get_all):
        # Création d’un objet simulé (fake place)
        mock_place = MagicMock()
        mock_place.id = "1"
        mock_place.title = "Beach House"
        mock_place.description = "Relax by the sea"
        mock_place.price = 120.0
        mock_place.latitude = 36.5
        mock_place.longitude = -5.0
        mock_place.owner.id = "user-123"
        mock_place.max_person = 6
        # Simulation de la valeur retournée par la façade
        mock_get_all.return_value = [mock_place]

        # Appel GET de l’endpoint
        response = self.client.get("/places/")
        # Vérifie que le statut est 200 OK
        self.assertEqual(response.status_code, 200)
        # Vérifie que le titre est présent dans la réponse
        self.assertIn("Beach House", response.get_data(as_text=True))

    # Teste la création d’un lieu avec des données valides
    @patch("app.api.v1.places.facade.create_place")
    def test_create_place_success(self, mock_create):
        # Simule un objet lieu renvoyé par la façade
        mock_place = MagicMock()
        mock_place.id = "1"
        mock_place.title = self.valid_place["title"]
        mock_place.description = self.valid_place["description"]
        mock_place.price = self.valid_place["price"]
        mock_place.latitude = self.valid_place["latitude"]
        mock_place.longitude = self.valid_place["longitude"]
        mock_place.owner.id = self.valid_place["owner_id"]
        mock_place.max_person = self.valid_place["max_person"]
        mock_place.amenities = []
        mock_create.return_value = mock_place

        # Envoie une requête POST avec les données valides
        response = self.client.post("/places/", json=self.valid_place)
        # Vérifie que la réponse est un succès (201)
        self.assertEqual(response.status_code, 201)
        self.assertIn("Beach House", response.get_data(as_text=True))

    # Teste la création d’un lieu avec des données invalides
    @patch("app.api.v1.places.facade.create_place")
    def test_create_place_invalid(self, mock_create):
        # Simule une ValueError émise par la façade
        mock_create.side_effect = ValueError("Invalid price")
        invalid_place = self.valid_place.copy()
        invalid_place["price"] = -5

        # Envoie une requête POST avec un prix invalide
        response = self.client.post("/places/", json=invalid_place)
        # Vérifie que la réponse est une erreur 400
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid price", response.get_data(as_text=True))

    # Teste la récupération d’un lieu spécifique avec succès
    @patch("app.api.v1.places.facade.get_place")
    def test_get_single_place_success(self, mock_get):
        # Création d’un objet de lieu simulé
        mock_place = MagicMock()
        mock_place.id = "1"
        mock_place.title = "Cozy Hut"
        mock_place.description = "Hidden in the forest"
        mock_place.price = 75.0
        mock_place.latitude = 40.0
        mock_place.longitude = 2.0
        mock_place.owner.id = "user-123"
        mock_place.owner.first_name = "Alice"
        mock_place.owner.last_name = "Doe"
        mock_place.owner.email = "alice@example.com"
        mock_place.max_person = 3
        mock_place.amenities = []
        mock_get.return_value = mock_place

        # Envoie une requête GET pour un ID donné
        response = self.client.get("/places/1")
        # Vérifie le code de retour et le contenu
        self.assertEqual(response.status_code, 200)
        self.assertIn("Cozy Hut", response.get_data(as_text=True))

    # Teste la récupération d’un lieu inexistant
    @patch("app.api.v1.places.facade.get_place")
    def test_get_place_not_found(self, mock_get):
        # Simule une absence de lieu
        mock_get.return_value = None
        response = self.client.get("/places/not-found")
        # Vérifie que la réponse est une erreur 404
        self.assertEqual(response.status_code, 404)
        self.assertIn("Place not found", response.get_data(as_text=True))

    # Teste la mise à jour d’un lieu avec succès
    @patch("app.api.v1.places.facade.update_place")
    def test_update_place_success(self, mock_update):
        # Simule une mise à jour réussie
        updated = MagicMock()
        updated.id = "1"
        updated.title = "New Title"
        updated.description = "Updated"
        updated.price = 140
        updated.latitude = 34.0
        updated.longitude = 5.0
        updated.owner.id = "user-123"
        updated.max_person = 5
        updated.amenities = []
        mock_update.return_value = updated

        # Envoie une requête PUT avec des données valides
        response = self.client.put("/places/1", json=self.valid_place)
        # Vérifie que le nom mis à jour est présent
        self.assertEqual(response.status_code, 200)
        self.assertIn("New Title", response.get_data(as_text=True))

    # Teste la mise à jour d’un lieu inexistant
    @patch("app.api.v1.places.facade.update_place")
    def test_update_place_not_found(self, mock_update):
        # Simule une absence de lieu à mettre à jour
        mock_update.return_value = None
        response = self.client.put("/places/999", json=self.valid_place)
        self.assertEqual(response.status_code, 404)

    # Teste la mise à jour avec des données invalides
    @patch("app.api.v1.places.facade.update_place")
    def test_update_place_invalid_data(self, mock_update):
        # Simule une erreur métier
        mock_update.side_effect = ValueError("Latitude out of bounds")
        bad_place = self.valid_place.copy()
        bad_place["latitude"] = 999

        # Envoie une requête PUT avec latitude invalide
        response = self.client.put("/places/1", json=bad_place)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Latitude out of bounds",
                      response.get_data(as_text=True))

    # Teste une erreur serveur inattendue lors de la mise à jour
    @patch("app.api.v1.places.facade.update_place")
    def test_update_place_server_error(self, mock_update):
        # Simule une exception serveur
        mock_update.side_effect = Exception("Server exploded")
        response = self.client.put("/places/1", json=self.valid_place)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Internal server error", response.get_data(as_text=True))


# Lance les tests lorsque ce fichier est exécuté directement
if __name__ == '__main__':
    unittest.main()
