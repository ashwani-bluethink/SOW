from django.db import models
import uuid

import random
import string



class PurchaseOrder(models.Model):
    PurchaseOrderID = models.CharField(primary_key=True, max_length=255,)
    Alias = models.CharField(max_length=255, null=True, blank=True)
    Supplier = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    products = models.ManyToManyField('Order.Products')
    received = models.BooleanField(default=False)
    submitted = models.BooleanField(default=False)
    tracking_id = models.CharField(max_length=255, null=True, blank=True)
    courier = models.CharField(max_length=255, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    
    def save(self, *args, **kwargs):
        supplier_chars = self.Supplier[:3]  
        order_chars = str(self.products)[:3] 
        self.PurchaseOrderID = str(supplier_chars) + str(order_chars)+ ''.join(random.choices(string.digits, k=3))
        random_numbers = ''.join(random.choices(string.digits, k=3))
        self.Alias = str(self.PurchaseOrderID) + str(random_numbers)
        super().save(*args, **kwargs)
    
    
    def __str__(self):
        return self.PurchaseOrderID

    
    
    
    
    