# Import necessary modules for repository pattern implementation
from abc import ABC, abstractmethod
from app.extensions import db

# Abstract class defining the repository interface


class Repository(ABC):
    """
    Abstract base class defining the contract for a repository interface.

    This class establishes a standardized interface for data persistence operations following
    the Repository pattern. Any concrete subclass must implement methods for standard
    CRUD operations and attribute-based filtering on domain entities.

    The Repository pattern provides a uniform interface for accessing data, abstracting
    the underlying storage mechanism (in-memory, database, file system, etc.) from the
    business logic layer.

    All implementing classes must provide:
    - Basic CRUD operations (Create, Read, Update, Delete)
    - Bulk retrieval operations
    - Attribute-based filtering capabilities

    This abstraction enables easy switching between different storage backends and
    facilitates unit testing by allowing mock implementations.
    """

    @abstractmethod
    def add(self, obj):
        """
        Add a new object to the repository.

        Persists a new domain entity to the underlying storage mechanism.
        The implementation should handle any storage-specific operations like
        session management, transaction handling, and constraint validation.

        Args:
            obj: The domain entity object to be stored

        Raises:
            Exception: Implementation-specific exceptions for storage failures,
                      constraint violations, or validation errors

        Example:
            repository.add(user_instance)  # Stores user in underlying storage
        """
        # Method to add an object to the repository
        pass

    @abstractmethod
    def get(self, obj_id):
        """
        Retrieve an object by its unique identifier.

        Fetches a single domain entity from storage using its primary key or
        unique identifier. Returns None if no object with the given ID exists.

        Args:
            obj_id (str): Unique identifier of the object to retrieve

        Returns:
            object or None: The domain entity if found, None if not found

        Example:
            user = repository.get("12345")  # Returns User instance or None
        """
        # Method to retrieve an object by its identifier
        pass

    @abstractmethod
    def get_all(self):
        """
        Retrieve all stored objects.

        Fetches all domain entities of the repository's type from storage.
        For large datasets, implementations should consider pagination or
        streaming to avoid memory issues.

        Returns:
            list: All objects in the repository, empty list if none exist

        Performance Note:
            This method loads all entities into memory. Use with caution for
            large datasets and consider implementing pagination in the service layer.

        Example:
            all_users = repository.get_all()  # Returns list of all User instances
        """
        # Method to retrieve all objects
        pass

    @abstractmethod
    def update(self, obj_id, data):
        """
        Update an existing object by ID.

        Modifies an existing domain entity in storage. The data parameter can be
        either a dictionary of attributes to update or a complete replacement object.

        Implementations should handle partial updates when data is a dictionary,
        updating only the specified attributes while preserving others.

        Args:
            obj_id (str): Unique identifier of the object to update
            data (dict or object): Updated attribute data or replacement object

        Returns:
            object: The updated domain entity

        Raises:
            KeyError: If no object with the given ID exists
            Exception: Implementation-specific exceptions for update failures

        Example:
            updated_user = repository.update("12345", {"email": "new@email.com"})
        """
        # Method to update an object with new data
        pass

    @abstractmethod
    def delete(self, obj_id):
        """
        Remove an object by its unique ID.

        Permanently removes a domain entity from storage. Implementations should
        handle any cascading operations or referential integrity constraints.

        Args:
            obj_id (str): Unique identifier of the object to remove

        Returns:
            bool: True if object was found and deleted, False if not found

        Example:
            success = repository.delete("12345")  # Returns True if deleted
        """
        # Method to delete an object by its identifier
        pass

    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value):
        """
        Retrieve objects that match a specific attribute value.

        Performs attribute-based filtering to find all entities where the specified
        attribute equals the given value. This enables flexible querying beyond
        simple ID-based lookups.

        Args:
            attr_name (str): Name of the attribute to filter by
            attr_value: Value to match against the attribute

        Returns:
            list: All objects matching the attribute criteria, empty list if none found

        Raises:
            AttributeError: If the specified attribute doesn't exist on the model

        Example:
            active_users = repository.get_by_attribute("is_active", True)
        """
        # Method to filter objects by attribute
        pass


# Concrete in-memory implementation of Repository (no database)
class InMemoryRepository(Repository):
    """
    Concrete in-memory implementation of the Repository interface.

    Stores domain entities in a Python dictionary using their 'id' attribute as keys.
    Provides full support for CRUD operations and attribute-based queries without
    requiring an external database or persistence layer.

    This implementation is ideal for:
    - Unit testing and development
    - Prototyping and proof-of-concept work
    - Small applications with minimal data requirements
    - Scenarios where data persistence between application restarts is not required

    Data Structure:
    - Uses a dictionary (_storage) where keys are object IDs and values are the objects
    - All operations are performed in memory with O(1) access time for ID-based operations
    - Attribute-based queries require O(n) iteration through all stored objects

    Limitations:
    - Data is lost when the application terminates
    - No transaction support or ACID guarantees
    - Limited scalability for large datasets
    - No concurrent access control
    """

    def __init__(self):
        """
        Initialize the in-memory storage.

        Creates an empty dictionary to serve as the internal storage mechanism.
        Each object will be stored with its 'id' attribute as the dictionary key.
        """
        # Internal dictionary serving as storage mechanism
        self._storage = {}

    def add(self, obj):
        """
        Add an object to the in-memory storage.

        Stores the object in the internal dictionary using its 'id' attribute as the key.
        If an object with the same ID already exists, it will be overwritten.

        Args:
            obj: Domain entity with an 'id' attribute

        Raises:
            AttributeError: If the object doesn't have an 'id' attribute

        Example:
            repository.add(user)  # Stores user with user.id as key
        """
        # Add object to dictionary using its ID as key
        self._storage[obj.id] = obj

    def get(self, obj_id):
        """
        Retrieve an object by ID from memory.

        Performs dictionary lookup using the provided ID as key.
        Returns None if no object with the given ID exists.

        Args:
            obj_id (str): Unique identifier of the object

        Returns:
            object or None: The stored object if found, None otherwise

        Time Complexity: O(1) - constant time dictionary lookup
        """
        # Retrieve object by ID, return None if not found
        return self._storage.get(obj_id)

    def get_all(self):
        """
        Return all stored objects as a list.

        Extracts all values from the storage dictionary and returns them as a list.
        The order of objects in the list is not guaranteed to be consistent.

        Returns:
            list: All stored objects, empty list if storage is empty

        Time Complexity: O(n) - creates new list with all stored objects
        """
        # Return all objects as a list
        return list(self._storage.values())

    def update(self, obj_id, data):
        """
        Update an existing object with new data.

        Supports two update modes:
        1. Dictionary mode: Updates specific attributes while preserving others
        2. Object replacement mode: Completely replaces the existing object

        Args:
            obj_id (str): ID of the object to update
            data (dict or object): New data or replacement object

        Returns:
            object: The updated object

        Raises:
            KeyError: If no object with the given ID exists

        Example:
            # Partial update
            repository.update("123", {"name": "New Name"})
            # Complete replacement
            repository.update("123", new_user_object)
        """
        # Handle dictionary-based partial updates
        if isinstance(data, dict):
            obj = self.get(obj_id)
            if not obj:
                raise KeyError("Object not found")
            # Update each attribute specified in the data dictionary
            for key, value in data.items():
                setattr(obj, key, value)
            return obj
        else:
            # Complete object replacement
            self._storage[obj_id] = data
            return data

    def delete(self, obj_id):
        """
        Remove an object from storage by ID.

        Attempts to delete the object with the specified ID from the storage dictionary.
        Returns a boolean indicating whether the deletion was successful.

        Args:
            obj_id (str): ID of the object to delete

        Returns:
            bool: True if object was found and deleted, False if not found

        Time Complexity: O(1) - constant time dictionary deletion
        """
        # Delete object if it exists in storage
        if obj_id in self._storage:
            del self._storage[obj_id]
            return True
        return False

    def get_by_attribute(self, attr_name, attr_value):
        """
        Filter objects by a specific attribute value.

        Iterates through all stored objects and returns those where the specified
        attribute equals the given value. Uses Python's getattr() function for
        dynamic attribute access.

        Args:
            attr_name (str): Name of the attribute to filter by
            attr_value: Value to match against

        Returns:
            list: Objects matching the attribute criteria

        Raises:
            AttributeError: If any object doesn't have the specified attribute

        Time Complexity: O(n) - must check all stored objects

        Example:
            admin_users = repository.get_by_attribute("is_admin", True)
        """
        # Filter objects based on attribute value using list comprehension
        return [obj for obj in self._storage.values() if getattr(obj, attr_name) == attr_value]


class SQLAlchemyRepository(Repository):
    """
    SQLAlchemy-backed repository implementation.

    Provides CRUD and attribute-based queries using SQLAlchemy ORM for database persistence.
    This implementation offers full ACID transaction support, referential integrity,
    and robust error handling for production database environments.

    Features:
    - Automatic transaction management with rollback on errors
    - SQLAlchemy ORM integration for type-safe database operations
    - Support for complex queries and relationships
    - Connection pooling and performance optimization
    - Thread-safe database access

    This implementation is suitable for:
    - Production applications requiring data persistence
    - Multi-user environments with concurrent access
    - Applications requiring complex queries and relationships
    - Systems requiring ACID transaction guarantees

    Database Support:
    - Compatible with all SQLAlchemy-supported databases (PostgreSQL, MySQL, SQLite, etc.)
    - Automatic schema management through SQLAlchemy migrations
    - Optimized query generation and execution plans
    """

    def __init__(self, model):
        """
        Initialize the repository with a specific SQLAlchemy model.

        Args:
            model: SQLAlchemy model class (e.g., User, Place, Review)
                  This model defines the database table structure and relationships
        """
        self.model = model

    def add(self, obj):
        """
        Add an object to the database with transaction management.

        Adds the object to the SQLAlchemy session and commits the transaction.
        If any error occurs during the operation, the transaction is rolled back
        to maintain database consistency.

        Args:
            obj: SQLAlchemy model instance to persist

        Raises:
            Exception: Database-specific exceptions (constraint violations, connection errors, etc.)
                      Original exception is re-raised after rollback for proper error handling

        Example:
            repository.add(user_instance)  # Commits to database or rolls back on error
        """
        try:
            # Add object to SQLAlchemy session
            db.session.add(obj)
            # Commit transaction to persist changes
            db.session.commit()
        except Exception as e:
            # Rollback transaction on any error to maintain consistency
            db.session.rollback()
            # Re-raise original exception for upstream error handling
            raise e

    def get(self, obj_id):
        """
        Retrieve an object by primary key using SQLAlchemy query.

        Uses SQLAlchemy's query.get() method which leverages the session cache
        and database primary key for efficient object retrieval.

        Args:
            obj_id (str): Primary key value of the object to retrieve

        Returns:
            object or None: SQLAlchemy model instance if found, None otherwise

        Performance Note:
            This method benefits from SQLAlchemy's first-level cache and identity map
        """
        return self.model.query.get(obj_id)

    def get_all(self):
        """
        Retrieve all objects of this model type from the database.

        Executes a SELECT * query for the model's table and returns all records
        as SQLAlchemy model instances. Use with caution for large tables.

        Returns:
            list: All model instances from the database

        Performance Warning:
            This loads all records into memory. Consider pagination for large datasets.
        """
        return self.model.query.all()

    def update(self, obj_id, data):
        """
        Update an existing database record with transaction safety.

        Retrieves the object by ID, updates its attributes, and commits the changes.
        Supports dictionary-based partial updates while preserving unchanged attributes.

        Args:
            obj_id (str): Primary key of the object to update
            data (dict): Dictionary of attribute names and new values

        Returns:
            object: Updated SQLAlchemy model instance

        Raises:
            KeyError: If no object with the given ID exists
            Exception: Database-specific exceptions with automatic rollback

        Example:
            updated_user = repository.update("123", {"email": "new@email.com"})
        """
        # Retrieve existing object from database
        obj = self.get(obj_id)
        if not obj:
            raise KeyError("Object not found")

        try:
            # Update attributes if data is provided as dictionary
            if isinstance(data, dict):
                for key, value in data.items():
                    setattr(obj, key, value)
            # Commit changes to database
            db.session.commit()
            return obj
        except Exception as e:
            # Rollback transaction on error to maintain consistency
            db.session.rollback()
            # Re-raise exception for upstream handling
            raise e

    def delete(self, obj_id):
        """
        Delete an object from the database with transaction safety.

        Retrieves the object by ID, removes it from the session, and commits the deletion.
        Handles referential integrity constraints based on database configuration.

        Args:
            obj_id (str): Primary key of the object to delete

        Returns:
            bool: True if object was found and deleted, False if not found

        Raises:
            Exception: Database-specific exceptions (foreign key constraints, etc.)
                      with automatic rollback
        """
        # Retrieve object to delete
        obj = self.get(obj_id)
        if not obj:
            return False
        try:
            # Remove object from session
            db.session.delete(obj)
            # Commit deletion to database
            db.session.commit()
            return True
        except Exception as e:
            # Rollback transaction on error
            db.session.rollback()
            # Re-raise exception for upstream handling
            raise e

    def get_by_attribute(self, attr_name, attr_value):
        """
        Return all records matching a specific attribute value.

        Performs a filtered query using SQLAlchemy's query interface to find all
        records where the specified attribute equals the given value. Always returns
        a list, even if no matches are found.

        Args:
            attr_name (str): Name of the model attribute to filter by
            attr_value: Value to match against the attribute

        Returns:
            list: All matching model instances, empty list if none found

        Raises:
            ValueError: If attr_name is not a valid attribute of the model

        Example:
            active_users = repository.get_by_attribute("is_active", True)
            # Generates SQL: SELECT * FROM users WHERE is_active = true
        """
        try:
            # Get the SQLAlchemy attribute object for dynamic querying
            attr = getattr(self.model, attr_name)
            # Execute filtered query and return all matching results
            return self.model.query.filter(attr == attr_value).all()
        except AttributeError:
            # Raise descriptive error for invalid attribute names
            raise ValueError(
                f"{attr_name} is not a valid attribute of {self.model.__name__}")

    def get_amenity_by_name(self, name):
        """
        Retrieve a single amenity by its name.

        Specialized query method for finding amenities by their name attribute.
        Uses SQLAlchemy's filter_by for exact string matching and first() to
        return only the first match or None.

        Args:
            name (str): The exact name of the amenity to find

        Returns:
            object or None: The amenity model instance if found, None otherwise

        Example:
            wifi_amenity = repository.get_amenity_by_name("WiFi")
        """
        return self.model.query.filter_by(name=name).first()
