import uuid
from datetime import datetime


class BaseModel:
    """
    Abstract base model providing shared attributes and methods.

    All domain entities (e.g., User, Place, Amenity) inherit from this class
    to gain common metadata such as UUID-based identity and automatic
    timestamp management for creation and updates.

    Attributes:
        id (str): Universally unique identifier (UUID4) for the entity.
        created_at (datetime): Timestamp representing creation time.
        updated_at (datetime): Timestamp reflecting the last modification time.
    """

    def __init__(self):
        """Initializes a new instance with a UUID and current timestamps."""
        # Génère un identifiant unique pour chaque instance
        self.id = str(uuid.uuid4())
        # Enregistre la date de création de l'instance
        self.created_at = datetime.now()
        # Initialise la date de dernière mise à jour à la création
        self.updated_at = datetime.now()

    def save(self):
        """
        Persist the current instance state by refreshing the update timestamp.

        This method updates the 'updated_at' field to the current datetime,
        typically used after a mutation to mark the modification time.
        """
        # Met à jour le timestamp pour refléter la dernière modification
        self.updated_at = datetime.now()

    def update(self, data):
        """
        Dynamically update instance attributes based on a dictionary payload.

        Iterates through each key/value in the input dictionary, updating
        matching attributes on the instance if they exist. After applying changes,
        the update timestamp is refreshed.

        Args:
            data (dict): Dictionary of attribute names and their new values.
        """
        # Parcourt les paires clé-valeur du dictionnaire
        for key, value in data.items():
            # Vérifie que l'attribut existe dans l'objet
            if hasattr(self, key):
                # Met à jour l'attribut avec la nouvelle valeur
                setattr(self, key, value)
        # Rafraîchit le timestamp de mise à jour
        self.save()
