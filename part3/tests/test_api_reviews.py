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


def test_get_reviews(client):
    response = client.get('/api/v1/reviews/')
    assert response.status_code == 200
    assert isinstance(response.json, list)
