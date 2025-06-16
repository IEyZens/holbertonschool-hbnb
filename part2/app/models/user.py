from .base_model import BaseModel
import re
from .place import Place
from .review import Review


class User(BaseModel):
    """
    Represents a user of the HBnB platform.

    Attributes:
        first_name (str): User's first name, max 50 characters.
        last_name (str): User's last name, max 50 characters.
        email (str): Unique email address.
        is_admin (bool): Whether the user has admin rights. Defaults to False.
        places (list): List of Place instances owned by the user.
        reviews (list): List of Review instances written by the user.
    """

    existing_emails = set()

    def __init__(self, first_name, last_name, email, is_admin=False):
        """
        Initializes a User with validated attributes.

        Raises:
            ValueError: If any attribute is invalid or email is not unique.
            TypeError: If 'is_admin' is not a boolean.
        """
        super().__init__()

        if not first_name or len(first_name) > 50:
            raise ValueError(
                "Invalid first name: The maximum number of characters is 50.")

        if not last_name or len(last_name) > 50:
            raise ValueError(
                "Invalid last name: The maximum number of characters is 50.")

        if not isinstance(is_admin, bool):
            raise TypeError(
                "Invalid is_admin flag: must be a boolean (True or False).")

        if not re.fullmatch(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}', email):
            raise ValueError("Invalid email: must be a valid email address.")
        if email in User.existing_emails:
            raise ValueError(
                "Email already exists: each user must have a unique email address.")
        User.existing_emails.add(email)

        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        self.places = []
        self.reviews = []

    def add_place(self, place):
        """
        Adds a Place instance to the user's list of owned places.

        Args:
            place (Place): A valid Place instance.

        Raises:
            TypeError: If the argument is not a Place instance.
        """
        if not isinstance(place, Place):
            raise TypeError("add_place() expected a Place instance.")
        self.places.append(place)

    def add_review(self, review):
        """
        Adds a Review instance to the user's list of reviews.

        Args:
            review (Review): A valid Review instance.

        Raises:
            TypeError: If the argument is not a Review instance.
        """
        if not isinstance(review, Review):
            raise TypeError("add_review() expected a Review instance.")
        self.reviews.append(review)
