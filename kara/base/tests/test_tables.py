from django.test import RequestFactory, TestCase

from kara.base.tables import Table

from .models import Character, Fruit, Skill


class FruitTable(Table):
    pass


class CharacterTable(Table):
    pass


class TableTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Fruit.objects.create(name="hello", price=10000, expiration_date="2024-12-31")
        cls.factory = RequestFactory()
        cls.model = Fruit
        cls.queryset = Fruit.objects.all()

    def test_table_columns(self):
        request = self.factory.get("/fake-url/")
        table = FruitTable(request, self.model, self.queryset)
        self.assertEqual(table.columns, ["id", "name", "price", "expiration_date"])
        self.assertEqual(
            table.verbose_columns,
            ["Who are you!!", "Price expensive!!", "expiration date"],
        )


class TableSearchTest(TestCase):
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
        characters = [Character(nickname=name) for name in case]
        Character.objects.bulk_create(characters)
        cls.queryset = Character.objects.all().order_by("id")
        cls.factory = RequestFactory()

    def test_search(self):
        cases = [
            ("sky", ["nickname"], ["Blue Sky", "Red Sky"]),
            ("sunny hill", ["nickname__iexact"], ["Sunny Hill"]),
            (
                "Happy",
                ["nickname__startswith"],
                ["Happy Cloud", "Happy Hills", "Happy Sunday"],
            ),
            (
                "Sky",
                ["nickname__startswith", "nickname__endswith"],
                ["Blue Sky", "Red Sky", "Sky Rain"],
            ),
        ]
        request = self.factory.get("/fake-url/")
        table = CharacterTable(request, Character, self.queryset)
        for value, search_fields, expected_results in cases:
            with self.subTest(search_fields=search_fields, value=value):
                table.search_fields = search_fields
                queryset = table.get_search_result(self.queryset, value)
                result = list(queryset.values_list("nickname", flat=True))
                for expected_result in expected_results:
                    self.assertIn(expected_result, result)

    def test_invalid_field_set_search_field(self):
        request = self.factory.get("/fake-url/")
        table = CharacterTable(request, Character, self.queryset)
        table.search_fields = ["level"]
        with self.assertRaises(TypeError) as error:
            table.get_search_result(self.queryset, "invalid")
        self.assertEqual(
            str(error.exception),
            "Search logic only supports fields of type `CharField` or `TextField`"
            '("level" field type is `IntegerField`)',
        )

    def test_relation_field_search(self):
        character = Character.objects.get(nickname="Fast Rabbit")
        skill = Skill.objects.create(name="Fire Rain", damage=100)
        character.skill = skill
        character.save()
        request = self.factory.get("/fake-url/")
        table = CharacterTable(request, Character, self.queryset)
        table.search_fields = ["skill__name__exact"]
        queryset = table.get_search_result(self.queryset, "Fire Rain")
        self.assertEqual(queryset[0].nickname, "Fast Rabbit")

    def test_multiple_field_search(self):
        character = Character.objects.get(nickname="Sky Rain")
        skill = Skill.objects.create(name="Make Happy", damage=0)
        character.skill = skill
        character.save()
        request = self.factory.get("/fake-url/")
        table = CharacterTable(request, Character, self.queryset)
        table.search_fields = ["nickname__startswith", "skill__name"]
        queryset = table.get_search_result(self.queryset, "Happy")
        result = list(queryset.values_list("nickname", flat=True))
        expected_username = ["Happy Cloud", "Happy Hills", "Happy Sunday", "Sky Rain"]
        for username in expected_username:
            self.assertIn(username, result)
