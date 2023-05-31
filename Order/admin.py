from django.contrib import admin

# Register your models here.
from .models import Order, OrderLine,Products

# admin.site.register(Order)
# admin.site.register(OrderLine)
# admin.site.register(Products)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('OrderID', 'ShippingOption', 'DatePlaced', 'OrderStatus', 'SalesChannel')
    list_filter = ('OrderID', 'ShippingOption', 'DatePlaced', 'OrderStatus', 'SalesChannel')
    search_fields = ('OrderID', 'ShippingOption', 'DatePlaced', 'OrderStatus', 'SalesChannel')
    ordering = ('OrderID', 'ShippingOption', 'DatePlaced', 'OrderStatus', 'SalesChannel')
    
@admin.register(OrderLine)
class OrderLineAdmin(admin.ModelAdmin):
    list_display = ('OrderLineID', 'Order', 'Quantity', 'SKU', 'eBay')
    list_filter = ('OrderLineID', 'Order', 'Quantity', 'SKU', 'eBay')
    search_fields = ('OrderLineID', 'Order', 'Quantity', 'SKU', 'eBay')
    ordering = ('OrderLineID', 'Order', 'Quantity', 'SKU', 'eBay')
    
    
@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('order','order', 'OrderLine','sku', 'misc27', 'primary_supplier', 'inventory_id', 'default_price', 'ack')
    list_filter = ('order', 'sku', 'misc27', 'primary_supplier', 'inventory_id', 'default_price')
    search_fields = ('order', 'sku', 'misc27', 'primary_supplier', 'inventory_id', 'default_price')
    ordering = ('order', 'sku', 'misc27', 'primary_supplier', 'inventory_id', 'default_price')
    