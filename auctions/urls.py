from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<str:product_id>/listing",views.listing,name="listing"),
    path("<str:product_id>/addbid",views.add_bid,name="addbid"),
    path("<str:product_id>/addcomment",views.add_comment,name="addcomment"),
    path("<str:product_id>/closelisting",views.close_listing,name="closelisting"),
    path("addlisting",views.add_listing,name="addlisting"),
    path("user",views.users,name='user'),#sucess
    path("watchlist/<str:product_id>/", views.watchlist, name="watchlist"),
    path("category",views.category,name='category')
]
