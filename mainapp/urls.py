from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import index, orders, account, auth


urlpatterns = [
    path("", index.home, name="home"),
    path("filter", index.filter_products, name="filter_products"),
    path("orders", orders.orders_history, name="orders"),
    path("buykey", orders.buy_a_key, name="key"),
    path("account", account.account, name="account"),
    path("balancehistory", account.balance_history, name="balancehistory"),
    path('login/', auth.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', auth.SignUpView.as_view(), name='signup'),
]
