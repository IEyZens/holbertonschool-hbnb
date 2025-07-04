from abc import ABC, abstractmethod
from app import db

# Classe abstraite définissant l'interface d’un repository


class Repository(ABC):
    """
    Abstract base class defining the contract for a repository interface.

    Any concrete subclass must implement methods for standard
    CRUD operations and attribute-based filtering on domain entities.
    """

    @abstractmethod
    def add(self, obj):
        """
        Add a new object to the repository.

        Args:
            obj: The object to be stored.
        """
        # Méthode pour ajouter un objet au dépôt
        pass

    @abstractmethod
    def get(self, obj_id):
        """
        Retrieve an object by its unique identifier.

        Args:
            obj_id (str): Unique ID of the object.

        Returns:
            object or None
        """
        # Méthode pour récupérer un objet par son identifiant
        pass

    @abstractmethod
    def get_all(self):
        """
        Retrieve all stored objects.

        Returns:
            list: All objects in the repository.
        """
        # Méthode pour récupérer tous les objets
        pass

    @abstractmethod
    def update(self, obj_id, data):
        """
        Update an existing object by ID.

        Args:
            obj_id (str): ID of the object to update.
            data (dict or object): Updated data or replacement object.

        Returns:
            object: The updated object.
        """
        # Méthode pour mettre à jour un objet avec de nouvelles données
        pass

    @abstractmethod
    def delete(self, obj_id):
        """
        Remove an object by its unique ID.

        Args:
            obj_id (str): ID of the object to remove.

        Returns:
            bool: True if deleted, False otherwise.
        """
        # Méthode pour supprimer un objet par son identifiant
        pass

    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value):
        """
        Retrieve objects that match a specific attribute value.

        Args:
            attr_name (str): Name of the attribute.
            attr_value: Value to filter by.

        Returns:
            list: Matching objects.
        """
        # Méthode pour filtrer des objets selon un attribut
        pass


# Implémentation concrète du Repository en mémoire (sans base de données)
class InMemoryRepository(Repository):
    """
    Concrete in-memory implementation of the Repository interface.

    Stores domain entities in a dictionary using their 'id' as keys.
    Provides full support for CRUD operations and attribute-based queries.
    """

    def __init__(self):
        # Dictionnaire interne servant de stockage
        self._storage = {}

    def add(self, obj):
        # Ajoute un objet dans le dictionnaire avec sa clé ID
        self._storage[obj.id] = obj

    def get(self, obj_id):
        # Récupère un objet par ID, retourne None si absent
        return self._storage.get(obj_id)

    def get_all(self):
        # Retourne tous les objets sous forme de liste
        return list(self._storage.values())

    def update(self, obj_id, data):
        # Si les données sont sous forme de dictionnaire, effectue une mise à jour attribut par attribut
        if isinstance(data, dict):
            obj = self.get(obj_id)
            if not obj:
                raise KeyError("Object not found")
            for key, value in data.items():
                setattr(obj, key, value)
            return obj
        else:
            # Sinon, remplace complètement l’objet existant par le nouvel objet
            self._storage[obj_id] = data
            return data

    def delete(self, obj_id):
        # Supprime un objet si l'ID existe dans le stockage
        if obj_id in self._storage:
            del self._storage[obj_id]
            return True
        return False

    def get_by_attribute(self, attr_name, attr_value):
        # Filtre les objets selon une valeur d’attribut
        return [obj for obj in self._storage.values() if getattr(obj, attr_name) == attr_value]


class SQLAlchemyRepository(Repository):
    def __init__(self, model):
        self.model = model

    def add(self, obj):
        db.session.add(obj)
        db.session.commit()

    def get(self, obj_id):
        return self.model.query.get(obj_id)

    def get_all(self):
        return self.model.query.all()

    def update(self, obj_id, data):
        obj = self.get(obj_id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
            db.session.commit()

    def delete(self, obj_id):
        obj = self.get(obj_id)
        if obj:
            db.session.delete(obj)
            db.session.commit()

    def get_by_attribute(self, attr_name, attr_value):
        return self.model.query.filter_by(**{attr_name: attr_value}).first()
