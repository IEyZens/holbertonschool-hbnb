#!/usr/bin/env python3
"""
Simple test script to verify database connectivity and basic operations.
"""

from app import create_app, db
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review


def test_database_connection():
    """Test basic database connectivity and table creation."""
    app = create_app()

    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")

            # Test basic operations
            # Create a test user
            test_user = User(
                first_name="Test",
                last_name="User",
                email="test@example.com",
                password="testpass123"
            )

            db.session.add(test_user)
            db.session.commit()
            print("✅ User creation successful")

            # Query the user back
            retrieved_user = User.query.filter_by(
                email="test@example.com").first()
            if retrieved_user:
                print(
                    f"✅ User retrieval successful: {retrieved_user.first_name} {retrieved_user.last_name}")

            # Clean up
            db.session.delete(retrieved_user)
            db.session.commit()
            print("✅ User deletion successful")

            print("\n🎉 All database tests passed!")

        except Exception as e:
            print(f"❌ Database test failed: {str(e)}")
            return False

    return True


if __name__ == "__main__":
    test_database_connection()
