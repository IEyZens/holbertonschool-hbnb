from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.services import facade

api = Namespace('auth', description='Authentication operations')

# Model for input validation
login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})


@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        login_data = api.payload
        user = facade.get_user_by_email(login_data['email'])
        if user and user.verify_password(login_data['password']):
            access_token = create_access_token(
                identity={'id': user.id, 'is_admin': user.is_admin})
            return {
                'access_token': access_token,
                'token_type': 'Bearer',
            }, 200
        return {'message': 'Invalid credentials'}, 401


@api.route('/protected')
class ProtectedResource(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        return {'message': f'Hello, user {current_user["id"]}'}, 200
