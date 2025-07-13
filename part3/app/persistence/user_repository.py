from app.models.user import User
from app.persistence.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(User)

    def get_user_by_email(self, email):
        """
        Retrieve a user by email address.

        Args:
            email (str): The user's email.

        Returns:
            User or None: The user instance if found, else None.
        """
        return self.model.query.filter_by(email=email).first()

    def get_user_by_id(self, user_id):
        return self.model.query.get(user_id)
