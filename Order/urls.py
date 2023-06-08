from django.contrib import admin
from django.urls import path
from . import views

app_name = 'Order'

urlpatterns = [
    path('order_data_api/', views.order_data_view, name='order_data_view'),#remove 
    path('insert_update_order_data_in_db/', views.insert_order_data, name='insert_update_order_data_in_db'),
    path("product_insert_db/", views.product_insert_db, name="product_insert_db"),
  
    path('dashboard/',views.Dashboard,name='dashboard'),
    path('get_suppliers/', views.Get_Suppliers, name="get_suppliers"),
    path('letest_supplier/', views.Lestest_Suppliers, name="letest_supplier"),
    path("supplier_sku/", views.Suppliers_SKU, name="supplier_sku"),
    path("Create_purchase_order/", views.Create_purchase_order, name="Create_purchase_order"),
    
    
   
    
    path('list_of_po_stock_update_suppliers/',views.List_Of_PO_Stock_Update_suppliers,name='list_of_po_stock_update_suppliers'),
    path("supplier_po_list", views.Supplier_PO_List, name="supplier_po_list"),
    path("po_stock_update/", views.Updated_PO_Stock, name="po_stock_update"),
    path('po_stock_update_excel/',views.po_stock_update_excel,name='po_stock_update_excel'),
    path('generate-pdf/<int:id>', views.generate_pdf, name='generate_pdf'),
    path('create_purchase_order/', views.Create_purchase_order, name='create_purchase_order'),
    
 
    
    path("do_false/", views.do_false, name="do_false"),
    
   
  
]
