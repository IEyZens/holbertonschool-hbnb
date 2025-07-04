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
    @api.expect(amenity_model)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        amenity_data = api.payload

        try:
            new_amenity = facade.create_amenity(amenity_data)
            return {
                'id': new_amenity.id,
                'name': new_amenity.name
            }, 201

        except ValueError as e:
            return {'error': str(e)}, 400


@api.route('/amenities/<amenity_id>')
class AdminAmenityModify(Resource):
    @api.expect(amenity_model)
    @api.response(200, 'Amenity updated successfully')
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def put(self, amenity_id):
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
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
