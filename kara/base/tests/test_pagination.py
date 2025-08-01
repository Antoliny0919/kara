from django.test import RequestFactory, TestCase

from kara.accounts.factories import UserFactory
from kara.accounts.models import User
from kara.base.pagination import Pagination


class PaginationTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        for i in range(1, 101):
            UserFactory.create(username=f"user-{i}")
        cls.queryset = User.objects.all().order_by("id")
        cls.factory = RequestFactory()

    def test_pagination(self):
        request = self.factory.get("/fake-url/")
        pagination = Pagination(request, self.queryset, 5)
        self.assertEqual(pagination.result_count, 100)
        self.assertTrue(pagination.multi_page)
        pagination = Pagination(request, self.queryset, 200)
        self.assertFalse(pagination.multi_page)

    def test_pagination_page_range(self):
        request = self.factory.get("/fake-url/")
        ELLIPSIS = "…"
        case = [
            (2, 6, [1, 2, 3, 4, 5, 6, 7, 8, 9, ELLIPSIS, 49, 50]),
            (3, 10, [1, 2, ELLIPSIS, 7, 8, 9, 10, 11, 12, 13, ELLIPSIS, 33, 34]),
            (4, 23, [1, 2, ELLIPSIS, 20, 21, 22, 23, 24, 25]),
            (5, 20, [1, 2, ELLIPSIS, 17, 18, 19, 20]),
            (10, 8, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
            (20, 1, [1, 2, 3, 4, 5]),
        ]
        for list_per_page, current_page, expected_page_range in case:
            with self.subTest(list_per_page=list_per_page, current_page=current_page):
                pagination = Pagination(request, self.queryset, list_per_page)
                pagination.page_num = current_page
                self.assertEqual(list(pagination.page_range), expected_page_range)

    def test_pagination_result_objects(self):
        request = self.factory.get("/fake-url/")
        case = [
            (2, 25, ["49", "50"]),
            (4, 12, ["45", "46", "47", "48"]),
            (5, 10, ["46", "47", "48", "49", "50"]),
            (7, 11, ["71", "72", "73", "74", "75", "76", "77"]),
            (10, 10, ["91", "92", "93", "94", "95", "96", "97", "98", "99", "100"]),
            (200, 1, [str(i) for i in range(1, 101)]),
        ]
        User.objects.all().delete()
        for i in range(1, 101):
            UserFactory.create(username=i)
        queryset = User.objects.all().order_by("id")
        for list_per_page, current_page, expect_object_names in case:
            pagination = Pagination(request, queryset, list_per_page)
            pagination.page_num = current_page
            objects = pagination.get_objects()
            object_names = list(objects.values_list("username", flat=True))
            self.assertEqual(object_names, expect_object_names)
