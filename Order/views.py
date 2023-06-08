
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
import json
import requests
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.shortcuts import render
from .models import Order, OrderLine, Products
from django.db.models import Q
from warehouse.models import PurchaseOrder
import time
from django.contrib import messages
from datetime import datetime, date
import pandas as pd
import openpyxl
import os
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML


def api_order_response(dict_filter, List_of_OutputSelector=None, new_headers=None):
    url = "https://www.findsports.com.au/do/WS/NetoAPI"
    parent_dict = {}
    dict_export_status = {}
    dict_filter = dict_filter.copy()
    dict_filter['OutputSelector'] = List_of_OutputSelector
    dict_export_status["ExportStatus"] = "Exported"
    dict_filter["UpdateResults"] = dict_export_status
    parent_dict['Filter'] = dict_filter
    payload = json.dumps(parent_dict)
    product_headers_order = {
        'NETOAPI_ACTION': "GetOrder",
        'NETOAPI_USERNAME': "API-User-Product",
        'NETOAPI_KEY': "v0fmsHHYPqfq99lFnPJ1kQbIgynkbLJq",
        'Accept': "application/json",
        'Content-Type': "application/javascript",
        'cache-control': "no-cache",
        'Postman-Token': "2473156a-3bcc-4a64-8079-04c3a395b5ea"
    }
    if new_headers is None:
        header = product_headers_order
        response = requests.request("POST", url, data=payload, headers=header)
        json1_data = json.loads(response.text)
    return json1_data


def order_data_view():
    dict_filter = {'OrderStatus': 'New Backorder'}
    output_selector = ['OrderID', 'OrderStatus',
                       'ShippingOption', 'SalesChannel', 'OrderLine', 'DatePlaced']
    # dict_filter = {'DatePlacedFrom': "2022-06-29 00:00:00",
    #                'OrderStatus': ['New Backorder', 'Pending Pickup']}
    # output_selector = ['OrderID', 'OrderStatus',
    #                    'ShippingOption', 'SalesChannel', 'OrderLine', 'DatePlaced']
    new_headers = None
    order_data = api_order_response(dict_filter, output_selector, new_headers)
    return order_data


def insert_order_data(request):
    order_data = order_data_view()
    orders = order_data['Order']
    for order_info in orders:
        order_lines_data = order_info.pop('OrderLine', [])
        order_id = order_info['OrderID']

        order, created = Order.objects.update_or_create(
            OrderID=order_id, defaults=order_info)

        for order_line_data in order_lines_data:
            order_line_id = order_line_data['OrderLineID']

            # Add the order reference to the order line data
            order_line_data['Order'] = order

            order_line, created = OrderLine.objects.update_or_create(
                OrderLineID=order_line_id, defaults=order_line_data)
    return JsonResponse({'message': 'Data inserted successfully'})


def api_product_response(dict_filter, List_of_OutputSelector=None, new_headers=None):
    url = "https://www.findsports.com.au/do/WS/NetoAPI"
    product_headers_products = {
        'NETOAPI_ACTION': "GetItem",
        'NETOAPI_USERNAME': "API-User-Product",
        'NETOAPI_KEY': "v0fmsHHYPqfq99lFnPJ1kQbIgynkbLJq",
        'Accept': "application/json",
        'Content-Type': "application/javascript",
        'cache-control': "no-cache",
        'Postman-Token': "2473156a-3bcc-4a64-8079-04c3a395b5ea"
    }
    parent_dict = {}
    dict_export_status = {}
    dict_filter['OutputSelector'] = List_of_OutputSelector
    dict_export_status["ExportStatus"] = "Exported"
    dict_filter["UpdateResults"] = dict_export_status
    parent_dict['Filter'] = dict_filter
    payload = json.dumps(parent_dict)

    if new_headers is None:
        header = product_headers_products

    response = requests.request("POST", url, data=payload, headers=header)
    json_data = response.json()

    return json_data


def product_insert_db(request):

    skus_and_orders = OrderLine.objects.only('SKU', 'Order')
    api_fields = ['SKU', 'PrimarySupplier',
                  'DefaultPrice', 'SupplierId', 'Misc27']


def product_insert_db(request):
    skus_and_orders = OrderLine.objects.only('SKU', 'Order', 'OrderLineID')
    api_fields = ['SKU', 'PrimarySupplier',
                  'DefaultPrice', 'SupplierId', 'Misc27']

    # Fetch all products and put them in a dictionary for fast lookups
    existing_products = {
        product.sku: product for product in Products.objects.all()}

    for orderline_instance in skus_and_orders:
        product_info = api_product_response(
            {'SKU': orderline_instance.SKU},
            api_fields,
            None
        )

        product_defaults = {
            'order': orderline_instance.Order,
            'OrderLine': orderline_instance,
            'sku': orderline_instance.SKU,
            'misc27': product_info['Item'][0]['Misc27'],
            'primary_supplier': product_info['Item'][0]['PrimarySupplier'],
            'inventory_id': product_info['Item'][0]['InventoryID'],
            'default_price': float(product_info['Item'][0]['DefaultPrice']),
            'ack': product_info["Ack"],
        }

        # Check if the product already exists in the table
        existing_product = existing_products.get(orderline_instance.SKU)

        if existing_product:
            # Update existing product information
            for key, value in product_defaults.items():
                setattr(existing_product, key, value)
            existing_product.save()
        else:
            # Create a new product entry
            Products.objects.create(**product_defaults)

    return JsonResponse({'message': 'Product information stored successfully.'})


def Dashboard(request):
    return render(request, 'dashboard_temp/index.html')


def do_false(request):
    products = Products.objects.filter(po_generated=True)
    products.update(po_generated=False)
    return JsonResponse({"message": "Updated successfully."})


def Get_Suppliers(request):
    return redirect('Order:letest_supplier')


def Lestest_Suppliers(request):
    suppliers = Products.objects.filter(
        po_generated=False).values_list('primary_supplier', flat=True)
    unique_suppliers_list = list(set(suppliers))
    context = {
        'unique_suppliers': unique_suppliers_list
    }
    return render(request, 'dashboard_temp/get_suppliers.html', context)


def Suppliers_SKU(request):
    if request.method == "POST":
        supplier = request.POST.get('supplier')
        skus = Products.objects.filter(
            primary_supplier=supplier, po_generated=False)
        context = {
            "supplier_skus": skus,
            "supplier": supplier,
        }
        return render(request, 'dashboard_temp/suppliers_sku.html', context)
    return redirect("Order:letest_supplier")


def Create_purchase_order(request):
    if request.method == "POST":
        supplier = request.POST.get('supplier')
        supplier_skus = Products.objects.select_related('order', 'OrderLine').filter(
            primary_supplier=supplier,
            po_generated=False
        )
        # Iterate over the supplier's SKUs and add them to the purchase order
        list_of_products = []
        total_price = Decimal(0.0)  # Initialize total price
        for supplier_sku in supplier_skus:
            product = supplier_sku
            supplier_sku.po_generated = True
            supplier_sku.save()

            list_of_products.append(product)

            # Add the product's misc27 value to the total price
            total_price += Decimal(product.misc27)

        # Create a new purchase order
        purchase_order = PurchaseOrder(
            Supplier=supplier, total_cost=total_price)
        purchase_order.save()

        # Add the products to the purchase order
        purchase_order.products.set(list_of_products)

        context = {
            "supplier": supplier,
            "purchase_order": purchase_order,
        }
        return render(request, 'dashboard_temp/PO_details_after_genrate_PO.html', context)
    return redirect("Order:letest_supplier")


def List_Of_PO_Stock_Update_suppliers(request):
    purchase_orders = PurchaseOrder.objects.filter(submitted=False)
    suppliers = set(
        purchase_order.Supplier for purchase_order in purchase_orders)
    unique_suppliers = list(suppliers)
    
    
    context = {
        "unique_suppliers": unique_suppliers,
    }
    return render(request, 'dashboard_temp/list_of_po_stock_update_suppliers.html', context)

def Supplier_PO_List(request):
    if request.method == "GET":
        supplier = request.GET.get('supplier')
        purchase_orders = PurchaseOrder.objects.filter(Supplier=supplier, submitted=False)
        
        purchase_order_id = [purchase_order.PurchaseOrderID for purchase_order in purchase_orders]
        return JsonResponse(purchase_order_id, safe=False)



def Updated_PO_Stock(request):
    po_id = request.GET.get('po_id')
    purchase_order = PurchaseOrder.objects.get(PurchaseOrderID=po_id)
    for i in purchase_order.products.all():
        print(i,"!!!!!!!!!!!")
    
    return render(request, 'dashboard_temp/PO_Stock_Update.html', {'purchase_order': purchase_order})
    






def po_stock_update_excel(request):
    if request.method == 'POST':
        excel_file = request.FILES['excel_file']
        purchase_order_id = request.POST.get('PurchaseOrderID')
        file_extension = os.path.splitext(excel_file.name)[1].lower()
        try:
            # Read the Excel file using pandas with appropriate engine based on file extension
            if file_extension == '.xls':
                df = pd.read_excel(excel_file, engine='xlrd')
            elif file_extension == '.xlsx':
                df = pd.read_excel(excel_file, engine='openpyxl')
            else:
                messages.error(
                    request, "Invalid file format. Only .xls and .xlsx are supported.")
                redirect_url = reverse('Order:po_stock_update')
                return redirect(redirect_url)
            if 'SKU' in df.columns and 'Stock' in df.columns:
                for index, row in df.iterrows():
                    sku = row['SKU']
                    stock = row['Stock']
                    # Update the stock based on the SKU
                    order_lines = OrderLine.objects.filter(SKU=sku)
                    for order_line in order_lines:
                        order_line.quantities_received = stock
                        order_line.save()

                url = reverse('Order:po_stock_update')
                url_with_params = url + f'?Purchase_id={purchase_order_id}'
                return redirect(url_with_params)

            else:
                messages.error(
                    request, "Invalid Excel file. Column names are missing.")
                url = reverse('Order:po_stock_update')
                url_with_params = url + f'?Purchase_id={purchase_order_id}'
                return redirect(url_with_params)

        except Exception as e:
            messages.error(request, "Error: {}".format(e))
            url = reverse('Order:po_stock_update')
            url_with_params = url + f'?Purchase_id={purchase_order_id}'
            return redirect(url_with_params)

    messages.info(request, "Invalid request.")
    url = reverse('Order:po_stock_update')
    url_with_params = url + f'?Purchase_id={purchase_order_id}'
    return redirect(url_with_params)


def generate_pdf(request, id):

    purchase_order = PurchaseOrder.objects.get(PurchaseOrderID=id)
    purchase_order_id = id
    PO_Details = {
        'PurchaseOrderID': purchase_order.PurchaseOrderID,
        'Alias': purchase_order.Alias,
        'Supplier': purchase_order.Supplier,
        'date_created': purchase_order.date_created,
        'tracking_id': purchase_order.tracking_id,
        'courier': purchase_order.courier,
        'total_cost': purchase_order.total_cost,
        "submitted": purchase_order.submitted,
    }
    PO_Orders = purchase_order.products.all()
    total_quantity = sum(
        [order.OrderLine.quantities_received for order in PO_Orders])

    context = {
        'PO_Details': PO_Details,
        'PO_Orders': PO_Orders,
        'purchase_order_id': purchase_order_id,
        'total_quantity': total_quantity,
    }
    html_string = render_to_string('dashboard_temp/pdf.html', context=context)
    pdf_file = HTML(string=html_string).write_pdf()
    response = HttpResponse(content_type='application/pdf')
    file_name = f"Purchase_Order_{purchase_order_id}.pdf"
    response['Content-Disposition'] = 'attachment; file_name="{}"'.format(
        file_name)
    response.write(pdf_file)

    return response
