import unittest

from phone_inspector import PhoneInputError, inspect_number


class InspectNumberTests(unittest.TestCase):
    def test_iranian_number_with_persian_digits_is_normalized_and_formatted(self):
        details = inspect_number("۰۹۱۲ ۱۲۳ ۴۵۶۷")

        self.assertTrue(details.valid)
        self.assertTrue(details.possible)
        self.assertEqual(details.country_calling_code, "+98")
        self.assertEqual(details.region_code, "IR")
        self.assertEqual(details.number_type, "تلفن همراه")
        self.assertEqual(details.e164, "+989121234567")
        self.assertEqual(details.international, "+98 912 123 4567")

    def test_international_number_ignores_default_region(self):
        details = inspect_number("+1 202-555-0123", "IR")

        self.assertEqual(details.country_calling_code, "+1")
        self.assertEqual(details.region_code, "US")
        self.assertEqual(details.e164, "+12025550123")

    def test_impossible_number_is_reported_instead_of_accepted(self):
        details = inspect_number("123", "IR")

        self.assertFalse(details.possible)
        self.assertFalse(details.valid)

    def test_empty_input_has_user_facing_error(self):
        with self.assertRaisesRegex(PhoneInputError, "وارد نشده"):
            inspect_number("  ")

    def test_letters_are_rejected(self):
        with self.assertRaisesRegex(PhoneInputError, "نویسه‌های مجاز"):
            inspect_number("0912abc4567")

    def test_unparseable_number_has_user_facing_error(self):
        with self.assertRaises(PhoneInputError):
            inspect_number("++")


if __name__ == "__main__":
    unittest.main()
