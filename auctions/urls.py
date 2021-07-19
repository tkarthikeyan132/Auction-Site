from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting", views.createlisting, name="createlisting"),
    path("closedlistings", views.closedlistings, name="closedlistings"),
    path("categories", views.categories_list, name="categories"),
    path("categories/<int:id>", views.category, name="category"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("listing/<int:id>/commentadded", views.comment, name="comment"),
    path("listing/<int:id>/bidadded", views.bid, name="bid"),
    path("watchlist/<int:id>", views.watchlist, name="watchlist"),
    path("listing/<int:id>/addwatchlist", views.addwatchlist, name="addwatchlist"),
    path("listing/<int:id>/removewatchlist", views.removewatchlist, name="removewatchlist"),
    path("listing/<int:id>/closelisting", views.closelisting, name="closelisting")
]
