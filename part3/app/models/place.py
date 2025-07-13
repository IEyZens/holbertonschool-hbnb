# Importation des modules nécessaires
from app.models.user import User
from app.extensions import db, bcrypt
from sqlalchemy.orm import relationship
import uuid
from .base_model import BaseModel


# Association table for Place-Amenity many-to-many relationship
place_amenity = db.Table('place_amenity',
                         db.Column('place_id', db.String(36), db.ForeignKey(
                             'places.id'), primary_key=True),
                         db.Column('amenity_id', db.String(36), db.ForeignKey(
                             'amenities.id'), primary_key=True)
                         )


class Place(BaseModel):
    __tablename__ = 'places'

    id = db.Column(db.String(36), primary_key=True,
                   default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    max_person = db.Column(db.Integer, nullable=True)

    owner_id = db.Column(db.String(36), db.ForeignKey(
        'users.id'), nullable=False)
    owner = relationship('User', back_populates='owned_places')

    reviews = relationship('Review', back_populates='place', lazy=True)
    amenities = relationship('Amenity', secondary=place_amenity,
                             lazy='subquery', backref=db.backref('places', lazy=True))

    def __init__(self, title, description, price, latitude, longitude, owner, max_person=None):
        super().__init__()

        if not title or len(title) > 100:
            raise ValueError(
                "Invalid title: must be a non-empty string up to 100 characters.")
        if price < 0:
            raise ValueError("Invalid price: must be >= 0.")
        if latitude < -90 or latitude > 90:
            raise ValueError("Invalid latitude: must be between -90 and 90.")
        if longitude < -180 or longitude > 180:
            raise ValueError(
                "Invalid longitude: must be between -180 and 180.")
        if max_person is not None:
            if not isinstance(max_person, int) or max_person < 1:
                raise ValueError("max_person must be a positive integer.")

        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner
        self.max_person = max_person
