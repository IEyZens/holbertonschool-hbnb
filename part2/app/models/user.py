from .base_model import BaseModel
import re


class User(BaseModel):
    """
    Entity representing a user registered on the HBnB platform.

    This model encapsulates identity, access control, and relationships
    with other entities such as Place and Review. It includes data validation
    for length, email format, and uniqueness constraints.

    Attributes:
        first_name (str): User's first name, max 50 characters.
        last_name (str): User's last name, max 50 characters.
        email (str): Unique and valid email address.
        is_admin (bool): Whether the user has administrative privileges.
        places (list): List of Place instances owned by the user.
        reviews (list): List of Review instances authored by the user.
    """

    # Ensemble statique pour suivre les emails existants (unicité)
    existing_emails = set()

    def __init__(self, first_name: str, last_name: str, email: str, is_admin: bool = False):
        """
        Initialize a User entity with validation and uniqueness checks.

        Enforces length constraints on names, ensures the email format is valid
        using a regular expression, and checks that the email is not already registered.
        Tracks related places and reviews.

        Args:
            first_name (str): Given name of the user.
            last_name (str): Surname of the user.
            email (str): Unique email address.
            is_admin (bool, optional): Admin rights flag. Defaults to False.

        Raises:
            ValueError: For invalid name/email or if email already exists.
            TypeError: If is_admin is not a boolean.
        """
        # Appel au constructeur de BaseModel (id, created_at, updated_at)
        super().__init__()

        # Validation du prénom : non vide, max 50 caractères
        if not first_name or len(first_name) > 50:
            raise ValueError(
                "Invalid first name: The maximum number of characters is 50.")

        # Validation du nom : non vide, max 50 caractères
        if not last_name or len(last_name) > 50:
            raise ValueError(
                "Invalid last name: The maximum number of characters is 50.")

        # Vérifie que le drapeau is_admin est un booléen
        if not isinstance(is_admin, bool):
            raise TypeError(
                "Invalid is_admin flag: must be a boolean (True or False).")

        # Vérifie que l’email respecte le format standard via une expression régulière
        if not re.fullmatch(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}', email):
            raise ValueError("Invalid email: must be a valid email address.")

        # Vérifie l’unicité de l’email
        if email in User.existing_emails:
            raise ValueError(
                "Email already exists: each user must have a unique email address.")

        # Ajoute l'email au set global pour éviter les doublons
        User.existing_emails.add(email)

        # Affectation des attributs à l’instance utilisateur
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        # Initialisation de la liste des lieux créés par l'utilisateur
        self.places = []
        # Initialisation de la liste des avis publiés par l'utilisateur
        self.reviews = []

    def add_place(self, place):
        """
        Associates a Place entity with this user (ownership).

        Args:
            place (Place): A valid Place instance owned by the user.

        Raises:
            TypeError: If the object is not of type Place.
        """
        # Importation locale pour éviter les importations circulaires
        from .place import Place
        # Vérifie que l'objet est bien une instance de Place
        if not isinstance(place, Place):
            raise TypeError("add_place() expected a Place instance.")
        # Ajoute le lieu à la liste des lieux de l’utilisateur
        self.places.append(place)

    def add_review(self, review):
        """
        Associates a Review entity with this user (authorship).

        Args:
            review (Review): A valid Review instance created by the user.

        Raises:
            TypeError: If the object is not of type Review.
        """
        # Importation locale pour éviter les dépendances croisées
        from .review import Review
        # Vérifie que l'objet est bien une instance de Review
        if not isinstance(review, Review):
            raise TypeError("add_review() expected a Review instance.")
        # Ajoute l’avis à la liste des reviews de l’utilisateur
        self.reviews.append(review)
