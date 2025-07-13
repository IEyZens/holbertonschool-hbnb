# Import necessary modules for Flask API functionality
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask import request
from app.services import facade


# Create a namespace for review-related operations in the API
api = Namespace('reviews', description='Review operations')


# Define main review model for complete review data with all relationships
review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'user_id': fields.String(required=True, description='ID of the user'),
    'place_id': fields.String(required=True, description='ID of the place')
})

# Define input model for review creation requests
review_input_model = api.model('ReviewInput', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'place_id': fields.String(required=True, description='ID of the place')
})

# Define update model for review modifications (all fields optional)
review_update_model = api.model('ReviewUpdate', {
    'text': fields.String(required=False, description='Text of the review'),
    'rating': fields.Integer(required=False, description='Rating of the place (1-5)'),
})


@api.route('/')
class ReviewList(Resource):
    """
    REST API Resource for handling collection-level operations on Review entities.
    
    This class provides endpoints for:
    - Creating new reviews (POST)
    - Retrieving all reviews (GET)
    
    Review creation includes validation of user/place relationships and ensures
    users cannot review their own places. Authentication is required for creation.
    """

    @api.expect(review_input_model)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def post(self):
        """
        Create a new review for a place.
        
        This endpoint allows authenticated users to create reviews for places.
        The system validates that users cannot review their own places and
        ensures all required data is provided and valid.
        
        Returns:
            dict: Created review data with status 201, or error with appropriate status
        """
        # Extract current user ID from JWT token
        current_user = get_jwt_identity()

        try:
            # Extract review data from request payload
            review_data = api.payload

            # Create new review using facade layer (includes business logic validation)
            new_review = facade.create_review(review_data, current_user)

            # Return created review details
            return {
                'id': new_review.id,
                'text': new_review.text,
                'rating': new_review.rating,
                'place_id': new_review.place.id,
                'user_id': new_review.user.id
            }, 201
            
        except ValueError as e:
            # Handle business logic validation errors (e.g., user reviewing own place)
            return {'error': str(e)}, 400
        except Exception as e:
            # Handle unexpected server errors
            return {'error': 'Internal server error'}, 500

    @api.response(200, 'List of reviews retrieved successfully')
    def get(self):
        """
        Retrieve all reviews from the database.
        
        Returns a comprehensive list of all reviews with associated user and place
        information. This endpoint is publicly accessible for displaying reviews.
        
        Returns:
            list: List of review dictionaries with complete information
        """
        # Retrieve all reviews from database via facade
        reviews = facade.get_all_reviews()
        
        # Build response list with review details and relationships
        return [{
            'id': r.id,
            'text': r.text,
            'rating': r.rating,
            'user_id': r.user.id,
            'place_id': r.place.id
        } for r in reviews], 200


@api.route('/<review_id>')
class ReviewResource(Resource):
    """
    REST API Resource for handling individual Review entity operations.
    
    This class provides endpoints for:
    - Retrieving a specific review (GET)
    - Updating review content (PUT)
    - Deleting reviews (DELETE)
    
    All modification operations include proper authentication and authorization
    checks to ensure users can only modify their own reviews (unless admin).
    """

    @api.response(200, 'Review retrieved successfully')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """
        Retrieve a specific review by its ID.
        
        Returns complete review information including associated user and place IDs.
        This endpoint is publicly accessible for displaying individual reviews.
        
        Args:
            review_id (str): Unique identifier of the review
            
        Returns:
            dict: Review data or error message with appropriate status
        """
        # Retrieve review from database using facade
        review = facade.get_review(review_id)
        
        # Check if review exists
        if not review:
            return {'error': 'Review not found'}, 404
            
        # Return complete review information
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
        Update an existing review.
        
        Users can only update their own reviews (text and rating).
        Admin users can update any review. The user_id and place_id
        cannot be modified to maintain data integrity.
        
        Args:
            review_id (str): Unique identifier of the review to update
            
        Returns:
            dict: Updated review data or error message with appropriate status
        """
        # Extract current user information from JWT
        current_user = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        # Extract update data from request payload
        review_api = api.payload

        # Prevent modification of user_id to maintain data integrity
        if 'user_id' in review_api:
            return {'error': 'You cannot modify user_id'}, 400

        try:
            # Retrieve existing review from database
            review = facade.get_review(review_id)
        except ValueError:
            return {'error': 'Review not found'}, 404

        # Check user authorization (owner or admin)
        if not is_admin and review.user.id != current_user:
            return {'error': 'Unauthorized action'}, 403

        try:
            # Update review using facade layer
            updated_review = facade.update_review(review_id, review_api)
            
            # Return updated review data
            return {
                'id': updated_review.id,
                'text': updated_review.text,
                'rating': updated_review.rating,
                'place_id': updated_review.place.id,
                'user_id': updated_review.user.id
            }, 200
            
        except ValueError as e:
            # Handle business logic validation errors
            return {'error': str(e)}, 400
        except Exception as e:
            # Handle unexpected server errors
            return {'error': 'Internal server error', 'details': str(e)}, 500

    @api.response(200, 'Review deleted successfully')
    @api.response(404, 'Review not found')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def delete(self, review_id):
        """
        Delete a review.
        
        Users can delete their own reviews, and admin users can delete any review.
        This operation is irreversible and will permanently remove the review
        from the system.
        
        Args:
            review_id (str): Unique identifier of the review to delete
            
        Returns:
            dict: Success message with status 200, or error message
        """
        # Extract current user information from JWT
        current_user = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        try:
            # Retrieve review to verify existence and get owner information
            review = facade.get_review(review_id)
        except ValueError:
            return {'error': 'Review not found'}, 404

        # Check user authorization (owner or admin)
        if not is_admin and review.user.id != current_user:
            return {'error': 'Unauthorized action'}, 403

        try:
            # Delete review using facade layer
            facade.delete_review(review_id)
            
            # Return success message
            return {'message': 'Review successfully deleted'}, 200
            
        except ValueError as e:
            # Handle business logic errors
            return {'error': str(e)}, 400
        except Exception as e:
            # Handle unexpected server errors
            return {'error': 'Internal server error', 'details': str(e)}, 500
