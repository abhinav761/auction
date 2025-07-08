from django.contrib.auth.models import AbstractUser
from django.db import models
class Listing(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name=models.CharField(max_length=69)
    base_price=models.DecimalField(decimal_places=2,max_digits=10)
    product_image=models.URLField(blank=True)
    category=models.CharField(max_length=20,blank=True)
    is_active=models.BooleanField(default=True)
    listing_time=models.DateField(auto_now_add=True)
    def __str__(self) -> str:
        return f"id: {self.product_id} product: {self.product_name} || price: {self.base_price} ||active: {self.is_active}"

class User(AbstractUser):
    auctions=models.ManyToManyField(Listing,related_name="auctioner",blank=True)
    watchlist=models.ManyToManyField(Listing,related_name='followers',blank=True)
    def __str__(self) -> str:
        return f"name:{self.username}"

class Comments(models.Model):
    name=models.ForeignKey(User,related_name="user_comments",on_delete=models.CASCADE)
    comment_time=models.DateTimeField(auto_now_add=True)
    comment_content=models.CharField(max_length=250)
    product=models.ForeignKey(Listing,related_name='product_comments',on_delete=models.CASCADE)
    def __str__(self) -> str:
        return f"dataitem: \n  user: {self.name}|| product: {self.product.product_name} \n  comment:{self.comment_content} "

class Bids(models.Model):
    price=models.DecimalField(max_digits=10, decimal_places=2)
    bid_time=models.DateTimeField(auto_now_add=True)
    bidder=models.ForeignKey(User,related_name='user_bids',on_delete=models.CASCADE)
    bid_product=models.ForeignKey(Listing,related_name='product_bids',on_delete=models.CASCADE)
    status=models.CharField(default="highest",max_length=30)
    def __str__(self):
        return f"dataitem: \n user: {self.bidder} product: {self.bid_product.product_name} price: {self.price}"

