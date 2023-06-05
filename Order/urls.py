from django.contrib import admin
from django.urls import path
from . import views

app_name = 'Order'

urlpatterns = [
    path('order_data_api/', views.order_data_view, name='order_data_view'),#remove 
    path('insert_update_order_data_in_db/', views.insert_order_data, name='insert_update_order_data_in_db'),
    path("product_insert_db/", views.product_insert_db, name="product_insert_db"),
    path("Create_purchase_order/", views.Create_purchase_order, name="Create_purchase_order"),
    
    
    path('dashboard/',views.Dashboard,name='dashboard'),
    path("new_purches_order/",views.New_Purchase_Order,name='new_purches_order'),
    path("purchase_order_details/<int:id>",views.Purchase_Order_Details,name='purchase_order_details'),
    path('po_stock_update/',views.PO_Stock_Update,name='po_stock_update'),
    path('po_stock_update_excel/',views.po_stock_update_excel,name='po_stock_update_excel'),
    path('generate-pdf/<int:id>', views.generate_pdf, name='generate_pdf'),
 
    
    path("do_false/", views.do_false, name="do_false"),
    
   
  
]
