# Importation des modules nécessaires
from app.extensions import db
import uuid
from datetime import datetime


class BaseModel(db.Model):
    """
    Abstract base class providing common fields and methods for all data models.

    This class supplies a unique identifier, creation and update timestamps, and utility methods for saving and updating model instances. All models inheriting from BaseModel will automatically include these features.

    Attributes:
        id: Unique identifier for the instance (type can be customized by subclasses).
        created_at (datetime): Timestamp of creation.
        updated_at (datetime): Timestamp of last update.
    """

    __abstract__ = True

    # Note: id field is not defined here - subclasses must define their own id field
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def save(self):
        """
        Persist the current instance state by refreshing the update timestamp.

        This method updates the 'updated_at' field to the current datetime, typically used after a mutation to mark the modification time.
        """
        # Met à jour le timestamp pour refléter la dernière modification
        self.updated_at = datetime.utcnow()
        db.session.add(self)

    def update(self, data):
        """
        Dynamically update instance attributes based on a dictionary payload.

        Iterates through each key/value in the input dictionary, updating matching attributes on the instance if they exist. After applying changes, the update timestamp is refreshed.

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
        db.session.commit()
