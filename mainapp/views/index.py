from django.core.paginator import Paginator
from ..models import Product, Account
from django.shortcuts import render, redirect
from django.db.models import Q


def home(request):
    products = Product.objects.all()
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj.object_list,
        'page_obj': page_obj,
        'types': Product.PRODUCT_TYPES
    }

    if request.user.is_authenticated:
        account = Account.objects.filter(user=request.user)
        context = {
            'account': account[0],
            'products': page_obj.object_list,
            'page_obj': page_obj,
            'types': Product.PRODUCT_TYPES
        }

    return render(request, 'store/home.html', context)


def filter_products(request):
    if not request.headers.get('HX-Request'):
        return redirect("home")

    search_query = request.GET.get('q')
    type = request.GET.get('type')
    page_number = request.GET.get('page', 1)

    products = Product.objects.all()

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
        )

    if type:
        products = products.filter(product_type=type)

    paginator = Paginator(products, 20)
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj.object_list,
        'page_obj': page_obj
    }

    return render(request, 'store/partials/product_list.html', context)
