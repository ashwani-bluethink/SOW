# Generated by Django 4.2.1 on 2023-05-30 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Order', '0004_orderline_ebay'),
    ]

    operations = [
        migrations.CreateModel(
            name='Products',
            fields=[
                ('sku', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('misc27', models.CharField(max_length=10)),
                ('primary_supplier', models.CharField(max_length=100)),
                ('inventory_id', models.CharField(max_length=10)),
                ('default_price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
    ]
