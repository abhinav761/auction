from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .models import *
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django import forms

from django import forms
class ListForm(forms.Form):
    name = forms.CharField(
        label="Title",
        max_length=65,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500 bg-white text-gray-900',
            'placeholder': 'Enter a descriptive title for your item',
            'style': 'font-family: Amazon Ember, Arial, sans-serif; font-size: 14px;'
        })
    )
    
    price = forms.DecimalField(
        label="Starting Bid",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full pl-8 pr-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500 bg-white text-gray-900',
            'placeholder': '0.00',
            'min': '0.01',
            'step': '0.01',
            'style': 'font-family: Amazon Ember, Arial, sans-serif; font-size: 14px;'
        })
    )
    
    image = forms.URLField(
        label="Image URL",
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'w-full px-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500 bg-white text-gray-900',
            'placeholder': 'https://example.com/image.jpg',
            'style': 'font-family: Amazon Ember, Arial, sans-serif; font-size: 14px;'
        })
    )
    
    category = forms.CharField(
        label="Category",
        max_length=30,
        widget=forms.Select(choices=[
            ('', 'Select a category'),
            ('electronics', 'Electronics'),
            ('clothing', 'Clothing & Accessories'),
            ('home', 'Home & Garden'),
            ('sports', 'Sports & Outdoors'),
            ('automotive', 'Automotive'),
            ('books', 'Books & Media'),
            ('collectibles', 'Collectibles'),
            ('other', 'Other')
        ], attrs={
            'class': 'w-full px-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500 bg-white text-gray-900 appearance-none',
            'style': 'font-family: Amazon Ember, Arial, sans-serif; font-size: 14px;'
        })
    )

class BidForm(forms.Form):
    price = forms.DecimalField(
        label="Bid Amount",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full pl-8 pr-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500 bg-white text-gray-900',
            'placeholder': '$0.00',
            'min': '0.01',
            'step': '0.01',
            'style': 'font-family: Amazon Ember, Arial, sans-serif; font-size: 14px;'
        })
    )
    



def index(request):
    listings = Listing.objects.filter(is_active=True)
    return render(request, "auctions/index.html",{"listings":listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
def add_bid(request,product_id):
    user_id = request.user.id
    product=Listing.objects.get(pk=product_id)
    auctioner=product.auctioner.all().first()
    if request.method=='POST':
        form=BidForm(request.POST)
        if form.is_valid():
            user=User.objects.get(pk=user_id) #user object of the page
            product = Listing.objects.get(pk=product_id)           
            a=product.base_price #baseprice of listing
            price=form.cleaned_data["price"]
            if price>a:
                product.base_price=price 
                product.save() #newbid price is highest
                all_bids=product.product_bids.all() 
                for bid in all_bids:
                    bid.status="outbid" #all bids get outbid
                Bids.objects.create(
                    price=request.POST["price"],
                    bidder=user,
                    bid_product=product)
                #create new bid
                return HttpResponseRedirect(reverse("listing",args=[product_id]))
            else:
                return render(request,'auctions/addbid.html',{
                    'form':form,
                    "status":f"Bidding Failed you need to bid Higher than {a}",
                    'product':product,
                    'auctioner':auctioner})
    else:
        form=BidForm()
        product=Listing.objects.get(pk=product_id) #product object for bid
        return render(request,'auctions/addbid.html',{'form':form,"status":None,'product':product,'auctioner':auctioner})



#done with listing
@login_required
def add_listing(request):
    if request.method == 'POST':
        form = ListForm(request.POST)    
        if form.is_valid():
            user1 = request.user
            user = User.objects.get(pk=user1.pk)
            name = form.cleaned_data['name']
            price = form.cleaned_data['price']
            image = form.cleaned_data['image']
            category=form.cleaned_data['category']
            # Create new listing
            listing = Listing.objects.create(
                product_name=name,
                base_price=price,
                product_image=image,
                category=category
            )
            user.auctions.add(listing)

            return redirect('listing', product_id=listing.pk)  # Redirect to the listing detail view
    else:
        if request.user.is_authenticated:
            form=ListForm()
            return render(request,'auctions/addlisting.html',{'form':form})
        else:
            return redirect('login')
def close_listing(request,product_id):
    product=Listing.objects.get(pk=product_id) 
    product.is_active=False
    product.save()
    bids=product.product_bids.all()
    for bid in bids:
        if bid.status =="highest":
            bid.status="win"
        else:
            bid.status="lost"
    return redirect('listing',product_id=product_id)


def add_comment(request,product_id):
    if request.user.is_authenticated:
        user_id = request.user.id
        if request.method=='POST':
            c=request.POST["content"]
            user=User.objects.get(pk=user_id)
            p=Listing.objects.get(pk=product_id)
            Comments.objects.create(name=user,product=p,comment_content=c)
            return redirect('listing',product_id=product_id)
        else:
            return render(request,'auctions/listing.html',{'product_id':product_id})

def listing(request,product_id):
    thisproduct=Listing.objects.get(pk=product_id)
    content=Comments.objects.filter(product=thisproduct)
    product=Listing.objects.get(pk=product_id)
    
    if request.user.is_authenticated:
        user = request.user
        outbids=product.product_bids.filter(status="outbid")
        outbiders=[outbid.bidder for outbid in outbids]
        highestbid=product.product_bids.filter(status="highest").first()
        highestbidder=highestbid.bidder if highestbid else None
        auctioner=product.auctioner.all().first()
        is_in_watchlist = user.watchlist.filter(pk=product.pk).exists()
        return render(request,"auctions/listing.html",{
            "user":user,
            "product":product,
            'comments':content,
            'outbiders':outbiders,
            'highestbidder':highestbidder,
            'auctioner':auctioner,
            'is_in_watchlist': is_in_watchlist,})
    else:
        user = request.user
        auctioner=product.auctioner.all().first()
        product=Listing.objects.get(pk=product_id)
        outbids=product.product_bids.filter(status="outbid")
        outbiders=[outbid.bidder for outbid in outbids]
        highestbid=product.product_bids.filter(status="highest").first()
        highestbidder=highestbid.bidder if highestbid else None
        return render(request,"auctions/listing.html",{
            "user":user,
            "product":product,
            'comments':content,
            'outbids':outbids,
            'highestbidder':highestbidder,
            'auctioner':auctioner,
            'is_in_watchlist': True})
#sucess
def users(request):
    user_profile = User.objects.get(id=request.user.id)
    watchlist=user_profile.watchlist.all()
    auctions=user_profile.auctions.all()
    userbids=user_profile.user_bids.all()
    usercomments=user_profile.user_comments.all()
    return render(request,'auctions/user.html',{
        'user':user_profile,
        "watchlist":watchlist,
        'auctions':auctions,
        'userbids':userbids,
        "usercomments":usercomments})

def watchlist(request,product_id):
    product=Listing.objects.get(pk=product_id)
    user=User.objects.get(pk=request.user.id)
    user.watchlist.add(product)
    return redirect(reverse('listing',kwargs={'product_id': product_id}))

def category(request):
    products = Listing.objects.filter(is_active=True)
    categories = list(set([product.category for product in products]))
    category = request.POST.get('category') or None
    if category:
        products = products.filter(category=category)
    return render(request, 'auctions/category.html', {
        'category': category,
        'categories': categories,
        'products': products,
    })
