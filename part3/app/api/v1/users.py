from flask_restx import Namespace, Resource, fields
from app.services import facade

# Création du namespace RESTx pour les opérations utilisateur
api = Namespace('users', description='User operations')

# Définition du modèle utilisateur utilisé pour la validation et la documentation Swagger
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True, description='Password of the user')
})


@api.route('/')
class UserList(Resource):
    """
    Resource for collection-level user entity operations.

    This endpoint handles user registration and listing. On creation,
    it enforces email uniqueness and input schema validation.
    """

    # Indique que la requête doit respecter le modèle user_model et être validée
    @api.expect(user_model, validate=True)
    # Réponse 201 si l'utilisateur est créé avec succès
    @api.response(201, 'User successfully created')
    # Réponse 400 si l’email est déjà utilisé
    @api.response(400, 'Email already registered')
    # Réponse 400 si les données sont invalides
    @api.response(400, 'Invalid input data')
    def post(self):
        """
        Register a new user.

        Validates input fields and ensures the email is not already in use.
        Creates a new User entity through the business layer and returns
        the resulting resource representation.

        Returns:
            dict: Created user data with HTTP 201, or error with HTTP 400.
        """
        # Récupération des données utilisateur issues du corps de la requête
        user_data = api.payload

        # Vérifie si un utilisateur existe déjà avec le même email
        existing_user = facade.get_user_by_email(user_data['email'])
        if existing_user:
            # Retourne une erreur si l'email est déjà enregistré
            return {'error': 'Email already registered'}, 400

        # Création d’un nouvel utilisateur via la couche de service
        new_user = facade.create_user(user_data)
        # Retourne les informations de l’utilisateur créé
        return {
            'id': new_user.id,
            'first_name': new_user.first_name,
            'last_name': new_user.last_name,
            'email': new_user.email
        }, 201

    @api.response(200, 'List of users retrieved successfully')
    def get(self):
        """
        Retrieve all users.

        Returns:
            tuple: A list of user dictionaries and an HTTP 200 status code.
        """
        # Récupère tous les utilisateurs via la façade
        users = facade.get_all_users()
        # Construit et retourne la liste des utilisateurs avec leurs champs publics
        return [
            {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            }
            for user in users
        ], 200


@api.route('/<user_id>')
class UserResource(Resource):
    """
    Resource for individual user entity operations.

    This route allows retrieval of a specific user profile by ID.
    """

    # Réponse 200 si les informations de l'utilisateur sont récupérées
    @api.response(200, 'User details retrieved successfully')
    # Réponse 404 si l'utilisateur n'existe pas
    @api.response(404, 'User not found')
    def get(self, user_id):
        """
        Retrieve user data by unique identifier.

        Args:
            user_id (str): UUID of the user entity.

        Returns:
            dict: User information with HTTP 200, or error with HTTP 404.
        """
        # Récupération de l'utilisateur via la façade en fonction de son ID
        user = facade.get_user(user_id)
        if not user:
            # Retourne une erreur 404 si l'utilisateur n'est pas trouvé
            return {'error': 'User not found'}, 404
        # Retourne les informations de l'utilisateur trouvé
        return {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        }, 200

    @api.expect(user_model)
    @api.response(200, 'User updated successfully')
    @api.response(404, 'User not found')
    @api.response(400, 'Invalid input data')
    def put(self, user_id):
        """
        Update an existing user's information.

        Args:
            user_id (str): The ID of the user to update.

        Returns:
            dict: Updated user data if successful.
            tuple: Error message and HTTP status code if failed.
        """
        # Récupération des données envoyées dans la requête
        user_api = api.payload

        try:
            # Mise à jour de l'utilisateur via la façade
            user_data = facade.update_user(user_id, user_api)

            # Retourne les informations de l'utilisateur mis à jour
            return {
                'id': user_data.id,
                'first_name': user_data.first_name,
                'last_name': user_data.last_name,
                'email': user_data.email
            }, 200

        except ValueError as e:
            # Gestion d'une erreur si l'utilisateur n'existe pas ou si l'entrée est invalide
            return {'error': str(e)}, 400
