from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


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


class Key(models.Model):
    KEY_STATUS = (
        ('AVAILABLE', 'متاح'),
        ('SOLD', 'مباع'),
    )

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='keys')
    key = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10, choices=KEY_STATUS, default='AVAILABLE')
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
            self.total_price = self.key.price
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


"""
### Hierarchical Category Table

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'parent'],
                name='unique_category_name_per_parent'
            )
        ]
        verbose_name_plural = "Categories"


### Allow Price Categories

class Product(models.Model):
    PRODUCT_TYPES = (
        ('GAME', 'Game'),
        ('SOFTWARE', 'Software'),
    )
    name = models.CharField(max_length=200)
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPES)

class PriceCategory(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='price_categories'
    )
    name = models.CharField(max_length=100)  # e.g., "Standard", "Deluxe Edition"
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('product', 'name')  # Ensure unique category names per product

class Key(models.Model):
    KEY_STATUS = (
        ('AVAILABLE', 'Available'),
        ('SOLD', 'Sold'),
    )

    price_category = models.ForeignKey(
        PriceCategory,
        on_delete=models.CASCADE,
        related_name='keys'
    )
    key = models.CharField(max_length=255, unique=True)
    status = models.CharField(
        max_length=10,
        choices=KEY_STATUS,
        default='AVAILABLE'
    )
    sold_at = models.DateTimeField(null=True, blank=True)
"""
