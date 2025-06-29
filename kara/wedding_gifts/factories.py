import factory
from factory import fuzzy

from kara.accounts.factories import UserFactory

from .models import CashGift, GiftTag, InKindGift, WeddingGiftRegistry


class GiftTagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GiftTag

    owner = factory.SubFactory(UserFactory)
    name = factory.Faker("name")


class WeddingGiftRegistryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WeddingGiftRegistry

    owner = factory.SubFactory(UserFactory)
    side = factory.Iterator(["Groom", "Bride"])
    receiver = factory.Faker("name")
    receptionist = factory.Faker("name")
    wedding_date = factory.Faker("date_between", start_date="-10y", end_date="today")
    in_kind_gifts_allow = factory.Faker("pybool")


class CashGiftFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CashGift

    registry = factory.SubFactory(WeddingGiftRegistryFactory)
    name = factory.Faker("name")
    price = factory.Faker("random_int", min=10000, max=10000000)
    receipt_date = factory.Faker("date_between", start_date="-10y", end_date="today")


class InKindGiftFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InKindGift

    registry = factory.SubFactory(WeddingGiftRegistryFactory)
    name = factory.Faker("name")
    price = factory.Faker("random_int", min=10000, max=10000000)
    receipt_date = factory.Faker("date_between", start_date="-10y", end_date="today")
    kind = fuzzy.FuzzyChoice(
        [choice[0] for choice in InKindGift.KIND_CHOICES if choice[0] != "other"]
    )
