from ..models import Product, Account
from django.shortcuts import render


def home(request):
    products = Product.objects.all()[:20]
    context = {
        'products': products,
        'types': Product.PRODUCT_TYPES
    }

    if request.user.is_authenticated:
        account = Account.objects.filter(user=request.user)
        context = {
            'account': account[0],
            'products': products,
            'types': Product.PRODUCT_TYPES
        }

    return render(request, 'store/home.html', context)


def filter_products(request):
    type = request.GET.get('type')
    products = Product.objects.all()

    if type:
        products = products.filter(product_type=type)

    products = products[:20]
    return render(request, 'store/partials/product_list.html', {'products': products})
