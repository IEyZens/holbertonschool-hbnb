from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from app.services import facade

# Création du namespace RESTx pour les opérations liées aux avis utilisateurs
api = Namespace('admin', description='Admin operations')

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


@api.route('/reviews/<review_id>')
class AdminReviewResource(Resource):
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
        current_user = get_jwt_identity()

        is_admin = current_user.get('is_admin', False)
        user_id = current_user.get('id')

        review = facade.get_review(review_id)

        if not review:
            return {'error': 'Review not found'}, 404

        if not is_admin and review.user.id != user_id:
            return {'error': 'Unauthorized action'}, 403

        review_api = api.payload

        try:
            review_data = facade.update_review(review_id, review_api)

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

    @api.response(200, 'Review deleted successfully')
    # Réponse 404 si l'avis n'est pas trouvé
    @api.response(404, 'Review not found')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def delete(self, review_id):
        current_user = get_jwt_identity()

        is_admin = current_user.get('is_admin', False)
        user_id = current_user.get('id')

        review = facade.get_review(review_id)

        if not review:
            return {'error': 'Review not found'}, 404

        if not is_admin and review.user.id != user_id:
            return {'error': 'Unauthorized action'}, 403

        try:
            review_data = facade.delete_review(review_id)

            if not review_data:
                return {'error': 'Review not found'}, 404
            else:
                return {'message': 'Review successfully deleted'}, 200

        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': 'Internal server error', 'details': str(e)}, 500
