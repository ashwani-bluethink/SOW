from django.db import models
import uuid





class PurchaseOrder(models.Model):
    PurchaseOrderID = models.AutoField(primary_key=True)
    Alias = models.CharField(max_length=255, null=True, blank=True)
    Order = models.ForeignKey('Order.Order', on_delete=models.CASCADE)
    Supplier = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    products = models.ManyToManyField('Order.Products')
    received = models.BooleanField(default=False)
    submitted = models.BooleanField(default=False)
    tracking_id = models.CharField(max_length=255, null=True, blank=True)
    courier = models.CharField(max_length=255, null=True, blank=True)
    total_cost = models.FloatField()
    
    
    

    
    
    
    
    