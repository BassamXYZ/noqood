from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )


class BalanceHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Product(models.Model):
    PRODUCT_TYPES = (
        ('GAME', 'Game'),
        ('SOFTWARE', 'Software'),
        ('SUBSCRIPTION', 'Subscription'),
    )
    name = models.CharField(max_length=200)
    product_type = models.CharField(max_length=15, choices=PRODUCT_TYPES)
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name='Product Image'
    )


class Key(models.Model):
    KEY_STATUS = (
        ('AVAILABLE', 'Available'),
        ('SOLD', 'Sold'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    key = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10, choices=KEY_STATUS, default='AVAILABLE')
    sold_at = models.DateTimeField(null=True, blank=True)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    key = models.ForeignKey(
        Key, on_delete=models.SET_NULL, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


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
