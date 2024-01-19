from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, models
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid, Comment


#get watchlist count
def get_watchlist(request):
    try:
        user = User.objects.get(username=request.user)
    except User.DoesNotExist:
        return None
    return user.watchlist.all().count()



def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all(), 
        "watchlist_count": get_watchlist(request)
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

@login_required
def create(request):
    if request.method == "POST":
        title = request.POST["title"]
        bid = request.POST["bid"]
        description = request.POST["description"]
        image = request.POST["image"]
        category = request.POST["category"]

        Listing(title=title, startingBid=bid, description=description, image=image, user=request.user, category=category).save()

        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/create.html", {
            "watchlist_count": get_watchlist(request)
        })
    

def listing(request, listing_id):
    try:
        listingPage = Listing.objects.get(id=listing_id)
    except Listing.DoesNotExist:
        raise Http404("Listing not found.")
    try:
        user = User.objects.get(username=request.user)
    except User.DoesNotExist:
        user = None
    
    if request.method == "POST":
        comment = request.POST["comment"]

        Comment(user=user, item=listingPage, comment=comment).save()    

    in_watchlist = listingPage in user.watchlist.all()

    return render(request, "auctions/listing.html", {
        "listing": listingPage,
        "bid_count": listingPage.bids.all().count(),
        "watchlist_count": get_watchlist(request),
        "in_watchlist": in_watchlist,
        "message": None,
        "comments": listingPage.comments.all().order_by('-timestamp')
    })


@login_required
def watchlist(request):

    user = User.objects.get(username=request.user)

    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        action = request.POST["action"]

        try:
            listing = Listing.objects.get(id=listing_id)
        except Listing.DoesNotExist:
            raise Http404("Listing not found.")
        
        if action == "add":
            user.watchlist.add(listing)
        elif action == "remove":
            user.watchlist.remove(listing)
        
        return HttpResponseRedirect(reverse("watchlist"))
    
    else:
        return render(request, "auctions/watchlist.html", {
            "watchlist_count": get_watchlist(request),
            "listings": user.watchlist.all()
        })


@login_required
def bid(request):
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        bid = float(request.POST["bid"])

        try:
            listing = Listing.objects.get(id=listing_id)
        except Listing.DoesNotExist:
            raise Http404("Listing not found.")
                  
        max = listing.bids.aggregate(models.Max("bid", default=0))

        if bid < listing.startingBid or bid < max["bid__max"]:
        
            in_watchlist = listing in User.objects.get(username=request.user).watchlist.all()

            return render(request, "auctions/listing.html", {
                "listing": listing,
                "bid_count": listing.bids.all().count(),
                "watchlist_count": get_watchlist(request),
                "in_watchlist": in_watchlist,
                "message": "Bid must be higher than minimum bid",
                "highestBid": max
    })
        else:
            Bid(user=request.user, item=listing, bid=bid).save()
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))
        


def userStore(request, username):
    try:
        user = User.objects.get(username=username)
    except Listing.DoesNotExist:
        raise Http404("User not found.")
    

    return render(request, "auctions/userStore.html", {
        "username": username,
        "watchlist_count": get_watchlist(request),
        "listings": user.listings.all()
    })


@login_required
def close(request):

    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        winner = request.POST["winner"]

        try:
            listing = Listing.objects.get(id=listing_id)
        except Listing.DoesNotExist:
            raise Http404("Listing not found.")
        try:
            winner = User.objects.get(username=winner)
        except Listing.DoesNotExist:
            raise Http404("User not found.")
        
        if request.user != winner:
            listing.winner = winner
            listing.save()

        return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))



def categories(request):
    listings = Listing.objects.order_by().values_list('category').distinct()
    listings = [listing[0] for listing in listings if listing[0].isalnum() and listing[0] != 'none']

    return render(request, "auctions/categories.html", {
        "listings": listings, 
        "watchlist_count": get_watchlist(request)
    })

def category(request, cat):
    if cat in (listing.category for listing in Listing.objects.all()):
        return render(request, "auctions/watchlist.html", {
            "cat": cat,
            "listings": Listing.objects.filter(category=cat), 
            "watchlist_count": get_watchlist(request)
        })
    else:
        raise Http404("Category not found.")
