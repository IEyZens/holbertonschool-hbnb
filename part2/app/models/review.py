from .base_model import BaseModel
from .user import User
from .place import Place

class Review(BaseModel):
    def __init__(self, text, rating, place, user):
        super().__init__()

        if not text or len(text) < 1:
            raise ValueError("Invalid review text: 'text' must be a non-empty string.")

        if rating < 1 or rating > 5:
            raise ValueError("Invalid rating: The rating must be between 1 and 5.")

        if not isinstance(user, User):
            raise TypeError("Invalid user: must be an instance of the User class.")

        if not isinstance(place, Place):
            raise TypeError("Invalid place: must be an instance of the Place class.")

        self.text = text
        self.rating = rating
        self.place = place
        self.user = user
