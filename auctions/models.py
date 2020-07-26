from django.contrib.auth.models import AbstractUser
from django.db import models

from .static.auctions.utils import CATEGORIES


class User(AbstractUser):
    pass


class Listing(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=256)
    starting_bid = models.PositiveSmallIntegerField()
    price = models.PositiveSmallIntegerField()
    image_url = models.URLField(max_length=256)
    category = models.CharField(max_length=8, choices=CATEGORIES)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"


class Bid(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} bids {self.amount} on {self.listing}"


class Comment(models.Model):
    content = models.CharField(max_length=256)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.listing} by {self.user}"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ManyToManyField(Listing, blank=True)

    def __str__(self):
        return f"{self.user}"
