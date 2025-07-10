# Importation des modules nécessaires
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from app.services import facade

# Création du namespace pour les opérations d'authentification
api = Namespace('auth', description='Authentication operations')

# Modèle pour la validation des entrées lors de la connexion
login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})


@api.route('/login')
class Login(Resource):
    """
    Resource for user authentication (login).

    This endpoint validates user credentials and returns a JWT access token if authentication is successful.
    """
    @api.expect(login_model)
    def post(self):
        """
        Authenticate a user and return a JWT access token.

        Returns:
            dict: Access token and token type if credentials are valid, else error message.
        """
        # Récupération des données de connexion envoyées par l'utilisateur
        login_data = api.payload
        # Recherche de l'utilisateur correspondant à l'email
        user = facade.get_user_by_email(login_data['email'])
        # Vérification du mot de passe
        if user and user.verify_password(login_data['password']):
            # Création du token JWT en cas d'authentification réussie
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={'is_admin': user.is_admin})
            return {
                'access_token': access_token,
                'token_type': 'Bearer',
            }, 200
        # Retourne une erreur si les identifiants sont invalides
        return {'message': 'Invalid credentials'}, 401


@api.route('/protected')
class ProtectedResource(Resource):
    """
    Resource for a protected endpoint requiring authentication.
    """
    @jwt_required()
    def get(self):
        """
        Return a greeting message for the authenticated user.
        """
        # Récupération de l'identité de l'utilisateur courant à partir du JWT
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        return {
            'message': f'Hello, user {current_user_id}',
            'is_admin': is_admin
        }, 200
