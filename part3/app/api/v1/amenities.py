# Importation des modules nécessaires
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

# Création d’un namespace Flask-RESTx pour les opérations liées aux commodités (amenities)
api = Namespace('amenities', description='Amenity operations')

# Définition du modèle de données pour la validation d'entrée et la documentation Swagger
amenity_model = api.model('Amenity', {
    # Champ requis : nom de la commodité
    'name': fields.String(required=True, description='Name of the amenity')
})


@api.route('/')
class AmenityList(Resource):
    """
    Resource class for managing collection-level operations on amenities.

    This class provides endpoints to create a new amenity or retrieve all existing amenities.
    Input validation is performed using the API model, and business logic is handled by the facade layer.
    """

    # Spécifie que cette méthode attend un corps de requête conforme au modèle amenity_model
    @api.expect(amenity_model)
    # Réponse en cas de succès : commodité créée
    @api.response(201, 'Amenity successfully created')
    # Réponse en cas d’échec de validation des données
    @api.response(400, 'Invalid input data')
    def post(self):
        """
        Create a new amenity.

        This endpoint receives a JSON payload validated against the Amenity model.
        The creation logic is delegated to the business facade layer. On success, returns the created amenity with its ID.
        On failure, returns an error message with HTTP 400.

        Returns:
            tuple: (JSON response, HTTP status code)
        """
        # Récupération des données envoyées dans le corps de la requête
        amenity_data = api.payload

        try:
            # Appel à la façade pour créer une commodité
            new_amenity = facade.create_amenity(amenity_data)
            # Retourne les données de la commodité créée
            return {
                'id': new_amenity.id,
                'name': new_amenity.name
            }, 201
        except ValueError as e:
            # En cas d'erreur de validation métier, retour d'une réponse 400 avec le message d'erreur
            return {'error': str(e)}, 400

    # Réponse en cas de succès : liste des commodités renvoyée
    @api.response(200, 'List of amenities retrieved successfully')
    def get(self):
        """
        Retrieve all amenities.

        This endpoint queries the backend service layer to get all amenities currently stored.
        Returns a list of amenity objects (id and name) with HTTP 200.

        Returns:
            tuple: (list of amenities as JSON, HTTP status code)
        """
        # Appel à la façade pour récupérer toutes les commodités
        amenities = facade.get_all_amenities()
        # Retourne une liste de commodités sous forme de dictionnaires
        return [
            {
                'id': amenity.id,
                'name': amenity.name
            }
            for amenity in amenities
        ], 200


@api.route('/<amenity_id>')
class AmenityResource(Resource):
    """
    Resource class for managing item-level operations on a single amenity.

    This class provides endpoints to retrieve or update a specific amenity by its unique ID.
    All business logic is delegated to the facade layer, and input data is strictly validated.
    """

    # Réponse en cas de succès : détails d’une commodité récupérés
    @api.response(200, 'Amenity details retrieved successfully')
    # Réponse si l’identifiant ne correspond à aucune commodité
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """
        Retrieve details of a specific amenity.

        This endpoint returns the details of an amenity identified by its unique ID.
        If the amenity is not found, returns an error message with HTTP 404.

        Args:
            amenity_id (str): Unique identifier of the amenity.

        Returns:
            tuple: (amenity details as JSON, HTTP status code)
        """
        # Recherche de la commodité via la façade
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            # Retour d’une erreur 404 si la commodité est introuvable
            return {'error': 'Amenity not found'}, 404

        # Retourne les détails de la commodité trouvée
        return {
            'id': amenity.id,
            'name': amenity.name
        }, 200

    # Spécifie que la requête PUT doit contenir des données correspondant au modèle amenity_model
    @api.expect(amenity_model)
    # Réponse si la mise à jour est réussie
    @api.response(200, 'Amenity updated successfully')
    # Réponse si la commodité à mettre à jour n'existe pas
    @api.response(404, 'Amenity not found')
    # Réponse si les données d’entrée sont invalides
    @api.response(400, 'Invalid input data')
    def put(self, amenity_id):
        """
        Update a specific amenity.

        This endpoint accepts a JSON payload with updated data for the amenity identified by the given ID.
        If the amenity exists, it is updated and the new data is returned. If not, returns an error message with HTTP 404.
        On invalid input, returns an error message with HTTP 400.

        Args:
            amenity_id (str): Unique identifier of the amenity.

        Returns:
            tuple: (updated amenity as JSON, HTTP status code)
        """
        # Récupération des données d'entrée fournies dans le corps de la requête
        amenity_api = api.payload

        try:
            # Mise à jour de la commodité via la façade
            amenity_data = facade.update_amenity(amenity_id, amenity_api)

            if not amenity_data:
                # Retourne une erreur 404 si aucune commodité n’a été trouvée pour l’ID donné
                return {'error': 'Amenity not found'}, 404

            # Retourne les informations de la commodité mise à jour
            return {
                'id': amenity_data.id,
                'name': amenity_data.name
            }, 200

        except ValueError as e:
            # Retourne une erreur 400 si une exception métier est levée
            return {'error': str(e)}, 400
