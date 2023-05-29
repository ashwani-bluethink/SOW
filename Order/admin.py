from django.contrib import admin
from .models import Order, OrderLine
# Register your models here.


@admin.register(Order)
class AdminOrder(admin.ModelAdmin):
    list_display = ('OrderID', 'DatePlaced', 'OrderStatus', 'ShippingOption', 'SalesChannel')
    list_filter = ('OrderStatus', 'ShippingOption', 'SalesChannel')
    search_fields = ('OrderID', 'OrderStatus', 'ShippingOption', 'SalesChannel')

@admin.register(OrderLine)
class AdminOrderLine(admin.ModelAdmin):
    list_display = ('OrderLineID', 'SKU', 'Quantity', 'Order')
    list_filter = ('SKU', 'Quantity', 'Order')
    search_fields = ('OrderLineID', 'SKU', 'Quantity', 'Order')