# Import necessary modules for Flask API functionality
from flask import request, current_app as app
from flask_restx import Namespace, Resource, fields
from app.extensions import db
from app.models.user import User
from app.models.place import Place
from app.models.amenity import Amenity
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade


# Create a namespace for place-related operations in the API
api = Namespace('places', description='Place operations')


# Define amenity model used within a place response
amenity_model = api.model('PlaceAmenity', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity')
})


# Define user model linked to a place (owner information)
user_model = api.model('PlaceUser', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='First name of the owner'),
    'last_name': fields.String(description='Last name of the owner'),
    'email': fields.String(description='Email of the owner')
})


# Define review model associated with a place
review_model = api.model('PlaceReview', {
    'id': fields.String(description='Review ID'),
    'text': fields.String(description='Text of the review'),
    'rating': fields.Integer(description='Rating of the place (1-5)'),
    'user_id': fields.String(description='ID of the user'),
    'user': fields.Nested(user_model, description='Reviewing user')
})


# Define main model representing a complete place with all relationships
place_model = api.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(required=True, description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'owner_id': fields.String(required=True, description='ID of the owner'),
    'max_person': fields.Integer(required=True, description='Maximum number of persons allowed'),
    'owner': fields.Nested(user_model, description='Owner of the place'),
    'amenities': fields.List(fields.Nested(amenity_model), description='List of amenities'),
    'reviews': fields.List(fields.Nested(review_model), description='List of reviews')
})

# Define input model for place creation requests
place_input_model = api.model('PlaceInput', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(required=False, description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'max_person': fields.Integer(required=True, description='Maximum number of persons allowed'),
    'amenities': fields.List(fields.String, description='List of amenity names')
})

# Define input model for place update requests (all fields optional)
place_update_model = api.model('PlaceUpdateInput', {
    'title': fields.String(required=False, description='Title of the place'),
    'description': fields.String(required=False, description='Description of the place'),
    'price': fields.Float(required=False, description='Price per night'),
    'latitude': fields.Float(required=False, description='Latitude of the place'),
    'longitude': fields.Float(required=False, description='Longitude of the place'),
    'max_person': fields.Integer(required=False, description='Maximum number of persons allowed'),
    'amenities': fields.List(fields.String, description='List of amenity names')
})


@api.route('/')
class PlaceList(Resource):
    """
    REST API Resource for handling collection-level operations on Place entities.

    This class provides endpoints for:
    - Creating new places (POST)
    - Retrieving all places (GET)

    All operations include proper authentication, validation, and error handling.
    The facade pattern is used to delegate business logic to the service layer.
    """

    @api.expect(place_input_model)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def post(self):
        """
        Create a new place.

        This endpoint creates a new place with the provided data. It performs
        validation, handles amenity creation/assignment, and ensures proper
        authentication and authorization.

        Returns:
            dict: Created place data with status 201, or error with appropriate status
        """
        # Extract user ID from JWT token
        user_id = get_jwt_identity()

        # Retrieve user object from database using the ID
        user = facade.get_user_by_id(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        # Parse JSON data from request body
        data = request.get_json()
        if not data:
            return {'error': 'Missing JSON body'}, 400

        # Extract amenity names from request data (defaults to empty list)
        amenity_names = data.get("amenities", [])

        # Validate amenity names format and content
        for name in amenity_names:
            if not isinstance(name, str) or not name.strip():
                return {'error': f'Invalid amenity name: {name}'}, 400

        try:
            # Prepare place data dictionary for facade layer
            place_data = {
                'title': data.get("title"),
                'description': data.get("description"),
                'price': data.get("price"),
                'latitude': data.get("latitude"),
                'longitude': data.get("longitude"),
                'max_person': data.get("max_person")
            }

            # Process amenities: retrieve existing or create new ones
            amenity_ids = []
            for name in amenity_names:
                # Clean amenity name by removing whitespace
                name = name.strip()

                # Try to find existing amenity by name
                amenity_list = facade.get_amenity_by_name(name)

                if amenity_list and len(amenity_list) > 0:
                    # Use existing amenity (first match)
                    amenity = amenity_list[0]
                else:
                    # Create new amenity if it doesn't exist
                    amenity = facade.create_amenity({'name': name})

                # Collect amenity ID for place creation
                amenity_ids.append(amenity.id)

            # Add amenity IDs to place data if any amenities were processed
            if amenity_ids:
                place_data['amenities'] = amenity_ids

            # Create place using facade layer
            new_place = facade.create_place(place_data, user_id)

        except ValueError as e:
            # Handle business logic validation errors
            return {'error': str(e)}, 400
        except Exception as e:
            # Log unexpected errors for debugging
            app.logger.error(f"Error creating place: {e}")
            # Rollback database transaction to maintain consistency
            db.session.rollback()
            return {'error': 'Failed to create Place'}, 500

        # Return created place data with success status
        return {
            'id': new_place.id,
            'title': new_place.title,
            'description': new_place.description,
            'price': new_place.price,
            'latitude': new_place.latitude,
            'longitude': new_place.longitude,
            'max_person': new_place.max_person,
            'amenities': [a.name for a in new_place.amenities] if new_place.amenities else [],
            'owner_id': new_place.owner_id
        }, 201

    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """
        Retrieve all places from the database.

        Returns a comprehensive list of all places with their associated
        owner information, amenities, and metadata including timestamps.

        Returns:
            list: List of place dictionaries with complete information
        """
        try:
            # Retrieve all places from the database via facade
            places = facade.get_all_places()

            # Build comprehensive response with place details
            return [{
                'id': place.id,
                'title': place.title,
                'description': place.description,
                'price': place.price,
                'latitude': place.latitude,
                'longitude': place.longitude,
                'max_person': place.max_person,
                'owner_id': place.owner_id,
                # Include owner details if available
                'owner': {
                    'id': place.owner.id,
                    'first_name': place.owner.first_name,
                    'last_name': place.owner.last_name,
                    'email': place.owner.email
                } if place.owner else None,
                # Include amenity details if available
                'amenities': [
                    {
                        'id': amenity.id,
                        'name': amenity.name
                    } for amenity in place.amenities
                ] if place.amenities else [],
                # Include timestamp information if available
                'created_at': place.created_at.isoformat() if hasattr(place, 'created_at') and place.created_at else None,
                'updated_at': place.updated_at.isoformat() if hasattr(place, 'updated_at') and place.updated_at else None
            } for place in places], 200

        except Exception as e:
            # Log retrieval errors for debugging
            app.logger.error(f"Error retrieving places: {e}")
            return {'error': 'Failed to retrieve places'}, 500


@api.route('/<place_id>')
class PlaceResource(Resource):
    """
    REST API Resource for handling individual Place entity operations.

    This class provides endpoints for:
    - Retrieving a specific place (GET)
    - Updating a place (PUT)
    - Deleting a place (DELETE)

    All operations include proper authentication, authorization checks,
    and validation of user permissions.
    """

    @api.response(200, 'Place retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """
        Retrieve a specific place by its ID.

        Args:
            place_id (str): Unique identifier of the place

        Returns:
            dict: Place data or error message with appropriate status
        """
        # Retrieve place from database using facade
        place = facade.get_place(place_id)

        # Check if place exists
        if not place:
            return {'error': 'Place not found'}, 404

        print('➡️ place retourné depuis backend:', place)

        # Return place data
        return {
            'id': place.id,
            'title': place.title,
            'description': place.description,
            'price': place.price,
            'latitude': place.latitude,
            'longitude': place.longitude,
            'owner_id': place.owner.id,
            'max_person': place.max_person,
            'amenities': [
                {
                    'id': amenity.id,
                    'name': amenity.name
                } for amenity in place.amenities
            ] if place.amenities else [],

            'reviews': [
                {
                    'id': review.id,
                    'text': review.text,
                    'rating': review.rating,
                    'user_id': review.user_id,
                    'user': {
                        'id': review.user.id,
                        'first_name': review.user.first_name,
                        'last_name': review.user.last_name,
                        'email': review.user.email
                    } if review.user else None
                } for review in place.reviews
            ] if place.reviews else [],
        }, 200

    @api.expect(place_update_model)
    @api.response(200, 'Place updated successfully')
    @api.response(404, 'Place not found')
    @api.response(403, 'Unauthorized action')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def put(self, place_id):
        """
        Update an existing place.

        This endpoint allows updating place information. Only the place owner
        or an admin user can perform updates. The owner_id field cannot be modified.

        Args:
            place_id (str): Unique identifier of the place to update

        Returns:
            dict: Updated place data or error message with appropriate status
        """
        # Parse JSON data from request body
        place_data = request.get_json()

        # Extract current user information from JWT
        current_user = get_jwt_identity()
        claims = get_jwt()

        # Validate request contains data
        if not place_data:
            return {'error': 'Missing JSON body'}, 400

        try:
            # Retrieve existing place from database
            place = facade.get_place(place_id)
        except ValueError:
            return {'error': 'Place not found'}, 404

        # Check user authorization (owner or admin)
        is_admin = claims.get('is_admin', False)
        if not is_admin and place.owner.id != current_user:
            return {'error': 'Unauthorized action'}, 403

        # Prevent modification of owner_id field
        if 'owner_id' in place_data:
            return {'error': 'You cannot modify owner_id'}, 400

        # Handle amenities update if provided in request
        if 'amenities' in place_data:
            amenity_names = place_data.get('amenities', [])

            # Validate amenity names format
            for name in amenity_names:
                if not isinstance(name, str) or not name.strip():
                    return {'error': f'Invalid amenity name: {name}'}, 400

            # Process amenities: retrieve existing or create new ones
            amenity_ids = []
            for name in amenity_names:
                # Clean amenity name
                name = name.strip()

                # Try to find existing amenity
                amenity_list = facade.get_amenity_by_name(name)

                if amenity_list and len(amenity_list) > 0:
                    # Use existing amenity
                    amenity = amenity_list[0]
                else:
                    # Create new amenity if it doesn't exist
                    amenity = facade.create_amenity({'name': name})

                # Convert to format expected by facade (dictionary with id key)
                amenity_ids.append({'id': amenity.id})

            # Replace amenity names with formatted amenity objects
            place_data['amenities'] = amenity_ids

        try:
            # Update place using facade layer
            updated_place = facade.update_place(place_id, place_data)

            # Return updated place data
            return {
                'id': updated_place.id,
                'title': updated_place.title,
                'description': updated_place.description,
                'price': updated_place.price,
                'latitude': updated_place.latitude,
                'longitude': updated_place.longitude,
                'owner_id': updated_place.owner.id,
                'max_person': updated_place.max_person,
                'amenities': [{'id': a.id, 'name': a.name} for a in updated_place.amenities]
            }, 200

        except ValueError as e:
            # Handle business logic validation errors
            return {'error': str(e)}, 400
        except Exception as e:
            # Handle unexpected errors
            return {'error': 'Internal server error', 'details': str(e)}, 500

    @api.response(204, 'Place deleted successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Place not found')
    @jwt_required()
    def delete(self, place_id):
        """
        Delete a place.

        This endpoint allows deletion of a place. Only the place owner
        or an admin user can perform deletions.

        Args:
            place_id (str): Unique identifier of the place to delete

        Returns:
            Empty response with status 204 on success, or error message
        """
        # Extract current user information from JWT
        current_user = get_jwt_identity()
        claims = get_jwt()

        try:
            # Retrieve place to verify existence and get owner information
            place = facade.get_place(place_id)
        except ValueError:
            return {'error': 'Place not found'}, 404

        # Check user authorization (owner or admin)
        is_admin = claims.get('is_admin', False)
        if not is_admin and place.owner.id != current_user:
            return {'error': 'Unauthorized action'}, 403

        try:
            # Delete place using facade layer
            facade.delete_place(place_id)

            # Return empty response with success status
            return '', 204

        except ValueError as e:
            # Handle business logic errors
            return {'error': str(e)}, 400
        except Exception as e:
            # Handle unexpected errors
            return {'error': 'Internal server error', 'details': str(e)}, 500
