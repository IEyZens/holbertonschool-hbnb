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

    @patch('app.services.facade.create_amenity')
    def test_create_amenity_success(self, mock_create):
        mock_amenity = MagicMock(id='123', name='Wi-Fi')
        mock_create.return_value = mock_amenity

        response = self.client.post('/amenities/', json={'name': 'Wi-Fi'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), {'id': '123', 'name': 'Wi-Fi'})

    @patch('app.services.facade.create_amenity')
    def test_create_amenity_invalid(self, mock_create):
        mock_create.side_effect = ValueError("Invalid data")

        response = self.client.post('/amenities/', json={'name': ''})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.get_json())

    @patch('app.services.facade.get_all_amenities')
    def test_get_all_amenities(self, mock_get_all):
        mock_get_all.return_value = [
            MagicMock(id='1', name='Wi-Fi'),
            MagicMock(id='2', name='Pool')
        ]
        response = self.client.get('/amenities/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)

    @patch('app.services.facade.get_amenity')
    def test_get_amenity_by_id_found(self, mock_get):
        mock_get.return_value = MagicMock(id='1', name='Wi-Fi')

        response = self.client.get('/amenities/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['name'], 'Wi-Fi')

    @patch('app.services.facade.get_amenity')
    def test_get_amenity_by_id_not_found(self, mock_get):
        mock_get.return_value = None

        response = self.client.get('/amenities/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.get_json())

    @patch('app.services.facade.update_amenity')
    def test_update_amenity_success(self, mock_update):
        mock_update.return_value = MagicMock(id='1', name='Updated Name')

        response = self.client.put('/amenities/1', json={'name': 'Updated Name'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['name'], 'Updated Name')

    @patch('app.services.facade.update_amenity')
    def test_update_amenity_not_found(self, mock_update):
        mock_update.return_value = None

        response = self.client.put('/amenities/999', json={'name': 'New Name'})
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.get_json())

    @patch('app.services.facade.update_amenity')
    def test_update_amenity_invalid_data(self, mock_update):
        mock_update.side_effect = ValueError("Invalid data")

        response = self.client.put('/amenities/1', json={'name': ''})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.get_json())

if __name__ == '__main__':
    unittest.main()
