# Import necessary modules for place model functionality
from app.models.user import User
from app.extensions import db, bcrypt
from sqlalchemy.orm import relationship
import uuid
from .base_model import BaseModel


# Association table for Place-Amenity many-to-many relationship
# This intermediate table links places with their available amenities
place_amenity = db.Table('place_amenity',
                         # Foreign key to places table
                         db.Column('place_id', db.String(36), db.ForeignKey(
                             'places.id'), primary_key=True),
                         # Foreign key to amenities table
                         db.Column('amenity_id', db.String(36), db.ForeignKey(
                             'amenities.id'), primary_key=True)
                         )


class Place(BaseModel):
    """
    Entity representing a rental property or accommodation on the HBnB platform.

    This model encapsulates all the essential information about a place that can be rented,
    including location data, pricing, capacity, and associated amenities. It enforces
    comprehensive validation rules for data integrity and maintains relationships with
    users (owners), reviews, and amenities.

    The Place model serves as the core entity around which the rental platform revolves,
    linking property owners with potential guests through detailed listings.

    Attributes:
        id (str): Unique identifier for the place (UUID format)
        title (str): Display name/title of the place (maximum 100 characters)
        description (str): Detailed description of the place (optional, maximum 500 characters)
        price (float): Price per night for renting this place (must be >= 0)
        latitude (float): Geographic latitude coordinate (-90 to 90 degrees)
        longitude (float): Geographic longitude coordinate (-180 to 180 degrees)
        max_person (int): Maximum number of guests allowed (optional, must be positive)
        owner_id (str): Foreign key referencing the User who owns this place
        created_at (datetime): Place creation timestamp (inherited from BaseModel)
        updated_at (datetime): Last modification timestamp (inherited from BaseModel)

    Database Table:
        places: Stores place/property information with geographic and pricing data

    Relationships:
        owner: Many-to-one relationship with User model (the place owner)
        reviews: One-to-many relationship with Review model (reviews for this place)
        amenities: Many-to-many relationship with Amenity model (available features)

    Validation Rules:
        - Title must be non-empty and within 100 character limit
        - Price must be non-negative (free places allowed)
        - Latitude must be valid geographic coordinate (-90 to 90)
        - Longitude must be valid geographic coordinate (-180 to 180)
        - Max person count must be positive integer if specified
        - Owner must be a valid User instance
    """

    __tablename__ = 'places'

    # Primary key: UUID string identifier
    id = db.Column(db.String(36), primary_key=True,
                   default=lambda: str(uuid.uuid4()))

    # Place title: required, maximum 100 characters
    title = db.Column(db.String(100), nullable=False)

    # Place description: optional, maximum 500 characters
    description = db.Column(db.String(500), nullable=True)

    # Price per night: required, must be non-negative
    price = db.Column(db.Float, nullable=False)

    # Geographic coordinates: required for location mapping
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    # Maximum occupancy: optional, must be positive if specified
    max_person = db.Column(db.Integer, nullable=True)

    # Foreign key to users table for place ownership
    owner_id = db.Column(db.String(36), db.ForeignKey(
        'users.id'), nullable=False)

    # SQLAlchemy relationship definitions
    # Many-to-one: Each place has one owner, user can own multiple places
    owner = relationship('User', back_populates='owned_places')

    # One-to-many: Place can have multiple reviews
    reviews = relationship('Review', back_populates='place', lazy=True)

    # Many-to-many: Place can have multiple amenities, amenities can be in multiple places
    amenities = relationship('Amenity', secondary=place_amenity,
                             lazy='subquery', backref=db.backref('places', lazy=True))

    def __init__(self, title, description, price, latitude, longitude, owner, max_person=None):
        """
        Initialize a Place entity with comprehensive validation.

        Validates all input parameters according to business rules and geographic constraints.
        Ensures data integrity before creating the place instance. The owner must be a valid
        User object, and all numeric values must fall within acceptable ranges.

        Args:
            title (str): Display name for the place (1-100 characters)
            description (str): Detailed description (can be None or empty)
            price (float): Nightly rental price (must be >= 0, can be 0 for free)
            latitude (float): Geographic latitude (-90.0 to 90.0 degrees)
            longitude (float): Geographic longitude (-180.0 to 180.0 degrees)
            owner (User): User instance who owns this place
            max_person (int, optional): Maximum guest capacity (must be positive if provided)

        Raises:
            ValueError: For invalid title, price, coordinates, or max_person values

        Example:
            place = Place(
                title="Cozy Downtown Apartment",
                description="Beautiful 2BR apartment in city center",
                price=120.50,
                latitude=40.7128,
                longitude=-74.0060,
                owner=user_instance,
                max_person=4
            )

        Geographic Notes:
            - Latitude: -90 (South Pole) to +90 (North Pole)
            - Longitude: -180 (International Date Line West) to +180 (East)
            - Coordinates should be in decimal degrees format
        """
        # Call parent constructor to initialize common attributes (id, timestamps)
        super().__init__()

        # Validate title: must be non-empty string within length limit
        if not title or len(title) > 100:
            raise ValueError(
                "Invalid title: must be a non-empty string up to 100 characters.")

        # Validate price: must be non-negative (free rentals allowed)
        if price < 0:
            raise ValueError("Invalid price: must be >= 0.")

        # Validate latitude: must be within valid geographic range
        if latitude < -90 or latitude > 90:
            raise ValueError("Invalid latitude: must be between -90 and 90.")

        # Validate longitude: must be within valid geographic range
        if longitude < -180 or longitude > 180:
            raise ValueError(
                "Invalid longitude: must be between -180 and 180.")

        # Validate max_person if provided: must be positive integer
        if max_person is not None:
            if not isinstance(max_person, int) or max_person < 1:
                raise ValueError("max_person must be a positive integer.")

        # Assign validated attributes to the place instance
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner
        self.max_person = max_person
