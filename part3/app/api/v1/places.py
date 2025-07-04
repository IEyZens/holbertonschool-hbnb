# Importation des modules nécessaires
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade


# Création d’un namespace pour les opérations relatives aux lieux (places)
api = Namespace('places', description='Place operations')


# Définition du modèle de commodité utilisé dans un lieu
amenity_model = api.model('PlaceAmenity', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity')
})


# Définition du modèle utilisateur lié à un lieu
user_model = api.model('PlaceUser', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='First name of the owner'),
    'last_name': fields.String(description='Last name of the owner'),
    'email': fields.String(description='Email of the owner')
})


# Définition du modèle de commentaire associé à un lieu
review_model = api.model('PlaceReview', {
    'id': fields.String(description='Review ID'),
    'text': fields.String(description='Text of the review'),
    'rating': fields.Integer(description='Rating of the place (1-5)'),
    'user_id': fields.String(description='ID of the user')
})


# Définition du modèle principal représentant un lieu
place_model = api.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(required=True, description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'owner_id': fields.String(required=True, description='ID of the owner'),
    'max_person': fields.Integer(required=True, description='Maximum number of persons allowed'),
    'owner': fields.Nested(user_model, description='Owner of the place'),
    'amenities': fields.List(fields.Nested(amenity_model), description='List of amenities'),
    'reviews': fields.List(fields.Nested(review_model), description='List of reviews')
})

place_input_model = api.model('PlaceInput', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(required=True, description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'owner_id': fields.String(required=True, description='ID of the owner'),
    'max_person': fields.Integer(required=True, description='Maximum number of persons allowed'),
    'amenities': fields.List(fields.String, description='List of amenity IDs')
})

place_update_model = api.model('PlaceInput', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(required=True, description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'max_person': fields.Integer(required=True, description='Maximum number of persons allowed'),
    'amenities': fields.List(fields.String, description='List of amenity IDs')
})


@api.route('/')
class PlaceList(Resource):
    """
    Resource class that handles collection-level operations on Place data.

    This endpoint allows creation of new Place entities and retrieval of all existing Place records. It enforces data contract validation, and delegates business logic to the facade service layer.
    """

    # Indique que la requête attend des données conformes au modèle place_model
    @api.expect(place_input_model)
    # Réponse 201 si la création est un succès
    @api.response(201, 'Place successfully created')
    # Réponse 400 en cas de données invalides
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def post(self):
        """
        Create a new place entity.

        Accepts a validated JSON payload describing the new place to be created. Validation includes constraints on numeric fields, coordinates, and foreign keys. Returns a concise representation of the newly created Place.

        Returns:
            dict: JSON object containing key place attributes and HTTP 201 status, or HTTP 400 with error details.
        """
        # Extraction des données envoyées dans la requête
        place_data = api.payload
        current_user = get_jwt_identity()

        try:
            # Appel à la façade pour créer un nouveau lieu
            new_place = facade.create_place(place_data, current_user)

            # Retourne les données essentielles du lieu nouvellement créé
            return {
                'id': new_place.id,
                'title': new_place.title,
                'description': new_place.description,
                'price': new_place.price,
                'latitude': new_place.latitude,
                'longitude': new_place.longitude,
                'owner_id': new_place.owner.id,
                'max_person': new_place.max_person,
                'amenities': [amenity.name for amenity in new_place.amenities]
            }, 201
        except ValueError as e:
            # Retourne une erreur 400 si les données sont invalides au niveau métier
            return {'error': str(e)}, 400

    # Réponse 200 si récupération réussie
    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """
        Retrieve a list of all places.

        This method returns all Place entities currently registered in memory. Each record contains the core metadata required for public display.

        Returns:
            list: A list of place objects with HTTP 200 status.
        """
        # Récupère tous les lieux depuis la façade
        places = facade.get_all_places()

        # Retourne une liste de lieux sous forme de dictionnaires
        return [
            {
                'id': p.id,
                'title': p.title,
                'description': p.description,
                'price': p.price,
                'latitude': p.latitude,
                'longitude': p.longitude,
                'owner_id': p.owner.id,
                'max_person': p.max_person,
            }
            for p in places
        ], 200


@api.route('/<place_id>')
class PlaceResource(Resource):
    """
    Resource class that manages data for a single Place instance.

    This endpoint supports retrieval and update operations for a specific Place entity identified by a UUID. Payloads and identifiers are validated to ensure consistency and correct linkage to nested resources.
    """

    # Réponse 200 si les détails du lieu sont trouvés
    @api.response(200, 'Place details retrieved successfully')
    # Réponse 404 si aucun lieu ne correspond à l’ID
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """
        Retrieve the details of a specific place.

        Args:
            place_id (str): The UUID of the place resource.

        Returns:
            dict: JSON-formatted place details with nested user and amenities data, or HTTP 404 if not found.
        """
        try:
            # Récupération du lieu ciblé par son ID
            place = facade.get_place(place_id)
            if not place:
                # Retourne 404 si le lieu est introuvable
                return {'error': 'Place not found'}, 404

            # Retourne les détails complets du lieu
            return {
                'id': place.id,
                'title': place.title,
                'description': place.description,
                'price': place.price,
                'latitude': place.latitude,
                'longitude': place.longitude,
                'owner_id': place.owner.id,
                'owner': {
                    'id': place.owner.id,
                    'first_name': place.owner.first_name,
                    'last_name': place.owner.last_name,
                    'email': place.owner.email
                },
                'max_person': place.max_person,
                'amenities': [
                    {
                        'id': amenity.id,
                        'name': amenity.name
                    }
                    for amenity in place.amenities
                ]
            }, 200
        except ValueError:
            # Gestion d’erreur métier générique : retourne 404
            return {'error': 'Place not found'}, 404

    # Indique que la requête attend des données conformes au modèle place_model
    @api.expect(place_update_model)
    # Réponse 200 si mise à jour réussie
    @api.response(200, 'Place updated successfully')
    # Réponse 404 si le lieu n’existe pas
    @api.response(404, 'Place not found')
    @api.response(403, 'Unauthorized action')
    # Réponse 400 si les données sont invalides
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def put(self, place_id):
        """
        Update an existing place entity.

        Accepts a payload that may partially or fully replace the place's attributes. Performs validation on updated values (e.g., price, coordinates) and updates the repository.

        Args:
            place_id (str): The UUID of the place to update.

        Returns:
            dict: Updated place details with HTTP 200, or HTTP 400/404 with error information.
        """
        # Données mises à jour provenant du client
        place_api = api.payload
        current_user = get_jwt_identity()
        place = facade.get_place(place_id)

        if not place:
            return {'error': 'Place not found'}, 404

        if place.owner.id != current_user["id"]:
            return {'error': 'Unauthorized action'}, 403

        try:

            # Appel à la façade pour mettre à jour un lieu
            place_data = facade.update_place(place_id, place_api)

            if not place_data:
                # Retourne 404 si le lieu n’est pas trouvé
                return {'error': 'Place not found'}, 404

            # Retourne les nouvelles données du lieu mis à jour
            return {
                'id': place_data.id,
                'title': place_data.title,
                'description': place_data.description,
                'price': place_data.price,
                'latitude': place_data.latitude,
                'longitude': place_data.longitude,
                'owner_id': place_data.owner.id,
                'max_person': place_data.max_person,
                'amenities': [amenity.name for amenity in place_data.amenities]
            }, 200
        except ValueError as e:
            # Retourne une erreur métier si les données sont invalides
            return {'error': str(e)}, 400
        except Exception as e:
            # Gestion générique d’exception serveur : erreur 500
            return {'error': 'Internal server error', 'details': str(e)}, 500
