import unittest
from app.models.place import Place
from app.models.user import User
from app.models.review import Review
from app.models.amenity import Amenity

class TestPlaceModel(unittest.TestCase):
    def setUp(self):
        self.user = User("Jane", "Doe", "jane.doe@example.com")

    def tearDown(self):
        User.existing_emails.clear()

    def test_create_valid_place(self):
        place = Place("Nice House", "Great view", 100.0, 45.0, 5.0, self.user, 4)
        self.assertEqual(place.title, "Nice House")
        self.assertEqual(place.owner, self.user)
        self.assertEqual(place.max_person, 4)

    def test_title_too_long_raises(self):
        with self.assertRaises(ValueError):
            Place("T" * 101, "Desc", 100.0, 45.0, 5.0, self.user, 2)

    def test_empty_title_raises(self):
        with self.assertRaises(ValueError):
            Place("", "Desc", 100.0, 45.0, 5.0, self.user, 2)

    def test_negative_price_raises(self):
        with self.assertRaises(ValueError):
            Place("Title", "Desc", -1.0, 45.0, 5.0, self.user, 2)

    def test_latitude_out_of_bounds_raises(self):
        with self.assertRaises(ValueError):
            Place("Title", "Desc", 50.0, -91.0, 5.0, self.user, 2)

    def test_longitude_out_of_bounds_raises(self):
        with self.assertRaises(ValueError):
            Place("Title", "Desc", 50.0, 45.0, 181.0, self.user, 2)

    def test_invalid_owner_type_raises(self):
        with self.assertRaises(TypeError):
            Place("Title", "Desc", 50.0, 45.0, 5.0, "not_a_user", 2)

    def test_max_person_less_than_one_raises(self):
        with self.assertRaises(ValueError):
            Place("Title", "Desc", 50.0, 45.0, 5.0, self.user, 0)

    def test_add_valid_review(self):
        place = Place("House", "Desc", 100.0, 45.0, 5.0, self.user, 2)
        review = Review("Nice", 5, place, self.user)
        place.add_review(review)
        self.assertIn(review, place.reviews)

    def test_add_invalid_review_type_raises(self):
        place = Place("House", "Desc", 100.0, 45.0, 5.0, self.user, 2)
        with self.assertRaises(TypeError):
            place.add_review("not_a_review")

    def test_add_valid_amenity(self):
        place = Place("House", "Desc", 100.0, 45.0, 5.0, self.user, 2)
        amenity = Amenity("Wi-Fi")
        place.add_amenity(amenity)
        self.assertIn(amenity, place.amenities)

    def test_add_invalid_amenity_type_raises(self):
        place = Place("House", "Desc", 100.0, 45.0, 5.0, self.user, 2)
        with self.assertRaises(TypeError):
            place.add_amenity(123)

if __name__ == '__main__':
    unittest.main()
