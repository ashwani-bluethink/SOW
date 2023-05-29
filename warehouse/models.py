from django.db import models
import uuid

class Purchase_Order(models.Model):
    Purchase_Order_ID = models.CharField(max_length=255, primary_key=True)
    Created_Date = models.DateTimeField()
    Supplier = models.CharField(max_length=255)
    Cost = models.FloatField()
    Tracking_ID = models.CharField(max_length=255)
    Courier_Company_Name = models.CharField(max_length=255)
    Order_Line_ID = models.CharField(max_length=255)
    SKU = models.CharField(max_length=255)
    Par_No = models.CharField(max_length=255)
    Quantity = models.IntegerField()
    
    class Meta:
        verbose_name_plural = "Purchase Order"
        
    def __str__(self):
        return self.Purchase_Order_ID
        


class Stock_Data(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Product = models.OneToOneField('Products', on_delete=models.CASCADE, primary_key=True)
    stock = models.IntegerField()
    
    class Meta:
        verbose_name_plural = "Stock Data"
    
    def __str__(self):
        return self.Product
        
    
    
    
    
    