# Importation des modules nécessaires
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade


# Création du namespace RESTx pour les opérations utilisateur
api = Namespace('users', description='User operations')


# Définition du modèle utilisateur utilisé pour la validation et la documentation Swagger
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True, description='Password of the user'),
    'is_admin': fields.Boolean(description='Admin status')
})

# Définition du modèle utilisateur utilisé pour la mise à jour
user_update_model = api.model('User', {
    'first_name': fields.String(required=False, description='First name of the user'),
    'last_name': fields.String(required=False, description='Last name of the user'),
    'email': fields.String(required=False, description='Email of the user'),
    'password': fields.String(required=False, description='Password of the user')
})


@api.route('/')
class UserList(Resource):
    @api.expect(user_model)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Invalid input or email already registered')
    def post(self):
        user_data = api.payload
        email = user_data.get('email')
        if facade.get_user_by_email(email):
            return {'error': 'Email already registered'}, 400
        new_user = facade.create_user(user_data)
        return {
            'id': new_user.id,
            'first_name': new_user.first_name,
            'last_name': new_user.last_name,
            'email': new_user.email
        }, 201

    @api.response(200, 'List of users retrieved successfully')
    def get(self):
        users = facade.get_all_users()
        return [{
            'id': u.id,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'email': u.email
        } for u in users], 200


@api.route('/<user_id>')
class UserResource(Resource):
    @api.response(200, 'User retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        }, 200

    @api.expect(user_update_model)
    @api.response(200, 'User updated successfully')
    @api.response(404, 'User not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def put(self, user_id):
        """
        Update an existing user's information. Users can only modify their own data.
        """
        current_user = get_jwt_identity()
        if current_user != user_id:
            return {'error': 'Unauthorized action'}, 403

        user_api = api.payload

        if 'email' in user_api or 'password' in user_api:
            return {'error': 'You cannot modify email or password'}, 400

        try:
            updated_user = facade.update_user(user_id, user_api)

            return {
                'id': updated_user.id,
                'first_name': updated_user.first_name,
                'last_name': updated_user.last_name,
                'email': updated_user.email,
                'is_admin': updated_user.is_admin
            }, 200

        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception:
            return {'error': 'Internal server error'}, 500

    @api.response(204, 'User deleted successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'User not found')
    @jwt_required()
    def delete(self, user_id):
        """
        Delete a user by ID. Only the user or an admin can delete the account.
        """
        current_user = get_jwt_identity()
        jwt_data = get_jwt()

        if current_user != user_id and not jwt_data.get("is_admin", False):
            return {'error': 'Unauthorized action'}, 403

        try:
            facade.delete_user(user_id)
            return '', 204
        except ValueError:
            return {'error': 'User not found'}, 404
        except Exception:
            return {'error': 'Internal server error'}, 500
