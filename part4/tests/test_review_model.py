# Importation de pytest pour les tests et des classes nécessaires à tester
import pytest
from app.models.review import Review
from app.models.user import User
from app.models.place import Place


# Fonction de configuration exécutée avant chaque test pour réinitialiser les emails
def setup_function():
    # Réinitialise l'ensemble des emails enregistrés pour éviter les conflits entre tests
    User.existing_emails.clear()


# Fonction utilitaire pour créer un utilisateur valide
def create_valid_user():
    # Retourne une instance de User valide avec des valeurs standards
    return User("John", "Doe", "john.doe@example.com", "password123")


# Fonction utilitaire pour créer un lieu valide associé à un utilisateur
def create_valid_place(user):
    # Retourne une instance de Place valide liée à l’utilisateur passé en argument
    return Place("Loft", "Nice and modern", 100, 48.85, 2.35, user, 2)


# Test de la création correcte d'une instance Review
def test_valid_review_creation():
    # Création d’un utilisateur et d’un lieu valides
    user = create_valid_user()
    place = create_valid_place(user)
    # Création d’une instance Review avec des données valides
    review = Review("Great stay!", 5, place, user)
    # Vérifie que les attributs ont bien été assignés
    assert review.text == "Great stay!"
    assert review.rating == 5
    assert review.user == user
    assert review.place == place


# Test paramétré pour vérifier les erreurs de texte de commentaire (vide ou None)
@pytest.mark.parametrize("text", ["", None])
def test_invalid_review_text(text):
    # Création d’un utilisateur et d’un lieu valides
    user = create_valid_user()
    place = create_valid_place(user)
    # Vérifie qu’une erreur est levée si le texte est invalide
    with pytest.raises(ValueError, match="Invalid review text"):
        Review(text, 4, place, user)


# Test paramétré pour vérifier que les notes en dehors de 1 à 5 lèvent une erreur
@pytest.mark.parametrize("rating", [0, 6, -1])
def test_invalid_rating(rating):
    # Création d’un utilisateur et d’un lieu valides
    user = create_valid_user()
    place = create_valid_place(user)
    # Vérifie que l’exception est bien levée pour un rating invalide
    with pytest.raises(ValueError, match="Invalid rating"):
        Review("Too high or too low", rating, place, user)


# Test que le type utilisateur invalide déclenche une erreur
def test_invalid_user_type():
    # Création d’un utilisateur et d’un lieu valides
    user = create_valid_user()
    place = create_valid_place(user)
    # Vérifie qu’une TypeError est levée si l’user n’est pas une instance User
    with pytest.raises(TypeError, match="Invalid user"):
        Review("Nice place", 4, place, "not a user")


# Test que le type place invalide déclenche une erreur
def test_invalid_place_type():
    # Création d’un utilisateur valide
    user = create_valid_user()
    # Vérifie qu’une TypeError est levée si place n’est pas une instance Place
    with pytest.raises(TypeError, match="Invalid place"):
        Review("Nice place", 4, "not a place", user)
