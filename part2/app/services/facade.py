from app.persistence.repository import InMemoryRepository
from app.models.user import User
from app.models.amenity import Amenity

class HBnBFacade:
    """
    Facade class providing a simplified interface for managing Users and Amenities.

    This class abstracts access to the underlying repositories and ensures
    business rules and error handling are applied consistently.
    """

    def __init__(self):
        """
        Initializes the repositories used by the facade.
        """
        self.user_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

    def create_user(self, user_data):
        """
        Creates and stores a new User instance.

        Args:
            user_data (dict): A dictionary containing keys such as
                'first_name', 'last_name', 'email', and 'is_admin'.

        Returns:
            User: The created User object.

        Raises:
            ValueError, TypeError: If the data provided is invalid.
        """
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        """
        Retrieves a User by their unique ID.

        Args:
            user_id (str): The UUID of the user.

        Returns:
            User: The user instance matching the ID.

        Raises:
            ValueError: If the user ID is not found.
        """
        try:
            return self.user_repo.get(user_id)
        except KeyError:
            raise ValueError("Error ID: The requested ID does not exist.")

    def get_user_by_email(self, email):
        """
        Retrieves a User by their email address.

        Args:
            email (str): The email address to search for.

        Returns:
            User: The user with the given email, or None if not found.
        """
        return self.user_repo.get_by_attribute('email', email)

    def update_user(self, user_id, data):
        """
        Updates the attributes of an existing user.

        Args:
            user_id (str): The UUID of the user to update.
            data (dict): Dictionary of updated fields and values.

        Returns:
            User: The updated user instance.

        Raises:
            ValueError: If the user ID is not found.
        """
        try:
            return self.user_repo.update(user_id, data)
        except KeyError:
            raise ValueError("Error ID: The requested ID does not exist.")

    def create_amenity(self, amenity_data):
        """
        Creates and stores a new Amenity instance.

        Args:
            amenity_data (dict): Dictionary containing the 'name' of the amenity.

        Returns:
            Amenity: The created Amenity object.

        Raises:
            ValueError, TypeError: If the name is invalid or missing.
        """
        amenity = Amenity(**amenity_data)
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id):
        """
        Retrieves an Amenity by its ID.

        Args:
            amenity_id (str): The UUID of the amenity.

        Returns:
            Amenity: The amenity instance matching the ID.

        Raises:
            ValueError: If the amenity ID is not found.
        """
        try:
            return self.amenity_repo.get(amenity_id)
        except KeyError:
            raise ValueError("Error ID: The requested ID does not exist.")

    def get_all_amenities(self):
        """
        Retrieves all available amenities.

        Returns:
            list[Amenity]: A list of all stored amenities.
        """
        try:
            return self.amenity_repo.get_all()
        except Exception:
            return []

    def update_amenity(self, amenity_id, amenity_data):
        """
        Updates the attributes of an existing amenity.

        Args:
            amenity_id (str): The UUID of the amenity to update.
            amenity_data (dict): Dictionary of updated fields and values.

        Returns:
            Amenity: The updated amenity instance.

        Raises:
            ValueError: If the amenity ID is not found.
        """
        try:
            return self.amenity_repo.update(amenity_id, amenity_data)
        except KeyError:
            raise ValueError("Error ID: The requested ID does not exist.")
