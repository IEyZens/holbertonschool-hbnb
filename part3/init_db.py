#!/usr/bin/env python3
"""
Database initialization script for HBnB application.

This script creates all database tables and can be used to set up
the database for development or production environments.
"""

from app import create_app
from app.extensions import db


def init_database():
    """Initialize the database by creating all tables."""
    app = create_app()

    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")

        # Optional: Add some initial data
        from app.models.amenity import Amenity

        # Check if amenities already exist
        existing_amenities = Amenity.query.count()
        if existing_amenities == 0:
            # Add some default amenities
            default_amenities = [
                Amenity(name="WiFi"),
                Amenity(name="Air Conditioning"),
                Amenity(name="Parking"),
                Amenity(name="Swimming Pool"),
                Amenity(name="Kitchen"),
            ]

            for amenity in default_amenities:
                db.session.add(amenity)

            db.session.commit()
            print("✅ Default amenities added!")


if __name__ == "__main__":
    init_database()
