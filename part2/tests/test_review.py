import unittest
from app.models.review import Review
from app.models.user import User
from app.models.place import Place

class TestReviewModel(unittest.TestCase):
    def setUp(self):
        self.valid_user = User("John", "Doe", "john@example.com")
        self.valid_place = Place("Nice place", 100, 45.0, 5.0)

    def test_create_valid_review(self):
        review = Review("Excellent stay", 5, self.valid_place, self.valid_user)
        self.assertEqual(review.text, "Excellent stay")
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.place, self.valid_place)
        self.assertEqual(review.user, self.valid_user)

    def test_empty_text_raises_value_error(self):
        with self.assertRaises(ValueError) as context:
            Review("", 4, self.valid_place, self.valid_user)
        self.assertIn("text", str(context.exception))

    def test_rating_too_low_raises_value_error(self):
        with self.assertRaises(ValueError) as context:
            Review("Bad", 0, self.valid_place, self.valid_user)
        self.assertIn("rating", str(context.exception))

    def test_rating_too_high_raises_value_error(self):
        with self.assertRaises(ValueError) as context:
            Review("Too perfect", 6, self.valid_place, self.valid_user)
        self.assertIn("rating", str(context.exception))

    def test_invalid_user_type_raises_type_error(self):
        with self.assertRaises(TypeError) as context:
            Review("Great", 5, self.valid_place, "not_a_user")
        self.assertIn("User", str(context.exception))

    def test_invalid_place_type_raises_type_error(self):
        with self.assertRaises(TypeError) as context:
            Review("Great", 5, "not_a_place", self.valid_user)
        self.assertIn("Place", str(context.exception))

if __name__ == '__main__':
    unittest.main()
