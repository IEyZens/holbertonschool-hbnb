# Importation des modules nécessaires
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

# Création d’un namespace Flask-RESTx pour les opérations liées aux commodités (amenities)
api = Namespace('amenities', description='Amenity operations')

# Définition du modèle de données pour la validation d'entrée et la documentation Swagger
amenity_model = api.model('Amenity', {
    # Champ requis : nom de la commodité
    'name': fields.String(required=True, description='Name of the amenity')
})


@api.route('/')
class AmenityList(Resource):
    """
    Resource class for managing collection-level operations on amenities.

    This class provides endpoints to create a new amenity or retrieve all existing amenities.
    Input validation is performed using the API model, and business logic is handled by the facade layer.
    """

    # Spécifie que cette méthode attend un corps de requête conforme au modèle amenity_model
    @api.expect(amenity_model)
    # Réponse en cas de succès : commodité créée
    @api.response(201, 'Amenity successfully created')
    # Réponse en cas d'échec de validation des données
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    @jwt_required()
    def post(self):
        """
        Create a new amenity. Only admins can create amenities.

        This endpoint receives a JSON payload validated against the Amenity model.
        The creation logic is delegated to the business facade layer. On success, returns the created amenity with its ID.
        On failure, returns an error message with HTTP 400.

        Returns:
            tuple: (JSON response, HTTP status code)
        """
        # Vérification des privilèges admin
        claims = get_jwt()
        if not claims.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403

        # Récupération des données envoyées dans le corps de la requête
        amenity_data = api.payload

        try:
            # Appel à la façade pour créer une commodité
            new_amenity = facade.create_amenity(amenity_data)
            # Retourne les données de la commodité créée
            return {
                'id': new_amenity.id,
                'name': new_amenity.name
            }, 201
        except ValueError as e:
            # En cas d'erreur de validation métier, retour d'une réponse 400 avec le message d'erreur
            return {'error': str(e)}, 400
        except Exception as e:
            # Gestion d'erreur générique
            return {'error': 'Internal server error'}, 500

    @api.response(200, 'List of amenities retrieved successfully')
    def get(self):
        amenities = facade.get_all_amenities()
        return [{'id': a.id, 'name': a.name} for a in amenities], 200


@api.route('/<amenity_id>')
class AmenityResource(Resource):
    """
    Resource class for managing item-level operations on a single amenity.

    This class provides endpoints to retrieve or update a specific amenity by its unique ID.
    All business logic is delegated to the facade layer, and input data is strictly validated.
    """

    @api.response(200, 'Amenity retrieved successfully')
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity not found'}, 404
        return {'id': amenity.id, 'name': amenity.name}, 200

    # Spécifie que la requête PUT doit contenir des données correspondant au modèle amenity_model
    @api.expect(amenity_model)
    # Réponse si la mise à jour est réussie
    @api.response(200, 'Amenity updated successfully')
    # Réponse si la commodité à mettre à jour n'existe pas
    @api.response(404, 'Amenity not found')
    # Réponse si les données d'entrée sont invalides
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    @jwt_required()
    def put(self, amenity_id):
        """
        Update a specific amenity. Only admins can update amenities.

        This endpoint accepts a JSON payload with updated data for the amenity identified by the given ID.
        If the amenity exists, it is updated and the new data is returned. If not, returns an error message with HTTP 404.
        On invalid input, returns an error message with HTTP 400.

        Args:
            amenity_id (str): Unique identifier of the amenity.

        Returns:
            tuple: (updated amenity as JSON, HTTP status code)
        """
        # Vérification des privilèges admin
        claims = get_jwt()
        if not claims.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403

        # Récupération des données d'entrée fournies dans le corps de la requête
        amenity_api = api.payload

        try:
            amenity_data = facade.update_amenity(amenity_id, amenity_api)
            if not amenity_data:
                return {'error': 'Amenity not found'}, 404
            return {
                'id': amenity_data.id,
                'name': amenity_data.name
            }, 200
        except ValueError as e:
            return {'error': str(e)}, 400
        except (ValueError, KeyError):
            return {'error': 'Amenity not found'}, 404

    @api.response(204, 'Amenity deleted successfully')
    @api.response(404, 'Amenity not found')
    @api.response(403, 'Admin privileges required')
    @jwt_required()
    def delete(self, amenity_id):
        """
        Delete a specific amenity. Only admins can delete amenities.
        """
        claims = get_jwt()
        if not claims.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403

        try:
            facade.delete_amenity(amenity_id)
            return '', 204
        except ValueError:
            return {'error': 'Amenity not found'}, 404
        except Exception:
            return {'error': 'Internal server error'}, 500
