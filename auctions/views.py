from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render,redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CommentForm, AuctionForm

from .models import User,Auction ,Bid, Comment, Category


def index(request):
    open_auctions = Auction.objects.filter(closed=False)
    return render(request, "auctions/index.html", {
        "auctions": open_auctions
    })

def auction(request, auction_id):
    auction = Auction.objects.get(id=auction_id)
    highest_bid = auction.bids.order_by('-bid_amount').first()
    user_highest_bid = None
    if request.user.is_authenticated:
        user_highest_bid = auction.bids.filter(user=request.user).order_by('-bid_amount').first()
    total_bids = auction.bids.count()

    comments = auction.comments.all().order_by('-timestamp')
    comment_form = CommentForm()

    if request.method == "POST":
        if request.user.is_authenticated:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.auction = auction
                new_comment.user = request.user
                new_comment.save()
                return redirect('auction', auction_id=auction_id)
        else:
            return redirect('login')

    return render(request, "auctions/auction.html", {
        "auction": auction,
        "highest_bid": highest_bid,
        "user_highest_bid": user_highest_bid,
        "total_bids": total_bids,
        "comments": comments,
        "comment_form": comment_form
   })

@login_required
def create_listing(request):
    if request.method == "POST":
        form = AuctionForm(request.POST, request.FILES)
        if form.is_valid():
            auction = form.save(commit=False)
            auction.user = request.user 
            auction.save()
            return redirect('index')
        else:
            # Print form errors for debugging
            print(form.errors)
    else:
        form = AuctionForm()
    return render(request, "auctions/create_listing.html", {
        "form": form
    })

@login_required
def place_bid(request, auction_id):
    auction = Auction.objects.get(id=auction_id)

    if auction.closed:
        messages.error(request, "This auction is closed. You cannot place a bid.")
        return redirect('auction', auction_id=auction_id)

    if request.method == "POST":
        bid_amount = request.POST.get("bid_amount")
        if bid_amount:
            bid_amount = float(bid_amount)
            highest_bid = auction.bids.order_by('-bid_amount').first()
            if highest_bid is None or bid_amount > highest_bid.bid_amount:
                if bid_amount > auction.price:
                    Bid.objects.create(auction=auction, user=request.user, bid_amount=bid_amount)
                    messages.success(request, "Your bid was placed successfully.")
                else:
                     messages.error(request, "Your bid must be higher than the starting price.")
            else:
                messages.error(request, "Your bid must be higher than the current highest bid.")
        else:
            messages.error(request, "Invalid bid amount.")
        return redirect('auction', auction_id=auction_id)
    return render(request, "auctions/auction.html", {"auction": auction})

@login_required
def close_auction(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    if request.user == auction.user:
        auction.closed = True
        auction.save()
        messages.success(request, "Auction closed successfully.")
    else:
        messages.error(request, "You are not authorized to close this auction.")
    return redirect('auction', auction_id=auction_id)

@login_required
def add_to_watchlist(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    request.user.watchlist.add(auction)
    messages.success(request, 'Auction added to your watchlist.')
    return redirect('auction', auction_id=auction_id)

@login_required 
def remove_from_watchlist(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    request.user.watchlist.remove(auction)
    messages.success(request, 'Auction removed from your watchlist.')
    return redirect('auction', auction_id=auction_id)

@login_required
def watchlist(request):
    watchlist_auctions = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "watchlist_auctions": watchlist_auctions
    })

def categories(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    if selected_category:
        auctions = Auction.objects.filter(category__name=selected_category)#(category=selected_category)
    else:
        auctions = Auction.objects.all()
    
    return render(request, "auctions/categories.html", {
        "categories": categories,
        "auctions": auctions,
        "selected_category": selected_category
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
