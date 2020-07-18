from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Listing, User

"""
TODO:
* prices don't handle decimals!

"""


CATEGORIES = (("LAP", "Laptop"), ("CON", "Console"), ("GAD", "Gadget"), ("GAM", "Game"), ("TEL", "TV"))


class NewListingForm(forms.Form):
    user = User
    title = forms.CharField(max_length=64)
    description = forms.CharField(max_length=256)
    starting_bid = forms.IntegerField()
    price = forms.IntegerField()
    image_url = forms.URLField(max_length=200)
    category = forms.ChoiceField(choices=CATEGORIES)
    active = forms.BooleanField()

    """
    CATEGORIES = (("LAP", "Laptop"), ("CON", "Console"), ("GAD", "Gadget"), ("GAM", "Game"), ("TEL", "TV"))
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    starting_bid = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    image_url = models.URLField(max_length=200)
    category = models.CharField(max_length=8, choices=CATEGORIES)
    active = models.BooleanField()
    """


# class EditEntryForm(forms.Form):
#     title = forms.CharField(label="Edit Entry")
#     content = forms.CharField(widget=forms.Textarea)


@login_required(login_url="auctions:login")
def index(request):
    user = request.user
    listings = Listing.objects.all().filter(user=user)
    return render(request, "auctions/index.html", {"listings": listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {"message": "Invalid username and/or password."})
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {"message": "Passwords must match."})

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {"message": "Username already taken."})
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url="auctions:login")
def create(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        return render(request, "auctions/create.html", {"form": form})

    return render(request, "auctions/create.html", {"form": NewListingForm()})
