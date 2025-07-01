from .base_model import BaseModel


class Review(BaseModel):
    """
    Entity representing a textual and numerical evaluation made by a user on a place.

    Encapsulates validation rules and strong typing for user-generated feedback.
    Enforces referential integrity by ensuring the user and place are valid domain objects.

    Attributes:
        text (str): The content of the review.
        rating (int): Rating between 1 and 5.
        place (Place): The place being reviewed (foreign key).
        user (User): The author of the review (foreign key).
    """

    def __init__(self, text: str, rating: int, place, user):
        """
        Initializes a Review entity and validates all its core fields.

        Args:
            text (str): Review message content.
            rating (int): Integer score, must be between 1 and 5.
            place (Place): The Place being reviewed.
            user (User): The User writing the review.

        Raises:
            ValueError: If text is empty or rating is outside the allowed range.
            TypeError: If place or user are not valid class instances.
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

        # Importation locale de User pour éviter les boucles d'import
        from .user import User
        # Vérifie que l’auteur est bien une instance de User
        if not isinstance(user, User):
            raise TypeError(
                "Invalid user: must be an instance of the User class.")

        # Importation locale de Place pour éviter les dépendances circulaires
        from .place import Place
        # Vérifie que le lieu est bien une instance de Place
        if not isinstance(place, Place):
            raise TypeError(
                "Invalid place: must be an instance of the Place class.")

        # Attribution des attributs à l’instance
        self.text = text
        self.rating = rating
        self.place = place
        self.user = user
