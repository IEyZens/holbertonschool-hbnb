import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_restx import Api
from app.api.v1.users import api as users_ns

class UserApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.api.add_namespace(users_ns, path='/users')
        self.client = self.app.test_client()

    @patch('app.services.facade.get_user_by_email')
    @patch('app.services.facade.create_user')
    def test_create_user_success(self, mock_create_user, mock_get_by_email):
        mock_get_by_email.return_value = None
        mock_user = MagicMock(
            id='123', first_name='Alice', last_name='Smith', email='alice@example.com'
        )
        mock_create_user.return_value = mock_user

        response = self.client.post('/users/', json={
            'first_name': 'Alice',
            'last_name': 'Smith',
            'email': 'alice@example.com'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()['email'], 'alice@example.com')

    @patch('app.services.facade.get_user_by_email')
    def test_create_user_email_already_registered(self, mock_get_by_email):
        mock_get_by_email.return_value = MagicMock()

        response = self.client.post('/users/', json={
            'first_name': 'Bob',
            'last_name': 'Brown',
            'email': 'bob@example.com'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.get_json())
        self.assertEqual(response.get_json()['error'], 'Email already registered')

    def test_create_user_invalid_data(self):
        # Missing email
        response = self.client.post('/users/', json={
            'first_name': 'Charlie',
            'last_name': 'Chaplin'
        })
        self.assertEqual(response.status_code, 400)

    @patch('app.services.facade.get_user')
    def test_get_user_by_id_success(self, mock_get_user):
        mock_user = MagicMock(
            id='1', first_name='John', last_name='Doe', email='john@example.com'
        )
        mock_get_user.return_value = mock_user

        response = self.client.get('/users/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['id'], '1')
        self.assertEqual(response.get_json()['email'], 'john@example.com')

    @patch('app.services.facade.get_user')
    def test_get_user_by_id_not_found(self, mock_get_user):
        mock_get_user.return_value = None

        response = self.client.get('/users/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.get_json())

if __name__ == '__main__':
    unittest.main()
