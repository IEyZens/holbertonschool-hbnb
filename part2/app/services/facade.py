from app.persistence.repository import InMemoryRepository
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review


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
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()

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

    def create_place(self, place_data):

        required_fields = ['title', 'description', 'price', 'latitude', 'longitude', 'owner_id', 'max_person']

        for field in required_fields:
            if field not in place_data:
                raise ValueError(f"Missing required field: {field}")

        if place_data['price'] < 0:
            raise ValueError("Price must be a non-negative number.")
        if place_data['max_person'] < 1:
            raise ValueError("Max person must be greater than 0.")
        if not (-90 <= place_data['latitude'] <= 90):
            raise ValueError("Latitude must be between -90 and 90 degrees.")
        if not (-180 <= place_data['longitude'] <= 180):
            raise ValueError("Longitude must be between -180 and 180 degrees.")

        owner = self.user_repo.get(place_data['owner_id'])
        if not owner:
            raise ValueError("Owner not found.")

        place = Place(
            title=place_data['title'],
            description=place_data['description'],
            price=place_data['price'],
            latitude=place_data['latitude'],
            longitude=place_data['longitude'],
            owner=owner,
            max_person=place_data['max_person']
        )
        place.amenities = []

        if 'amenities' in place_data:
            amenities = []
            for amenity in place_data["amenities"]:
                amenity_id = amenity["id"]
                new_amenity = self.amenity_repo.get(amenity_id)
                if new_amenity:
                    amenities.append(new_amenity)
            place.amenities = amenities

        self.place_repo.add(place)
        return place

    def get_place(self, place_id):
        """
        Retrieve a Place by its unique identifier.

        Args:
            place_id (str): The unique identifier of the place.

        Returns:
            Place: The corresponding Place object.

        Raises:
            ValueError: If no place with the given ID exists.
        """
        try:
            return self.place_repo.get(place_id)
        except KeyError:
            raise ValueError("Error ID: The requested ID does not exist.")

    def get_all_places(self):
        """
        Retrieve all Place instances.

        Returns:
            list: A list of all Place objects from the repository.
        """
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        """
        Update an existing Place instance with new data.

        Args:
            place_id (str): The unique identifier of the Place to update.
            place_data (dict): A dictionary containing the updated attributes.

        Returns:
            Place: The updated Place object.

        Raises:
            ValueError: If the place_id does not correspond to an existing Place.
        """
        place = self.place_repo.get(place_id)
        if not place:
            raise ValueError("Error ID: The requested ID does not exist.")

        if 'price' in place_data and place_data['price'] < 0:
            raise ValueError("Price must be a non-negative number.")
        if 'max_person' in place_data and place_data['max_person'] < 1:
            raise ValueError("Max person must be greater than 0.")
        if 'latitude' in place_data and not (-90 <= place_data['latitude'] <= 90):
            raise ValueError("Latitude must be between -90 and 90 degrees.")
        if 'longitude' in place_data and not (-180 <= place_data['longitude'] <= 180):
            raise ValueError("Longitude must be between -180 and 180 degrees.")

        for key in ['title', 'description', 'price', 'latitude', 'longitude', 'max_person']:
            if key in place_data:
                setattr(place, key, place_data[key])

        if 'amenities' in place_data:
            amenities = []
            for amenity in place_data['amenities']:
                amenity_id = amenity['id']
                new_amenity = self.amenity_repo.get(amenity_id)
                if new_amenity:
                    amenities.append(new_amenity)
            place.amenities = amenities

        self.place_repo.update(place_id, place)

        return place

    def create_review(self, review_data):

        user = self.user_repo.get(review_data['user_id'])
        if not user:
            raise ValueError("User does not exist.")

        place = self.place_repo.get(review_data['place_id'])
        if not place:
            raise ValueError("Place does not exist.")

        review = Review(
            text=review_data['text'],
            rating=review_data['rating'],
            user=user,
            place=place
        )

        self.review_repo.add(review)
        return review

    def get_review(self, review_id):
        try:
            return self.review_repo.get(review_id)
        except KeyError:
            raise ValueError("Error ID: The requested ID does not exist.")

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        reviews = self.review_repo.get_by_attribute('place', place_id)
        return reviews if reviews else []

    def update_review(self, review_id, review_data):
        try:
            return self.review_repo.update(review_id, review_data)
        except KeyError:
            raise ValueError("Error ID: The requested ID does not exist.")

    def delete_review(self, review_id):
        deleted = self.review_repo.delete(review_id)
        if not deleted:
            raise ValueError("Review not found")
        return True
