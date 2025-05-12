from django.shortcuts import render
from django.http import HttpResponse


def buy_a_key(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def orders_history(request):
    return HttpResponse("Hello, world. You're at the polls index.")
