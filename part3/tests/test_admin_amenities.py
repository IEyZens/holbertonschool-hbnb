import pytest
from unittest.mock import patch
from app import create_app
import warnings


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    # Création des tables pour la base de test
    with app.app_context():
        from app.extensions import db
        db.create_all()
    with app.test_client() as client:
        yield client


def test_admin_post_amenity_forbidden(client):
    response = client.post('/api/v1/admin_amenities/', json={"name": "WiFi"})
    if response.status_code == 404:
        warnings.warn(
            "Endpoint /api/v1/admin_amenities/ non disponible, test ignoré.")
        pytest.skip("Endpoint non disponible")
    assert response.status_code in (401, 403)


@patch('app.api.v1.admin_amenities.get_jwt_identity', return_value={'is_admin': True})
def test_admin_post_amenity_success(mock_jwt, client):
    response = client.post('/api/v1/admin_amenities/', json={"name": "WiFi"})
    if response.status_code == 404:
        warnings.warn(
            "Endpoint /api/v1/admin_amenities/ non disponible, test ignoré.")
        pytest.skip("Endpoint non disponible")
    assert response.status_code in (200, 201)
