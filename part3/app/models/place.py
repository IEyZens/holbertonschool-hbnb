# Importation des modules nécessaires
from app import db, bcrypt
import uuid
from .base_model import BaseModel

# Table d'association entre Place et Amenity (relation many-to-many)
place_amenity = db.Table('place_amenity',
                         db.Column('place_id', db.Integer, db.ForeignKey(
                             'places.id'), primary_key=True),
                         db.Column('amenity_id', db.Integer, db.ForeignKey(
                             'amenities.id'), primary_key=True)
                         )


class Place(BaseModel):
    """
    Domain entity representing a rentable place listed on the platform.

    This model encapsulates geographic, descriptive, and ownership data, and enforces strict validation constraints. It also manages relationships with User, Amenity, and Review entities.

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

    __tablename__ = 'places'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    max_person = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)

    reviews = db.relationship('Review', backref='place', lazy=True)
    amenities = db.relationship(
        'Amenity', secondary=place_amenity, backref='places', lazy=True)
    owner = db.relationship('User', backref='places', lazy=True)

    def __init__(self, title: str, description: str, price: float, latitude: float, longitude: float):
        """
        Initializes a new Place entity and validates all core attributes.

        Only maps the core attributes as specified in the task.
        No relationships are included at this stage.

        Args:
            title (str): The title of the place.
            description (str): The description of the place.
            price (float): Price per night (must be >= 0).
            latitude (float): Latitude in degrees (-90 to 90).
            longitude (float): Longitude in degrees (-180 to 180).

        Raises:
            ValueError: For out-of-range or missing data.
        """
        # Appel au constructeur de la classe parente pour initialiser id, created_at, updated_at
        super().__init__()

        # Vérifie que le titre n'est pas vide et ne dépasse pas 100 caractères
        if not title or len(title) > 100:
            raise ValueError(
                "Invalid title: must be a non-empty string up to 100 characters.")

        # Vérifie que le prix est positif ou nul
        if price < 0:
            raise ValueError(
                "Invalid price: must be a number greater than or equal to 0.")

        # Vérifie que la latitude est dans l'intervalle valide
        if latitude < -90 or latitude > 90:
            raise ValueError(
                "Invalid latitude: must be a float between -90 and 90 degrees.")

        # Vérifie que la longitude est dans l'intervalle valide
        if longitude < -180 or longitude > 180:
            raise ValueError(
                "Invalid longitude: must be a float between -180 and 180 degrees.")

        # Affectation des attributs à l'instance
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
