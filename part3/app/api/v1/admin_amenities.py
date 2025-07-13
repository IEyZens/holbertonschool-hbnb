# Importation des modules nécessaires
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade


# Création d’un namespace Flask-RESTx pour les opérations liées aux commodités (amenities)
api = Namespace('admin', description='Admin operations')


# Définition du modèle de données pour la validation d'entrée et la documentation Swagger
amenity_model = api.model('Amenity', {
    # Champ requis : nom de la commodité
    'name': fields.String(required=True, description='Name of the amenity')
})


@api.route('/amenities/')
class AdminAmenityCreate(Resource):
    """
    Resource for admin amenity creation.

    Allows an admin user to create a new amenity.
    """
    @api.expect(amenity_model)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def post(self):
        """
        Create a new amenity as an admin.

        Only admins can access this endpoint. It checks for admin rights, validates the input, and delegates creation to the service layer.

        Returns:
            dict: Created amenity data or error message.
        """
        # Récupération de l'utilisateur actuel et vérification des droits admin
        current_user = get_jwt_identity()
        claims = get_jwt()
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        # Récupération des données envoyées dans la requête
        amenity_data = api.payload

        try:
            # Création de la commodité via la façade
            new_amenity = facade.create_amenity(amenity_data)
            return {
                'id': new_amenity.id,
                'name': new_amenity.name
            }, 201

        except ValueError as e:
            # Gestion d'erreur si les données sont invalides
            return {'error': str(e)}, 400

        except Exception as e:
            # Gestion générique d'exception serveur : erreur 500
            return {'error': 'Internal server error'}, 500


@api.route('/amenities/<amenity_id>')
class AdminAmenityModify(Resource):

    @api.response(200, 'Amenity retrieved successfully')
    @api.response(404, 'Amenity not found')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def get(self, amenity_id):
        claims = get_jwt()
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403
        try:
            amenity = facade.get_amenity(amenity_id)
        except (ValueError, KeyError):
            return {'error': 'Amenity not found'}, 404
        return {
            'id': amenity.id,
            'name': amenity.name
        }, 200

    @api.expect(amenity_model, validate=True)
    @api.response(200, 'Amenity updated successfully')
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def put(self, amenity_id):
        claims = get_jwt()
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

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
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def delete(self, amenity_id):
        claims = get_jwt()
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        try:
            amenity = facade.get_amenity(amenity_id)
        except (ValueError, KeyError):
            return {'error': 'Amenity not found'}, 404

        try:
            facade.delete_amenity(amenity_id)
            return '', 204
        except Exception:
            return {'error': 'Internal server error'}, 500
