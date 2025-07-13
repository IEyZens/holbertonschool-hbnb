# Import necessary modules for base model functionality
from app.extensions import db
import uuid
from datetime import datetime


class BaseModel(db.Model):
    """
    Abstract base class providing common fields and methods for all data models.

    This class supplies a unique identifier, creation and update timestamps, and utility methods for 
    saving and updating model instances. All models inheriting from BaseModel will automatically 
    include these features, ensuring consistency across the application's data layer.

    This is an abstract class that cannot be instantiated directly - it must be inherited by 
    concrete model classes that define their own id field and any additional attributes.

    Attributes:
        id: Unique identifier for the instance (type can be customized by subclasses)
        created_at (datetime): Timestamp of when the record was created in the database
        updated_at (datetime): Timestamp of when the record was last modified
        
    Database Behavior:
        - created_at is automatically set when a new record is inserted
        - updated_at is automatically updated whenever the record is modified
        - The abstract flag prevents this class from creating its own database table
    """

    # Mark this as an abstract model - no table will be created for this class
    __abstract__ = True

    # Note: id field is not defined here - subclasses must define their own id field
    # This allows flexibility in id types (UUID, integer, etc.) based on specific model needs
    
    # Timestamp for record creation - automatically set to current UTC time on insert
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Timestamp for record updates - automatically updated on any modification
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def save(self):
        """
        Persist the current instance state by refreshing the update timestamp.

        This method updates the 'updated_at' field to the current datetime and adds the 
        instance to the database session. It's typically used after making changes to 
        model attributes to mark the modification time and prepare for database commit.
        
        Note: This method only adds to the session - db.session.commit() must be called 
        separately to actually persist changes to the database.
        
        Usage:
            model_instance.attribute = new_value
            model_instance.save()
            db.session.commit()  # Required to persist changes
        """
        # Update timestamp to reflect the latest modification time
        self.updated_at = datetime.utcnow()
        
        # Add this instance to the database session for persistence
        db.session.add(self)

    def update(self, data):
        """
        Dynamically update instance attributes based on a dictionary payload.

        Iterates through each key/value pair in the input dictionary, updating matching 
        attributes on the instance if they exist. After applying all changes, the update 
        timestamp is refreshed and changes are committed to the database.
        
        This method provides a convenient way to update multiple attributes at once,
        typically used when processing API requests or form data.

        Args:
            data (dict): Dictionary of attribute names and their new values
                        Only existing attributes will be updated - unknown keys are ignored
                        
        Example:
            user_data = {'first_name': 'John', 'email': 'john@example.com'}
            user.update(user_data)  # Updates first_name and email, commits to DB
            
        Security Note:
            This method only updates existing attributes, preventing injection of 
            unauthorized fields. Validation should still be performed at the service layer.
        """
        # Iterate through key-value pairs in the data dictionary
        for key, value in data.items():
            # Check if the attribute exists on this instance to prevent unwanted additions
            if hasattr(self, key):
                # Update the attribute with the new value
                setattr(self, key, value)
                
        # Update timestamp and add to session
        self.save()
        
        # Commit changes to the database immediately
        db.session.commit()
