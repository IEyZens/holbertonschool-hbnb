import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_restx import Api
from app.api.v1.amenities import api as amenities_ns


class AmenityApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.api.add_namespace(amenities_ns, path='/amenities')
        self.client = self.app.test_client()

    @patch('app.api.v1.amenities.facade.create_amenity')
    def test_create_amenity_success(self, mock_create):
        mock_amenity = MagicMock()
        mock_amenity.id = '123'
        mock_amenity.name = 'Wi-Fi'
        mock_create.return_value = mock_amenity

        response = self.client.post('/amenities/', json={'name': 'Wi-Fi'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), {'id': '123', 'name': 'Wi-Fi'})

    @patch('app.api.v1.amenities.facade.create_amenity')
    def test_create_amenity_invalid(self, mock_create):
        mock_create.side_effect = ValueError("Missing name")
        response = self.client.post('/amenities/', json={})
        self.assertEqual(response.status_code, 400)

    @patch('app.api.v1.amenities.facade.get_all_amenities')
    def test_get_all_amenities(self, mock_get_all):
        a1 = MagicMock()
        a1.id = '1'
        a1.name = 'Wi-Fi'
        a2 = MagicMock()
        a2.id = '2'
        a2.name = 'Pool'
        mock_get_all.return_value = [a1, a2]

        response = self.client.get('/amenities/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)

    @patch('app.api.v1.amenities.facade.get_amenity')
    def test_get_amenity_by_id_found(self, mock_get):
        mock_amenity = MagicMock()
        mock_amenity.id = '1'
        mock_amenity.name = 'Wi-Fi'
        mock_get.return_value = mock_amenity

        response = self.client.get('/amenities/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {'id': '1', 'name': 'Wi-Fi'})

    @patch('app.api.v1.amenities.facade.get_amenity')
    def test_get_amenity_by_id_not_found(self, mock_get):
        mock_get.return_value = None
        response = self.client.get('/amenities/999')
        self.assertEqual(response.status_code, 404)

    @patch('app.api.v1.amenities.facade.update_amenity')
    def test_update_amenity_success(self, mock_update):
        mock_amenity = MagicMock()
        mock_amenity.id = '1'
        mock_amenity.name = 'Updated Name'
        mock_update.return_value = mock_amenity

        response = self.client.put('/amenities/1', json={'name': 'Updated Name'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {'id': '1', 'name': 'Updated Name'})

    @patch('app.api.v1.amenities.facade.update_amenity')
    def test_update_amenity_invalid_data(self, mock_update):
        mock_update.side_effect = ValueError("Invalid data")
        response = self.client.put('/amenities/1', json={})
        self.assertEqual(response.status_code, 400)

    @patch('app.api.v1.amenities.facade.update_amenity')
    def test_update_amenity_not_found(self, mock_update):
        mock_update.return_value = None
        response = self.client.put('/amenities/999', json={'name': 'New Name'})
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
