from .base_model import BaseModel


class Amenity(BaseModel):
    """
    Represents a feature or service available at a place (e.g., Wi-Fi, Parking).

    Attributes:
        name (str): The name of the amenity, max 50 characters.
    """

    def __init__(self, name):
        """
        Initializes an Amenity with a validated name.

        Raises:
            ValueError: If the name is missing or exceeds 50 characters.
        """
        super().__init__()

        if not name or len(name) > 50:
            raise ValueError(
                "Invalid Amenity: 'name' is required and must be a string with a maximum of 50 characters.")

        self.name = name
