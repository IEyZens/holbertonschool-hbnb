from .base_model import BaseModel

class Place(BaseModel):
    def __init__(self, title, description, price, latitude, longitude, owner, max_person):
        super().__init__()

        if not title or len(title) > 100:
            raise ValueError("Invalid title: The title must be less than or equal to 100 characters.")

        if price < 0:
            raise ValueError("Invalid price: The price must be positive.")

        if latitude < 90 or latitude > -90:
            raise ValueError("Invalid latitude: Latitude must be between -90 and 90.")

        if longitude < 180 or longitude > -180:
            raise ValueError("Invalid longitude: Longitude must be between -180 and 180.")

        if owner is False:
            raise TypeError("Invalid owner: You must be the owner of the site.")

        if max_person < 1:
            raise ValueError("Invalid capacity: The maximum number of people must be at least 1.")


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
        self.reviews.append(review)

    def add_amenity(self, amenity):
        self.amenities.append(amenity)
