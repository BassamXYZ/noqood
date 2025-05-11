from django.urls import path

from .views import index, orders, account

urlpatterns = [
    path("", index.home, name="home"),
]
