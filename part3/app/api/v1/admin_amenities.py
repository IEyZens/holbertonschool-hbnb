# Import necessary modules for admin amenity management functionality
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

# Create Flask-RESTx namespace for admin amenity operations
api = Namespace('admin', description='Admin operations')

# Define data model for input validation and Swagger documentation
amenity_model = api.model('Amenity', {
    # Required field: amenity name
    'name': fields.String(required=True, description='Name of the amenity')
})


@api.route('/amenities/')
class AdminAmenityCreate(Resource):
    """
    Resource for admin amenity creation.

    This class provides endpoints for administrators to create new amenities in the system.
    Only users with admin privileges can access these operations for managing amenity data.
    
    Attributes:
        None
        
    Methods:
        post(): Create new amenity (admin only)
    """
    
    @api.expect(amenity_model)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def post(self):
        """
        Create a new amenity as an admin.

        This endpoint allows administrators to add new amenities to the system that can be
        associated with places. Input validation and business rules are enforced through the facade.
        
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
                "name": "Hot Tub"
            }
            
        Example Error Response:
            {
                "error": "Admin privileges required"
            }
        """
        # Get current user identity and claims from JWT token
        current_user = get_jwt_identity()
        claims = get_jwt()
        
        # Check admin privileges
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        # Extract amenity data from request payload
        amenity_data = api.payload

        try:
            # Create amenity through facade with validation
            new_amenity = facade.create_amenity(amenity_data)
            
            # Return created amenity data
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


@api.route('/amenities/<amenity_id>')
class AdminAmenityModify(Resource):
    """
    Resource for admin amenity modification operations.

    This class provides endpoints for administrators to manage individual amenities including
    retrieving, updating, and deleting amenity records. All operations require admin privileges.
    
    Attributes:
        None
        
    Methods:
        get(amenity_id): Retrieve specific amenity by ID (admin only)
        put(amenity_id): Update specific amenity (admin only)
        delete(amenity_id): Delete specific amenity (admin only)
    """

    @api.response(200, 'Amenity retrieved successfully')
    @api.response(404, 'Amenity not found')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def get(self, amenity_id):
        """
        Retrieve a specific amenity by its ID. Only admins can access this endpoint.

        This endpoint allows administrators to view detailed information about a specific
        amenity using its unique identifier.
        
        Args:
            amenity_id (str): Unique identifier of the amenity to retrieve
            
        Headers Required:
            Authorization: Bearer <jwt_token> (with admin privileges)
            
        Returns:
            dict: Amenity data with ID and name (200),
                  or error message for access denied (403),
                  or amenity not found (404)
                  
        Example Success Response:
            {
                "id": "12345",
                "name": "Swimming Pool"
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
            # Retrieve amenity from facade using provided ID
            amenity = facade.get_amenity(amenity_id)
            
        except (ValueError, KeyError):
            # Handle case where amenity doesn't exist
            return {'error': 'Amenity not found'}, 404
            
        # Return amenity data with ID and name
        return {
            'id': amenity.id,
            'name': amenity.name
        }, 200

    @api.expect(amenity_model, validate=True)
    @api.response(200, 'Amenity updated successfully')
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def put(self, amenity_id):
        """
        Update a specific amenity. Only admins can update amenities.

        This endpoint allows administrators to modify amenity information including the name.
        Input validation is performed and business rules are enforced through the facade.
        
        Args:
            amenity_id (str): Unique identifier of the amenity to update
            
        Expected Input:
            - name (str): Updated name for the amenity
            
        Headers Required:
            Authorization: Bearer <jwt_token> (with admin privileges)
            
        Returns:
            dict: Updated amenity data (200),
                  or error message for invalid input (400),
                  or access denied (403),
                  or amenity not found (404)
                  
        Example Success Response:
            {
                "id": "12345",
                "name": "Heated Swimming Pool"
            }
            
        Example Error Response:
            {
                "error": "Amenity not found"
            }
        """
        # Check admin privileges from JWT token claims
        claims = get_jwt()
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        # Extract amenity data from request payload
        amenity_api = api.payload
        
        try:
            # Attempt to update amenity with new data through facade
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
            # Handle business validation errors with specific error message
            return {'error': str(e)}, 400
            
        except (ValueError, KeyError):
            # Handle cases where amenity doesn't exist
            return {'error': 'Amenity not found'}, 404

    @api.response(204, 'Amenity deleted successfully')
    @api.response(404, 'Amenity not found')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def delete(self, amenity_id):
        """
        Delete a specific amenity. Only admins can delete amenities.

        This endpoint allows administrators to permanently remove an amenity from the system.
        Associated place-amenity relationships may be affected depending on business rules.
        
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
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        try:
            # Verify amenity exists before attempting deletion
            amenity = facade.get_amenity(amenity_id)
            
        except (ValueError, KeyError):
            # Handle case where amenity doesn't exist
            return {'error': 'Amenity not found'}, 404

        try:
            # Attempt to delete amenity through facade
            facade.delete_amenity(amenity_id)
            
            # Return empty response with 204 status on successful deletion
            return '', 204
            
        except Exception:
            # Handle unexpected errors during deletion
            return {'error': 'Internal server error'}, 500
