from .base_model import BaseModel
import re
from .place import Place
from .review import Review

class User(BaseModel):

    existing_emails = set()

    def __init__(self, first_name, last_name, email, is_admin=False):
        super().__init__()

        if not first_name or len(first_name) > 50:
            raise ValueError("Invalid first name: The maximum number of characters is 50.")

        if not last_name or len(last_name) > 50:
            raise ValueError("Invalid last name: The maximum number of characters is 50.")

        if not isinstance(is_admin, bool):
            raise TypeError("Invalid is_admin flag: must be a boolean (True or False).")

        if not re.fullmatch(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}', email):
            raise ValueError("Invalid email: must be a valid email address.")
        if email in User.existing_emails:
            raise ValueError("Email already exists: each user must have a unique email address.")
        User.existing_emails.add(email)

        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        self.places = []
        self.reviews = []

    def add_place(self, place):
        if not isinstance(place, Place):
            raise TypeError("add_place() expected a Place instance.")
        self.places.append(place)

    def add_review(self, review):
        if not isinstance(review, Review):
            raise TypeError("add_review() expected a Review instance.")
        self.reviews.append(review)
