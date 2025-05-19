from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone


class Account(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='account')
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Account"


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('DEPOSIT', 'إيداع'),
        ('PURCHASE', 'شراء'),
        ('WITHDRAWAL', 'سحب'),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(
        max_length=15, choices=TRANSACTION_TYPES)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    order = models.ForeignKey(
        'Order', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'عملية'
        verbose_name_plural = 'العمليات'

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount}"


class Product(models.Model):
    PRODUCT_TYPES = (
        ('GAME', 'لعبة'),
        ('SOFTWARE', 'برنامج'),
        ('SUBSCRIPTION', 'اشتراك'),
    )
    name = models.CharField(max_length=200)
    product_type = models.CharField(max_length=15, choices=PRODUCT_TYPES)
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name='صورة المنتج'
    )

    def __str__(self):
        return self.name


class PriceCategory(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='price_categories'
    )
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('product', 'name')


class Key(models.Model):
    KEY_STATUS = (
        ('AVAILABLE', 'متاح'),
        ('SOLD', 'مباع'),
    )

    price_category = models.ForeignKey(
        PriceCategory,
        on_delete=models.CASCADE,
        related_name='keys',
        null=True  # Add this line temporarily
    )
    key = models.CharField(max_length=255, unique=True)
    status = models.CharField(
        max_length=10,
        choices=KEY_STATUS,
        default='AVAILABLE'
    )
    sold_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.key}"


class Order(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    key = models.ForeignKey(
        Key, on_delete=models.SET_NULL, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            self.total_price = self.key.price_category.price
        super().save(*args, **kwargs)


# Signals

@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)


@receiver(post_save, sender=Order)
def complete_order(sender, instance, created, **kwargs):
    if instance.is_completed and not instance.key.status == 'SOLD':
        # Update key status
        instance.key.status = 'SOLD'
        instance.key.sold_at = timezone.now()
        instance.key.save()

        # Create transaction
        Transaction.objects.create(
            user=instance.user,
            amount=-instance.total_price,
            transaction_type='PURCHASE',
            balance_after=instance.user.account.balance - instance.total_price,
            order=instance
        )

        # Update account balance
        account = instance.user.account
        account.balance -= instance.total_price
        account.save()


@receiver(pre_save, sender=Account)
def capture_original_balance(sender, instance, **kwargs):
    """Capture the balance before saving."""
    if instance.pk:
        try:
            original = Account.objects.get(pk=instance.pk)
            instance._original_balance = original.balance
        except Account.DoesNotExist:
            instance._original_balance = None
    else:
        instance._original_balance = None


@receiver(post_save, sender=Account)
def create_admin_transaction(sender, instance, created, **kwargs):
    """Create a transaction if the balance was changed via the admin."""
    from_admin = getattr(instance, '_from_admin', False)
    if not from_admin:
        return

    if hasattr(instance, '_from_admin'):
        del instance._from_admin

    if created:
        if instance.balance != 0:
            Transaction.objects.create(
                user=instance.user,
                amount=instance.balance,
                transaction_type='DEPOSIT',
                balance_after=instance.balance,
                order=None
            )
        return

    original_balance = getattr(instance, '_original_balance', None)
    if original_balance is None:
        return

    new_balance = instance.balance
    difference = new_balance - original_balance
    if difference == 0:
        return

    transaction_type = 'DEPOSIT' if difference > 0 else 'WITHDRAWAL'
    Transaction.objects.create(
        user=instance.user,
        amount=difference,
        transaction_type=transaction_type,
        balance_after=new_balance,
        order=None
    )
