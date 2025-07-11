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
    """
    Resource for admin amenity modification.

    Allows an admin user to update an existing amenity.
    """
    @api.expect(amenity_model)
    @api.response(200, 'Amenity updated successfully')
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def put(self, amenity_id):
        """
        Update an amenity as an admin.

        Only admins can update amenities. This method validates admin rights, input data, and updates an amenity if it exists.

        Returns:
            dict: Updated amenity data or error message.
        """
        # Récupération de l'utilisateur actuel et vérification des droits admin
        current_user = get_jwt_identity()
        claims = get_jwt()
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        # Récupération des données envoyées dans la requête
        amenity_api = api.payload

        try:
            # Mise à jour de la commodité via la façade
            amenity_data = facade.update_amenity(amenity_id, amenity_api)

            if not amenity_data:
                # Retourne une erreur si la commodité n'a pas été trouvée
                return {'error': 'Amenity not found'}, 404

            # Retourne la commodité mise à jour
            return {
                'id': amenity_data.id,
                'name': amenity_data.name
            }, 200

        except ValueError as e:
            # Gestion d'erreur si les données sont invalides
            return {'error': str(e)}, 400

        except Exception as e:
            # Gestion générique d'exception serveur : erreur 500
            return {'error': 'Internal server error'}, 500
