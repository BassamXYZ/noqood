from ..models import Product
from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    products = Product.objects.all()[:20]
    return render(request, 'store/home.html', {
        'products': products,
        'types': Product.PRODUCT_TYPES
    })


def filter_products(request):
    type = request.GET.get('type')
    products = Product.objects.all()

    if type:
        products = products.filter(product_type=type)

    products = products[:20]
    return render(request, 'store/partials/product_list.html', {'products': products})
