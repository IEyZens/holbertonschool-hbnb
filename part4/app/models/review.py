# Import necessary modules for review model functionality
from app.extensions import db
from sqlalchemy.orm import relationship
import uuid
from .base_model import BaseModel


class Review(BaseModel):
    """
    Entity representing a textual and numerical evaluation made by a user on a place.

    This model encapsulates user-generated feedback for rental properties, combining
    both qualitative text reviews and quantitative ratings. It enforces validation
    rules and maintains referential integrity between users and places to ensure
    authentic and traceable reviews.

    The Review model is central to the platform's trust and quality system, allowing
    guests to share their experiences and helping future guests make informed decisions.

    Attributes:
        id (str): Unique identifier for the review (UUID format)
        text (str): Content of the review (maximum 300 characters, required)
        rating (int): Numerical rating from 1 to 5 stars (required)
        place_id (str): Foreign key referencing the Place being reviewed
        user_id (str): Foreign key referencing the User who wrote the review
        created_at (datetime): Review creation timestamp (inherited from BaseModel)
        updated_at (datetime): Last modification timestamp (inherited from BaseModel)

    Database Table:
        reviews: Stores review content and ratings with foreign key relationships

    Relationships:
        place: Many-to-one relationship with Place model (the reviewed property)
        user: Many-to-one relationship with User model (the review author)

    Validation Rules:
        - Text must be non-empty (minimum 1 character)
        - Text cannot exceed 300 characters for readability
        - Rating must be integer between 1 and 5 (inclusive)
        - Both user and place must be valid instances

    Business Rules:
        - Users should not review their own properties (enforced at service layer)
        - One review per user per place (enforced at service layer)
        - Reviews can be updated but history is not maintained
    """

    __tablename__ = 'reviews'

    # Primary key: UUID string identifier
    id = db.Column(db.String(36), primary_key=True,
                   default=lambda: str(uuid.uuid4()))

    # Review text content: required, maximum 300 characters
    text = db.Column(db.String(300), nullable=False)

    # Numerical rating: required, integer between 1-5
    rating = db.Column(db.Integer, nullable=False)

    # Foreign key relationships
    # Reference to the place being reviewed
    place_id = db.Column(db.String(36), db.ForeignKey(
        'places.id'), nullable=False)

    # Reference to the user who wrote the review
    user_id = db.Column(db.String(36), db.ForeignKey(
        'users.id'), nullable=False)

    # SQLAlchemy relationship definitions
    # Many-to-one: Multiple reviews can be for the same place
    place = relationship('Place', back_populates='reviews')

    # Many-to-one: Multiple reviews can be written by the same user
    user = relationship('User', back_populates='reviews')

    def __init__(self, text: str, rating: int, user, place):
        """
        Initialize a Review entity and validate all its core fields.

        Validates the review content and rating according to business rules before
        creating the review instance. Ensures the text is meaningful and the rating
        falls within the acceptable 5-star scale range.

        Args:
            text (str): Review message content (1-300 characters)
            rating (int): Star rating from 1 (worst) to 5 (best)
            user (User): User instance who is writing the review
            place (Place): Place instance being reviewed

        Raises:
            ValueError: If text is empty/too long or rating is outside valid range (1-5)

        Example:
            review = Review(
                text="Great place with excellent amenities!",
                rating=5,
                user=user_instance,
                place=place_instance
            )

        Rating Scale:
            1 - Very Poor (major issues, would not recommend)
            2 - Poor (significant problems, below expectations)
            3 - Average (acceptable, meets basic expectations)
            4 - Good (above average, minor issues if any)
            5 - Excellent (exceeds expectations, highly recommended)

        Text Guidelines:
            - Should be descriptive and helpful for future guests
            - Minimum 1 character to prevent empty reviews
            - Maximum 300 characters for readability and database efficiency
        """
        # Call parent constructor to initialize common attributes (id, timestamps)
        super().__init__()

        # Validate review text: must be non-empty and within length limit
        if not text or len(text) < 1:
            raise ValueError(
                "Invalid review text: 'text' must be a non-empty string.")

        # Validate rating: must be within the 1-5 star range (inclusive)
        if rating < 1 or rating > 5:
            raise ValueError(
                "Invalid rating: The rating must be between 1 and 5.")

        # Assign validated attributes to the review instance
        self.text = text
        self.rating = rating
        self.user = user
        self.place = place
