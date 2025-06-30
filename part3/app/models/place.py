from .base_model import BaseModel


class Place(BaseModel):
    """
    Domain entity representing a rentable place listed on the platform.

    This model encapsulates geographic, descriptive, and ownership data, and enforces
    strict validation constraints. It also manages relationships with User, Amenity,
    and Review entities.

    Attributes:
        title (str): Title of the place, max 100 characters.
        description (str): Optional description of the place.
        price (float): Price per night, must be >= 0.
        latitude (float): Latitude coordinate, between -90 and 90.
        longitude (float): Longitude coordinate, between -180 and 180.
        owner (User): The User who owns this place.
        max_person (int): Maximum capacity.
        reviews (list): List of associated Review instances.
        amenities (list): List of associated Amenity instances.
    """

    def __init__(self, title: str, description: str, price: float, latitude: float, longitude: float, owner, max_person: int):
        """
        Initializes a new Place entity and validates all core attributes.

        Enforces geolocation bounds, pricing constraints, title length,
        and verifies that owner is a valid User instance. Reviews and amenities
        are initialized as empty lists by default.

        Raises:
            ValueError: For out-of-range or missing data.
            TypeError: If the owner is not a User instance.
        """
        # Appel au constructeur de la classe parente pour initialiser id, created_at, updated_at
        super().__init__()

        # Vérifie que le titre n’est pas vide et ne dépasse pas 100 caractères
        if not title or len(title) > 100:
            raise ValueError(
                "Invalid title: must be a non-empty string up to 100 characters.")

        # Vérifie que le prix est positif ou nul
        if price < 0:
            raise ValueError(
                "Invalid price: must be a number greater than or equal to 0.")

        # Vérifie que la latitude est dans l’intervalle valide
        if latitude < -90 or latitude > 90:
            raise ValueError(
                "Invalid latitude: must be a float between -90 and 90 degrees.")

        # Vérifie que la longitude est dans l’intervalle valide
        if longitude < -180 or longitude > 180:
            raise ValueError(
                "Invalid longitude: must be a float between -180 and 180 degrees.")

        # Importation locale de la classe User pour éviter les importations circulaires
        from .user import User
        # Vérifie que l'owner est une instance de User
        if not isinstance(owner, User):
            raise TypeError(
                "Invalid owner: must be an instance of the User class.")

        # Vérifie que la capacité maximale est au moins de 1 personne
        if max_person < 1:
            raise ValueError("Invalid capacity: must be at least 1 person.")

        # Affectation des attributs à l’instance
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner
        self.max_person = max_person
        # Initialisation de la liste des avis
        self.reviews = []
        # Initialisation de la liste des commodités
        self.amenities = []

    def add_review(self, review):
        """
        Associates a Review instance to this Place.

        Args:
            review (Review): A valid Review entity.

        Raises:
            TypeError: If the object is not a Review.
        """
        # Importation locale pour éviter les dépendances circulaires
        from .review import Review
        # Vérifie que l'objet passé est bien une instance de Review
        if not isinstance(review, Review):
            raise TypeError(
                "Invalid review: must be an instance of the Review class.")
        # Ajout du commentaire à la liste des avis
        self.reviews.append(review)

    def add_amenity(self, amenity):
        """
        Associates an Amenity instance to this Place.

        Args:
            amenity (Amenity): A valid Amenity entity.

        Raises:
            TypeError: If the object is not an Amenity.
        """
        # Importation locale pour éviter les dépendances circulaires
        from .amenity import Amenity
        # Vérifie que l'objet passé est bien une instance de Amenity
        if not isinstance(amenity, Amenity):
            raise TypeError(
                "Invalid amenity: must be an instance of the Amenity class.")
        # Ajout de l'élément à la liste des commodités
        self.amenities.append(amenity)
