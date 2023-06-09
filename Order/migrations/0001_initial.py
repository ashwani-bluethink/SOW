# Generated by Django 4.2.1 on 2023-05-30 09:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order_Data',
            fields=[
                ('order_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('shipping_option', models.CharField(max_length=100)),
                ('date_placed', models.DateTimeField()),
                ('order_status', models.CharField(max_length=100)),
                ('sales_channel', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name_plural': 'Orders',
            },
        ),
        migrations.CreateModel(
            name='OrderLine_Data',
            fields=[
                ('order_line_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('quantity', models.IntegerField()),
                ('sku', models.CharField(max_length=100)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_lines', to='Order.order_data')),
            ],
            options={
                'verbose_name_plural': 'Order Lines',
            },
        ),
    ]
