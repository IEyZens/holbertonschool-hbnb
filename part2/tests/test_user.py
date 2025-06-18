import unittest
from app.models.user import User
from app.models.place import Place
from app.models.review import Review

class TestUserModel(unittest.TestCase):
    def setUp(self):
        # Clear emails between tests
        User.existing_emails.clear()

    def test_create_valid_user(self):
        user = User("Alice", "Smith", "alice@example.com")
        self.assertEqual(user.first_name, "Alice")
        self.assertEqual(user.last_name, "Smith")
        self.assertEqual(user.email, "alice@example.com")
        self.assertFalse(user.is_admin)

    def test_first_name_too_long(self):
        with self.assertRaises(ValueError) as ctx:
            User("A" * 51, "Smith", "unique1@example.com")
        self.assertIn("first name", str(ctx.exception))

    def test_last_name_too_long(self):
        with self.assertRaises(ValueError) as ctx:
            User("Alice", "B" * 51, "unique2@example.com")
        self.assertIn("last name", str(ctx.exception))

    def test_invalid_email_format(self):
        with self.assertRaises(ValueError) as ctx:
            User("Alice", "Smith", "invalid-email")
        self.assertIn("email address", str(ctx.exception))

    def test_duplicate_email(self):
        User("Bob", "Smith", "bob@example.com")
        with self.assertRaises(ValueError) as ctx:
            User("Bobby", "Smith", "bob@example.com")
        self.assertIn("already exists", str(ctx.exception))

    def test_non_boolean_is_admin(self):
        with self.assertRaises(TypeError) as ctx:
            User("Alice", "Smith", "admin@example.com", is_admin="yes")
        self.assertIn("must be a boolean", str(ctx.exception))

    def test_add_valid_place(self):
        user = User("Alice", "Smith", "alice.place@example.com")
        place = Place("Nice house", 120, 45.0, 4.5)
        user.add_place(place)
        self.assertIn(place, user.places)

    def test_add_invalid_place_type(self):
        user = User("Alice", "Smith", "alice.wrongplace@example.com")
        with self.assertRaises(TypeError) as ctx:
            user.add_place("not a place")
        self.assertIn("Place", str(ctx.exception))

    def test_add_valid_review(self):
        user = User("Alice", "Smith", "alice.review@example.com")
        place = Place("Nice house", 120, 45.0, 4.5)
        review = Review("Great place!", 5, place, user)
        user.add_review(review)
        self.assertIn(review, user.reviews)

    def test_add_invalid_review_type(self):
        user = User("Alice", "Smith", "alice.wrongreview@example.com")
        with self.assertRaises(TypeError) as ctx:
            user.add_review(42)
        self.assertIn("Review", str(ctx.exception))

if __name__ == '__main__':
    unittest.main()
