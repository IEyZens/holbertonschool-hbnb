import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_restx import Api
from app.api.v1.reviews import api as reviews_ns

class ReviewApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.api.add_namespace(reviews_ns, path='/reviews')
        self.client = self.app.test_client()

    @patch('app.services.facade.create_review')
    def test_create_review_success(self, mock_create):
        mock_review = MagicMock(
            id='1',
            text='Great!',
            rating=5,
            place=MagicMock(id='101'),
            user=MagicMock(id='u001')
        )
        mock_create.return_value = mock_review

        response = self.client.post('/reviews/', json={
            'text': 'Great!',
            'rating': 5,
            'place_id': '101',
            'user_id': 'u001'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()['text'], 'Great!')

    @patch('app.services.facade.create_review')
    def test_create_review_invalid(self, mock_create):
        mock_create.side_effect = ValueError("Missing field")

        response = self.client.post('/reviews/', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.get_json())

    @patch('app.services.facade.get_all_reviews')
    def test_get_all_reviews(self, mock_get_all):
        mock_get_all.return_value = [
            MagicMock(id='1', text='Nice', rating=4, place=MagicMock(id='p1'), user=MagicMock(id='u1'))
        ]

        response = self.client.get('/reviews/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)
        self.assertEqual(response.get_json()[0]['id'], '1')

    @patch('app.services.facade.get_review')
    def test_get_review_found(self, mock_get):
        mock_review = MagicMock(
            id='1', text='Awesome', rating=5,
            place=MagicMock(id='p1'), user=MagicMock(id='u1')
        )
        mock_get.return_value = mock_review

        response = self.client.get('/reviews/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['rating'], 5)

    @patch('app.services.facade.get_review')
    def test_get_review_not_found(self, mock_get):
        mock_get.side_effect = ValueError("Not found")

        response = self.client.get('/reviews/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.get_json())

    @patch('app.services.facade.update_review')
    def test_update_review_success(self, mock_update):
        mock_review = MagicMock(
            id='1', text='Updated', rating=3,
            place=MagicMock(id='p1'), user=MagicMock(id='u1')
        )
        mock_update.return_value = mock_review

        response = self.client.put('/reviews/1', json={
            'text': 'Updated',
            'rating': 3,
            'place_id': 'p1',
            'user_id': 'u1'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['text'], 'Updated')

    @patch('app.services.facade.update_review')
    def test_update_review_not_found(self, mock_update):
        mock_update.side_effect = KeyError("Not found")

        response = self.client.put('/reviews/999', json={
            'text': 'Updated',
            'rating': 3,
            'place_id': 'p1',
            'user_id': 'u1'
        })
        self.assertEqual(response.status_code, 404)

    @patch('app.services.facade.update_review')
    def test_update_review_invalid_data(self, mock_update):
        mock_update.side_effect = ValueError("Bad input")

        response = self.client.put('/reviews/1', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.get_json())

    @patch('app.services.facade.delete_review')
    def test_delete_review_success(self, mock_delete):
        mock_delete.return_value = True

        response = self.client.delete('/reviews/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.get_json())

    @patch('app.services.facade.delete_review')
    def test_delete_review_not_found(self, mock_delete):
        mock_delete.return_value = None

        response = self.client.delete('/reviews/999')
        self.assertEqual(response.status_code, 404)

    @patch('app.services.facade.delete_review')
    def test_delete_review_keyerror(self, mock_delete):
        mock_delete.side_effect = KeyError("Not found")

        response = self.client.delete('/reviews/123')
        self.assertEqual(response.status_code, 404)

    @patch('app.services.facade.get_reviews_by_place')
    def test_get_reviews_by_place_success(self, mock_get_by_place):
        mock_get_by_place.return_value = [
            MagicMock(id='1', text='Nice', rating=4, place=MagicMock(id='p1'), user=MagicMock(id='u1'))
        ]

        response = self.client.get('/reviews/places/p1/reviews')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]['place_id'], 'p1')

    @patch('app.services.facade.get_reviews_by_place')
    def test_get_reviews_by_place_not_found(self, mock_get_by_place):
        mock_get_by_place.side_effect = KeyError("Place not found")

        response = self.client.get('/reviews/places/invalid_id/reviews')
        self.assertEqual(response.status_code, 404)
