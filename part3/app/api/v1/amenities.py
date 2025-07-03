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
    Resource class managing collection-level operations for amenity data.

    This endpoint allows clients to create a new amenity entity or
    retrieve the full list of existing amenities. Input validation is
    performed via API models, and business rules are enforced through the facade layer.
    """

    # Spécifie que cette méthode attend un corps de requête conforme au modèle amenity_model
    @api.expect(amenity_model)
    # Réponse en cas de succès : commodité créée
    @api.response(201, 'Amenity successfully created')
    # Réponse en cas d’échec de validation des données
    @api.response(400, 'Invalid input data')
    def post(self):
        """
        Create a new amenity entry.

        Receives a JSON payload validated against the Amenity data model.
        Delegates creation logic to the business facade layer and returns
        a structured response including the generated amenity ID.

        Returns:
            JSON: Amenity representation with HTTP 201 on success,
                  or HTTP 400 with error details.
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
        Retrieve all available amenities.

        Queries the backend service layer to retrieve all amenity data
        currently stored. The result is returned as a list of structured
        dictionaries containing amenity IDs and names.

        Returns:
            JSON: List of amenity objects with HTTP 200.
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
    Resource class managing item-level operations on a single amenity.

    This endpoint supports retrieval and update of a specific amenity,
    identified by its unique ID. All logic is delegated to the facade layer,
    and strict validation rules apply to incoming data.
    """

    # Réponse en cas de succès : détails d’une commodité récupérés
    @api.response(200, 'Amenity details retrieved successfully')
    # Réponse si l’identifiant ne correspond à aucune commodité
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """
        Retrieve details of a specific amenity.

        Args:
            amenity_id (str): Unique identifier of the amenity resource.

        Returns:
            JSON: Amenity details if found (HTTP 200), or error message (HTTP 404).
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
        Update a specific amenity record.

        Accepts a JSON payload with updated data for the amenity identified
        by the provided ID. If the amenity exists, it is updated and returned.
        Otherwise, appropriate error status is returned.

        Args:
            amenity_id (str): Unique identifier of the amenity.

        Returns:
            JSON: Updated amenity object or error message.
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
