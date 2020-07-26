import random

from django_seed import Seed

from auctions.models import Bid, Comment, Listing, User

from .static.auctions.utils import FOTO_URLS, TITLES

SEEDER = Seed.seeder()

AMOUNT = 15
MIN = 5
MAX = 84

PRICE = lambda x: random.randint(MIN, MAX)
FOTO_URL = lambda x: random.choice(FOTO_URLS)
TITLE = lambda x: random.choice(TITLES)

SEEDER.add_entity(User, AMOUNT)
SEEDER.add_entity(Listing, AMOUNT, {"title": TITLE, "starting_bid": PRICE, "price": PRICE, "image_url": FOTO_URL,})
SEEDER.add_entity(Bid, AMOUNT)
SEEDER.add_entity(Comment, AMOUNT)


SEEDER.execute()  # returns inserted pk's
