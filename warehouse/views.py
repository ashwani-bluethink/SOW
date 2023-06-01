from django.shortcuts import render
from .models import PurchaseOrder

# Create your views here.

def Dashboard(request):
    return render(request, 'dashboard_temp/index.html')


def Order_details(request):
    return render(request, 'dashboard_temp/Order_detalis.html')



def New_Purchase_Order(request):
    return render(request, 'dashboard_temp/new_purches_order.html')


def lestest_suppliers(request):
    latest_suppliers = PurchaseOrder.objects.order_by('-date_created').values_list('Supplier', flat=True)
    return render(request, 'dashboard_temp/latest_suppliers.html', {'latest_suppliers': latest_suppliers})
