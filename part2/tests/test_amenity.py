import unittest
from app.models.amenity import Amenity

class TestAmenityModel(unittest.TestCase):
    def test_create_valid_amenity(self):
        amenity = Amenity("Wi-Fi")
        self.assertEqual(amenity.name, "Wi-Fi")

    def test_create_with_non_string_name(self):
        with self.assertRaises(TypeError) as context:
            Amenity(123)
        self.assertIn("not a string", str(context.exception))

    def test_create_with_empty_name(self):
        with self.assertRaises(ValueError) as context:
            Amenity("")
        self.assertIn("required", str(context.exception))

    def test_create_with_name_too_long(self):
        long_name = "x" * 51
        with self.assertRaises(ValueError) as context:
            Amenity(long_name)
        self.assertIn("maximum of 50 characters", str(context.exception))

if __name__ == '__main__':
    unittest.main()
