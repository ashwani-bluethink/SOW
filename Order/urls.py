from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('order_data_api/', views.order_data_view, name='order_data_view'),#remove 
    path('insert_update_order_data_in_db/', views.insert_order_data, name='insert_update_order_data_in_db'),
    path("product_insert_db/", views.product_insert_db, name="product_insert_db"),
    path("get_suppliers_and_products/", views.get_suppliers_and_products, name="get_suppliers_and_products"),
    path('get_supplier_names/', views.get_supplier_names, name='get_supplier_names'),
   
  
]
