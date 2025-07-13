# Import necessary modules for authentication functionality
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from app.services import facade

# Create namespace for authentication operations
api = Namespace('auth', description='Authentication operations')

# Model for validating login input data
login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})


@api.route('/login')
class Login(Resource):
    """
    Resource for user authentication (login).

    This endpoint validates user credentials and returns a JWT access token if authentication is successful.
    It handles the login process by verifying email and password, then generating a JWT token for authenticated users.
    
    Attributes:
        None
        
    Methods:
        post(): Authenticate user credentials and return JWT token
    """
    
    @api.expect(login_model)
    def post(self):
        """
        Authenticate a user and return a JWT access token.

        This method processes login requests by validating the provided email and password.
        If credentials are valid, it generates a JWT access token with user identity and admin status.
        
        Expected Input:
            - email (str): User's email address
            - password (str): User's password
            
        Returns:
            dict: Success response with access token and token type (200), 
                  or error message for invalid credentials (401),
                  or internal server error (500)
                  
        Example Success Response:
            {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "Bearer"
            }
            
        Example Error Response:
            {
                "message": "Invalid credentials"
            }
        """
        try:
            # Extract login data from the request payload
            login_data = api.payload
            
            # Search for user with the provided email address
            user = facade.get_user_by_email(login_data['email'])
            
            # Verify password if user exists
            if user and user.verify_password(login_data['password']):
                # Create JWT access token with user identity and admin status
                access_token = create_access_token(
                    identity=str(user.id),
                    additional_claims={'is_admin': user.is_admin})
                
                # Return successful authentication response
                return {
                    'access_token': access_token,
                    'token_type': 'Bearer',
                }, 200
            
            # Return error if credentials are invalid
            return {'message': 'Invalid credentials'}, 401
            
        except Exception as e:
            # Handle any unexpected errors during authentication
            return {'error': 'Internal server error'}, 500


@api.route('/protected')
class ProtectedResource(Resource):
    """
    Resource for a protected endpoint requiring authentication.

    This endpoint demonstrates JWT token validation and provides access to authenticated users only.
    It extracts user information from the JWT token and returns personalized data.
    
    Attributes:
        None
        
    Methods:
        get(): Return greeting message for authenticated user with admin status
    """
    
    @jwt_required()
    def get(self):
        """
        Return a greeting message for the authenticated user.

        This method requires a valid JWT token in the Authorization header.
        It extracts the user identity and admin status from the token claims.
        
        Headers Required:
            Authorization: Bearer <jwt_token>
            
        Returns:
            dict: Greeting message with user ID and admin status (200)
                  
        Example Response:
            {
                "message": "Hello, user 123",
                "is_admin": true
            }
            
        Raises:
            401: If JWT token is missing, invalid, or expired
        """
        # Extract current user ID from JWT token identity
        current_user_id = get_jwt_identity()
        
        # Get additional claims from JWT token
        claims = get_jwt()
        
        # Extract admin status from token claims (default to False if not present)
        is_admin = claims.get('is_admin', False)
        
        # Return personalized greeting with user info
        return {
            'message': f'Hello, user {current_user_id}',
            'is_admin': is_admin
        }, 200
