from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create_listing"),
    path("<int:auction_id>", views.auction, name="auction"),
    path("<int:auction_id>/place_bid", views.place_bid, name="place_bid"),
    path('watchlist/', views.watchlist, name='watchlist'),
    path("<int:auction_id>/add_to_watchlist", views.add_to_watchlist, name="add_to_watchlist"),
    path("<int:auction_id>/remove_from_watchlist", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("categories", views.categories, name="categories"),
    path('<int:auction_id>/close', views.close_auction, name='close_auction')
]
