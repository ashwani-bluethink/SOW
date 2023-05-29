from django.db import models
import uuid
from django.db import models

class Order(models.Model):
    ShippingOption = models.CharField(max_length=255)
    CustomerRef4 = models.CharField(max_length=255, blank=True)
    SalesChannel = models.CharField(max_length=255)
    InternalOrderNotes = models.TextField(blank=True)
    OrderID = models.CharField(max_length=255, primary_key=True)
    CustomerRef6 = models.CharField(max_length=255, blank=True)
    CustomerRef3 = models.CharField(max_length=255, blank=True)
    DatePlaced = models.DateTimeField()
    OrderStatus = models.CharField(max_length=255)
    CustomerRef5 = models.TextField(blank=True)
    CustomerRef7 = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name_plural = "Orders"

    def __str__(self):
        return self.OrderID


class OrderLine(models.Model):
    eBay = models.CharField(max_length=255, blank=True)
    Quantity = models.IntegerField()
    SKU = models.CharField(max_length=255)
    OrderLineID = models.CharField(max_length=255, primary_key=True)
    ItemNotes = models.TextField(blank=True)
    Order = models.ForeignKey(Order, related_name='order_lines', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Order Lines"
        
    def __str__(self):
        return self.OrderLineID
    
    
    
class Products(models.Model):
    SKU = models.CharField(max_length=255, primary_key=True)
    Product_Name = models.CharField(max_length=255)
    Product_Description = models.CharField(max_length=255)
    Product_Price = models.FloatField()
    product_Qty = models.IntegerField()
    
    class Meta:
        verbose_name_plural = "Products"
    
    def __str__(self):
        return self.SKU

class Supplier(models.Model):
    Supplier_ID = models.CharField(max_length=255, primary_key=True)
    Supplier_Name = models.CharField(max_length=255)
    Supplier_Address = models.CharField(max_length=255)
    Supplier_Phone = models.CharField(max_length=255)
    Supplier_Email = models.CharField(max_length=255)
    
    class Meta:
        verbose_name_plural = "Supplier"
    
    def __str__(self):
        return self.Supplier_ID
    
