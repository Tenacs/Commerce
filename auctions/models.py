from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', blank=True, related_name="watchlists")


class Listing(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    startingBid = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    image = models.CharField(max_length=255, default=None)
    category = models.CharField(max_length=50, default="No Category Listed")
    timestamp = models.DateTimeField(auto_now_add=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="winner", default=None, null=True)

    def __str__(self):
        return f"{self.title} id:{self.id} : {self.description} --- Starting Bid: {self.startingBid} --- user: {self.user} --- category: {self.category} --- image: {self.image}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    timestamp = models.DateTimeField(auto_now_add=True)
    bid = models.DecimalField(max_digits=10, decimal_places=2)

    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenters")
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    comment = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)