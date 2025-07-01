from .base_model import BaseModel


class Amenity(BaseModel):
    """
    Data model representing an amenity entity associated with a place.

    This class defines a structured feature such as Wi-Fi or Parking,
    applying constraints on its attributes for data integrity and
    consistency across the application.

    Attributes:
        name (str): The name of the amenity, required and limited to 50 characters.
    """

    def __init__(self, name: str):
        """
        Construct an Amenity object with validation.

        Ensures the input meets type and length constraints before
        persisting the attribute in memory. Inherits standard metadata
        such as UUID and timestamps from the base model.

        Args:
            name (str): The display name of the amenity.

        Raises:
            TypeError: If name is not a string.
            ValueError: If name is missing or exceeds 50 characters.
        """
        # Appel au constructeur de la classe parente pour initialiser les attributs communs
        super().__init__()

        # Vérifie que le nom est bien une chaîne de caractères
        if not isinstance(name, str):
            raise TypeError("String error: Your input is not a string.")

        # Vérifie que le nom n'est pas vide et ne dépasse pas 50 caractères
        if not name or len(name) > 50:
            raise ValueError(
                "Invalid Amenity: 'name' is required and must be a string with a maximum of 50 characters.")

        # Affectation de l'attribut name à l'objet
        self.name = name
