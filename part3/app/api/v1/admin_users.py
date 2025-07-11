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
    """
    Resource for admin operations on a specific user.

    Allows an admin to update a user’s data.
    """
    @api.expect(user_update_model)
    @api.response(200, 'User updated successfully')
    @api.response(404, 'User not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def put(self, user_id):
        """
        Update a user by their ID. Only admins can update users.

        Args:
            user_id (str): The UUID of the user to update.

        Returns:
            dict: Updated user data or error details.
        """
        current_user = get_jwt_identity()
        claims = get_jwt()
        user_api = api.payload

        # Vérifie si l'utilisateur courant est admin
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        email = user_api.get('email')

        # Vérifie si l'email est déjà utilisé par un autre utilisateur
        if email:
            existing_user = facade.get_user_by_email(email)
            if existing_user and str(existing_user.id) != user_id:
                return {'error': 'Email is already in use'}, 400

        # Récupère l'utilisateur à mettre à jour
        user = facade.get_user(user_id)

        if not user:
            return {'error': 'User not found'}, 404

        try:
            # Tente de mettre à jour l'utilisateur avec les nouvelles données
            user_data = facade.update_user(user_id, user_api)

            return {
                'id': user_data.id,
                'first_name': user_data.first_name,
                'last_name': user_data.last_name,
                'email': user_data.email,
                'is_admin': user_data.is_admin
            }, 200

        except ValueError as e:
            # Retourne une erreur métier si les données sont invalides
            return {'error': str(e)}, 400

        except Exception as e:
            # Gestion générique d'exception serveur : erreur 500
            return {'error': 'Internal server error'}, 500


@api.route('/users/')
class AdminUserCreate(Resource):
    """
    Resource for admin user creation.

    Allows an admin to create a new user.
    """
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Invalid input or email already registered')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def post(self):
        """
        Create a new user. Only admins can create users.

        Returns:
            dict: Newly created user data or error details.
        """
        current_user = get_jwt_identity()
        claims = get_jwt()
        # Vérifie si l'utilisateur courant est admin
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        try:
            user_data = api.payload
            email = user_data.get('email')

            # Vérifie si l'email est déjà enregistré
            if facade.get_user_by_email(email):
                return {'error': 'Email already registered'}, 400

            # Crée le nouvel utilisateur
            new_user = facade.create_user(user_data)
            return {
                'id': new_user.id,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'email': new_user.email,
                'is_admin': new_user.is_admin
            }, 201

        except ValueError as e:
            # Retourne une erreur métier si les données sont invalides
            return {'error': str(e)}, 400

        except Exception as e:
            # Gestion générique d'exception serveur : erreur 500
            return {'error': 'Internal server error'}, 500
