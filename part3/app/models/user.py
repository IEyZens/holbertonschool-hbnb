# Import necessary modules for user model functionality
from app.extensions import db, bcrypt
from sqlalchemy.orm import relationship
import uuid
from .base_model import BaseModel
import re


class User(BaseModel):
    """
    Entity representing a user registered on the HBnB platform.

    This model encapsulates user identity, authentication, and access control functionality.
    It includes comprehensive data validation for names, email format, password security,
    and enforces uniqueness constraints on email addresses.

    The User model serves as the central identity system for the platform, linking to
    places they own and reviews they've written. Password security is handled through
    bcrypt hashing with automatic salting.

    Attributes:
        id (str): Unique identifier for the user (UUID format)
        first_name (str): User's first name, maximum 50 characters
        last_name (str): User's last name, maximum 50 characters
        email (str): Unique and valid email address, automatically normalized to lowercase
        password (str): Bcrypt-hashed password for authentication
        is_admin (bool): Whether the user has administrative privileges (default: False)
        created_at (datetime): Account creation timestamp (inherited from BaseModel)
        updated_at (datetime): Last account modification timestamp (inherited from BaseModel)

    Database Table:
        users: Stores user account information with unique email constraint

    Relationships:
        owned_places: One-to-many relationship with Place model (places owned by this user)
        reviews: One-to-many relationship with Review model (reviews written by this user)

    Security Features:
        - Email addresses are automatically normalized (stripped and lowercased)
        - Passwords are hashed using bcrypt with automatic salt generation
        - Email format validation using regular expressions
        - Minimum password length enforcement (8 characters)
    """

    __tablename__ = 'users'

    # Primary key: UUID string identifier
    id = db.Column(db.String(36), primary_key=True,
                   default=lambda: str(uuid.uuid4()))

    # User's first name: required, maximum 50 characters
    first_name = db.Column(db.String(50), nullable=False)

    # User's last name: required, maximum 50 characters
    last_name = db.Column(db.String(50), nullable=False)

    # Email address: required, unique across all users, maximum 120 characters
    email = db.Column(db.String(120), nullable=False, unique=True)

    # Hashed password: required, stored as bcrypt hash (128 characters max)
    password = db.Column(db.String(128), nullable=False)

    # Admin status: boolean flag for administrative privileges
    is_admin = db.Column(db.Boolean, default=False)

    # SQLAlchemy relationship definitions
    # One-to-many: User can own multiple places
    owned_places = relationship('Place', back_populates='owner', lazy=True)

    # One-to-many: User can write multiple reviews
    reviews = relationship('Review', back_populates='user', lazy=True)

    def __init__(self, first_name: str, last_name: str, email: str, password: str, is_admin: bool = False):
        """
        Initialize a User entity with comprehensive validation.

        Enforces length constraints on names, validates email format using regular expressions,
        ensures password security requirements, and automatically hashes the password for storage.
        All inputs are validated before assignment to prevent invalid data entry.

        Args:
            first_name (str): Given name of the user (1-50 characters)
            last_name (str): Surname of the user (1-50 characters)
            email (str): Valid email address (will be normalized to lowercase)
            password (str): Plain text password (minimum 8 characters, will be hashed)
            is_admin (bool, optional): Admin rights flag. Defaults to False.

        Raises:
            ValueError: For invalid name length, email format, or password requirements
            TypeError: If is_admin is not a boolean type

        Example:
            user = User("John", "Doe", "john.doe@example.com", "securepass123")
            admin = User("Jane", "Smith", "jane@admin.com", "adminpass456", True)

        Security Notes:
            - Email is automatically normalized (stripped and lowercased)
            - Password is immediately hashed and the plain text is not stored
            - Email format validation prevents common injection patterns
        """
        # Call parent constructor to initialize common attributes (id, timestamps)
        super().__init__()

        # Validate first name: not empty and within length limit
        if not first_name or len(first_name) > 50:
            raise ValueError(
                "Invalid first name: The maximum number of characters is 50.")

        # Validate last name: not empty and within length limit
        if not last_name or len(last_name) > 50:
            raise ValueError(
                "Invalid last name: The maximum number of characters is 50.")

        # Validate admin flag is boolean type
        if not isinstance(is_admin, bool):
            raise TypeError(
                "Invalid is_admin flag: must be a boolean (True or False).")

        # Normalize and validate email format using regex pattern
        email = email.strip().lower()
        if not re.fullmatch(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}', email):
            raise ValueError("Invalid email: must be a valid email address.")

        # Validate password meets minimum security requirements
        if not password or len(password) < 8:
            raise ValueError(
                "Invalid password: Your password must not be empty or less than 8 characters long.")

        # Assign validated attributes to the user instance
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin

        # Hash the password immediately for security
        self.hash_password(password)

    def hash_password(self, password):
        """
        Hash the user's password using bcrypt and store it in the password attribute.

        Uses bcrypt's built-in salt generation for enhanced security. The original plain text
        password is not stored anywhere in the system. The resulting hash is stored as a
        UTF-8 decoded string for database compatibility.

        Args:
            password (str): The plain text password to hash

        Security Features:
            - Automatic salt generation (different for each password)
            - Adaptive hashing cost (adjustable work factor)
            - Resistant to rainbow table attacks
            - UTF-8 encoding for consistent storage

        Example:
            user.hash_password("myplaintextpassword")
            # user.password now contains bcrypt hash like "$2b$12$..."
        """
        # Generate bcrypt hash with automatic salt and store as UTF-8 string
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """
        Verify a plain text password against the stored hashed password.

        Uses bcrypt's secure comparison function to check if the provided password
        matches the stored hash. This method is constant-time to prevent timing attacks.

        Args:
            password (str): The plain text password to verify

        Returns:
            bool: True if password matches the stored hash, False otherwise

        Security Features:
            - Constant-time comparison prevents timing attacks
            - Handles salt extraction automatically
            - Safe against hash collision attempts

        Example:
            if user.verify_password("userpassword"):
                # Password is correct, proceed with authentication
                pass
            else:
                # Password is incorrect, deny access
                pass
        """
        # Use bcrypt's secure verification function to compare password with stored hash
        return bcrypt.check_password_hash(self.password, password)
