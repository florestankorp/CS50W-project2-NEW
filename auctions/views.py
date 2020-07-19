from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Comment, Listing, User

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
    image_url = forms.URLField(max_length=200)
    category = forms.ChoiceField(choices=CATEGORIES)


def index(request):
    return render(request, "auctions/index.html", {"listings": Listing.objects.all()})


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
    errors = []
    form = NewListingForm(request.POST)
    print(User.objects.get(username=request.user).pk)

    if request.method == "POST" and form.is_valid():
        listing = Listing()
        listing.user = User.objects.get(username=request.user)
        listing.title = request.POST["title"]
        listing.description = request.POST["description"]
        listing.starting_bid = request.POST["starting_bid"]
        listing.price = listing.starting_bid
        listing.image_url = request.POST["image_url"]
        listing.category = request.POST["category"]
        listing.active = True
        listing.save()

        return HttpResponseRedirect(reverse("auctions:index"))

    return render(request, "auctions/create.html", {"form": NewListingForm()})


def listing(request, listing_id):
    listing = Listing.objects.all().filter(pk=listing_id)
    comments = Comment.objects.all().filter(listing=listing[0])

    return render(request, "auctions/listing.html", {"listing": listing[0], "comments": comments})
