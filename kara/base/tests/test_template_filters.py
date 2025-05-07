from django.template import Context, Template
from django.test import SimpleTestCase


class FileNameTests(SimpleTestCase):

    def test_file_name_filter(self):
        template = Template("{% load base_filters %}{{ value|file_name }}")
        cases = [
            ("cake/cheeze_cake.jpg", "cheeze_cake.jpg"),
            ("bread/cake/strawberry_cake.png", "strawberry_cake.png"),
            ("blueberry_cake.jpeg", "blueberry_cake.jpeg"),
        ]
        for value, expected_value in cases:
            with self.subTest(case=value):
                context = Context({"value": value})
                rendered = template.render(context)
                self.assertEqual(rendered, expected_value)
