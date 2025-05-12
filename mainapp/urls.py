from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import index, auth, account, actions


urlpatterns = [
    path("", index.home, name="home"),
    path("filter/", index.filter_products, name="filter_products"),
    path('signup/', auth.signup_view, name='signup'),
    path('login/', auth.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("account/", account.account, name="account"),
    path("history/", account.history, name="history"),
    path("buykey/", actions.buy_a_key, name="key"),
]
