from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import index, auth, account, actions


urlpatterns = [
    path("", index.home, name="home"),
    path("filter/", index.filter_products, name="filter_products"),
    path('login/', auth.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("account/", account.account, name="account"),
    path("history/", account.history, name="history"),
    path('purchase/<int:price_category_id>/',
         actions.purchase, name='purchase'),
]
