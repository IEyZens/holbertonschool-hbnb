from .base_model import BaseModel
from .user import User
from .place import Place


class Review(BaseModel):
    """
    Represents a review left by a user for a place.

    Attributes:
        text (str): The content of the review.
        rating (int): Rating between 1 and 5.
        place (Place): The place being reviewed.
        user (User): The author of the review.
    """

    def __init__(self, text, rating, place, user):
        """
        Initializes a Review with validated input.

        Raises:
            ValueError: If text is empty or rating is out of bounds.
            TypeError: If place or user are not valid instances.
        """
        super().__init__()

        if not text or len(text) < 1:
            raise ValueError(
                "Invalid review text: 'text' must be a non-empty string.")

        if rating < 1 or rating > 5:
            raise ValueError(
                "Invalid rating: The rating must be between 1 and 5.")

        if not isinstance(user, User):
            raise TypeError(
                "Invalid user: must be an instance of the User class.")

        if not isinstance(place, Place):
            raise TypeError(
                "Invalid place: must be an instance of the Place class.")

        self.text = text
        self.rating = rating
        self.place = place
        self.user = user
