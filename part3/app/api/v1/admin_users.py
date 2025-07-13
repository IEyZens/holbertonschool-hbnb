# Import necessary modules for admin user management functionality
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

# Create RESTx namespace for admin user operations
api = Namespace('admin', description='Admin operations')

# Define user model for validation and Swagger documentation
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True, description='Password of the user'),
    'is_admin': fields.Boolean(required=True, description='Admin status')
})

# Define user update model with optional fields
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

    This class provides endpoints for administrators to manage individual users including
    retrieving, updating, and deleting user accounts. All operations require admin privileges
    and proper authentication.
    
    Attributes:
        None
        
    Methods:
        get(user_id): Retrieve specific user by ID (admin only)
        put(user_id): Update specific user (admin only)
        delete(user_id): Delete specific user (admin only)
    """
    
    @api.response(200, 'User retrieved successfully')
    @api.response(404, 'User not found')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def get(self, user_id):
        """
        Retrieve a user by their ID. Only admins can view users.

        This endpoint allows administrators to retrieve detailed information about any user
        in the system using their unique identifier. User passwords are excluded from the response.
        
        Args:
            user_id (str): The UUID of the user to retrieve
            
        Headers Required:
            Authorization: Bearer <jwt_token> (with admin privileges)
            
        Returns:
            dict: User data without password (200),
                  or error message for access denied (403),
                  or user not found (404)
                  
        Example Success Response:
            {
                "id": "12345",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "is_admin": false
            }
            
        Example Error Response:
            {
                "error": "Admin privileges required"
            }
        """
        # Check admin privileges from JWT token claims
        claims = get_jwt()
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        try:
            # Retrieve user from facade using provided ID
            user = facade.get_user(user_id)
            
        except (ValueError, KeyError):
            # Handle case where user doesn't exist
            return {'error': 'User not found'}, 404

        # Return user data excluding password for security
        return {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_admin': user.is_admin
        }, 200

    @api.expect(user_update_model)
    @api.response(200, 'User updated successfully')
    @api.response(404, 'User not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def put(self, user_id):
        """
        Update a user by their ID. Only admins can update users.

        This endpoint allows administrators to modify user information including personal details,
        email address, password, and admin status. Email uniqueness is enforced across the system.
        
        Args:
            user_id (str): The UUID of the user to update
            
        Expected Input:
            - first_name (str, optional): Updated first name
            - last_name (str, optional): Updated last name
            - email (str, optional): Updated email address
            - password (str, optional): Updated password
            - is_admin (bool, optional): Updated admin status
            
        Headers Required:
            Authorization: Bearer <jwt_token> (with admin privileges)
            
        Returns:
            dict: Updated user data without password (200),
                  or error message for invalid input (400),
                  or access denied (403),
                  or user not found (404),
                  or internal server error (500)
                  
        Example Success Response:
            {
                "id": "12345",
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith@example.com",
                "is_admin": true
            }
            
        Example Error Response:
            {
                "error": "Email is already in use"
            }
        """
        # Get current user identity and claims from JWT token
        current_user = get_jwt_identity()
        claims = get_jwt()
        
        # Extract user data from request payload
        user_api = api.payload

        # Check admin privileges
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        # Validate email uniqueness if email is being updated
        email = user_api.get('email')
        if email:
            # Clean and normalize email address
            email = email.strip().lower()
            
            # Check if email is already in use by another user
            existing_user = facade.get_user_by_email(email)
            if existing_user and str(existing_user.id) != user_id:
                return {'error': 'Email is already in use'}, 400

        try:
            # Verify user exists before attempting update
            user = facade.get_user(user_id)
            
        except (ValueError, KeyError):
            # Handle case where user doesn't exist
            return {'error': 'User not found'}, 404

        try:
            # Attempt to update user with new data through facade
            user_data = facade.update_user(user_id, user_api)

            # Return updated user data excluding password
            return {
                'id': user_data.id,
                'first_name': user_data.first_name,
                'last_name': user_data.last_name,
                'email': user_data.email,
                'is_admin': user_data.is_admin
            }, 200

        except ValueError as e:
            # Handle business validation errors with specific error message
            return {'error': str(e)}, 400

        except Exception as e:
            # Handle unexpected errors with generic error message
            return {'error': 'Internal server error'}, 500

    @api.response(204, 'User deleted successfully')
    @api.response(404, 'User not found')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def delete(self, user_id):
        """
        Delete a user by their ID. Only admins can delete users.

        This endpoint allows administrators to permanently remove a user from the system.
        All associated data may be affected depending on business rules implemented in the facade.
        
        Args:
            user_id (str): The UUID of the user to delete
            
        Headers Required:
            Authorization: Bearer <jwt_token> (with admin privileges)
            
        Returns:
            Empty response (204) on success,
            or error message for access denied (403),
            or user not found (404),
            or internal server error (500)
            
        Example Error Response:
            {
                "error": "User not found"
            }
        """
        # Check admin privileges from JWT token claims
        claims = get_jwt()
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        try:
            # Verify user exists before attempting deletion
            user = facade.get_user(user_id)
            
        except (ValueError, KeyError):
            # Handle case where user doesn't exist
            return {'error': 'User not found'}, 404

        try:
            # Attempt to delete user through facade
            facade.delete_user(user_id)
            
            # Return empty response with 204 status on successful deletion
            return '', 204
            
        except (ValueError, KeyError):
            # Handle case where user doesn't exist during deletion
            return {'error': 'User not found'}, 404
            
        except Exception:
            # Handle unexpected errors during deletion
            return {'error': 'Internal server error'}, 500


@api.route('/users/')
class AdminUserCreate(Resource):
    """
    Resource for admin user creation.

    This class provides endpoints for administrators to create new user accounts with
    full control over user attributes including admin status. Email uniqueness is enforced.
    
    Attributes:
        None
        
    Methods:
        post(): Create new user account (admin only)
    """
    
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Invalid input or email already registered')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def post(self):
        """
        Create a new user. Only admins can create users.

        This endpoint allows administrators to create new user accounts with complete control
        over all user attributes. Email addresses must be unique across the system.
        
        Expected Input:
            - first_name (str): First name of the user
            - last_name (str): Last name of the user
            - email (str): Email address of the user
            - password (str): Password for the user account
            - is_admin (bool): Whether the user should have admin privileges
            
        Headers Required:
            Authorization: Bearer <jwt_token> (with admin privileges)
            
        Returns:
            dict: Created user data without password (201),
                  or error message for invalid input (400),
                  or access denied (403),
                  or internal server error (500)
                  
        Example Success Response:
            {
                "id": "12345",
                "first_name": "Alice",
                "last_name": "Johnson",
                "email": "alice.johnson@example.com",
                "is_admin": false
            }
            
        Example Error Response:
            {
                "error": "Email already registered"
            }
        """
        # Get current user identity and claims from JWT token
        current_user = get_jwt_identity()
        claims = get_jwt()
        
        # Check admin privileges
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        try:
            # Extract user data from request payload
            user_data = api.payload
            
            # Clean and validate email address
            email = user_data.get('email')
            if email:
                email = email.strip().lower()
                
            # Check if email is already registered
            if facade.get_user_by_email(email):
                return {'error': 'Email already registered'}, 400

            # Create new user through facade with validation
            new_user = facade.create_user(user_data)
            
            # Return created user data excluding password for security
            return {
                'id': new_user.id,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'email': new_user.email,
                'is_admin': new_user.is_admin
            }, 201

        except ValueError as e:
            # Handle business validation errors with specific error message
            return {'error': str(e)}, 400

        except Exception as e:
            # Handle unexpected errors with generic error message
            return {'error': 'Internal server error'}, 500
