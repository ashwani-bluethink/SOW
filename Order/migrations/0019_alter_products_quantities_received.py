# Generated by Django 4.2.1 on 2023-06-01 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Order', '0018_products_po_generated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='quantities_received',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
