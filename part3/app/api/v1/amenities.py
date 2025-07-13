# Import necessary modules for amenity management functionality
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

# Create Flask-RESTx namespace for amenity operations
api = Namespace('amenities', description='Amenity operations')

# Define data model for input validation and Swagger documentation
amenity_model = api.model('Amenity', {
    # Required field: amenity name
    'name': fields.String(required=True, description='Name of the amenity')
})


@api.route('/')
class AmenityList(Resource):
    """
    Resource class for managing collection-level operations on amenities.

    This class provides endpoints to create a new amenity or retrieve all existing amenities.
    Input validation is performed using the API model, and business logic is handled by the facade layer.
    Only administrators can create amenities, while amenity retrieval is publicly accessible.
    
    Attributes:
        None
        
    Methods:
        post(): Create a new amenity (admin only)
        get(): Retrieve all amenities
    """

    @api.expect(amenity_model)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    @jwt_required()
    def post(self):
        """
        Create a new amenity. Only admins can create amenities.

        This endpoint receives a JSON payload validated against the Amenity model.
        The creation logic is delegated to the business facade layer. On success, returns the created amenity with its ID.
        Authentication is required and only users with admin privileges can create amenities.

        Expected Input:
            - name (str): Name of the amenity to create
            
        Headers Required:
            Authorization: Bearer <jwt_token> (with admin privileges)
            
        Returns:
            dict: Created amenity with ID and name (201),
                  or error message for invalid input (400),
                  or access denied for non-admin users (403),
                  or internal server error (500)
                  
        Example Success Response:
            {
                "id": "12345",
                "name": "WiFi"
            }
            
        Example Error Response:
            {
                "error": "Admin privileges required"
            }
        """
        # Check admin privileges from JWT token claims
        claims = get_jwt()
        if not claims.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403

        # Extract amenity data from request payload
        amenity_data = api.payload

        try:
            # Call facade to create new amenity with validation
            new_amenity = facade.create_amenity(amenity_data)
            
            # Return created amenity data with success status
            return {
                'id': new_amenity.id,
                'name': new_amenity.name
            }, 201
            
        except ValueError as e:
            # Handle business validation errors with specific error message
            return {'error': str(e)}, 400
            
        except Exception as e:
            # Handle unexpected errors with generic error message
            return {'error': 'Internal server error'}, 500

    @api.response(200, 'List of amenities retrieved successfully')
    def get(self):
        """
        Retrieve all amenities.

        This endpoint returns a list of all available amenities in the system.
        No authentication is required for this operation.
        
        Returns:
            list: List of amenities with their IDs and names (200)
            
        Example Response:
            [
                {"id": "1", "name": "WiFi"},
                {"id": "2", "name": "Pool"},
                {"id": "3", "name": "Parking"}
            ]
        """
        # Retrieve all amenities from the facade layer
        amenities = facade.get_all_amenities()
        
        # Return list of amenities with ID and name for each
        return [{'id': a.id, 'name': a.name} for a in amenities], 200


@api.route('/<amenity_id>')
class AmenityResource(Resource):
    """
    Resource class for managing item-level operations on a single amenity.

    This class provides endpoints to retrieve, update, or delete a specific amenity by its unique ID.
    All business logic is delegated to the facade layer, and input data is strictly validated.
    Update and delete operations require admin privileges.
    
    Attributes:
        None
        
    Methods:
        get(amenity_id): Retrieve specific amenity by ID
        put(amenity_id): Update specific amenity (admin only)
        delete(amenity_id): Delete specific amenity (admin only)
    """

    @api.response(200, 'Amenity retrieved successfully')
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """
        Retrieve a specific amenity by its ID.

        This endpoint returns the details of a single amenity identified by the provided ID.
        No authentication is required for this operation.
        
        Args:
            amenity_id (str): Unique identifier of the amenity
            
        Returns:
            dict: Amenity data with ID and name (200),
                  or error message if amenity not found (404)
                  
        Example Success Response:
            {
                "id": "12345",
                "name": "WiFi"
            }
            
        Example Error Response:
            {
                "error": "Amenity not found"
            }
        """
        # Retrieve amenity from facade using provided ID
        amenity = facade.get_amenity(amenity_id)
        
        # Check if amenity exists
        if not amenity:
            return {'error': 'Amenity not found'}, 404
            
        # Return amenity data with ID and name
        return {'id': amenity.id, 'name': amenity.name}, 200

    @api.expect(amenity_model)
    @api.response(200, 'Amenity updated successfully')
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    @jwt_required()
    def put(self, amenity_id):
        """
        Update a specific amenity. Only admins can update amenities.

        This endpoint accepts a JSON payload with updated data for the amenity identified by the given ID.
        If the amenity exists, it is updated and the new data is returned. If not, returns an error message.
        Authentication is required and only users with admin privileges can update amenities.

        Args:
            amenity_id (str): Unique identifier of the amenity to update
            
        Expected Input:
            - name (str): Updated name for the amenity
            
        Headers Required:
            Authorization: Bearer <jwt_token> (with admin privileges)

        Returns:
            dict: Updated amenity data (200),
                  or error message for invalid input (400),
                  or access denied for non-admin users (403),
                  or amenity not found (404)
                  
        Example Success Response:
            {
                "id": "12345",
                "name": "High-Speed WiFi"
            }
            
        Example Error Response:
            {
                "error": "Amenity not found"
            }
        """
        # Check admin privileges from JWT token claims
        claims = get_jwt()
        if not claims.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403

        # Extract updated amenity data from request payload
        amenity_api = api.payload

        try:
            # Call facade to update amenity with new data
            amenity_data = facade.update_amenity(amenity_id, amenity_api)
            
            # Check if amenity was found and updated
            if not amenity_data:
                return {'error': 'Amenity not found'}, 404
                
            # Return updated amenity data
            return {
                'id': amenity_data.id,
                'name': amenity_data.name
            }, 200
            
        except ValueError as e:
            # Handle business validation errors
            return {'error': str(e)}, 400
            
        except (ValueError, KeyError):
            # Handle cases where amenity doesn't exist
            return {'error': 'Amenity not found'}, 404

    @api.response(204, 'Amenity deleted successfully')
    @api.response(404, 'Amenity not found')
    @api.response(403, 'Admin privileges required')
    @jwt_required()
    def delete(self, amenity_id):
        """
        Delete a specific amenity. Only admins can delete amenities.

        This endpoint removes an amenity from the system using its unique ID.
        Authentication is required and only users with admin privileges can delete amenities.
        On successful deletion, returns an empty response with status 204.
        
        Args:
            amenity_id (str): Unique identifier of the amenity to delete
            
        Headers Required:
            Authorization: Bearer <jwt_token> (with admin privileges)
            
        Returns:
            Empty response (204) on success,
            or error message for access denied (403),
            or amenity not found (404),
            or internal server error (500)
            
        Example Error Response:
            {
                "error": "Amenity not found"
            }
        """
        # Check admin privileges from JWT token claims
        claims = get_jwt()
        if not claims.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403

        try:
            # Call facade to delete amenity by ID
            facade.delete_amenity(amenity_id)
            
            # Return empty response with 204 status on successful deletion
            return '', 204
            
        except ValueError:
            # Handle case where amenity doesn't exist
            return {'error': 'Amenity not found'}, 404
            
        except Exception:
            # Handle unexpected errors during deletion
            return {'error': 'Internal server error'}, 500
