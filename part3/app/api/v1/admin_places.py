# Import necessary modules for admin place management functionality
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

# Create namespace for admin place operations
api = Namespace('admin', description='Admin operations')

# Define amenity model used within places
amenity_model = api.model('PlaceAmenity', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity')
})

# Define user model linked to places
user_model = api.model('PlaceUser', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='First name of the owner'),
    'last_name': fields.String(description='Last name of the owner'),
    'email': fields.String(description='Email of the owner')
})

# Define review model associated with places
review_model = api.model('PlaceReview', {
    'id': fields.String(description='Review ID'),
    'text': fields.String(description='Text of the review'),
    'rating': fields.Integer(description='Rating of the place (1-5)'),
    'user_id': fields.String(description='ID of the user')
})

# Define main model representing a place
place_model = api.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'owner_id': fields.String(required=True, description='ID of the owner'),
    'max_person': fields.Integer(required=True, description='Maximum number of persons allowed'),
    'owner': fields.Nested(user_model, description='Owner of the place'),
    'amenities': fields.List(fields.Nested(amenity_model), description='List of amenities'),
})

# Define place update model with optional fields
place_update_model = api.model('Place', {
    'title': fields.String(required=False, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=False, description='Price per night'),
    'latitude': fields.Float(required=False, description='Latitude of the place'),
    'longitude': fields.Float(required=False, description='Longitude of the place'),
    'max_person': fields.Integer(required=False, description='Maximum number of persons allowed'),
    'amenities': fields.List(fields.Nested(amenity_model), description='List of amenities'),
})


@api.route('/places/<place_id>')
class AdminPlaceModify(Resource):
    """
    Resource for admin operations on a specific place.

    This class provides endpoints for administrators and place owners to manage individual places
    including retrieving, updating, and deleting place listings. Access control ensures only
    admins or the place owner can modify place data.

    Attributes:
        None

    Methods:
        get(place_id): Retrieve specific place by ID (admin or owner)
        put(place_id): Update specific place (admin or owner)
        delete(place_id): Delete specific place (admin or owner)
    """

    @api.response(200, 'Place retrieved successfully')
    @api.response(404, 'Place not found')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def get(self, place_id):
        """
        Retrieve a place by its ID. Only admins or the owner can view.

        This endpoint allows authorized users (admins or place owners) to retrieve detailed
        information about a specific place including owner details and amenities.

        Args:
            place_id (str): The UUID of the place to retrieve

        Headers Required:
            Authorization: Bearer <jwt_token>

        Returns:
            dict: Complete place data including owner and amenities (200),
                  or error message for unauthorized access (403),
                  or place not found (404)

        Example Success Response:
            {
                "id": "12345",
                "title": "Cozy Apartment",
                "description": "Beautiful downtown apartment",
                "price": 120.0,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "owner_id": "67890",
                "max_person": 4,
                "owner": {
                    "id": "67890",
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com"
                },
                "amenities": [
                    {"id": "1", "name": "WiFi"},
                    {"id": "2", "name": "Pool"}
                ]
            }

        Example Error Response:
            {
                "error": "Unauthorized action"
            }
        """
        # Get current user identity and claims from JWT token
        current_user = get_jwt_identity()
        claims = get_jwt()

        # Extract admin status and user ID for authorization
        is_admin = claims.get('is_admin', False)
        user_id = current_user

        try:
            # Retrieve place from facade using provided ID
            place = facade.get_place(place_id)

        except (ValueError, KeyError):
            # Handle case where place doesn't exist
            return {'error': 'Place not found'}, 404

        # Check authorization: only admin or place owner can access
        if not is_admin and place.owner.id != user_id:
            return {'error': 'Unauthorized action'}, 403

        # Return complete place data including nested owner and amenities
        return {
            'id': place.id,
            'title': place.title,
            'description': place.description,
            'price': place.price,
            'latitude': place.latitude,
            'longitude': place.longitude,
            'owner_id': place.owner.id,
            'max_person': place.max_person,
            'owner': {
                'id': place.owner.id,
                'first_name': place.owner.first_name,
                'last_name': place.owner.last_name,
                'email': place.owner.email
            },
            'amenities': [
                {'id': a.id, 'name': a.name} for a in place.amenities
            ]
        }, 200

    @api.expect(place_update_model)
    @api.response(200, 'Place updated successfully')
    @api.response(404, 'Place not found')
    @api.response(403, 'Unauthorized action')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def put(self, place_id):
        """
        Update a place by its ID. Only admins or the owner can update.

        This endpoint allows authorized users to modify place information including
        details, pricing, location, and amenities. All fields are optional for partial updates.

        Args:
            place_id (str): The UUID of the place to update

        Expected Input:
            - title (str, optional): Updated title of the place
            - description (str, optional): Updated description
            - price (float, optional): Updated price per night
            - latitude (float, optional): Updated latitude coordinate
            - longitude (float, optional): Updated longitude coordinate
            - max_person (int, optional): Updated maximum occupancy
            - amenities (list, optional): Updated list of amenities

        Headers Required:
            Authorization: Bearer <jwt_token>

        Returns:
            dict: Updated place data (200),
                  or error message for invalid input (400),
                  or unauthorized access (403),
                  or place not found (404),
                  or internal server error (500)

        Example Success Response:
            {
                "id": "12345",
                "title": "Luxury Apartment",
                "description": "Renovated downtown apartment",
                "price": 150.0,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "owner_id": "67890",
                "max_person": 6,
                "amenities": ["WiFi", "Pool", "Gym"]
            }

        Example Error Response:
            {
                "error": "Invalid input data"
            }
        """
        # Get current user identity and claims from JWT token
        current_user = get_jwt_identity()
        claims = get_jwt()

        # Extract admin status and user ID for authorization
        is_admin = claims.get('is_admin', False)
        user_id = current_user

        try:
            # Verify place exists before attempting update
            place = facade.get_place(place_id)

        except (ValueError, KeyError):
            # Handle case where place doesn't exist
            return {'error': 'Place not found'}, 404

        # Check authorization: only admin or place owner can update
        if not is_admin and place.owner.id != user_id:
            return {'error': 'Unauthorized action'}, 403

        # Extract place data from request payload
        place_api = api.payload

        try:
            # Attempt to update place with new data through facade
            place_data = facade.update_place(place_id, place_api)

            # Return updated place data with amenity names
            return {
                'id': place_data.id,
                'title': place_data.title,
                'description': place_data.description,
                'price': place_data.price,
                'latitude': place_data.latitude,
                'longitude': place_data.longitude,
                'owner_id': place_data.owner.id,
                'max_person': place_data.max_person,
                'amenities': [amenity.name for amenity in place_data.amenities]
            }, 200

        except ValueError as e:
            # Handle business validation errors with specific error message
            return {'error': str(e)}, 400

        except Exception as e:
            # Handle unexpected errors with detailed error information
            return {'error': 'Internal server error', 'details': str(e)}, 500

    @api.response(204, 'Place deleted successfully')
    @api.response(404, 'Place not found')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def delete(self, place_id):
        """
        Delete a place by its ID. Only admins or the owner can delete.

        This endpoint allows authorized users to permanently remove a place listing from the system.
        All associated data (reviews, bookings) may be affected depending on business rules.

        Args:
            place_id (str): The UUID of the place to delete

        Headers Required:
            Authorization: Bearer <jwt_token>

        Returns:
            Empty response (204) on success,
            or error message for unauthorized access (403),
            or place not found (404),
            or internal server error (500)

        Example Error Response:
            {
                "error": "Place not found"
            }
        """
        # Get current user identity and claims from JWT token
        current_user = get_jwt_identity()
        claims = get_jwt()

        # Extract admin status and user ID for authorization
        is_admin = claims.get('is_admin', False)
        user_id = current_user

        try:
            # Verify place exists before attempting deletion
            place = facade.get_place(place_id)

        except (ValueError, KeyError):
            # Handle case where place doesn't exist
            return {'error': 'Place not found'}, 404

        # Check authorization: only admin or place owner can delete
        if not is_admin and place.owner.id != user_id:
            return {'error': 'Unauthorized action'}, 403

        try:
            # Attempt to delete place through facade
            facade.delete_place(place_id)

            # Return empty response with 204 status on successful deletion
            return '', 204

        except Exception:
            # Handle unexpected errors during deletion
            return {'error': 'Internal server error'}, 500
