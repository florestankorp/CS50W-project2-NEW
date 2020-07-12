from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


# class Category(models.Model):
#     name = models.CharField(max_length=64)


class Listing(models.Model):
    CATEGORIES = (("LAP", "Laptop"), ("CON", "Console"), ("GAD", "Gadget"), ("GAM", "Game"), ("TEL", "TV"))
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    starting_bid = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    image_url = models.URLField(max_length=200)
    category = models.CharField(max_length=8, choices=CATEGORIES)
    active = models.BooleanField()

    def __str__(self):
        return f"title: {self.title}"


class Bid(models.Model):
    amount = models.PositiveIntegerField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)


class Comment(models.Model):
    content = models.CharField(max_length=256)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ManyToManyField(Listing, blank=True)
