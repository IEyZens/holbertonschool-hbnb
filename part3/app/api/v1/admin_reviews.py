# Import necessary modules for admin review management functionality
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask import request
from app.services import facade

# Create RESTx namespace for admin review operations
api = Namespace('admin', description='Admin operations')

# Define Review model for input validation and Swagger documentation
review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'user_id': fields.String(required=True, description='ID of the user'),
    'place_id': fields.String(required=True, description='ID of the place')
})

# Define review update model with optional fields
review_update_model = api.model('Review', {
    'text': fields.String(required=False, description='Text of the review'),
    'rating': fields.Integer(required=False, description='Rating of the place (1-5)'),
})


@api.route('/reviews/<review_id>')
class AdminReviewResource(Resource):
    """
    Resource for admin operations on a specific review.

    This class provides endpoints for administrators and review authors to manage individual reviews
    including retrieving, updating, and deleting review entries. Access control ensures only
    admins or the review author can modify review data.
    
    Attributes:
        None
        
    Methods:
        get(review_id): Retrieve specific review by ID (admin or author)
        put(review_id): Update specific review (admin or author)
        delete(review_id): Delete specific review (admin or author)
    """
    
    @api.response(200, 'Review retrieved successfully')
    @api.response(404, 'Review not found')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def get(self, review_id):
        """
        Retrieve a review by its ID. Only admins or the review's author can view it.

        This endpoint allows authorized users (admins or review authors) to retrieve detailed
        information about a specific review including associated user and place information.
        
        Args:
            review_id (str): The UUID of the review to retrieve
            
        Headers Required:
            Authorization: Bearer <jwt_token>
            
        Returns:
            dict: Review data with user and place IDs (200),
                  or error message for unauthorized access (403),
                  or review not found (404)
                  
        Example Success Response:
            {
                "id": "12345",
                "text": "Great place to stay!",
                "rating": 5,
                "user_id": "67890",
                "place_id": "54321"
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
            # Retrieve review from facade using provided ID
            review = facade.get_review(review_id)
            
        except (ValueError, KeyError):
            # Handle case where review doesn't exist
            return {'error': 'Review not found'}, 404

        # Check authorization: only admin or review author can access
        if not is_admin and review.user.id != user_id:
            return {'error': 'Unauthorized action'}, 403

        # Return review data with associated user and place IDs
        return {
            'id': review.id,
            'text': review.text,
            'rating': review.rating,
            'user_id': review.user.id,
            'place_id': review.place.id
        }, 200

    @api.expect(review_update_model)
    @api.response(200, 'Review updated successfully')
    @api.response(404, 'Review not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def put(self, review_id):
        """
        Update a review by its ID. Only admins or the review's author can update.

        This endpoint allows authorized users to modify review content including text and rating.
        Business rules and validation are enforced through the facade layer.
        
        Args:
            review_id (str): The UUID of the review to update
            
        Expected Input:
            - text (str, optional): Updated review text
            - rating (int, optional): Updated rating (1-5)
            
        Headers Required:
            Authorization: Bearer <jwt_token>
            
        Returns:
            dict: Updated review data (200),
                  or error message for invalid input (400),
                  or unauthorized access (403),
                  or review not found (404),
                  or internal server error (500)
                  
        Example Success Response:
            {
                "id": "12345",
                "text": "Updated review text",
                "rating": 4,
                "place_id": "54321",
                "user_id": "67890"
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
            # Verify review exists before attempting update
            review = facade.get_review(review_id)
            
        except (ValueError, KeyError):
            # Handle case where review doesn't exist
            return {'error': 'Review not found'}, 404

        # Check authorization: only admin or review author can update
        if not is_admin and review.user.id != user_id:
            return {'error': 'Unauthorized action'}, 403

        # Extract review data from request payload
        review_api = api.payload

        try:
            # Attempt to update review with new data through facade
            review_data = facade.update_review(review_id, review_api)

            # Return updated review data
            return {
                'id': review_data.id,
                'text': review_data.text,
                'rating': review_data.rating,
                'place_id': review_data.place.id,
                'user_id': review_data.user.id
            }, 200

        except ValueError as e:
            # Handle business validation errors with specific error message
            return {'error': str(e)}, 400
            
        except Exception as e:
            # Handle unexpected errors with detailed error information
            return {'error': 'Internal server error', 'details': str(e)}, 500

    @api.response(200, 'Review deleted successfully')
    @api.response(404, 'Review not found')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def delete(self, review_id):
        """
        Delete a review by its ID. Only admins or the review's author can delete.

        This endpoint allows authorized users to permanently remove a review from the system.
        The deletion behavior depends on business rules implemented in the facade layer.
        
        Args:
            review_id (str): The UUID of the review to delete
            
        Headers Required:
            Authorization: Bearer <jwt_token>
            
        Returns:
            dict: Success message (200),
            or error message for invalid input (400),
            or unauthorized access (403),
            or review not found (404),
            or internal server error (500)
            
        Example Success Response:
            {
                "message": "Review successfully deleted"
            }
            
        Example Error Response:
            {
                "error": "Review not found"
            }
        """
        # Get current user identity and claims from JWT token
        current_user = get_jwt_identity()
        claims = get_jwt()

        # Extract admin status and user ID for authorization
        is_admin = claims.get('is_admin', False)
        user_id = current_user

        try:
            # Verify review exists before attempting deletion
            review = facade.get_review(review_id)
            
        except (ValueError, KeyError):
            # Handle case where review doesn't exist
            return {'error': 'Review not found'}, 404

        # Check authorization: only admin or review author can delete
        if not is_admin and review.user.id != user_id:
            return {'error': 'Unauthorized action'}, 403

        try:
            # Attempt to delete review through facade
            review_data = facade.delete_review(review_id)

            # Check if deletion was successful
            if not review_data:
                return {'error': 'Review not found'}, 404
            else:
                return {'message': 'Review successfully deleted'}, 200

        except ValueError as e:
            # Handle business validation errors with specific error message
            return {'error': str(e)}, 400
            
        except Exception as e:
            # Handle unexpected errors with detailed error information
            return {'error': 'Internal server error', 'details': str(e)}, 500
