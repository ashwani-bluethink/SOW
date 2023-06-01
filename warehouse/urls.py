from django.contrib import admin
from django.urls import path
from .views import Dashboard,Order_details,New_Purchase_Order

app_name = 'warehouse'
urlpatterns = [
  path('dashboard/',Dashboard,name='dashboard'),
  path('Order_details/',Order_details,name='Order_details'),
  path("new_purches_order/",New_Purchase_Order,name='new_purches_order')
  ]
