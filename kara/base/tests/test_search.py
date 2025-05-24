from django.test import RequestFactory, TestCase

from kara.accounts.factories import UserFactory
from kara.accounts.models import User
from kara.base.tables import Table


class UserTable(Table):
    pass


class SearchTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        case = [
            "Blue Fox",
            "Sunny Hill",
            "Blue Sky",
            "Red Sky",
            "Happy Cloud",
            "Fast Rabbit",
            "Happy Hills",
            "Happy Sunday",
            "Sky Rain",
        ]
        for name in case:
            UserFactory(username=name)
        cls.queryset = User.objects.all().order_by("id")
        cls.factory = RequestFactory()

    def test_search(self):
        cases = [
            ("sky", ["username"], ["Blue Sky", "Red Sky"]),
            ("sunny hill", ["username__iexact"], ["Sunny Hill"]),
            (
                "Happy",
                ["username__startswith"],
                ["Happy Cloud", "Happy Hills", "Happy Sunday"],
            ),
            (
                "Sky",
                ["username__startswith", "username__endswith"],
                ["Blue Sky", "Red Sky", "Sky Rain"],
            ),
        ]
        request = self.factory.get("/fake-url/")
        table = UserTable(request, User, self.queryset)
        for value, search_fields, expected_results in cases:
            with self.subTest(search_fields=search_fields, value=value):
                table.search_fields = search_fields
                queryset = table.get_search_result(self.queryset, value)
                result = list(queryset.values_list("username", flat=True))
                for expected_result in expected_results:
                    self.assertIn(expected_result, result)

    def test_invalid_field_set_search_field(self):
        request = self.factory.get("/fake-url/")
        table = UserTable(request, User, self.queryset)
        table.search_fields = ["is_staff"]
        with self.assertRaises(TypeError) as error:
            table.get_search_result(self.queryset, "invalid")
        self.assertEqual(
            str(error.exception),
            "Search logic only supports fields of type `CharField` or `TextField`"
            '("is_staff" field type is `BooleanField`)',
        )

    def test_relation_field_search(self):
        user = User.objects.get(username="Fast Rabbit")
        user.profile.bio = "Hello my name is Fast Rabbit!!!"
        user.profile.save()
        request = self.factory.get("/fake-url/")
        table = UserTable(request, User, self.queryset)
        table.search_fields = ["profile__bio__exact"]
        queryset = table.get_search_result(
            self.queryset, "Hello my name is Fast Rabbit!!!"
        )
        self.assertEqual(queryset[0].username, "Fast Rabbit")

    def test_multiple_field_search(self):
        user = User.objects.get(username="Sky Rain")
        user.profile.bio = "Happy"
        user.profile.save()
        request = self.factory.get("/fake-url/")
        table = UserTable(request, User, self.queryset)
        table.search_fields = ["username__startswith", "profile__bio__exact"]
        queryset = table.get_search_result(self.queryset, "Happy")
        result = list(queryset.values_list("username", flat=True))
        expected_username = ["Happy Cloud", "Happy Hills", "Happy Sunday", "Sky Rain"]
        for username in expected_username:
            self.assertIn(username, result)
