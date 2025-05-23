import factory

from kara.accounts.factories import UserFactory

from .models import CashGift, WeddingGiftRegistry


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
