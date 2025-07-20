# Importation de pytest pour le framework de test
import pytest

# Importation du modèle Amenity à tester
from app.models.amenity import Amenity


# Test de la création valide d'une commodité
def test_valid_amenity_creation():
    # Création d'une commodité avec un nom valide
    a = Amenity("WiFi")

    # Vérifie que l'objet créé est bien une instance de la classe Amenity
    assert isinstance(a, Amenity)

    # Vérifie que le nom est bien attribué
    assert a.name == "WiFi"


# Paramétrage du test pour vérifier les types invalides passés à Amenity
@pytest.mark.parametrize("name", [None, 123, 45.6, [], {}])
def test_amenity_name_type_error(name):
    # Attend une exception de type TypeError si le nom n'est pas une chaîne de caractères
    with pytest.raises(TypeError, match="String error"):
        Amenity(name)


# Paramétrage du test pour tester des noms vides ou trop longs
@pytest.mark.parametrize("name", ["", "A" * 51])
def test_amenity_name_value_error(name):
    # Attend une exception de type ValueError si le nom est vide ou dépasse la longueur maximale
    with pytest.raises(ValueError, match="Invalid Amenity"):
        Amenity(name)
