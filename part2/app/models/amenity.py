from .base_model import BaseModel

class Amenity(BaseModel):
    def __init__(self, name):
        super().__init__()

        if not name or len(name) > 50:
            raise ValueError("Invalid Amenity: 'name' is required and must be a string with a maximum of 50 characters.")

        self.name = name
