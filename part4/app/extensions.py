"""
Centralized extension initialization for the HBnB Flask application.

This module defines instances of Flask extensions (SQLAlchemy, Bcrypt, JWTManager)
to be initialized within the application factory.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
