from django.db import models
import uuid
from django.db import models

class Order(models.Model):
    OrderID = models.CharField(max_length=100,primary_key=True,)
    ShippingOption = models.CharField(max_length=100)
    DatePlaced = models.DateTimeField()
    OrderStatus = models.CharField(max_length=100)
    SalesChannel = models.CharField(max_length=100)

    
    class Meta:
        verbose_name_plural = "Orders"
        ordering = ('-DatePlaced',)

    def __str__(self):
        return self.OrderID


class OrderLine(models.Model):
    OrderLineID = models.CharField(max_length=100, primary_key=True,)
    Order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_lines')
    Quantity = models.IntegerField()
    SKU = models.CharField(max_length=100)
    eBay = models.CharField(max_length=100,null=True, blank=True)
    
   

    class Meta:
        verbose_name_plural = "Order Lines"
        ordering = ('-OrderLineID',)
        
    def __str__(self):
        return self.OrderLineID
    
    
    


class Products(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='products')
    OrderLine = models.OneToOneField(OrderLine, on_delete=models.CASCADE, related_name='products',primary_key=True)
    sku = models.CharField(max_length=100)
    misc27 = models.CharField(max_length=10)
    primary_supplier = models.CharField(max_length=100)
    inventory_id = models.CharField(max_length=10)
    default_price = models.FloatField()
    ack = models.CharField(max_length=10,null=True, blank=True)
    quantities_received = models.IntegerField(null=True, blank=True)
    
    
    class Meta:
        verbose_name_plural = "Products"
        ordering = ('-sku',)
       

    def __str__(self):
        return self.sku

    
    
    



