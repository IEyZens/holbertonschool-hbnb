from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
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

review_update_model = api.model('Review', {
    'text': fields.String(required=False, description='Text of the review'),
    'rating': fields.Integer(required=False, description='Rating of the place (1-5)'),
})


@api.route('/')
class ReviewList(Resource):
    """
    Resource for collection-level operations on review entities.

    Supports creation of a new review and retrieval of all stored reviews.
    Ensures data contract validation and delegates all logic to the business layer.
    """

    # Indique que le corps de la requête doit respecter le modèle review_model
    @api.expect(review_model)
    # Réponse 201 si la création de l'avis est réussie
    @api.response(201, 'Review successfully created')
    # Réponse 400 si les données envoyées sont invalides
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def post(self):
        """
        Create a new review entry.

        Validates the input payload, checks for foreign key integrity (user/place),
        and stores the review using the service layer. Errors return meaningful HTTP status.

        Returns:
            dict: Created review metadata or HTTP 400 with error message.
        """
        current_user = get_jwt_identity()

        try:
            # Récupération des données JSON issues de la requête
            review_data = request.json

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

    # Réponse 200 si la liste des avis est récupérée avec succès
    @api.response(200, 'List of reviews retrieved successfully')
    def get(self):
        """
        Retrieve all reviews from the system.

        This endpoint returns a flat list of all review entities available.
        The data is structured according to the internal representation schema.

        Returns:
            list: All reviews with HTTP 200.
        """
        # Appel à la façade pour récupérer tous les avis
        reviews = facade.get_all_reviews()

        # Retourne la liste des avis formatés
        return [
            {
                'id': r.id,
                'text': r.text,
                'rating': r.rating,
                'place_id': r.place.id,
                'user_id': r.user.id
            }
            for r in reviews
        ], 200


@api.route('/<review_id>')
class ReviewResource(Resource):
    """
    Resource for single-entity operations on a Review.

    Supports retrieving, updating, and deleting a specific review
    identified by its unique identifier.
    """

    # Réponse 200 si les détails de l'avis sont récupérés
    @api.response(200, 'Review details retrieved successfully')
    # Réponse 404 si l'avis n'est pas trouvé
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """
        Retrieve a specific review entity by ID.

        Args:
            review_id (str): Unique identifier of the review.

        Returns:
            dict: Review data with HTTP 200, or error message with HTTP 404.
        """
        try:
            # Recherche de l'avis via la façade
            review = facade.get_review(review_id)

            # Retourne les données de l'avis trouvé
            return {
                'id': review.id,
                'text': review.text,
                'rating': review.rating,
                'place_id': review.place.id,
                'user_id': review.user.id
            }, 200
        except ValueError as e:
            # Retourne une erreur si l'avis est introuvable
            return {'error': str(e)}, 404

    # Indique que la requête PUT attend un corps conforme à review_model
    @api.expect(review_update_model)
    # Réponse 200 si la mise à jour est effectuée
    @api.response(200, 'Review updated successfully')
    # Réponse 404 si l'avis n'existe pas
    @api.response(404, 'Review not found')
    # Réponse 400 si les données envoyées sont invalides
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def put(self, review_id):
        """
        Update an existing review entry.

        Accepts a JSON payload with the updated attributes. Verifies data integrity
        and applies changes in-place via the service layer.

        Args:
            review_id (str): Review unique identifier.

        Returns:
            dict: Updated review with HTTP 200, or error message with HTTP 400/404.
        """
        # Récupération des nouvelles données pour la mise à jour
        review_api = api.payload
        current_user = get_jwt_identity()
        review = facade.get_review(review_id)

        if not review:
            return {'error': 'Review not found'}, 404

        if review.user.id != current_user["id"]:
            return {'error': 'Unauthorized action'}, 403

        try:
            # Mise à jour de l'avis via la façade
            review_data = facade.update_review(review_id, review_api)

            if not review_data:
                return {'error': 'Review not found'}, 404

            # Retourne les nouvelles données de l'avis
            return {
                'id': review_data.id,
                'text': review_data.text,
                'rating': review_data.rating,
                'place_id': review_data.place.id,
                'user_id': review_data.user.id
            }, 200
        except ValueError as e:
            # Retourne une erreur si l'avis est introuvable
            return {'error': str(e)}, 400
        except Exception as e:
            # Gestion générique d’exception serveur : erreur 500
            return {'error': 'Internal server error', 'details': str(e)}, 500

    # Réponse 200 si la suppression est réussie
    @api.response(200, 'Review deleted successfully')
    # Réponse 404 si l'avis n'est pas trouvé
    @api.response(404, 'Review not found')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def delete(self, review_id):
        """
        Delete a review entity by ID.

        Args:
            review_id (str): The UUID of the review to delete.

        Returns:
            dict: Success confirmation or HTTP 404 error.
        """
        current_user = get_jwt_identity()
        review = facade.get_review(review_id)

        if not review:
            return {'error': 'Review not found'}, 404

        if review.user.id != current_user["id"]:
            return {'error': 'Unauthorized action'}, 403

        try:
            # Suppression de l'avis via la façade
            review_data = facade.delete_review(review_id)

            if not review_data:
                # Retourne une erreur si l'avis est introuvable
                return {'error': 'Review not found'}, 404
            else:
                # Confirmation de la suppression
                return {'message': 'Review successfully deleted'}, 200
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': 'Internal server error', 'details': str(e)}, 500


@api.route('/places/<place_id>/reviews')
class PlaceReviewList(Resource):
    """
    Resource for retrieving reviews bound to a specific Place.

    Allows clients to fetch all reviews related to a given place entity.
    """

    # Réponse 200 si les avis du lieu sont récupérés
    @api.response(200, 'List of reviews for the place retrieved successfully')
    # Réponse 404 si le lieu n'existe pas
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """
        Retrieve all reviews for a given place ID.

        Args:
            place_id (str): The UUID of the place whose reviews are requested.

        Returns:
            list: List of reviews linked to the place, or HTTP 404 if place is invalid.
        """
        try:
            # Récupère tous les avis liés à un lieu via son ID
            reviews = facade.get_reviews_by_place(place_id)

            # Retourne la liste des avis formatée
            return [
                {
                    'id': r.id,
                    'text': r.text,
                    'rating': r.rating,
                    'place_id': r.place.id,
                    'user_id': r.user.id
                }
                for r in reviews
            ], 200
        except KeyError as e:
            # Gestion d’erreur si le lieu est introuvable ou invalide
            return {'error': str(e)}, 404
