# Importation des modules nécessaires
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask import request
from app.services import facade


# Création du namespace RESTx pour les opérations liées aux avis utilisateurs
api = Namespace('reviews', description='Review operations')


# Définition du modèle Review utilisé pour la validation d'entrée et la documentation Swagger
review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'user_id': fields.String(required=True, description='ID of the user'),
    'place_id': fields.String(required=True, description='ID of the place')
})

review_input_model = api.model('ReviewInput', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'user_id': fields.String(required=True, description='ID of the user'),
    'place_id': fields.String(required=True, description='ID of the place')
})

review_update_model = api.model('Review', {
    'text': fields.String(required=False, description='Text of the review'),
    'rating': fields.Integer(required=False, description='Rating of the place (1-5)'),
})


@api.route('/')
class ReviewList(Resource):
    """
    Resource for collection-level operations on review entities.

    Supports creation of a new review and retrieval of all stored reviews. Ensures data contract validation and delegates all logic to the business layer.
    """

    # Indique que le corps de la requête doit respecter le modèle review_model
    @api.expect(review_input_model)
    # Réponse 201 si la création de l'avis est réussie
    @api.response(201, 'Review successfully created')
    # Réponse 400 si les données envoyées sont invalides
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def post(self):
        """
        Create a new review entry.

        Validates the input payload, checks for foreign key integrity (user/place), and stores the review using the service layer. Errors return meaningful HTTP status.

        Returns:
            dict: Created review metadata or HTTP 400 with error message.
        """
        current_user = get_jwt_identity()

        try:
            # Récupération des données JSON issues de la requête
            review_data = api.payload

            # Création d'un nouvel avis via la façade
            new_review = facade.create_review(review_data, current_user)

            # Retourne les détails de l'avis créé
            return {
                'id': new_review.id,
                'text': new_review.text,
                'rating': new_review.rating,
                'place_id': new_review.place.id,
                'user_id': new_review.user.id
            }, 201
        except ValueError as e:
            # Gestion d'erreur métier si les données sont invalides
            return {'error': str(e)}, 400
        except Exception as e:
            # Gestion d'erreur générique
            return {'error': 'Internal server error'}, 500

    @api.response(200, 'List of reviews retrieved successfully')
    def get(self):
        reviews = facade.get_all_reviews()
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
    Resource for single-entity operations on a Review.

    Supports retrieving, updating, and deleting a specific review identified by its unique identifier.
    """

    @api.response(200, 'Review retrieved successfully')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
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
        current_user = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        review_api = api.payload

        # Interdiction de modifier user_id
        if 'user_id' in review_api:
            return {'error': 'You cannot modify user_id'}, 400

        try:
            review = facade.get_review(review_id)
        except ValueError:
            return {'error': 'Review not found'}, 404

        if not is_admin and review.user.id != current_user:
            return {'error': 'Unauthorized action'}, 403

        try:
            updated_review = facade.update_review(review_id, review_api)
            return {
                'id': updated_review.id,
                'text': updated_review.text,
                'rating': updated_review.rating,
                'place_id': updated_review.place.id,
                'user_id': updated_review.user.id
            }, 200
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': 'Internal server error', 'details': str(e)}, 500

    @api.response(200, 'Review deleted successfully')
    @api.response(404, 'Review not found')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def delete(self, review_id):
        current_user = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        try:
            review = facade.get_review(review_id)
        except ValueError:
            return {'error': 'Review not found'}, 404

        if not is_admin and review.user.id != current_user:
            return {'error': 'Unauthorized action'}, 403

        try:
            facade.delete_review(review_id)
            return {'message': 'Review successfully deleted'}, 200
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': 'Internal server error', 'details': str(e)}, 500
