from .models import Account
from django.contrib import admin

from .models import Account, Product, PriceCategory, Key

admin.site.register(Product)
admin.site.register(PriceCategory)
admin.site.register(Key)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        """Set a flag when saving via the admin."""
        obj._from_admin = True
        super().save_model(request, obj, form, change)
