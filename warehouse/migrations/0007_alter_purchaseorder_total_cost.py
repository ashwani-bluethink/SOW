# Generated by Django 4.2.1 on 2023-06-01 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0006_purchaseorder_total_cost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseorder',
            name='total_cost',
            field=models.FloatField(),
        ),
    ]
