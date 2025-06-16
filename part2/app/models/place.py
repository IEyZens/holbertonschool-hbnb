from .base_model import BaseModel
from .review import Review
from .amenity import Amenity
from .user import User


class Place(BaseModel):
    """
    Represents a rentable place on the platform.

    Attributes:
        title (str): Title of the place, max 100 characters.
        description (str): Optional description of the place.
        price (float): Price per night, must be >= 0.
        latitude (float): Latitude coordinate, between -90 and 90.
        longitude (float): Longitude coordinate, between -180 and 180.
        owner (User): The User who owns this place.
        max_person (int): Maximum capacity.
        reviews (list): List of associated Review instances.
        amenities (list): List of associated Amenity instances.
    """

    def __init__(self, title, description, price, latitude, longitude, owner, max_person):
        """
        Initializes a Place with validated attributes.

        Raises:
            ValueError: For invalid numeric or string constraints.
            TypeError: If 'owner' is not a User instance.
        """
        super().__init__()

        if not title or len(title) > 100:
            raise ValueError(
                "Invalid title: must be a non-empty string up to 100 characters.")

        if price < 0:
            raise ValueError(
                "Invalid price: must be a number greater than or equal to 0.")

        if latitude < -90 or latitude > 90:
            raise ValueError(
                "Invalid latitude: must be a float between -90 and 90 degrees.")

        if longitude < -180 or longitude > 180:
            raise ValueError(
                "Invalid longitude: must be a float between -180 and 180 degrees.")

        if not isinstance(owner, User):
            raise TypeError(
                "Invalid owner: must be an instance of the User class.")

        if max_person < 1:
            raise ValueError("Invalid capacity: must be at least 1 person.")

        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner
        self.max_person = max_person
        self.reviews = []
        self.amenities = []

    def add_review(self, review):
        """
        Adds a Review to the place.

        Args:
            review (Review): A valid Review instance.

        Raises:
            TypeError: If the argument is not a Review.
        """
        if not isinstance(review, Review):
            raise TypeError(
                "Invalid review: must be an instance of the Review class.")
        self.reviews.append(review)

    def add_amenity(self, amenity):
        """
        Adds an Amenity to the place.

        Args:
            amenity (Amenity): A valid Amenity instance.

        Raises:
            TypeError: If the argument is not an Amenity.
        """
        if not isinstance(amenity, Amenity):
            raise TypeError(
                "Invalid amenity: must be an instance of the Amenity class.")
        self.amenities.append(amenity)
