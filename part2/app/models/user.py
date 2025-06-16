from .base_model import BaseModel
import re

class User(BaseModel):
    def __init__(self, first_name, last_name, email, is_admin):
        super().__init__()

        if not first_name or len(first_name) > 50:
            raise ValueError("Invalid first name: The maximum number of characters is 50.")

        if not last_name or len(last_name) > 50:
            raise ValueError("Invalid name: The maximum number of characters is 50.")

        if not is_admin:
            raise TypeError("Admin required: You do not have administrator access.")

        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin

    def check(email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

        if (re.fullmatch(regex, email)):
            print("Your email address is valid.")
        else:
            print("Your email address is invalid.")
