# Generated by Django 4.2.1 on 2023-06-01 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Order', '0017_products_quantities_received'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='po_generated',
            field=models.BooleanField(default=False),
        ),
    ]
