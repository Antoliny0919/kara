from django.db import models


class Fruit(models.Model):
    name = models.CharField(max_length=255, verbose_name="name label")
    price = models.IntegerField(verbose_name="price label")
    expiration_date = models.DateField()


class Cake(models.Model):
    KIND_CHOICES = [
        ("cheese", "Cheese"),
        ("chocolate", "Chocolate"),
        ("blueberry", "Blueberry"),
    ]
    name = models.CharField(max_length=100)
    kind = models.CharField(choices=KIND_CHOICES)
    kind_detail = models.TextField()
    price = models.IntegerField()


class Character(models.Model):
    nickname = models.CharField(max_length=100)
    level = models.IntegerField(default=0)
    skill = models.ForeignKey("Skill", on_delete=models.SET_NULL, null=True)


class Skill(models.Model):
    name = models.CharField(max_length=100)
    damage = models.IntegerField()
