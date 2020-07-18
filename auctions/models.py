from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Listing(models.Model):
    CATEGORIES = (("LAP", "Laptop"), ("CON", "Console"), ("GAD", "Gadget"), ("GAM", "Game"), ("TEL", "TV"))
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    starting_bid = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    image_url = models.URLField(max_length=200)
    category = models.CharField(max_length=8, choices=CATEGORIES)
    active = models.BooleanField()

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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    listing = models.ManyToManyField(Listing, blank=True)
    # user can only have one watchlist!

    def __str__(self):
        return f"{self.user}"
