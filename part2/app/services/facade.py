from app.persistence.repository import InMemoryRepository
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review


class HBnBFacade:
    """
    Application service layer acting as a unified facade for domain operations.

    This class coordinates business logic, enforces validation rules,
    handles repository delegation, and centralizes access to core actions
    such as user management, listing creation, amenities, and reviews.

    Responsibilities:
        - Orchestrates creation, update, and retrieval of all domain entities
        - Applies validation and relationship integrity (e.g., Place.owner must exist)
        - Abstracts access to the persistence layer (InMemoryRepository)
    """

    def __init__(self):
        """
        Initializes the internal repositories for each entity type.
        """
        self.user_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()

    def create_user(self, user_data):
        """
        Create and store a new User entity.

        Args:
            user_data (dict): Includes 'first_name', 'last_name', 'email', 'is_admin'.

        Returns:
            User: The created user object.
        """
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        """
        Retrieve a user by unique ID.

        Args:
            user_id (str): UUID of the user.

        Returns:
            User: Corresponding user object.

        Raises:
            ValueError: If user not found.
        """
        try:
            return self.user_repo.get(user_id)
        except KeyError:
            raise ValueError("Error ID: The requested ID does not exist.")

    def get_user_by_email(self, email):
        """
        Retrieve a user by their email address.

        Args:
            email (str): Unique email.

        Returns:
            User or None: The matching user or None if not found.
        """
        return self.user_repo.get_by_attribute('email', email)

    def update_user(self, user_id, data):
        """
        Update user attributes.

        Args:
            user_id (str): ID of the user to update.
            data (dict): Fields to modify.

        Returns:
            User: The updated object.
        """
        try:
            return self.user_repo.update(user_id, data)
        except KeyError:
            raise ValueError("Error ID: The requested ID does not exist.")

    def create_amenity(self, amenity_data):
        """
        Create and store a new amenity.

        Args:
            amenity_data (dict): Must contain 'name'.

        Returns:
            Amenity: The persisted amenity.
        """
        amenity = Amenity(**amenity_data)
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id):
        """
        Retrieve an amenity by ID.

        Args:
            amenity_id (str): UUID.

        Returns:
            Amenity: The matching amenity object.
        """
        try:
            return self.amenity_repo.get(amenity_id)
        except KeyError:
            raise ValueError("Error ID: The requested ID does not exist.")

    def get_all_amenities(self):
        """
        Get all stored amenities.

        Returns:
            list[Amenity]: All amenities.
        """
        try:
            return self.amenity_repo.get_all()
        except Exception:
            return []

    def update_amenity(self, amenity_id, amenity_data):
        """
        Update an existing amenity.

        Args:
            amenity_id (str): ID to update.
            amenity_data (dict): Updated fields.

        Returns:
            Amenity: Updated amenity object.
        """
        try:
            return self.amenity_repo.update(amenity_id, amenity_data)
        except KeyError:
            raise ValueError("Error ID: The requested ID does not exist.")

    def create_place(self, place_data):
        """
        Create a new Place with data validation and relation enforcement.

        Ensures owner exists and coordinates/price are valid.

        Args:
            place_data (dict): Must include title, price, coordinates, etc.

        Returns:
            Place: The persisted place object.

        Raises:
            ValueError: For missing fields or invalid constraints.
        """
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
        Retrieve a place by ID.

        Args:
            place_id (str): Place UUID.

        Returns:
            Place: The matching object.
        """
        try:
            return self.place_repo.get(place_id)
        except KeyError:
            raise ValueError("Error ID: The requested ID does not exist.")

    def get_all_places(self):
        """
        Return all places in repository.

        Returns:
            list: List of Place instances.
        """
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        """
        Update an existing Place.

        Validates numeric/geo fields and applies attribute changes.

        Args:
            place_id (str): ID of the place.
            place_data (dict): Partial or full update fields.

        Returns:
            Place: Updated place object.
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
        """
        Create a new Review and bind it to a user and place.

        Args:
            review_data (dict): Must include text, rating, user_id, place_id.

        Returns:
            Review: Created review object.
        """
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
        """
        Retrieve a single Review by ID.

        Returns:
            Review: The review object.
        """
        try:
            return self.review_repo.get(review_id)
        except KeyError:
            raise ValueError("Error ID: The requested ID does not exist.")

    def get_all_reviews(self):
        """
        Get all reviews stored in the repository.

        Returns:
            list[Review]: All reviews.
        """
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        """
        Retrieve all reviews for a given place.

        Args:
            place_id (str): Place ID.

        Returns:
            list[Review]: Reviews associated with that place.
        """
        reviews = self.review_repo.get_by_attribute('place', place_id)
        return reviews if reviews else []

    def update_review(self, review_id, review_data):
        """
        Update a review by ID.

        Args:
            review_id (str): Review identifier.
            review_data (dict): New data.

        Returns:
            Review: Updated object.
        """
        try:
            return self.review_repo.update(review_id, review_data)
        except KeyError:
            raise ValueError("Error ID: The requested ID does not exist.")

    def delete_review(self, review_id):
        """
        Delete a review entity from storage.

        Args:
            review_id (str): Review ID.

        Returns:
            bool: True if deletion succeeded, else False.
        """
        deleted = self.review_repo.delete(review_id)
        if not deleted:
            raise ValueError("Review not found")
        return True
