# Import necessary modules for facade service layer functionality
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

    This class serves as the central orchestrator for all business logic in the HBnB application,
    implementing the Facade pattern to provide a simplified interface to complex subsystems.
    It coordinates operations between different domain entities (Users, Places, Amenities, Reviews)
    while enforcing business rules, validation constraints, and data integrity.

    The facade acts as the primary entry point for all business operations, abstracting the
    complexity of multiple repositories and domain models from the presentation layer (API endpoints).
    This design ensures separation of concerns and makes the system more maintainable and testable.

    Key Responsibilities:
    - Orchestrates creation, retrieval, update, and deletion of all domain entities
    - Enforces business rules and validation constraints across entity relationships
    - Manages cross-entity operations (e.g., ensuring place owners exist, preventing self-reviews)
    - Provides transaction coordination and data consistency guarantees
    - Abstracts repository layer complexity from API controllers
    - Centralizes business logic for easier maintenance and testing

    Architecture Benefits:
    - Single point of access for all business operations
    - Consistent error handling and validation patterns
    - Simplified API layer with reduced coupling to domain models
    - Easy to mock for unit testing
    - Clear separation between business logic and data access

    Domain Entity Management:
    - Users: Registration, authentication, profile management, admin operations
    - Places: Property listings, ownership validation, geographic constraints
    - Amenities: Feature management, place associations
    - Reviews: User feedback, rating validation, ownership constraints

    Business Rule Enforcement:
    - Email uniqueness and format validation
    - Geographic coordinate constraints for places
    - Review ownership rules (no self-reviews, one review per user per place)
    - Price and capacity validation for places
    - Referential integrity between entities
    """

    def __init__(self):
        """
        Initialize the facade with repository instances for each domain entity.

        Sets up the data access layer by creating specialized repository instances
        for each domain model. This establishes the connection between the business
        logic layer and the persistence layer, enabling data operations while
        maintaining clean separation of concerns.

        Repository Configuration:
        - UserRepository: Specialized repository with email-based lookup capabilities
        - SQLAlchemyRepository instances: Generic repositories for other domain entities
        - All repositories configured with appropriate SQLAlchemy models
        - Transaction management handled at repository level
        """
        # Initialize specialized user repository with email lookup capabilities
        self.user_repo = UserRepository()

        # Initialize generic SQLAlchemy repositories for other domain entities
        self.place_repo = SQLAlchemyRepository(Place)
        self.review_repo = SQLAlchemyRepository(Review)
        self.amenity_repo = SQLAlchemyRepository(Amenity)

    # ==================== USER MANAGEMENT OPERATIONS ====================

    def create_user(self, user_data):
        """
        Create and store a new User entity with validation.

        Processes user registration data and creates a new user account in the system.
        Validation is handled by the User model constructor, ensuring data integrity
        before persistence. This method serves as the entry point for user registration.

        Args:
            user_data (dict): User information including:
                - first_name (str): User's first name
                - last_name (str): User's last name
                - email (str): Unique email address
                - password (str): Plain text password (will be hashed)
                - is_admin (bool, optional): Admin privileges flag

        Returns:
            User: The created and persisted user instance with generated ID and timestamps

        Raises:
            ValueError: If user data fails model validation (invalid email, short password, etc.)
            Exception: Database-specific exceptions for constraint violations or connection issues

        Example:
            user_data = {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "password": "securepassword123",
                "is_admin": False
            }
            new_user = facade.create_user(user_data)
        """
        # Create User instance with validation (constructor handles password hashing)
        user = User(**user_data)

        # Persist user to database through repository
        self.user_repo.add(user)

        return user

    def get_user(self, user_id):
        """
        Retrieve a user by their unique identifier.

        Fetches a user record using their UUID primary key. This method is commonly
        used for authorization checks and user profile operations where the user ID
        is already known (e.g., from JWT tokens).

        Args:
            user_id (str): UUID of the user to retrieve

        Returns:
            User: The user instance with all attributes and relationships

        Raises:
            ValueError: If no user exists with the specified ID

        Example:
            user = facade.get_user("12345-67890-abcdef")
            print(f"User: {user.first_name} {user.last_name}")
        """
        # Retrieve user from repository by primary key
        user = self.user_repo.get(user_id)

        # Validate user exists and raise descriptive error if not found
        if not user:
            raise ValueError("Error ID: The requested ID does not exist.")

        return user

    def get_user_by_email(self, email):
        """
        Retrieve a user by their email address.

        Performs email-based user lookup, primarily used for authentication flows
        where users log in with their email address. Returns None if no matching
        user is found, allowing calling code to handle authentication failures.

        Args:
            email (str): Email address to search for (should be normalized)

        Returns:
            User or None: The matching user instance, or None if not found

        Example:
            user = facade.get_user_by_email("john.doe@example.com")
            if user and user.verify_password(password):
                # Authentication successful
                pass
        """
        # Delegate to specialized user repository method for email lookup
        return self.user_repo.get_user_by_email(email)

    def get_user_by_id(self, user_id):
        """
        Alternative method for retrieving users by ID.

        Provides the same functionality as get_user() but with a more explicit method name.
        This method exists for API consistency and may have different error handling
        in future implementations.

        Args:
            user_id (str): UUID of the user to retrieve

        Returns:
            User or None: User instance if found, None otherwise
        """
        # Delegate to user repository's ID-based lookup method
        return self.user_repo.get_user_by_id(user_id)

    def get_all_users(self):
        """
        Retrieve all users in the system.

        Fetches all user records from the database. This method includes error handling
        to return an empty list if database access fails, ensuring API stability.
        Use with caution in production environments with large user bases.

        Returns:
            list[User]: All user instances, or empty list if none exist or on error

        Performance Warning:
            This method loads all users into memory. Consider pagination for large datasets.

        Example:
            all_users = facade.get_all_users()
            print(f"Total users: {len(all_users)}")
        """
        try:
            # Attempt to retrieve all users from repository
            return self.user_repo.get_all()
        except Exception:
            # Return empty list on any database error to maintain API stability
            return []

    def update_user(self, user_id, data):
        """
        Update user attributes with validation and security handling.

        Modifies an existing user's information while enforcing business rules and
        security constraints. Special handling is provided for email validation and
        password updates to ensure data integrity and security.

        Args:
            user_id (str): UUID of the user to update
            data (dict): Dictionary of attributes to update, may include:
                - first_name, last_name: Name updates
                - email: Email address (validated for format)
                - password: New password (will be hashed before storage)
                - is_admin: Admin status changes

        Returns:
            User: The updated user instance

        Raises:
            ValueError: If user not found, email format invalid, or other validation errors

        Security Notes:
            - Passwords are automatically hashed before storage
            - Email format validation prevents malformed addresses
            - Original password data is removed from the data dict for security

        Example:
            update_data = {"email": "newemail@example.com", "password": "newpassword123"}
            updated_user = facade.update_user("12345", update_data)
        """
        # Verify user exists before attempting update
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("Error ID: The requested ID does not exist.")

        # Validate email format if email is being updated
        if 'email' in data:
            email = data['email']
            # Use regex pattern matching for email validation
            if not re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}", email):
                raise ValueError(
                    "Invalid email: must be a valid email address.")

        # Handle password updates with proper hashing
        if 'password' in data:
            # Hash new password using user's hash_password method
            user.hash_password(data.pop('password'))

        # Apply updates through repository layer
        return self.user_repo.update(user_id, data)

    def delete_user(self, user_id):
        """
        Delete a user entity from the system.

        Removes a user account from the database after verifying the user exists.
        This operation may cascade to related entities depending on database
        configuration and foreign key constraints.

        Args:
            user_id (str): UUID of the user to delete

        Returns:
            bool: True if deletion succeeded

        Raises:
            ValueError: If user not found

        Cascade Considerations:
            Depending on database configuration, deleting a user may affect:
            - Places owned by the user
            - Reviews written by the user
            - Related authentication tokens

        Example:
            success = facade.delete_user("12345-67890-abcdef")
        """
        # Verify user exists before attempting deletion
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("User not found")

        # Perform deletion through repository
        self.user_repo.delete(user_id)

        return True

    # ==================== AMENITY MANAGEMENT OPERATIONS ====================

    def create_amenity(self, amenity_data):
        """
        Create and store a new amenity with validation.

        Creates a new amenity that can be associated with places. Validation is
        handled by the Amenity model constructor to ensure data integrity.

        Args:
            amenity_data (dict): Amenity information containing:
                - name (str): Name of the amenity (e.g., "WiFi", "Pool")

        Returns:
            Amenity: The created and persisted amenity instance

        Raises:
            ValueError: If amenity data fails model validation
            Exception: Database-specific exceptions

        Example:
            amenity_data = {"name": "Swimming Pool"}
            new_amenity = facade.create_amenity(amenity_data)
        """
        # Create Amenity instance with validation (constructor handles name formatting)
        amenity = Amenity(**amenity_data)

        # Persist amenity to database through repository
        self.amenity_repo.add(amenity)

        return amenity

    def get_amenity(self, amenity_id):
        """
        Retrieve an amenity by its unique identifier.

        Fetches an amenity record using its UUID primary key for use in place
        associations and amenity management operations.

        Args:
            amenity_id (str): UUID of the amenity to retrieve

        Returns:
            Amenity: The amenity instance

        Raises:
            ValueError: If no amenity exists with the specified ID

        Example:
            amenity = facade.get_amenity("12345-67890-abcdef")
            print(f"Amenity: {amenity.name}")
        """
        # Retrieve amenity from repository by primary key
        amenity = self.amenity_repo.get(amenity_id)

        # Validate amenity exists and raise descriptive error if not found
        if not amenity:
            raise ValueError("Error ID: The requested ID does not exist.")

        return amenity

    def get_amenity_by_name(self, name):
        """
        Retrieve an amenity by its name.

        Performs name-based amenity lookup with automatic name formatting to match
        the title case format used in the database. This method is useful for
        finding existing amenities during place creation.

        Args:
            name (str): Name of the amenity to find

        Returns:
            list: Amenities matching the name (may be empty)

        Example:
            amenities = facade.get_amenity_by_name("wifi")  # Finds "Wifi"
        """
        # Use repository's attribute-based query with formatted name
        return self.amenity_repo.get_by_attribute('name', name.strip().title())

    def get_all_amenities(self):
        """
        Retrieve all amenities in the system.

        Fetches all amenity records from the database with error handling to ensure
        API stability. Used for displaying available amenities in place creation forms.

        Returns:
            list[Amenity]: All amenity instances, or empty list on error

        Example:
            all_amenities = facade.get_all_amenities()
            for amenity in all_amenities:
                print(f"Available: {amenity.name}")
        """
        try:
            # Attempt to retrieve all amenities from repository
            return self.amenity_repo.get_all()
        except Exception:
            # Return empty list on any database error
            return []

    def update_amenity(self, amenity_id, amenity_data):
        """
        Update an existing amenity with validation.

        Modifies amenity information while enforcing business rules such as
        name length constraints and proper formatting.

        Args:
            amenity_id (str): UUID of the amenity to update
            amenity_data (dict): Updated amenity data containing:
                - name (str): New name for the amenity

        Returns:
            Amenity: The updated amenity instance

        Raises:
            ValueError: If amenity not found or validation fails

        Example:
            update_data = {"name": "High-Speed WiFi"}
            updated_amenity = facade.update_amenity("12345", update_data)
        """
        # Verify amenity exists before attempting update
        amenity = self.amenity_repo.get(amenity_id)
        if not amenity:
            raise ValueError("Error ID: The requested ID does not exist.")

        # Validate name if being updated
        if 'name' in amenity_data:
            name = amenity_data['name']
            if not name or len(name) > 50:
                raise ValueError("Name must be between 1 and 50 characters.")

        # Apply updates through repository layer
        return self.amenity_repo.update(amenity_id, amenity_data)

    def delete_amenity(self, amenity_id):
        """
        Delete an amenity entity from the system.

        Removes an amenity from the database after verification. May affect
        place-amenity associations depending on database constraints.

        Args:
            amenity_id (str): UUID of the amenity to delete

        Returns:
            bool: True if deletion succeeded

        Raises:
            ValueError: If amenity not found

        Example:
            success = facade.delete_amenity("12345-67890-abcdef")
        """
        # Verify amenity exists before attempting deletion
        amenity = self.amenity_repo.get(amenity_id)
        if not amenity:
            raise ValueError("Amenity not found")

        # Perform deletion through repository
        self.amenity_repo.delete(amenity_id)

        return True

    # ==================== PLACE MANAGEMENT OPERATIONS ====================

    def create_place(self, place_data, current_user):
        """
        Create a new Place with comprehensive validation and relationship enforcement.

        Creates a property listing with full validation of geographic coordinates,
        pricing constraints, and ownership relationships. Handles amenity associations
        and ensures data integrity across all related entities.

        Args:
            place_data (dict): Place information including:
                - title (str): Display name for the place
                - description (str): Detailed description
                - price (float): Nightly rental price (must be >= 0)
                - latitude (float): Geographic latitude (-90 to 90)
                - longitude (float): Geographic longitude (-180 to 180)
                - max_person (int): Maximum occupancy (must be > 0)
                - amenities (list, optional): List of amenity IDs or objects
            current_user (str): UUID of the authenticated user (becomes owner)

        Returns:
            Place: The created and persisted place instance

        Raises:
            ValueError: For missing required fields, invalid constraints, or owner validation

        Business Rules Enforced:
            - All required fields must be present
            - Price must be non-negative (free places allowed)
            - Coordinates must be within valid geographic ranges
            - Maximum occupancy must be positive
            - Owner must be a valid existing user
            - Invalid amenity IDs are silently skipped

        Example:
            place_data = {
                "title": "Cozy Downtown Apartment",
                "description": "Beautiful 2BR in city center",
                "price": 120.50,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "max_person": 4,
                "amenities": ["amenity-id-1", "amenity-id-2"]
            }
            new_place = facade.create_place(place_data, user_id)
        """
        # Define and validate required fields
        required_fields = ['title', 'price',
                           'latitude', 'longitude', 'max_person']

        # Check for missing required fields
        for field in required_fields:
            if field not in place_data:
                raise ValueError(f"Missing required field: {field}")

        # Validate pricing constraints (non-negative, allows free places)
        if place_data['price'] < 0:
            raise ValueError("Price must be a non-negative number.")

        # Validate occupancy constraints (must be positive)
        if place_data['max_person'] < 1:
            raise ValueError("Max person must be greater than 0.")

        # Validate geographic coordinate constraints
        if not (-90 <= place_data['latitude'] <= 90):
            raise ValueError("Latitude must be between -90 and 90 degrees.")
        if not (-180 <= place_data['longitude'] <= 180):
            raise ValueError("Longitude must be between -180 and 180 degrees.")

        # Validate owner exists and set ownership relationship
        owner = self.user_repo.get(current_user)
        if not owner:
            raise ValueError("Owner not found.")

        # Create Place instance with validated data and owner relationship
        place = Place(
            title=place_data['title'],
            description=place_data['description'],
            price=place_data['price'],
            latitude=place_data['latitude'],
            longitude=place_data['longitude'],
            owner=owner,  # Required owner parameter for relationship
            max_person=place_data['max_person']
        )

        # Initialize amenities list and process amenity associations
        place.amenities = []
        if 'amenities' in place_data:
            amenities = []
            for amenity in place_data["amenities"]:
                # Handle both string IDs and object format for flexibility
                if isinstance(amenity, dict):
                    amenity_id = amenity["id"]
                else:
                    amenity_id = amenity

                try:
                    # Retrieve amenity instance and add to collection
                    new_amenity = self.amenity_repo.get(amenity_id)
                    if new_amenity:
                        amenities.append(new_amenity)
                except:
                    # Skip invalid amenity IDs silently to allow partial success
                    continue
            place.amenities = amenities

        # Persist place to database through repository
        self.place_repo.add(place)

        return place

    def get_place(self, place_id):
        """
        Retrieve a place by its unique identifier.

        Fetches a place record with all related data including owner information,
        amenities, and reviews for display in detail views.

        Args:
            place_id (str): UUID of the place to retrieve

        Returns:
            Place: The place instance with all relationships loaded

        Raises:
            ValueError: If no place exists with the specified ID

        Example:
            place = facade.get_place("12345-67890-abcdef")
            print(f"Place: {place.title} by {place.owner.first_name}")
        """
        # Retrieve place from repository by primary key
        place = self.place_repo.get(place_id)

        # Validate place exists and raise descriptive error if not found
        if not place:
            raise ValueError("Error ID: The requested ID does not exist.")

        return place

    def get_all_places(self):
        """
        Return all places in the repository.

        Fetches all place listings for display in search results and listing pages.
        This method loads all places into memory, so consider pagination for large datasets.

        Returns:
            list[Place]: All place instances with relationships

        Performance Note:
            Consider implementing pagination in the API layer for large datasets.

        Example:
            all_places = facade.get_all_places()
            for place in all_places:
                print(f"{place.title}: ${place.price}/night")
        """
        # Return all places from repository
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        """
        Update an existing Place with validation and relationship management.

        Modifies place information while enforcing the same business rules as creation.
        Supports partial updates and handles amenity relationship changes.

        Args:
            place_id (str): UUID of the place to update
            place_data (dict): Partial or complete update data with same constraints as create

        Returns:
            Place: The updated place instance

        Raises:
            ValueError: If place not found or validation fails

        Business Rules:
            - Same validation rules as place creation
            - Amenity relationships can be completely replaced
            - Partial updates supported for all attributes

        Example:
            update_data = {
                "price": 150.00,
                "amenities": [{"id": "new-amenity-id"}]
            }
            updated_place = facade.update_place("12345", update_data)
        """
        # Verify place exists before attempting update
        place = self.place_repo.get(place_id)
        if not place:
            raise ValueError("Error ID: The requested ID does not exist.")

        # Validate updated fields using same rules as creation
        if 'price' in place_data and place_data['price'] < 0:
            raise ValueError("Price must be a non-negative number.")
        if 'max_person' in place_data and place_data['max_person'] < 1:
            raise ValueError("Max person must be greater than 0.")
        if 'latitude' in place_data and not (-90 <= place_data['latitude'] <= 90):
            raise ValueError("Latitude must be between -90 and 90 degrees.")
        if 'longitude' in place_data and not (-180 <= place_data['longitude'] <= 180):
            raise ValueError("Longitude must be between -180 and 180 degrees.")

        # Apply scalar attribute updates
        for key in ['title', 'description', 'price', 'latitude', 'longitude', 'max_person']:
            if key in place_data:
                setattr(place, key, place_data[key])

        # Handle amenity relationship updates
        if 'amenities' in place_data:
            amenities = []
            for amenity in place_data['amenities']:
                amenity_id = amenity['id']
                new_amenity = self.amenity_repo.get(amenity_id)
                if new_amenity:
                    amenities.append(new_amenity)
            place.amenities = amenities

        # Persist changes through repository
        self.place_repo.update(place_id, place)

        return place

    def delete_place(self, place_id):
        """
        Delete a place entity from the system.

        Removes a place listing from the database after verification. May cascade
        to related reviews depending on database configuration.

        Args:
            place_id (str): UUID of the place to delete

        Returns:
            bool: True if deletion succeeded

        Raises:
            ValueError: If place not found

        Example:
            success = facade.delete_place("12345-67890-abcdef")
        """
        # Verify place exists before attempting deletion
        place = self.place_repo.get(place_id)
        if not place:
            raise ValueError("Place not found")

        # Perform deletion through repository
        self.place_repo.delete(place_id)

        return True

    # ==================== REVIEW MANAGEMENT OPERATIONS ====================

    def create_review(self, review_data, current_user):
        """
        Create a new Review with business rule enforcement.

        Creates a user review for a place while enforcing critical business rules
        to maintain review integrity and prevent abuse. Validates relationships
        and ensures users cannot review their own properties or review the same
        place multiple times.

        Args:
            review_data (dict): Review information including:
                - text (str): Review content (1-300 characters)
                - rating (int): Star rating (1-5)
                - place_id (str): UUID of the place being reviewed
            current_user (str): UUID of the authenticated user writing the review

        Returns:
            Review: The created and persisted review instance

        Raises:
            ValueError: For business rule violations or validation failures

        Business Rules Enforced:
            - Users cannot review their own places
            - Users can only review each place once
            - Referenced user and place must exist
            - Review content and rating must meet validation criteria

        Example:
            review_data = {
                "text": "Great place with excellent amenities!",
                "rating": 5,
                "place_id": "place-uuid-here"
            }
            new_review = facade.create_review(review_data, user_id)
        """
        # Extract and validate user existence
        user_id = current_user
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("User does not exist.")

        # Validate place existence
        place = self.place_repo.get(review_data['place_id'])
        if not place:
            raise ValueError("Place does not exist.")

        # Enforce business rule: users cannot review their own places
        if place.owner.id == user_id:
            raise ValueError("You cannot review your own place")

        # Enforce business rule: one review per user per place
        existing_reviews = self.review_repo.get_by_attribute(
            'place_id', review_data['place_id'])
        for existing_review in existing_reviews:
            if existing_review.user.id == user_id:
                raise ValueError("You have already reviewed this place")

        # Create Review instance with validated relationships
        review = Review(
            text=review_data['text'],
            rating=review_data['rating'],
            user=user,
            place=place
        )

        # Persist review to database
        self.review_repo.add(review)

        return review

    def get_review(self, review_id):
        """
        Retrieve a single Review by its unique identifier.

        Fetches a review record with all relationship data for display in
        review management interfaces and detailed views.

        Args:
            review_id (str): UUID of the review to retrieve

        Returns:
            Review: The review instance with user and place relationships

        Raises:
            ValueError: If no review exists with the specified ID

        Example:
            review = facade.get_review("12345-67890-abcdef")
            print(f"Review by {review.user.first_name}: {review.text}")
        """
        # Retrieve review from repository by primary key
        review = self.review_repo.get(review_id)

        # Validate review exists and raise descriptive error if not found
        if not review:
            raise ValueError("Error ID: The requested ID does not exist.")

        return review

    def get_all_reviews(self):
        """
        Get all reviews stored in the repository.

        Fetches all review records for administrative interfaces and analytics.
        Use with caution for large datasets due to memory implications.

        Returns:
            list[Review]: All review instances with relationships

        Example:
            all_reviews = facade.get_all_reviews()
            avg_rating = sum(r.rating for r in all_reviews) / len(all_reviews)
        """
        # Return all reviews from repository
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        """
        Retrieve all reviews associated with a specific place.

        This method searches for reviews linked to a given place ID through the
        place's review relationship. This ensures consistency with the database
        relationship structure and provides accurate review collections.

        Args:
            place_id (str): UUID of the place whose reviews are requested

        Returns:
            list[Review]: Reviews linked to the specified place

        Raises:
            ValueError: If no place is found with the given ID

        Example:
            place_reviews = facade.get_reviews_by_place("place-uuid")
            for review in place_reviews:
                print(f"{review.rating}/5: {review.text}")
        """
        # Verify place exists before accessing reviews
        place = self.place_repo.get(place_id)
        if not place:
            raise ValueError("Place not found")

        # Return reviews through place relationship
        return place.reviews

    def update_review(self, review_id, review_data):
        """
        Update a review by ID with validation.

        Modifies review content while enforcing the same validation rules as
        creation. Supports partial updates for text and rating fields.

        Args:
            review_id (str): UUID of the review to update
            review_data (dict): Updated review data including:
                - text (str, optional): New review text
                - rating (int, optional): New rating (1-5)

        Returns:
            Review: The updated review instance

        Raises:
            ValueError: If review not found or validation fails

        Example:
            update_data = {"rating": 4, "text": "Updated review text"}
            updated_review = facade.update_review("12345", update_data)
        """
        # Verify review exists before attempting update
        review = self.review_repo.get(review_id)
        if not review:
            raise ValueError("Error ID: The requested ID does not exist.")

        # Validate rating if being updated
        if 'rating' in review_data and not (1 <= review_data['rating'] <= 5):
            raise ValueError("Rating must be between 1 and 5.")

        # Apply updates through repository layer
        return self.review_repo.update(review_id, review_data)

    def delete_review(self, review_id):
        """
        Delete a review entity from the system.

        Removes a review from the database after verification. This operation
        affects the place's review collection and average ratings.

        Args:
            review_id (str): UUID of the review to delete

        Returns:
            bool: True if deletion succeeded

        Raises:
            ValueError: If review not found

        Example:
            success = facade.delete_review("12345-67890-abcdef")
        """
        # Verify review exists before attempting deletion
        review = self.review_repo.get(review_id)
        if not review:
            raise ValueError("Review not found")

        # Perform deletion through repository
        self.review_repo.delete(review_id)

        return True
