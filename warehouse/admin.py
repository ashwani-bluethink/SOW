from django.contrib import admin

# Register your models here.

from .models import *

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ( 'Alias', 'Supplier', 'date_created', 'display_products', 'received', 'submitted', 'tracking_id', 'courier')
    list_filter = ('Alias', 'Supplier', 'date_created', 'received', 'submitted', 'tracking_id', 'courier',)
    search_fields = ( 'Alias', 'Supplier', 'date_created', 'received', 'submitted', 'tracking_id', 'courier')

    def display_products(self, obj):
        return ", ".join([str(product) for product in obj.products.all()])
    display_products.short_description = 'Products'


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)
    