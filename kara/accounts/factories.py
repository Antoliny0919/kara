import factory
from django.db.models.signals import post_save

from .models import User, UserProfile


@factory.django.mute_signals(post_save)
class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory("accounts.factories.UserFactory", profile=None)


@factory.django.mute_signals(post_save)
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "user_%d" % n)
    email = "example@example.com"
    profile = factory.RelatedFactory(ProfileFactory, factory_related_name="user")
