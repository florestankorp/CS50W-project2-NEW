from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Comment, Listing, User, Watchlist

"""
TODO:
* prices don't handle decimals!

"""


CATEGORIES = ["Laptop", "Console", "Gadget", "Game", "TV"]


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
    # form = NewListingForm(request.POST)

    # if request.method == "POST" and form.is_valid():
    #     listing = Listing()
    #     listing.user = User.objects.get(username=request.user)
    #     listing.title = request.POST["title"]
    #     listing.description = request.POST["description"]
    #     listing.starting_bid = request.POST["starting_bid"]
    #     listing.price = listing.starting_bid
    #     listing.image_url = request.POST["image_url"]
    #     listing.category = request.POST["category"]
    #     listing.active = True
    #     listing.save()

    #     return HttpResponseRedirect(reverse("auctions:index"))

    return render(request, "auctions/create.html", {"categories": CATEGORIES})


def listing(request, listing_id):
    is_watched = False
    listing = Listing.objects.all().filter(pk=listing_id)
    comments = Comment.objects.all().filter(listing=listing[0])

    if request.user.is_authenticated:
        user = User.objects.get(username=request.user)

        if request.method == "POST":
            if request.POST.get("watch"):
                toggle_watched(user, listing)
                return HttpResponseRedirect(reverse("auctions:listing", kwargs={"listing_id": listing_id}))

            if "bid" in request.POST:
                if request.POST["bid"] == "":
                    messages.add_message(request, messages.ERROR, "Please enter a bid", extra_tags="bid")
                    return HttpResponseRedirect(reverse("auctions:listing", kwargs={"listing_id": listing_id}))

                bid = int(request.POST["bid"])

                if place_bid(user, bid, listing) == 0:
                    messages.add_message(request, messages.SUCCESS, "Success")
                    return HttpResponseRedirect(reverse("auctions:listing", kwargs={"listing_id": listing_id}))
                else:
                    messages.add_message(request, messages.ERROR, "The bid was too low")
                    return HttpResponseRedirect(reverse("auctions:listing", kwargs={"listing_id": listing_id}))

            if "comment" in request.POST:
                if request.POST["comment"] == "":
                    messages.add_message(request, messages.ERROR, "Please enter a comment", extra_tags="comment")
                    return HttpResponseRedirect(reverse("auctions:listing", kwargs={"listing_id": listing_id}))

                comment = request.POST["comment"]
                place_comment(user, comment, listing)
                return HttpResponseRedirect(reverse("auctions:listing", kwargs={"listing_id": listing_id}))

        listing_in_watchlist = Watchlist.objects.filter(user=user, listing=listing[0])
        is_watched = bool(listing_in_watchlist)

    return render(
        request, "auctions/listing.html", {"listing": listing[0], "comments": comments, "is_watched": is_watched}
    )


def toggle_watched(user, listing):
    try:
        watch_list = Watchlist.objects.get(user=user)
        pass
    except Exception:
        watch_list = Watchlist()
        watch_list.user = user
        watch_list.save()
        pass

    listing_in_watchlist = Watchlist.objects.filter(user=user, listing=listing[0])
    is_watched = bool(listing_in_watchlist)

    if is_watched:
        watch_list.listing.remove(Listing.objects.get(pk=listing[0].pk))
    else:
        watch_list.listing.add(Listing.objects.get(pk=listing[0].pk))


def place_bid(user, bid, listing):
    fetched_listing = Listing.objects.get(pk=listing[0].pk)

    if bid > fetched_listing.price:
        fetched_listing.price = bid
        fetched_listing.save()
        return 0
    else:
        return 1


def place_comment(user, comment, listing):
    fetched_comment = Comment(user=user, listing=listing[0], content=comment)
    fetched_comment.save()


"""

if
- user is signed in
- user is the one who created the listing
- then user should have the ability to “close” the auction from this page, 
- which makes the highest bidder the winner of the auction and 
- which makes the listing no longer active.
"""
