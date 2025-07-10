# Importation des modules nécessaires
from app.extensions import db, bcrypt
from sqlalchemy.orm import relationship
import uuid
from .base_model import BaseModel
import re


class User(BaseModel):
    """
    Entity representing a user registered on the HBnB platform.

    This model encapsulates identity, access control, and validation.
    It includes data validation for length, email format, and uniqueness constraints.

    Attributes:
        first_name (str): User's first name, max 50 characters.
        last_name (str): User's last name, max 50 characters.
        email (str): Unique and valid email address.
        is_admin (bool): Whether the user has administrative privileges.
    """

    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True,
                   default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    # Relations SQLAlchemy
    places = relationship('Place', backref='owner', lazy=True)
    reviews = relationship('Review', backref='user', lazy=True)

    def __init__(self, first_name: str, last_name: str, email: str, password: str, is_admin: bool = False):
        """
        Initialize a User entity with validation.

        Enforces length constraints on names, ensures the email format is valid using a regular expression.

        Args:
            first_name (str): Given name of the user.
            last_name (str): Surname of the user.
            email (str): Unique email address.
            password (str): Password for the user account.
            is_admin (bool, optional): Admin rights flag. Defaults to False.

        Raises:
            ValueError: For invalid name/email/password.
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

        # Vérifie que l'email respecte le format standard via une expression régulière
        if not re.fullmatch(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}', email):
            raise ValueError("Invalid email: must be a valid email address.")

        if not password or len(password) < 8:
            raise ValueError(
                "Invalid password: Your password must not be empty or less than 8 characters long.")

        # Affectation des attributs à l'instance utilisateur
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        self.hash_password(password)

    def hash_password(self, password):
        """
        Hash the user's password using bcrypt and stores it in the password attribute.

        Args:
            password (str): The plain text password to hash.
        """
        # Génère un hash pour le mot de passe et l'attribue à l'utilisateur
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """
        Verify a plain text password against the hashed password.

        Args:
            password (str): The plain text password to verify.

        Returns:
            bool: True if password matches, False otherwise.
        """
        # Vérifie que le mot de passe fourni correspond au hash stocké
        return bcrypt.check_password_hash(self.password, password)
