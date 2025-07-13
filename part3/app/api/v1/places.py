# Importation des modules nécessaires
from flask import request, current_app as app
from flask_restx import Namespace, Resource, fields
from app.extensions import db
from app.models.user import User
from app.models.place import Place
from app.models.amenity import Amenity
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
    'description': fields.String(required=False, description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'max_person': fields.Integer(required=True, description='Maximum number of persons allowed'),
    'amenities': fields.List(fields.String, description='List of amenity IDs')
})

place_update_model = api.model('PlaceUpdateInput', {
    'title': fields.String(required=False, description='Title of the place'),
    'description': fields.String(required=False, description='Description of the place'),
    'price': fields.Float(required=False, description='Price per night'),
    'latitude': fields.Float(required=False, description='Latitude of the place'),
    'longitude': fields.Float(required=False, description='Longitude of the place'),
    'max_person': fields.Integer(required=False, description='Maximum number of persons allowed'),
    'amenities': fields.List(fields.String, description='List of amenity IDs')
})


@api.route('/')
class PlaceList(Resource):
    """
    Resource class that handles collection-level operations on Place data.

    This endpoint allows creation of new Place entities and retrieval of all existing Place records. It enforces data contract validation, and delegates business logic to the facade service layer.
    """

    @api.expect(place_input_model)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        user = facade.get_user_by_id(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        data = request.get_json()
        if not data:
            return {'error': 'Missing JSON body'}, 400

        amenity_names = data.get("amenities", [])

        # Validation des noms d'amenities
        for name in amenity_names:
            if not isinstance(name, str) or not name.strip():
                return {'error': f'Invalid amenity name: {name}'}, 400

        try:
            # Préparer les données pour la facade
            place_data = {
                'title': data.get("title"),
                'description': data.get("description"),
                'price': data.get("price"),
                'latitude': data.get("latitude"),
                'longitude': data.get("longitude"),
                'max_person': data.get("max_person")
            }

            # Récupérer ou créer les amenities et obtenir leurs IDs
            amenity_ids = []
            for name in amenity_names:
                name = name.strip()
                amenity_list = facade.get_amenity_by_name(name)

                if amenity_list and len(amenity_list) > 0:
                    amenity = amenity_list[0]
                else:
                    # Créer un nouvel amenity si il n'existe pas
                    amenity = facade.create_amenity({'name': name})

                amenity_ids.append(amenity.id)

            # Ajouter les IDs des amenities aux données de la place
            if amenity_ids:
                place_data['amenities'] = amenity_ids

            # Utiliser la facade pour créer la place
            new_place = facade.create_place(place_data, user_id)
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            app.logger.error(f"Error creating place: {e}")
            db.session.rollback()  # Annuler la transaction en cas d'erreur
            return {'error': 'Failed to create Place'}, 500

        return {
            'id': new_place.id,
            'title': new_place.title,
            'description': new_place.description,
            'price': new_place.price,
            'latitude': new_place.latitude,
            'longitude': new_place.longitude,
            'max_person': new_place.max_person,
            'amenities': [a.name for a in new_place.amenities] if new_place.amenities else [],
            'owner_id': new_place.owner_id
        }, 201

    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """
        Retrieve all places.

        Returns a list of all places with their basic information including
        owner details and amenities.

        Returns:
            list: List of place objects with metadata
        """
        try:
            places = facade.get_all_places()
            return [{
                'id': place.id,
                'title': place.title,
                'description': place.description,
                'price': place.price,
                'latitude': place.latitude,
                'longitude': place.longitude,
                'max_person': place.max_person,
                'owner_id': place.owner_id,
                'owner': {
                    'id': place.owner.id,
                    'first_name': place.owner.first_name,
                    'last_name': place.owner.last_name,
                    'email': place.owner.email
                } if place.owner else None,
                'amenities': [
                    {
                        'id': amenity.id,
                        'name': amenity.name
                    } for amenity in place.amenities
                ] if place.amenities else [],
                'created_at': place.created_at.isoformat() if hasattr(place, 'created_at') and place.created_at else None,
                'updated_at': place.updated_at.isoformat() if hasattr(place, 'updated_at') and place.updated_at else None
            } for place in places], 200
        except Exception as e:
            app.logger.error(f"Error retrieving places: {e}")
            return {'error': 'Failed to retrieve places'}, 500


@api.route('/<place_id>')
class PlaceResource(Resource):
    @api.response(200, 'Place retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        return {
            'id': place.id,
            'title': place.title,
            'description': place.description,
            'price': place.price,
            'latitude': place.latitude,
            'longitude': place.longitude,
            'owner_id': place.owner.id,
            'max_person': place.max_person
        }, 200

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
        place_data = request.get_json()
        current_user = get_jwt_identity()
        claims = get_jwt()

        if not place_data:
            return {'error': 'Missing JSON body'}, 400

        try:
            place = facade.get_place(place_id)
        except ValueError:
            return {'error': 'Place not found'}, 404

        is_admin = claims.get('is_admin', False)
        if not is_admin and place.owner.id != current_user:
            return {'error': 'Unauthorized action'}, 403

        # Interdiction de modifier owner_id
        if 'owner_id' in place_data:
            return {'error': 'You cannot modify owner_id'}, 400

        # Traitement spécial pour les amenities si présentes
        if 'amenities' in place_data:
            amenity_names = place_data.get('amenities', [])

            # Validation des noms d'amenities
            for name in amenity_names:
                if not isinstance(name, str) or not name.strip():
                    return {'error': f'Invalid amenity name: {name}'}, 400

            # Récupérer ou créer les amenities et obtenir leurs IDs
            amenity_ids = []
            for name in amenity_names:
                name = name.strip()
                amenity_list = facade.get_amenity_by_name(name)

                if amenity_list and len(amenity_list) > 0:
                    amenity = amenity_list[0]
                else:
                    # Créer un nouvel amenity si il n'existe pas
                    amenity = facade.create_amenity({'name': name})

                # Format attendu par la facade
                amenity_ids.append({'id': amenity.id})

            # Remplacer les noms par les objets avec IDs
            place_data['amenities'] = amenity_ids

        try:
            updated_place = facade.update_place(place_id, place_data)
            return {
                'id': updated_place.id,
                'title': updated_place.title,
                'description': updated_place.description,
                'price': updated_place.price,
                'latitude': updated_place.latitude,
                'longitude': updated_place.longitude,
                'owner_id': updated_place.owner.id,
                'max_person': updated_place.max_person,
                'amenities': [{'id': a.id, 'name': a.name} for a in updated_place.amenities]
            }, 200
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': 'Internal server error', 'details': str(e)}, 500

    @api.response(204, 'Place deleted successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Place not found')
    @jwt_required()
    def delete(self, place_id):
        current_user = get_jwt_identity()
        claims = get_jwt()

        try:
            place = facade.get_place(place_id)
        except ValueError:
            return {'error': 'Place not found'}, 404

        is_admin = claims.get('is_admin', False)
        if not is_admin and place.owner.id != current_user:
            return {'error': 'Unauthorized action'}, 403

        try:
            facade.delete_place(place_id)
            return '', 204
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': 'Internal server error', 'details': str(e)}, 500
