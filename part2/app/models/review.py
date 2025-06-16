from .base_model import BaseModel

class Review(BaseModel):
    def __init__(self, text, rating, place, user):
        super().__init__()

        if rating < 1 or rating > 5:
            raise ValueError("Invalid rating: The rating must be between 1 and 5.")

        

        self.text = text
        self.rating = rating
        self.place = place
        self.user = user
