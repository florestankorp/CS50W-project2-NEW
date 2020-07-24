from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "auctions"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category>", views.category, name="category"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
]
