# Generated by Django 4.2.1 on 2023-05-31 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Order', '0016_alter_products_orderline_alter_products_sku'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='quantities_received',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]