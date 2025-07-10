# Importation des modules nécessaires
from app import db
import uuid
from .base_model import BaseModel


class Review(BaseModel):
    """
    Entity representing a textual and numerical evaluation made by a user on a place.

    Encapsulates validation rules and strong typing for user-generated feedback. Enforces referential integrity by ensuring the user and place are valid domain objects.

    Attributes:
        text (str): The content of the review.
        rating (int): Rating between 1 and 5.
        place (Place): The place being reviewed (foreign key).
        user (User): The author of the review (foreign key).
    """

    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    text = db.Column(db.String(300), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey(
        'places.id'), nullable=False)

    def __init__(self, text: str, rating: int):
        """
        Initialize a Review entity and validate all its core fields.

        Only maps the core attributes as specified in the task.
        No relationships are included at this stage.

        Args:
            text (str): Review message content.
            rating (int): Integer score, must be between 1 and 5.

        Raises:
            ValueError: If text is empty or rating is outside the allowed range.
        """
        # Appel au constructeur de la classe parente pour initialiser les métadonnées communes
        super().__init__()

        # Vérifie que le texte de l'avis n'est pas vide
        if not text or len(text) < 1:
            raise ValueError(
                "Invalid review text: 'text' must be a non-empty string.")

        # Vérifie que la note est comprise entre 1 et 5 inclus
        if rating < 1 or rating > 5:
            raise ValueError(
                "Invalid rating: The rating must be between 1 and 5.")

        # Attribution des attributs à l'instance
        self.text = text
        self.rating = rating
