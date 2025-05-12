from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from ..models import Transaction, Account


@login_required
def account(request):
    account = Account.objects.filter(user=request.user)
    context = {
        'user': request.user,
        'account': account[0]
    }
    return render(request, 'store/account.html', context)


@login_required
def history(request):
    transactions = Transaction.objects.filter(
        user=request.user).order_by('-created_at')
    account = Account.objects.filter(user=request.user)

    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'user': request.user,
        'transactions': page_obj,
        'page': page_obj,
        'account': account[0]
    }
    return render(request, 'store/history.html', context)
