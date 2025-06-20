# Importation du module de test standard unittest
import unittest

# Importation de patch et MagicMock pour simuler des objets et fonctions
from unittest.mock import patch, MagicMock

# Importation de Flask pour instancier une application de test
from flask import Flask

# Importation de l'extension Flask-RESTx pour gérer les routes API
from flask_restx import Api

# Importation du module contenant les routes des commodités (amenities)
from app.api.v1 import amenities as amenities_api


# Définition d'une classe de test unitaire pour l'API des commodités
class AmenityAPITestCase(unittest.TestCase):

    # Méthode appelée avant chaque test
    def setUp(self):
        # Création d’une application Flask
        self.app = Flask(__name__)

        # Instanciation de l'API RESTx
        self.api = Api(self.app)

        # Ajout du namespace des commodités à l’API
        self.api.add_namespace(amenities_api.api, path='/amenities')

        # Création du client de test Flask pour simuler les requêtes HTTP
        self.client = self.app.test_client()

        # Données valides pour la création d'une commodité
        self.valid_amenity = {"name": "WiFi"}

    # Test de la récupération de toutes les commodités avec succès
    @patch("app.api.v1.amenities.facade.get_all_amenities")
    def test_get_all_amenities(self, mock_get_all):
        # Simulation d'un objet commodité
        mock_amenity = MagicMock()
        mock_amenity.id = "1"
        mock_amenity.name = "WiFi"

        # La fonction mockée retourne une liste contenant la commodité simulée
        mock_get_all.return_value = [mock_amenity]

        # Envoi d'une requête GET à l'endpoint
        response = self.client.get("/amenities/")

        # Vérifie que le code de réponse est 200
        self.assertEqual(response.status_code, 200)

        # Vérifie que le nom de la commodité apparaît bien dans la réponse
        self.assertIn("WiFi", response.get_data(as_text=True))

    # Test de la création d'une commodité avec succès
    @patch("app.api.v1.amenities.facade.create_amenity")
    def test_create_amenity_success(self, mock_create):
        # Création d’un mock représentant la commodité créée
        mock_amenity = MagicMock()
        mock_amenity.id = "1"
        mock_amenity.name = "WiFi"
        mock_create.return_value = mock_amenity

        # Envoi d'une requête POST avec les données valides
        response = self.client.post("/amenities/", json=self.valid_amenity)

        # Vérifie que la réponse est bien 201 (création)
        self.assertEqual(response.status_code, 201)

        # Vérifie que le nom est bien présent dans le corps de la réponse
        self.assertIn("WiFi", response.get_data(as_text=True))

    # Test d'échec de création de commodité à cause d'une donnée invalide
    @patch("app.api.v1.amenities.facade.create_amenity")
    def test_create_amenity_invalid(self, mock_create):
        # Simulation d’une erreur levée par la logique métier
        mock_create.side_effect = ValueError("Name is required")

        # Envoi d'une requête POST avec un nom vide
        response = self.client.post("/amenities/", json={"name": ""})

        # Vérifie que la réponse est une erreur 400
        self.assertEqual(response.status_code, 400)

        # Vérifie que le message d'erreur attendu est retourné
        self.assertIn("Name is required", response.get_data(as_text=True))

    # Test de récupération d’une commodité spécifique avec succès
    @patch("app.api.v1.amenities.facade.get_amenity")
    def test_get_single_amenity_success(self, mock_get):
        # Création d’un objet simulé pour la commodité à retourner
        mock_amenity = MagicMock()
        mock_amenity.id = "1"
        mock_amenity.name = "WiFi"
        mock_get.return_value = mock_amenity

        # Requête GET vers l’endpoint de récupération par ID
        response = self.client.get("/amenities/1")

        # Vérifie que le statut HTTP est 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Vérifie que le nom de la commodité est bien dans la réponse
        self.assertIn("WiFi", response.get_data(as_text=True))

    # Test de récupération d’une commodité inexistante
    @patch("app.api.v1.amenities.facade.get_amenity")
    def test_get_single_amenity_not_found(self, mock_get):
        # Le mock retourne None pour simuler une commodité introuvable
        mock_get.return_value = None

        # Envoi d'une requête GET avec un ID inexistant
        response = self.client.get("/amenities/404")

        # Vérifie que la réponse est une erreur 404
        self.assertEqual(response.status_code, 404)

        # Vérifie que le message d'erreur attendu est présent
        self.assertIn("Amenity not found", response.get_data(as_text=True))

    # Test de mise à jour réussie d’une commodité
    @patch("app.api.v1.amenities.facade.update_amenity")
    def test_update_amenity_success(self, mock_update):
        # Création d’un objet mis à jour simulé
        updated = MagicMock()
        updated.id = "1"
        updated.name = "Updated Amenity"
        mock_update.return_value = updated

        # Envoi d’une requête PUT avec les nouvelles données
        response = self.client.put(
            "/amenities/1", json={"name": "Updated Amenity"})

        # Vérifie que le code HTTP est 200 (mise à jour réussie)
        self.assertEqual(response.status_code, 200)

        # Vérifie que le nom mis à jour est dans la réponse
        self.assertIn("Updated Amenity", response.get_data(as_text=True))

    # Test de tentative de mise à jour d’une commodité inexistante
    @patch("app.api.v1.amenities.facade.update_amenity")
    def test_update_amenity_not_found(self, mock_update):
        # Simule le cas où la commodité n’est pas trouvée
        mock_update.return_value = None

        # Envoi d'une requête PUT avec un ID inexistant
        response = self.client.put("/amenities/999", json={"name": "WiFi"})

        # Vérifie que le serveur retourne une erreur 404
        self.assertEqual(response.status_code, 404)

        # Vérifie que le message d’erreur est explicite
        self.assertIn("Amenity not found", response.get_data(as_text=True))

    # Test d'échec de mise à jour à cause de données invalides
    @patch("app.api.v1.amenities.facade.update_amenity")
    def test_update_amenity_invalid(self, mock_update):
        # Simule une erreur métier (nom invalide)
        mock_update.side_effect = ValueError("Invalid name")

        # Requête PUT avec un nom vide
        response = self.client.put("/amenities/1", json={"name": ""})

        # Vérifie que le statut HTTP est 400 (données invalides)
        self.assertEqual(response.status_code, 400)

        # Vérifie que le message d'erreur est bien présent dans la réponse
        self.assertIn("Invalid name", response.get_data(as_text=True))


# Point d’entrée pour exécuter les tests via la ligne de commande
if __name__ == '__main__':
    unittest.main()
