from django.db import models
import uuid



class Supplier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    order_date = models.DateTimeField(null=True, blank=True)
    new_order = models.BooleanField(default=False)

    def __str__(self):
        return self.name



class PurchaseOrder(models.Model):
    Alias = models.CharField(max_length=255, null=True, blank=True)
    Supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders')
    date_created = models.DateTimeField(auto_now_add=True)
    products = models.ManyToManyField('Order.Products')
    received = models.BooleanField(default=False)
    submitted = models.BooleanField(default=False)
    tracking_id = models.CharField(max_length=255, null=True, blank=True)
    courier = models.CharField(max_length=255, null=True, blank=True)
    total_cost = models.FloatField()
    publish = models.BooleanField(default=False)
    

class PUrchaseOrderSUbmit(models.Model):
    PurchaseOrderID = models.AutoField(primary_key=True) 
    perchase_order = models.OneToOneField(PurchaseOrder, on_delete=models.CASCADE, related_name='purchase_order_submit')
    
    
    
    
    