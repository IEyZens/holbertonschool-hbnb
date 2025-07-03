from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

# Création du namespace RESTx pour les opérations utilisateur
api = Namespace('admin', description='Admin operations')

# Définition du modèle utilisateur utilisé pour la validation et la documentation Swagger
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True, description='Password of the user'),
    'is_admin': fields.Boolean(required=True, description='Admin status')
})

user_update_model = api.model('User', {
    'first_name': fields.String(required=False, description='First name of the user'),
    'last_name': fields.String(required=False, description='Last name of the user'),
    'email': fields.String(required=False, description='Email of the user'),
    'password': fields.String(required=False, description='Password of the user'),
    'is_admin': fields.Boolean(required=False, description='Admin status')
})

@api.route('/users/<user_id>')
class AdminUserResource(Resource):
    @api.expect(user_update_model)
    @api.response(200, 'User updated successfully')
    @api.response(404, 'User not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def put(self, user_id):
        current_user = get_jwt_identity()
        user_api = api.payload

        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        email = user_api.get('email')

        if email:
            existing_user = facade.get_user_by_email(email)
            if existing_user and str(existing_user.id) != user_id:
                return {'error': 'Email is already in use'}, 400

        user = facade.get_user(user_id)

        if not user:
            return {'error': 'User not found'}, 404

        try:
            user_data = facade.update_user(user_id, user_api)

            return {
                'id': user_data.id,
                'first_name': user_data.first_name,
                'last_name': user_data.last_name,
                'email': user_data.email,
                'is_admin': user_data.is_admin
            }, 200

        except ValueError as e:
            return {'error': str(e)}, 400


@api.route('/users/')
class AdminUserCreate(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Invalid input or email already registered')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        user_data = api.payload
        email = user_data.get('email')

        if facade.get_user_by_email(email):
            return {'error': 'Email already registered'}, 400

        new_user = facade.create_user(user_data)
        return {
            'id': new_user.id,
            'first_name': new_user.first_name,
            'last_name': new_user.last_name,
            'email': new_user.email,
            'is_admin': new_user.is_admin
        }, 201


@api.route('/users/<user_id>')
class AdminUserModify(Resource):
    @api.expect(user_update_model)
    @api.response(200, 'User updated successfully')
    @api.response(404, 'User not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def put(self, user_id):
        current_user = get_jwt_identity()
        user_api = api.payload
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        email = user_api.get('email')

        if email:
            existing_user = facade.get_user_by_email(email)
            if existing_user and str(existing_user.id) != user_id:
                return {'error': 'Email already in use'}, 400

        user = facade.get_user(user_id)

        if not user:
            return {'error': 'User not found'}, 404

        try:
            user_data = facade.update_user(user_id, user_api)

            return {
                'id': user_data.id,
                'first_name': user_data.first_name,
                'last_name': user_data.last_name,
                'email': user_data.email,
                'is_admin': user_data.is_admin
            }, 200

        except ValueError as e:
            return {'error': str(e)}, 400
