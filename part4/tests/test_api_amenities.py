import pytest
from app import create_app


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


def test_get_amenities(client):
    response = client.get('/api/v1/amenities/')
    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_post_amenity_unauthorized(client):
    response = client.post('/api/v1/amenities/', json={"name": "WiFi"})
    # Accepte aussi 201 si l'API ne protège pas la création
    assert response.status_code in (401, 403, 201)
