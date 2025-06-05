from django.db import models


class Fruit(models.Model):
    name = models.CharField(max_length=255, verbose_name="Who are you!!")
    price = models.IntegerField(verbose_name="Price expensive!!")
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
