from django.test import SimpleTestCase

from kara.base.utils import get_contrast_color


class BaseUtilsTests(SimpleTestCase):

    def test_get_contrast_color(self):
        cases = [
            ("#FFFFFF", "black"),  # White
            ("#000000", "white"),  # Black
            ("#FF0000", "white"),  # LightRed
            ("#00FF00", "black"),  # LightGreen
            ("#0000FF", "white"),  # DarkBlue
            ("#FFFF00", "black"),  # LightYellow
            ("808080", "black"),  # MiddleGrey
            ("C0C0C0", "black"),  # ShallowGrey
            ("#FFA500", "black"),  # MiddleLightOrange
            ("#333", "white"),  # DarkGrey
        ]
        for hex_code, expected_color in cases:
            with self.subTest(hex_code=hex_code):
                color = get_contrast_color(hex_code)
                self.assertEqual(color, expected_color)
