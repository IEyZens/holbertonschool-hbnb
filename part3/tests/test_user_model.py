# Importation du module pytest pour les tests unitaires et les assertions d'exception
import pytest

# Importation du modèle User pour les tests
from app.models.user import User

# Importation du modèle Place (utilisé pour tester l'association avec un utilisateur)
from app.models.place import Place

# Importation du modèle Review (utilisé pour tester les avis d'un utilisateur)
from app.models.review import Review


# Fonction exécutée avant chaque test pour réinitialiser les emails déjà utilisés
def setup_function():
    # Vide l'ensemble des emails existants pour éviter des erreurs de duplication entre tests
    User.existing_emails.clear()


# Test de la création d’un utilisateur valide
def test_valid_user_creation():
    # Création d’un nouvel utilisateur avec des attributs valides
    user = User("Alice", "Smith", "alice@example.com", "password123")

    # Vérifie que le prénom est correctement assigné
    assert user.first_name == "Alice"

    # Vérifie que le nom de famille est bien attribué
    assert user.last_name == "Smith"

    # Vérifie que l'email est bien enregistré
    assert user.email == "alice@example.com"

    # Vérifie que l'utilisateur n'est pas admin par défaut
    assert user.is_admin is False

    # Vérifie que l'utilisateur n'a pas de lieux associés à la création
    assert user.places == []

    # Vérifie que l'utilisateur n'a pas encore d'avis associés
    assert user.reviews == []


# Test paramétré sur des prénoms invalides (vide ou trop long)
@pytest.mark.parametrize("first_name", ["", "A" * 51])
def test_invalid_first_name(first_name):
    # Vérifie qu'une exception ValueError est levée avec un message explicite
    with pytest.raises(ValueError, match="Invalid first name"):
        User(first_name, "Doe", "user1@example.com", "password123")


# Test paramétré sur des noms de famille invalides
@pytest.mark.parametrize("last_name", ["", "B" * 51])
def test_invalid_last_name(last_name):
    # Vérifie que la création échoue avec un nom de famille invalide
    with pytest.raises(ValueError, match="Invalid last name"):
        User("John", last_name, "user2@example.com", "password123")


# Test paramétré sur plusieurs formats d’email incorrects
@pytest.mark.parametrize("email", [
    "invalidemail",
    "missing@domain",
    "@missingname.com",
    "user@.com",
    "user@com",
    "user@domain.c"
])
def test_invalid_email_format(email):
    # Vérifie qu’une ValueError est levée pour chaque email invalide
    with pytest.raises(ValueError, match="Invalid email"):
        User("Jane", "Doe", email, "password123")


# Test de la gestion des doublons d’email utilisateur
def test_duplicate_email_raises_error():
    # Création d'un premier utilisateur avec un email donné
    User("Bob", "Doe", "bob@example.com", "password123")

    # Deuxième création avec le même email : doit échouer
    with pytest.raises(ValueError, match="Email already exists"):
        User("Bobby", "Doe", "bob@example.com", "password123")


# Test que le champ is_admin doit impérativement être un booléen
def test_is_admin_must_be_boolean():
    # Création d'un utilisateur en passant une chaîne pour is_admin
    with pytest.raises(TypeError, match="must be a boolean"):
        User("Admin", "User", "admin@example.com",
             "password123", is_admin="yes")


# Test de l'ajout d'un lieu valide à un utilisateur
def test_add_place_to_user():
    # Création d'un utilisateur
    user = User("Eve", "Taylor", "eve@example.com", "password123")

    # Création d’un objet Place associé à l’utilisateur
    place = Place("Test Place", "Test description", 80, 48.85, 2.35, user, 4)

    # Ajout du lieu à l'utilisateur
    user.add_place(place)

    # Vérifie que le lieu est bien dans la liste des lieux de l’utilisateur
    assert place in user.places


# Test de l’ajout invalide d’un objet non-Place à la liste des lieux
def test_add_invalid_place_raises():
    # Création d’un utilisateur
    user = User("Tom", "Lee", "tom@example.com", "password123")

    # Ajout d’une chaîne de caractères au lieu d’un objet Place : doit lever TypeError
    with pytest.raises(TypeError):
        user.add_place("not a place")


# Test de l’ajout d’un avis valide à un utilisateur
def test_add_review_to_user():
    # Création d’un utilisateur
    user = User("Mia", "Stone", "mia@example.com", "password123")

    # Création d’un lieu auquel associer l’avis
    place = Place("Test Place", "Test description", 80, 48.85, 2.35, user, 4)

    # Création d’un avis sur ce lieu par l’utilisateur
    review = Review("Nice!", 5, place, user)

    # Ajout de l’avis à l’utilisateur
    user.add_review(review)

    # Vérifie que l’avis est bien ajouté à la liste des reviews
    assert review in user.reviews


# Test de l’ajout invalide d’un avis (type incorrect)
def test_add_invalid_review_raises():
    # Création d’un utilisateur
    user = User("Liam", "Fox", "liam@example.com", "password123")

    # Tentative d’ajouter un entier au lieu d’un objet Review : doit échouer
    with pytest.raises(TypeError):
        user.add_review(123)
