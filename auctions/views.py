from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import NewListForm
from .models import User,Listing,Bid,Comment,Tag


def index(request):
    return render(request, "auctions/index.html",{
        "listings":Listing.objects.all()
    })


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

#this func ccreates a new listing       
@login_required
def create(request):
    if request.method=="POST":
        form=NewListForm(request.POST,request.FILES)#get our form 
        if form.is_valid():#commit form data to a model
            instance=form.save(commit=False)
            instance.seller=request.user
            instance.save()
            tag=form.cleaned_data['tag']
            instance.tag.set(tag)
            instance.save()
            return HttpResponseRedirect(reverse('index'))
        else:#invalid form
            return render(request,"auctions/create.html",{
                "form":form
            })
    return render(request,"auctions/create.html",{#create the form
        "form":NewListForm()
            })   
#renders our listing page
def listing(request,listing):
    flag=0
    seller_flag=0
    winner_flag=0
    item=Listing.objects.get(name__iexact=listing)#item we are viewing
    tag=item.tag.all()
    comments=item.comments.all()
    if not request.user.is_anonymous:
        user=User.objects.get(username__iexact=request.user)
        if user.watch.filter(name=listing):#check if user is already watching the item
            flag=1
        if item.seller==request.user:#check if the user is our seller
            seller_flag=1  
        if item.current_bidder==request.user:#check if user has won the bid
            winner_flag=1                 
    return render(request,"auctions/listing.html",{
        "listing":item,"tags":tag,"comments":comments,"watchflag":flag,"sellerflag":seller_flag,"winnerflag":winner_flag
    })
#function to render our watchlist and to add or remove items from our watch list    
@login_required
def watchlist(request):    
    user=User.objects.get(username__iexact=request.user)
    if request.method=='POST':
        listing=request.POST["listing"]
        item=Listing.objects.get(name__iexact=listing)
        if  user.watch.filter(name=listing):#check if our item is in our watch list than we know to remove it
            user.watch.remove(item)
            messages.success(request,'Removed from watch list')
            return HttpResponseRedirect(reverse('listing', args=[listing]))
        #else add the item    
        user.watch.add(item)
        messages.success(request,'Added to watch list')
        return HttpResponseRedirect(reverse('listing', args=[listing]))
    return render(request,"auctions/watchlist.html",{
        "watches":user.watch.all()
    })

#func to create a bid for an item    
@login_required
def bid(request):
    user=User.objects.get(username__iexact=request.user)
    if request.method=='POST':
        name=request.POST["listing"]
        listing=Listing.objects.get(name__iexact=name)
        if not request.POST['bid']:#check if a bid has been enter
            messages.error(request,'Bid must be entered')
            return HttpResponseRedirect(reverse('listing',args=[name]))
        bid=float(request.POST["bid"])#if we do have a bid
        if(bid<=0):#check that the bid is positive
            messages.error(request,'Bid must be positive')
            return HttpResponseRedirect(reverse('listing',args=[name]))
        if (listing.price>bid):#check that the bid is higher than the current bid
            messages.error(request,'Bid must be higher then current price')
            return HttpResponseRedirect(reverse('listing',args=[name]))
        query= Bid.objects.filter(name__name=listing)    
        if(query):#if we have a bid already update that bid to the new one
           query.update(price=bid)
           listing.price=bid
           listing.current_bidder=user
           listing.save()
        else:#if we dont have any bids yet create a new bid
            query=Bid(name=listing,price=bid,bidder=user) 
            query.save()
            listing.price=bid
            listing.current_bidder=user
            listing.save()

        
        messages.success(request,'Bid entered')
        return HttpResponseRedirect(reverse('listing',args=[name]))
#func to close a listing
@login_required
def closelist(request,listing):
    if request.method=='POST':
        item=Listing.objects.get(name__iexact=listing)
        item.status=False
        item.save()
        return HttpResponseRedirect(reverse('listing',args=[listing]))
#func to create comments
@login_required
def comment(request,listing):
    user=User.objects.get(username__iexact=request.user)
    if request.method=='POST':
        item=Listing.objects.get(name__iexact=listing)#check what item we are commenting on
        comment=request.POST["comment"]#get our comment
        query=Comment(item=item,commenter=user,text=comment)#create it
        query.save()
        item.comments.add(query)
        return HttpResponseRedirect(reverse('listing',args=[listing]))
#func to filter by catagories
def category(request,cat):
    all_cat=Tag.objects.all()
    flag=False
    if cat=='all':#if we filter by all
        return render(request,"auctions/category.html",{
            "category":None,"listings":None,"allcats":all_cat,"flag":flag
        })
    flag=True;    
    listings=Listing.objects.filter(tag__name=cat)#if we filter by a specific catagory
    return render(request,"auctions/category.html",{
        "listings":listings,"category":cat,"allcats":all_cat,"flag":flag
    })

#func to check your bids and render them to a page    
@login_required
def mybids(request):
   try:
        bids=Listing.objects.filter(current_bidder__username=request.user).filter(status=True)
   except Bid.DoesNotExist:
        bids=None  
   try:
        won_bids=Listing.objects.filter(current_bidder__username=request.user).filter(status=False)
   except Listing.DoesNotExist:
        won_bids=None    
   return render(request,"auctions/userbids.html",{
        "bids":bids,"wonbids":won_bids
    })


