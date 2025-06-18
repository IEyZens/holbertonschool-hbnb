import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_restx import Api
from app.api.v1.places import api as places_ns

class PlaceApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.api.add_namespace(places_ns, path='/places')
        self.client = self.app.test_client()

    @patch('app.services.facade.create_place')
    def test_create_place_success(self, mock_create):
        mock_place = MagicMock(
            id='1', title='Charming Loft', description='Nice and cozy', price=150,
            latitude=48.85, longitude=2.35,
            owner=MagicMock(id='user1'), max_person=2,
            amenities=[MagicMock(name='Wi-Fi'), MagicMock(name='Parking')]
        )
        mock_create.return_value = mock_place

        response = self.client.post('/places/', json={
            'title': 'Charming Loft',
            'description': 'Nice and cozy',
            'price': 150,
            'latitude': 48.85,
            'longitude': 2.35,
            'owner_id': 'user1',
            'max_person': 2
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()['title'], 'Charming Loft')

    @patch('app.services.facade.create_place')
    def test_create_place_invalid_data(self, mock_create):
        mock_create.side_effect = ValueError("Invalid data")

        response = self.client.post('/places/', json={
            'title': '',
            'price': -10,
            'latitude': 999,
            'longitude': 999,
            'owner_id': '',
            'max_person': 0
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.get_json())

    @patch('app.services.facade.get_all_places')
    def test_get_all_places_success(self, mock_get_all):
        mock_get_all.return_value = [
            MagicMock(id='1', title='Villa', description='Sea view', price=200,
                      latitude=48.0, longitude=2.0,
                      owner=MagicMock(id='owner1'), max_person=4)
        ]
        response = self.client.get('/places/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)
        self.assertEqual(response.get_json()[0]['title'], 'Villa')

    @patch('app.services.facade.get_place')
    def test_get_place_by_id_success(self, mock_get):
        mock_place = MagicMock(
            id='1', title='Loft', description='Nice',
            price=100, latitude=48.0, longitude=2.0,
            owner=MagicMock(id='owner1', first_name='Jane', last_name='Doe', email='jane@example.com'),
            max_person=3,
            amenities=[MagicMock(id='a1', name='Wi-Fi')]
        )
        mock_get.return_value = mock_place

        response = self.client.get('/places/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('owner', response.get_json())

    @patch('app.services.facade.get_place')
    def test_get_place_by_id_not_found(self, mock_get):
        mock_get.return_value = None
        response = self.client.get('/places/404')
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.get_json())

    @patch('app.services.facade.get_place')
    def test_get_place_by_id_raises_value_error(self, mock_get):
        mock_get.side_effect = ValueError("Invalid ID")
        response = self.client.get('/places/bad-id')
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.get_json())

    @patch('app.services.facade.update_place')
    def test_update_place_success(self, mock_update):
        mock_place = MagicMock(
            id='1', title='Updated Loft', description='Updated desc', price=180,
            latitude=45.0, longitude=4.0,
            owner=MagicMock(id='owner1'), max_person=3,
            amenities=[MagicMock(name='Wi-Fi')]
        )
        mock_update.return_value = mock_place

        response = self.client.put('/places/1', json={
            'title': 'Updated Loft',
            'description': 'Updated desc',
            'price': 180,
            'latitude': 45.0,
            'longitude': 4.0,
            'owner_id': 'owner1',
            'max_person': 3
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['title'], 'Updated Loft')

    @patch('app.services.facade.update_place')
    def test_update_place_not_found(self, mock_update):
        mock_update.return_value = None
        response = self.client.put('/places/999', json={
            'title': 'Non-existent',
            'price': 100,
            'latitude': 0,
            'longitude': 0,
            'owner_id': 'x',
            'max_person': 1
        })
        self.assertEqual(response.status_code, 404)

    @patch('app.services.facade.update_place')
    def test_update_place_invalid_data(self, mock_update):
        mock_update.side_effect = ValueError("Bad input")
        response = self.client.put('/places/1', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.get_json())

    @patch('app.services.facade.update_place')
    def test_update_place_raises_unhandled_exception(self, mock_update):
        mock_update.side_effect = Exception("Database is down")

        response = self.client.put('/places/1', json={
            'title': 'X', 'price': 50, 'latitude': 1, 'longitude': 2,
            'owner_id': 'user', 'max_person': 1
        })
        self.assertEqual(response.status_code, 500)
        self.assertIn('Internal server error', response.get_json()['error'])

if __name__ == '__main__':
    unittest.main()
