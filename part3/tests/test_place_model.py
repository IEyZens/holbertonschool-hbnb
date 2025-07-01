# Importation de pytest pour les tests unitaires
import pytest

# Importation des modèles nécessaires
from app.models.place import Place
from app.models.user import User
from app.models.review import Review
from app.models.amenity import Amenity


# Fonction exécutée avant chaque test pour réinitialiser les emails
def setup_function():
    # Nettoyage de l'ensemble des emails déjà utilisés par les utilisateurs
    User.existing_emails.clear()


# Fonction utilitaire pour créer un utilisateur avec un email unique
def create_user():
    # Génère un UUID pour garantir l’unicité de l’email
    import uuid
    return User("Test", "Owner", f"{uuid.uuid4()}@example.com")


# Test de la création valide d'un lieu (Place)
def test_valid_place_creation():
    # Création d’un utilisateur
    user = create_user()
    # Création d’un lieu avec des données valides
    place = Place("Chalet", "Cosy spot", 120.0, 45.0, 2.0, user, 4)

    # Vérifie que tous les attributs sont correctement affectés
    assert place.title == "Chalet"
    assert place.price == 120.0
    assert place.latitude == 45.0
    assert place.longitude == 2.0
    assert place.owner == user
    assert place.max_person == 4
    assert place.reviews == []
    assert place.amenities == []


# Paramètre des titres invalides : vide ou trop long
@pytest.mark.parametrize("title", ["", "A" * 101])
def test_invalid_title(title):
    user = create_user()
    # Vérifie qu'une ValueError est levée pour un titre invalide
    with pytest.raises(ValueError, match="Invalid title"):
        Place(title, "desc", 100, 48.0, 2.0, user, 2)


# Paramètre des prix invalides : négatifs
@pytest.mark.parametrize("price", [-1.0, -100.5])
def test_invalid_price(price):
    user = create_user()
    # Vérifie qu'une ValueError est levée pour un prix invalide
    with pytest.raises(ValueError, match="Invalid price"):
        Place("Nice", "desc", price, 48.0, 2.0, user, 2)


# Paramètre des latitudes invalides : hors des bornes -90 à 90
@pytest.mark.parametrize("lat", [-91, 91])
def test_invalid_latitude(lat):
    user = create_user()
    # Vérifie qu'une ValueError est levée pour une latitude invalide
    with pytest.raises(ValueError, match="Invalid latitude"):
        Place("Nice", "desc", 100, lat, 2.0, user, 2)


# Paramètre des longitudes invalides : hors des bornes -180 à 180
@pytest.mark.parametrize("lon", [-181, 181])
def test_invalid_longitude(lon):
    user = create_user()
    # Vérifie qu'une ValueError est levée pour une longitude invalide
    with pytest.raises(ValueError, match="Invalid longitude"):
        Place("Nice", "desc", 100, 48.0, lon, user, 2)


# Teste si une erreur est levée lorsque le propriétaire n’est pas un User
def test_invalid_owner_type():
    # Vérifie qu'un TypeError est levé si le propriétaire est une chaîne
    with pytest.raises(TypeError, match="Invalid owner"):
        Place("Nice", "desc", 100, 48.0, 2.0, "not a user", 2)


# Teste si une erreur est levée pour une capacité invalide
def test_invalid_capacity():
    user = create_user()
    # Vérifie qu'une ValueError est levée si max_person est ≤ 0
    with pytest.raises(ValueError, match="Invalid capacity"):
        Place("Nice", "desc", 100, 48.0, 2.0, user, 0)


# Teste l’ajout d’un avis valide à un lieu
def test_add_review_to_place():
    user = create_user()
    place = Place("Loft", "Modern", 130, 48.0, 2.0, user, 2)
    review = Review("Awesome!", 5, place, user)
    # Ajoute l’avis au lieu
    place.add_review(review)
    # Vérifie que l’avis a bien été ajouté à la liste des avis
    assert review in place.reviews


# Teste que l’ajout d’un avis invalide (non Review) lève une erreur
def test_add_invalid_review():
    user = create_user()
    place = Place("Loft", "Modern", 130, 48.0, 2.0, user, 2)
    # Vérifie qu’un TypeError est levé pour un avis invalide
    with pytest.raises(TypeError, match="Invalid review"):
        place.add_review("not a review")


# Teste l’ajout valide d’une commodité à un lieu
def test_add_amenity_to_place():
    user = create_user()
    place = Place("Villa", "Luxury", 250, 48.0, 2.0, user, 4)
    amenity = Amenity("WiFi")
    # Ajoute l’amenity au lieu
    place.add_amenity(amenity)
    # Vérifie que l’amenity a bien été ajoutée à la liste
    assert amenity in place.amenities


# Teste l’ajout invalide d’une commodité (non Amenity)
def test_add_invalid_amenity():
    user = create_user()
    place = Place("Villa", "Luxury", 250, 48.0, 2.0, user, 4)
    # Vérifie qu’un TypeError est levé si on passe un entier
    with pytest.raises(TypeError, match="Invalid amenity"):
        place.add_amenity(123)
