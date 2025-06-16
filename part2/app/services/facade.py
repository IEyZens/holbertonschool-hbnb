from app.persistence.repository import InMemoryRepository
from app.models.user import User

class HBnBFacade:
    def __init__(self):
        self.user_repo = InMemoryRepository()

    def create_user(self, user_data):
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_by_attribute('email', email)

    def update_user(self, user_id, data):
        return self.user_repo.update(user_id, data)

    def create_amenity(self, amenity_data):
        # Espace réservé pour la logique de création d’une commodité
        pass

    def get_amenity(self, amenity_id):
        # Espace réservé pour la logique de récupération d’une commodité par ID
        pass

    def get_all_amenities(self):
        # Espace réservé pour la logique de récupération de toutes les commodités
        pass

    def update_amenity(self, amenity_id, amenity_data):
        # Espace réservé pour la logique de mise à jour d’une commodité
        pass
