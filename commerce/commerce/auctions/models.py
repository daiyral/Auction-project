from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watch=models.ManyToManyField('Listing',blank=True,related_name="watchlist")

class Tag(models.Model):
    name=models.CharField(max_length=32)

    def __str__(self):
        return f"{self.name}"

class Condition(models.Model):
    name=models.CharField(max_length=32)

    def __str__(self):
        return f"{self.name}"

class Listing(models.Model):
    name=models.CharField(max_length=64)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    date=models.DateTimeField(auto_now=True)
    description=models.TextField(max_length=1000,null=True)
    tag=models.ManyToManyField(Tag,blank=True,related_name="Category")
    condition=models.ForeignKey(Condition,on_delete=models.CASCADE,blank=True)
    image=models.ImageField(upload_to='listing_image',blank=True)
    seller=models.ForeignKey(User,on_delete=models.CASCADE)
    current_bidder=models.ForeignKey(User,on_delete=models.CASCADE,null=True,related_name="bidder")
    status=models.BooleanField(default=True)
    comments=models.ManyToManyField('Comment',blank=True,related_name="comments")
    def __str__(self):
        return f"{self.name}"

class Bid(models.Model):
    name=models.ForeignKey(Listing,on_delete=models.CASCADE)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    date=models.DateTimeField(auto_now=True)
    bidder=models.ForeignKey(User,on_delete=models.CASCADE,null=True)

    def __str__(self):
        return f"{self.bidder} bid:{self.price} on {self.name}"

class Comment(models.Model):
    item=models.ForeignKey(Listing,on_delete=models.CASCADE)
    commenter=models.ForeignKey(User,on_delete=models.CASCADE,related_name="Comments")
    text=models.TextField(max_length=1000)

    def __str__(self):
        return f"{self.commenter} commented on {self.item}"

