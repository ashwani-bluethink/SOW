# Generated by Django 4.2.1 on 2023-06-01 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0005_remove_purchaseorder_total_cost'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorder',
            name='total_cost',
            field=models.FloatField(blank=True, null=True),
        ),
    ]