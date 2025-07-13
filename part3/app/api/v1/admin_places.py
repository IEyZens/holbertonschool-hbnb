from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

# Création d’un namespace pour les opérations relatives aux lieux (places)
api = Namespace('admin', description='Admin operations')

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
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'owner_id': fields.String(required=True, description='ID of the owner'),
    'max_person': fields.Integer(required=True, description='Maximum number of persons allowed'),
    'owner': fields.Nested(user_model, description='Owner of the place'),
    'amenities': fields.List(fields.Nested(amenity_model), description='List of amenities'),
})

place_update_model = api.model('Place', {
    'title': fields.String(required=False, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=False, description='Price per night'),
    'latitude': fields.Float(required=False, description='Latitude of the place'),
    'longitude': fields.Float(required=False, description='Longitude of the place'),
    'max_person': fields.Integer(required=False, description='Maximum number of persons allowed'),
    'amenities': fields.List(fields.Nested(amenity_model), description='List of amenities'),
})


@api.route('/places/<place_id>')
class AdminPlaceModify(Resource):
    """
    Resource for admin operations on a specific place.

    This endpoint allows an admin or owner to update a place's details. Enforces authentication, authorization, and correct data contract for update operations.
    """
    @api.response(200, 'Place retrieved successfully')
    @api.response(404, 'Place not found')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def get(self, place_id):
        """
        Retrieve a place by its ID. Only admins or the owner can view.

        Args:
            place_id (str): The UUID of the place to retrieve.

        Returns:
            dict: Place data or error message.
        """
        current_user = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        user_id = current_user

        try:
            place = facade.get_place(place_id)
        except (ValueError, KeyError):
            return {'error': 'Place not found'}, 404

        if not is_admin and place.owner.id != user_id:
            return {'error': 'Unauthorized action'}, 403

        return {
            'id': place.id,
            'title': place.title,
            'description': place.description,
            'price': place.price,
            'latitude': place.latitude,
            'longitude': place.longitude,
            'owner_id': place.owner.id,
            'max_person': place.max_person,
            'owner': {
                'id': place.owner.id,
                'first_name': place.owner.first_name,
                'last_name': place.owner.last_name,
                'email': place.owner.email
            },
            'amenities': [
                {'id': a.id, 'name': a.name} for a in place.amenities
            ]
        }, 200

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
        Update a place by its ID. Only admins or the owner can update.

        Args:
            place_id (str): The UUID of the place to update.

        Returns:
            dict: Updated place information or error details with appropriate HTTP status.
        """
        # Récupération de l'identité de l'utilisateur courant
        current_user = get_jwt_identity()
        claims = get_jwt()

        # Vérifie si l'utilisateur est admin ou propriétaire
        is_admin = claims.get('is_admin', False)
        user_id = current_user

        try:
            place = facade.get_place(place_id)
        except (ValueError, KeyError):
            return {'error': 'Place not found'}, 404

        if not is_admin and place.owner.id != user_id:
            return {'error': 'Unauthorized action'}, 403

        # Récupère les données envoyées par l'API
        place_api = api.payload

        try:
            # Tente de mettre à jour le lieu avec les nouvelles données
            place_data = facade.update_place(place_id, place_api)

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

    @api.response(204, 'Place deleted successfully')
    @api.response(404, 'Place not found')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def delete(self, place_id):
        """
        Delete a place by its ID. Only admins or the owner can delete.

        Args:
            place_id (str): The UUID of the place to delete.

        Returns:
            Empty response with 204 status or error message.
        """
        current_user = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        user_id = current_user

        try:
            place = facade.get_place(place_id)
        except (ValueError, KeyError):
            return {'error': 'Place not found'}, 404

        if not is_admin and place.owner.id != user_id:
            return {'error': 'Unauthorized action'}, 403

        try:
            facade.delete_place(place_id)
            return '', 204
        except Exception:
            return {'error': 'Internal server error'}, 500
