from django.contrib import admin

# Register your models here.

from .models import PurchaseOrder

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('PurchaseOrderID', 'Alias', 'Supplier', 'date_created', 'display_products', 'received', 'submitted', 'tracking_id', 'courier', 'total_cost',)
    list_filter = ('PurchaseOrderID', 'Alias', 'Supplier', 'date_created', 'received', 'submitted', 'tracking_id', 'courier', 'total_cost', )
    search_fields = ('PurchaseOrderID', 'Alias', 'Supplier', 'date_created', 'received', 'submitted', 'tracking_id', 'courier', 'total_cost', )

    def display_products(self, obj):
        return ", ".join([str(product) for product in obj.products.all()])
    display_products.short_description = 'Products'

    