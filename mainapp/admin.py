from django.contrib import admin

from .models import Account, Product, Key

admin.site.register(Account)
admin.site.register(Product)
admin.site.register(Key)
