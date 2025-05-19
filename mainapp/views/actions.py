from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db import transaction
from ..models import PriceCategory, Key, Order, Account, Transaction
from django.utils import timezone


@login_required
@transaction.atomic
def purchase(request, price_category_id):
    price_category = get_object_or_404(PriceCategory, id=price_category_id)
    user = request.user

    try:
        account = Account.objects.select_for_update().get(user=user)
    except Account.DoesNotExist:
        return HttpResponse(
            '<div class="alert alert-danger p-1">الحساب غير موجود</div>',
            status=200
        )

    # Check balance
    if account.balance < price_category.price:
        return HttpResponse(
            f'<div class="alert alert-danger p-1">رصيدك غير كافي (المتبقي: {account.balance}$)</div>',
            status=200
        )

    # Get first available key
    key = Key.objects.select_for_update().filter(
        price_category=price_category,
        status='AVAILABLE'
    ).first()

    if not key:
        return HttpResponse(
            '<div class="alert alert-danger p-1">لا توجد مفاتيح متاحة حالياً</div>',
            status=200
        )

    # Update key status
    key.status = 'SOLD'
    key.sold_at = timezone.now()
    key.save()

    # Create order
    order = Order.objects.create(
        user=user,
        product=price_category.product,
        key=key,
        total_price=price_category.price,
        is_completed=True
    )

    # Update account balance
    account.balance -= price_category.price
    account.save()

    # Create transaction
    Transaction.objects.create(
        user=user,
        amount=-price_category.price,
        transaction_type='PURCHASE',
        balance_after=account.balance,
        order=order
    )

    return HttpResponse(
        f'<div class="alert alert-success p-1">'
        f'تم الشراء بنجاح! المفتاح: <strong>{key.key}</strong>'
        f'</div>'
    )
