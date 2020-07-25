# pylint: disable=C0114

from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Bid, Comment, Listing, User, Watchlist

CATEGORIES = (("LAP", "Laptop"), ("CON", "Console"), ("GAD", "Gadget"), ("GAM", "Game"), ("TEL", "TV"))


class NewListingForm(forms.Form):
    user = User
    title = forms.CharField(max_length=64)
    description = forms.CharField(max_length=256)
    starting_bid = forms.IntegerField()
    image_url = forms.URLField(max_length=200)
    category = forms.ChoiceField(choices=CATEGORIES)


def index(request):
    active_listings = Listing.objects.all().filter(active=True)
    return render(request, "auctions/index.html", {"listings": active_listings})


@login_required(login_url="auctions:login")
def watchlist(request):
    user = User.objects.get(username=request.user)
    watch_list = Watchlist.objects.get(user=user)
    return render(request, "auctions/watchlist.html", {"listings": watch_list.listing.all()})


def categories(request):
    return render(request, "auctions/categories.html", {"categories": CATEGORIES})


def category(request, category_param):
    listings = Listing.objects.filter(category=category_param)
    fetched_category = listings[0].get_category_display
    return render(request, "auctions/category.html", {"listings": listings, "category": fetched_category})


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
        listing = Listing()
        listing.user = User.objects.get(username=request.user)
        listing.title = request.POST["title"]
        listing.description = request.POST["description"]
        listing.starting_bid = request.POST["starting-bid"]
        listing.price = listing.starting_bid
        listing.image_url = request.POST["url"]
        listing.category = request.POST["category"]
        listing.active = True
        listing.save()

        return HttpResponseRedirect(reverse("auctions:index"))

    return render(request, "auctions/create.html", {"categories": CATEGORIES})


def listing(request, listing_id):
    is_watched = False
    is_owner = False
    winner = None

    fetched_listing = Listing.objects.filter(pk=listing_id)
    comments = Comment.objects.filter(listing=fetched_listing[0])

    if request.user.is_authenticated:
        user = User.objects.get(username=request.user)

        try:
            is_owner = bool(Listing.objects.get(user=user, pk=fetched_listing[0].pk))
        except Listing.DoesNotExist:
            is_owner = False

        if request.method == "POST":
            if "watch" in request.POST:
                toggle_watched(user, fetched_listing)
                return HttpResponseRedirect(reverse("auctions:listing", kwargs={"listing_id": listing_id}))

            elif "close" in request.POST:
                close_listing(fetched_listing)
                return HttpResponseRedirect(reverse("auctions:listing", kwargs={"listing_id": listing_id}))

            if "bid" in request.POST:
                if request.POST["bid"] == "":
                    messages.add_message(request, messages.ERROR, "Please enter a bid", extra_tags="bid")
                    return HttpResponseRedirect(reverse("auctions:listing", kwargs={"listing_id": listing_id}))

                bid = int(request.POST["bid"])

                # if bid was placed successfully it returns 0
                if place_bid(bid, user, fetched_listing) == 0:
                    messages.add_message(request, messages.SUCCESS, "Success")

                    return HttpResponseRedirect(reverse("auctions:listing", kwargs={"listing_id": listing_id}))
                else:
                    messages.add_message(request, messages.ERROR, "The bid was too low")
                    return HttpResponseRedirect(reverse("auctions:listing", kwargs={"listing_id": listing_id}))

            if "comment" in request.POST:
                if request.POST["comment"] == "":

                    # extra_tags in message to filter on message types in template
                    messages.add_message(request, messages.ERROR, "Please enter a comment", extra_tags="comment")
                    return HttpResponseRedirect(reverse("auctions:listing", kwargs={"listing_id": listing_id}))

                comment = request.POST["comment"]
                place_comment(user, comment, fetched_listing)
                return HttpResponseRedirect(reverse("auctions:listing", kwargs={"listing_id": listing_id}))

        if not fetched_listing[0].active:
            winner = get_winner(fetched_listing)

        listing_in_watchlist = Watchlist.objects.filter(user=user, listing=fetched_listing[0])
        is_watched = bool(listing_in_watchlist)

    return render(
        request,
        "auctions/listing.html",
        {
            "listing": fetched_listing[0],
            "comments": comments,
            "is_watched": is_watched,
            "is_owner": is_owner,
            "winner": winner,
            "user": user,
        },
    )


def toggle_watched(user, listing_param):
    # if watchlist is not found create it
    try:
        watch_list = Watchlist.objects.get(user=user)
    except (UnboundLocalError, Watchlist.DoesNotExist):
        watch_list = Watchlist()
        watch_list.user = user
        watch_list.save()

    listing_in_watchlist = Watchlist.objects.filter(user=user, listing=listing_param[0])
    is_watched = bool(listing_in_watchlist)

    if is_watched:
        watch_list.listing.remove(Listing.objects.get(pk=listing_param[0].pk))
    else:
        watch_list.listing.add(Listing.objects.get(pk=listing_param[0].pk))


def place_bid(bid, user, listing_param):
    fetched_listing = Listing.objects.get(pk=listing_param[0].pk)

    if bid > fetched_listing.price:
        # place bid
        new_bid = Bid()
        new_bid.user = user
        new_bid.amount = bid
        new_bid.listing = fetched_listing[0]
        new_bid.save()

        # update price
        fetched_listing.price = bid
        fetched_listing.save()
        return 0
    else:
        return 1


def close_listing(listing_param):
    fetched_listing = Listing.objects.get(pk=listing_param[0].pk)
    fetched_listing.active = False
    fetched_listing.save()


def get_winner(listing_param):
    fetched_bids = Bid.objects.all().filter(listing=listing_param[0])
    winner = fetched_bids.order_by("amount").first()
    return winner


def place_comment(user, comment, listing_param):
    fetched_comment = Comment(user=user, listing=listing_param[0], content=comment)
    fetched_comment.save()
