# Import necessary modules for Flask API functionality
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade


# Create a namespace for user-related operations in the API
api = Namespace('users', description='User operations')


# Define main user model for creation requests and complete user data
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True, description='Password of the user'),
    'is_admin': fields.Boolean(description='Admin status')
})

# Define user update model for partial updates (all fields optional)
user_update_model = api.model('UserUpdate', {
    'first_name': fields.String(required=False, description='First name of the user'),
    'last_name': fields.String(required=False, description='Last name of the user'),
    'email': fields.String(required=False, description='Email of the user'),
    'password': fields.String(required=False, description='Password of the user')
})


@api.route('/')
class UserList(Resource):
    """
    REST API Resource for handling collection-level operations on User entities.

    This class provides endpoints for:
    - Creating new users (POST)
    - Retrieving all users (GET)

    User creation includes email validation and duplicate checking.
    User listing excludes sensitive information like passwords.
    """

    @api.expect(user_model)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Invalid input or email already registered')
    def post(self):
        """
        Create a new user account.

        This endpoint creates a new user with the provided information.
        It validates that the email is not already registered in the system
        and ensures all required fields are provided.

        Returns:
            dict: Created user data (excluding password) with status 201,
                  or error message with status 400
        """
        # Extract user data from request payload
        user_data = api.payload

        # Get email from user data for duplicate validation
        email = user_data.get('email')

        # Check if email is already registered in the system
        if facade.get_user_by_email(email):
            return {'error': 'Email already registered'}, 400

        # Create new user using facade layer
        new_user = facade.create_user(user_data)

        # Return user data excluding sensitive information (password)
        return {
            'id': new_user.id,
            'first_name': new_user.first_name,
            'last_name': new_user.last_name,
            'email': new_user.email
        }, 201

    @api.response(200, 'List of users retrieved successfully')
    def get(self):
        """
        Retrieve all users from the database.

        Returns a list of all registered users with their basic information.
        Sensitive information like passwords and admin status are excluded
        from the response for security purposes.

        Returns:
            list: List of user dictionaries with basic information
        """
        # Retrieve all users from database via facade
        users = facade.get_all_users()

        # Build response list excluding sensitive information
        return [{
            'id': u.id,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'email': u.email
        } for u in users], 200


@api.route('/<user_id>')
class UserResource(Resource):
    """
    REST API Resource for handling individual User entity operations.

    This class provides endpoints for:
    - Retrieving a specific user (GET)
    - Updating user information (PUT)
    - Deleting a user account (DELETE)

    All modification operations include proper authentication and authorization
    checks to ensure users can only modify their own data (unless admin).
    """

    @api.response(200, 'User retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """
        Retrieve a specific user by their ID.

        Returns basic user information excluding sensitive data like passwords.
        This endpoint is publicly accessible for displaying user profiles.

        Args:
            user_id (str): Unique identifier of the user

        Returns:
            dict: User data or error message with appropriate status
        """
        # Retrieve user from database using facade
        user = facade.get_user(user_id)

        # Check if user exists
        if not user:
            return {'error': 'User not found'}, 404

        # Return user data excluding sensitive information
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
        Update an existing user's information.

        Users can only modify their own profile data. Email and password
        modifications are restricted for security reasons and must be handled
        through separate dedicated endpoints.

        Args:
            user_id (str): Unique identifier of the user to update

        Returns:
            dict: Updated user data or error message with appropriate status
        """
        # Extract current user ID from JWT token
        current_user = get_jwt_identity()

        # Verify user is authorized to modify this account
        if current_user != user_id:
            return {'error': 'Unauthorized action'}, 403

        # Extract update data from request payload
        user_api = api.payload

        # Prevent modification of sensitive fields (email and password)
        if 'email' in user_api or 'password' in user_api:
            return {'error': 'You cannot modify email or password'}, 400

        try:
            # Update user information using facade layer
            updated_user = facade.update_user(user_id, user_api)

            # Return updated user data including admin status
            return {
                'id': updated_user.id,
                'first_name': updated_user.first_name,
                'last_name': updated_user.last_name,
                'email': updated_user.email,
                'is_admin': updated_user.is_admin
            }, 200

        except ValueError as e:
            # Handle business logic validation errors
            return {'error': str(e)}, 400
        except Exception:
            # Handle unexpected errors without exposing internal details
            return {'error': 'Internal server error'}, 500

    @api.response(204, 'User deleted successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'User not found')
    @jwt_required()
    def delete(self, user_id):
        """
        Delete a user account.

        Users can delete their own account, and admin users can delete any account.
        This operation is irreversible and will remove all associated data.

        Args:
            user_id (str): Unique identifier of the user to delete

        Returns:
            Empty response with status 204 on success, or error message
        """
        # Extract current user information from JWT
        current_user = get_jwt_identity()
        jwt_data = get_jwt()

        # Check authorization: user can delete own account or admin can delete any
        if current_user != user_id and not jwt_data.get("is_admin", False):
            return {'error': 'Unauthorized action'}, 403

        try:
            # Delete user account using facade layer
            facade.delete_user(user_id)

            # Return empty response with success status
            return '', 204

        except ValueError:
            # Handle case where user doesn't exist
            return {'error': 'User not found'}, 404
        except Exception:
            # Handle unexpected errors
            return {'error': 'Internal server error'}, 500
