from flask_restx import Api
from flask import Blueprint

from app.api.v1.places import api as places_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.users import api as users_ns

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

api = Api(api_bp,
          title='HBnB API',
          version='1.0',
          description='API for HBnB project'
)

api.add_namespace(places_ns)
api.add_namespace(amenities_ns)
api.add_namespace(users_ns)
