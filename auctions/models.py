from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    watchlist = models.TextField(default="[]")

class Categorie(models.Model):
    category = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.category}"

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=512)
    starting_bid = models.IntegerField()
    current_price = models.IntegerField()
    time = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name="items_of_category")
    lister = models.ForeignKey(User, on_delete=models.CASCADE, related_name="active_items")
    active = models.BooleanField(default=True)
    image = models.URLField(null=True)

    def __str__(self):
        return f"{self.title}"

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids_of_user")
    price = models.IntegerField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids_of_listing")
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.listing} for {self.price}"

class Comment(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments_of_item")
    comment = models.CharField(max_length=1024)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments_of_listing")
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.commenter} on {self.listing}"

