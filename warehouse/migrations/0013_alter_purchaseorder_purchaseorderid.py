# Generated by Django 4.2.1 on 2023-06-06 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0012_alter_purchaseorder_supplier_delete_supplier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseorder',
            name='PurchaseOrderID',
            field=models.CharField(max_length=255, primary_key=True, serialize=False),
        ),
    ]
