from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import User, Listing, Bid, Comment, Categorie
import json
# from .forms import Listing

def index(request):
    listing_obj_list = Listing.objects.all()
    active_listing_object_list = []
    for lol in listing_obj_list:
        if lol.active is True:
            active_listing_object_list.append(lol)

    return render(request, "auctions/index.html",{
        "active_listings": active_listing_object_list
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
def createlisting(request):
    categories_objects = Categorie.objects.all()
    category_list = []
    for cat_obj in categories_objects:
        category_list.append(cat_obj.category)

    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        bid = request.POST["bid"]
        image = request.POST["image"]
        category = request.POST["category"]
        category_obj = Categorie.objects.get(category=category)
        active = True
        lister = request.user.username
        lister_obj = User.objects.get(username=lister)
        try:
            cl = Listing(title=title, description=description, starting_bid=bid, current_price=bid, category=category_obj, lister=lister_obj, active=active, image=image)
            cl.save()
            return render(request, "auctions/createlisting.html", {
                "categories" : category_list,
                "message": "Successfully added previous entry"
            })
        except IntegrityError:
            return render(request, "auctions/createlisting.html", {
                "categories" : category_list,
                "message": "Couldn't add previous entry"
            })

    return render(request, "auctions/createlisting.html", {
        "categories" : category_list
    })

def closedlistings(request):
    listing_obj_list = Listing.objects.all()
    closed_listing_object_list = []
    for lol in listing_obj_list:
        if lol.active is False:
            closed_listing_object_list.append(lol)

    return render(request, "auctions/closedlistings.html",{
        "closed_listings": closed_listing_object_list
    })

def categories_list(request):
    categories_objects = Categorie.objects.all()
    
    return render(request, "auctions/categories.html", {
        "categories" : categories_objects
    })

def category(request, id):
    category = Categorie.objects.get(id=id)
    category_listing_all = category.items_of_category.all()
    category_listing = []
    for cla in category_listing_all:
        if cla.active:
            category_listing.append(cla)

    return render(request, "auctions/category.html", {
        "category" : category,
        "category_listing" : category_listing
    })

def listing(request, id, message=False):
    listing_obj = Listing.objects.get(id=id)

    # Update Current price
    bids_obj_list = listing_obj.bids_of_listing.all()
    max_bid = listing_obj.starting_bid
    for bol in bids_obj_list:
        if bol.price > max_bid:
            max_bid = bol.price
    listing_obj.current_price = max_bid
    listing_obj.save()

    flag1 = False #User is lister
    flag2 = listing_obj.active #Listing is active
    flag3 = False #User have Listing in watchlist
    if request.user.is_authenticated:
        if listing_obj.lister.id == request.user.id:
            flag1 = True
        user_obj = User.objects.get(id=request.user.id)
        watchlist_list = json.dumps(user_obj.watchlist)
        if str(id) in watchlist_list:
            flag3 = True

    comments = listing_obj.comments_of_listing.all()
    return render(request, "auctions/listing.html", {
        "listing": listing_obj,
        "message": message,
        "comments": comments,
        "flag3": flag3
    })

@login_required
def comment(request, id):
    if request.POST:
        commenter_obj = User.objects.get(username=request.user.username)
        comment_txt = request.POST["comment_txt"]
        listing_id = id
        listing_obj = Listing.objects.get(id=listing_id)

        try:
            cmt = Comment(commenter=commenter_obj, comment=comment_txt, listing=listing_obj)
            cmt.save()
            return render(request, "auctions/listing.html", {
                "listing": listing_obj,
                "comments": listing_obj.comments_of_listing.all()
            })
        except IntegrityError:
            return render(request, "auctions/listing.html", {
                "listing": listing_obj,
                "message": "comment exceeded the size of 1024 characters",
                "comments": listing_obj.comments_of_listing.all()
            })

@login_required
def bid(request, id):
    if request.POST:
        bidder_obj = User.objects.get(username=request.user.username)
        price = request.POST["amount"]
        listing_id = id
        listing_obj = Listing.objects.get(id=listing_id)

        if int(price) <= int(listing_obj.current_price):
            # return render(request, "auctions/listing.html", {
            #     "listing": listing_obj,
            #     "message": "Bid amount must be strictly greater than current amount",
            #     "comments": listing_obj.comments_of_listing.all()
            # })
            return listing(request, id, "Bid amount must be strictly greater than current amount")

        try:
            b = Bid(bidder=bidder_obj, price=price, listing=listing_obj)
            b.save()
            listing_obj.current_price = price
            listing_obj.save()
            # return render(request, "auctions/listing.html", {
            #     "listing": listing_obj,
            #     "message": "Successfully added bid !",
            #     "comments": listing_obj.comments_of_listing.all()
            # })
            return listing(request, listing_id, "Successfully added bid !")

        except IntegrityError:
            # return render(request, "auctions/listing.html", {
            #     "listing": listing_obj,
            #     "message": "Sorry, Integrity Error",
            #     "comments": listing_obj.comments_of_listing.all()
            # })
            return listing(request, listing_id, "Sorry, Integrity Error")

@login_required
def watchlist(request, id):
    user_obj = User.objects.get(id=id)
    watchlist_list = json.loads(user_obj.watchlist)
    watchlisted_items_obj = []
    for wi in watchlist_list:
        watchlisted_items_obj.append(Listing.objects.get(id=int(wi)))
    return render(request, "auctions/watchlist.html", {
        "watchlisted_items": watchlisted_items_obj
    })

@login_required
def addwatchlist(request, id):
    if request.POST:
        user_obj = User.objects.get(id=request.user.id)
        watchlist_list = json.loads(user_obj.watchlist)
        watchlist_list.append(str(id))
        user_obj.watchlist = json.dumps(watchlist_list)
        user_obj.save()
        return redirect(reverse("listing", args=[int(id)]))

@login_required
def removewatchlist(request, id):
    if request.POST:
        user_obj = User.objects.get(id=request.user.id)
        watchlist_list = json.loads(user_obj.watchlist)
        watchlist_list.remove(str(id))
        user_obj.watchlist = json.dumps(watchlist_list)
        user_obj.save()
        return redirect(reverse("listing", args=[int(id)]))

@login_required
def closelisting(request, id):
    if request.POST:
        listing_obj = Listing.objects.get(id=id)
        bids_obj_list = listing_obj.bids_of_listing.all()
        if len(bids_obj_list) == 0:
            listing_obj.active = False
            listing_obj.save()
            return redirect(reverse("listing", args=[int(id)]))
        else:
            for bol in bids_obj_list:
                if bol.price == listing_obj.current_price:
                    listing_obj.active = False
                    listing_obj.lister = bol.bidder
                    listing_obj.save()
                    return redirect(reverse("listing", args=[int(id)]))