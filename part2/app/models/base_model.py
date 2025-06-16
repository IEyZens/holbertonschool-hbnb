import uuid
from datetime import datetime


class BaseModel:
    """
    Base class that defines common attributes and methods for all models.

    Attributes:
        id (str): Unique identifier generated using UUID4.
        created_at (datetime): Timestamp when the instance is created.
        updated_at (datetime): Timestamp when the instance was last updated.
    """

    def __init__(self):
        """Initializes a new instance with a UUID and timestamps."""
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def save(self):
        """
        Updates the 'updated_at' timestamp to the current datetime.
        """
        self.updated_at = datetime.now()

    def update(self, data):
        """
        Updates attributes from a dictionary and refreshes 'updated_at'.

        Args:
            data (dict): Dictionary of attributes to update.
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()
