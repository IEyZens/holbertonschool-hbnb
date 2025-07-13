from app.persistence.repository import SQLAlchemyRepository
from app.persistence.user_repository import UserRepository
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review
import re


class HBnBFacade:
    """
    Application service layer acting as a unified facade for domain operations.

    This class coordinates business logic, enforces validation rules,
    handles repository delegation, and centralizes access to core actions
    such as user management, listing creation, amenities, and reviews.

    Responsibilities:
        - Orchestrates creation, update, and retrieval of all domain entities
        - Applies validation and relationship integrity (e.g., Place.owner must exist)
        - Abstracts access to the persistence layer (SQLAlchemyRepository)
    """

    def __init__(self):
        """
        Initializes the internal repositories for each entity type.
        """
        self.user_repo = UserRepository()
        self.place_repo = SQLAlchemyRepository(Place)
        self.review_repo = SQLAlchemyRepository(Review)
        self.amenity_repo = SQLAlchemyRepository(Amenity)

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
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("Error ID: The requested ID does not exist.")
        return user

    def get_user_by_email(self, email):
        """
        Retrieve a user by their email address.

        Args:
            email (str): Unique email.

        Returns:
            User or None: The matching user or None if not found.
        """
        return self.user_repo.get_user_by_email(email)

    def get_user_by_id(self, user_id):
        return self.user_repo.get_user_by_id(user_id)

    def get_all_users(self):
        """
        Get all stored users.

        Returns:
            list[User]: All users.
        """
        try:
            return self.user_repo.get_all()
        except Exception:
            return []

    def update_user(self, user_id, data):
        """
        Update user attributes.

        Args:
            user_id (str): ID of the user to update.
            data (dict): Fields to modify.

        Returns:
            User: The updated object.
        """
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("Error ID: The requested ID does not exist.")

        if 'email' in data:
            email = data['email']
            if not re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}", email):
                raise ValueError(
                    "Invalid email: must be a valid email address.")

        if 'password' in data:
            user.hash_password(data.pop('password'))

        return self.user_repo.update(user_id, data)

    def delete_user(self, user_id):
        """
        Delete a user entity from storage.

        Args:
            user_id (str): User ID.

        Returns:
            bool: True if deletion succeeded, else False.
        """
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("User not found")
        self.user_repo.delete(user_id)
        return True

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
        amenity = self.amenity_repo.get(amenity_id)
        if not amenity:
            raise ValueError("Error ID: The requested ID does not exist.")
        return amenity

    def get_amenity_by_name(self, name):
        return self.amenity_repo.get_by_attribute('name', name.strip().title())

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
        amenity = self.amenity_repo.get(amenity_id)
        if not amenity:
            raise ValueError("Error ID: The requested ID does not exist.")

        if 'name' in amenity_data:
            name = amenity_data['name']
            if not name or len(name) > 50:
                raise ValueError("Name must be between 1 and 50 characters.")

        return self.amenity_repo.update(amenity_id, amenity_data)

    def delete_amenity(self, amenity_id):
        """
        Delete an amenity entity from storage.

        Args:
            amenity_id (str): Amenity ID.

        Returns:
            bool: True if deletion succeeded, else False.
        """
        amenity = self.amenity_repo.get(amenity_id)
        if not amenity:
            raise ValueError("Amenity not found")
        self.amenity_repo.delete(amenity_id)
        return True

    def create_place(self, place_data, current_user):
        """
        Create a new Place with data validation and relation enforcement.

        Ensures owner exists and coordinates/price are valid.

        Args:
            place_data (dict): Must include title, price, coordinates, etc.
            current_user (str): ID of the current authenticated user.

        Returns:
            Place: The persisted place object.

        Raises:
            ValueError: For missing fields or invalid constraints.
        """
        required_fields = ['title', 'price',
                           'latitude', 'longitude', 'max_person']

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

        # Set owner_id to current authenticated user
        owner = self.user_repo.get(current_user)
        if not owner:
            raise ValueError("Owner not found.")

        place = Place(
            title=place_data['title'],
            description=place_data['description'],
            price=place_data['price'],
            latitude=place_data['latitude'],
            longitude=place_data['longitude'],
            owner=owner,  # Ajouter le paramètre owner requis
            max_person=place_data['max_person']
        )

        place.amenities = []
        if 'amenities' in place_data:
            amenities = []
            for amenity in place_data["amenities"]:
                # Handle both string IDs and object format
                if isinstance(amenity, dict):
                    amenity_id = amenity["id"]
                else:
                    amenity_id = amenity

                try:
                    new_amenity = self.amenity_repo.get(amenity_id)
                    if new_amenity:
                        amenities.append(new_amenity)
                except:
                    # Skip invalid amenity IDs
                    continue
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
        place = self.place_repo.get(place_id)
        if not place:
            raise ValueError("Error ID: The requested ID does not exist.")
        return place

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

    def delete_place(self, place_id):
        """
        Delete a place entity from storage.

        Args:
            place_id (str): Place ID.

        Returns:
            bool: True if deletion succeeded, else False.
        """
        place = self.place_repo.get(place_id)
        if not place:
            raise ValueError("Place not found")
        self.place_repo.delete(place_id)
        return True

    def create_review(self, review_data, current_user):
        """
        Create a new Review and bind it to a user and place.

        Args:
            review_data (dict): Must include text, rating, user_id, place_id.
            current_user (str): ID of the current authenticated user.

        Returns:
            Review: Created review object.

        Raises:
            ValueError: If user tries to review own place or already reviewed the place.
        """
        user_id = current_user
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("User does not exist.")

        place = self.place_repo.get(review_data['place_id'])
        if not place:
            raise ValueError("Place does not exist.")

        # Check if user is trying to review their own place
        if place.owner.id == user_id:
            raise ValueError("You cannot review your own place")

        # Check if user has already reviewed this place
        existing_reviews = self.review_repo.get_by_attribute(
            'place_id', review_data['place_id'])
        for existing_review in existing_reviews:
            if existing_review.user.id == user_id:
                raise ValueError("You have already reviewed this place")

        review = Review(
            text=review_data['text'],
            rating=review_data['rating'],
            user=user,
            place=place
        )

        self.review_repo.add(review)
        place.add_review(review)

        return review

    def get_review(self, review_id):
        """
        Retrieve a single Review by ID.

        Returns:
            Review: The review object.
        """
        review = self.review_repo.get(review_id)
        if not review:
            raise ValueError("Error ID: The requested ID does not exist.")
        return review

    def get_all_reviews(self):
        """
        Get all reviews stored in the repository.

        Returns:
            list[Review]: All reviews.
        """
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        """
        Retrieve all reviews associated with a specific place.

        This method searches the entire review repository and filters out only
        those reviews that are linked to the given place ID. This approach ensures
        consistency even if the in-memory relationship between Place and its reviews
        is not directly maintained (e.g., after deserialization or repo refresh).

        Args:
            place_id (str): Unique identifier of the place whose reviews are requested.

        Returns:
            list[Review]: A list of Review instances that are linked to the specified place.

        Raises:
            KeyError: If no place is found with the given ID.
        """
        place = self.place_repo.get(place_id)
        if not place:
            raise ValueError("Place not found")
        return place.reviews

    def update_review(self, review_id, review_data):
        """
        Update a review by ID.

        Args:
            review_id (str): Review identifier.
            review_data (dict): New data.

        Returns:
            Review: Updated object.
        """
        review = self.review_repo.get(review_id)
        if not review:
            raise ValueError("Error ID: The requested ID does not exist.")

        if 'rating' in review_data and not (1 <= review_data['rating'] <= 5):
            raise ValueError("Rating must be between 1 and 5.")

        return self.review_repo.update(review_id, review_data)

    def delete_review(self, review_id):
        """
        Delete a review entity from storage.

        Args:
            review_id (str): Review ID.

        Returns:
            bool: True if deletion succeeded, else False.
        """
        review = self.review_repo.get(review_id)
        if not review:
            raise ValueError("Review not found")
        self.review_repo.delete(review_id)
        return True
