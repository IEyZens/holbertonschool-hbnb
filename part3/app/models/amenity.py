# Import necessary modules for amenity model functionality
from app.extensions import db, bcrypt
import uuid
from .base_model import BaseModel


class Amenity(BaseModel):
    """
    Data model representing an amenity entity associated with a place.

    This class defines a structured feature such as Wi-Fi or Parking, applying constraints on its attributes
    for data integrity and consistency across the application. Amenities can be associated with multiple places
    through a many-to-many relationship.

    Attributes:
        id (str): Unique identifier for the amenity (UUID format)
        name (str): The name of the amenity, required and limited to 50 characters
        created_at (datetime): Timestamp when the amenity was created (inherited from BaseModel)
        updated_at (datetime): Timestamp when the amenity was last updated (inherited from BaseModel)

    Database Table:
        amenities: Stores amenity records with unique names

    Relationships:
        places: Many-to-many relationship with Place model through place_amenity association table
    """

    __tablename__ = 'amenities'

    # Primary key: UUID string identifier
    id = db.Column(db.String(36), primary_key=True,
                   default=lambda: str(uuid.uuid4()))

    # Amenity name: required, maximum 50 characters
    name = db.Column(db.String(50), nullable=False)

    def __init__(self, name: str):
        """
        Construct an Amenity object with validation.

        Ensures the input meets type and length constraints before persisting the attribute in memory.
        Inherits standard metadata such as UUID and timestamps from the base model. The name is
        automatically cleaned (stripped of whitespace) and converted to title case for consistency.

        Args:
            name (str): The display name of the amenity (e.g., "WiFi", "Swimming Pool")

        Raises:
            TypeError: If name is not a string type
            ValueError: If name is missing, empty after stripping, or exceeds 50 characters

        Example:
            amenity = Amenity("wifi")  # Will be stored as "Wifi"
            amenity = Amenity("swimming pool")  # Will be stored as "Swimming Pool"
        """
        # Call parent constructor to initialize common attributes (id, timestamps)
        super().__init__()

        # Validate that name is a string type
        if not isinstance(name, str):
            raise TypeError("String error: Your input is not a string.")

        # Validate name is not empty and doesn't exceed length limit
        if not name or len(name.strip()) == 0 or len(name.strip()) > 50:
            raise ValueError(
                "Invalid Amenity: 'name' is required and must be a string with a maximum of 50 characters.")

        # Clean and format the name: strip whitespace and convert to title case
        self.name = name.strip().title()
