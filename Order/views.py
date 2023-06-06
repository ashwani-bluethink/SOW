
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
    # dict_filter = {'OrderStatus': 'New Backorder'}
    # output_selector = ['OrderID', 'OrderStatus',
    #                    'ShippingOption', 'SalesChannel', 'OrderLine', 'DatePlaced']
    dict_filter = {'DatePlacedFrom': "2022-06-01 00:00:00",
                   'OrderStatus': ['New Backorder', 'Pending Pickup']}
    output_selector = ['OrderID', 'OrderStatus',
                       'ShippingOption', 'SalesChannel', 'OrderLine', 'DatePlaced']
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


# def Create_purchase_order(request):
#     try:
#         suppliers = Products.objects.values('primary_supplier').distinct().order_by('primary_supplier')
#         unique_suppliers = [item['primary_supplier'] for item in suppliers]
#         result = {}
#         for supplier in unique_suppliers:
#             purchase_orders = Products.objects.select_related('order', 'OrderLine').filter(
#                 primary_supplier=supplier,
#                 po_generated=False
#             )
#             if purchase_orders.exists():  # Check if there are any purchase orders to create
#                 orders_list = []
#                 total_cost = 0.0
#                 for order in purchase_orders:
#                     misc27_sum = sum(float(product.misc27) for product in order.order.products.all())
#                     total_cost += misc27_sum
#                     orders_list.append({
#                         "OrderID": order.order.OrderID,
#                         "OrderLineID": order.OrderLine.OrderLineID,
#                         "SKU": order.sku,
#                         "Misc27": order.misc27,
#                         "PrimarySupplier": order.primary_supplier,
#                         "InventoryID": order.inventory_id,
#                         "DefaultPrice": order.default_price,
#                         "Ack": order.ack,
#                         "TotalMisc27": misc27_sum
#                     })

#                 # Save purchase order data in the PurchaseOrder model
#                 purchase_order = PurchaseOrder.objects.create(
#                     Supplier=supplier,
#                     total_cost=total_cost
#                 )


#                 # Bulk insertion of products
#                 products_to_add = [
#                     product for product in purchase_orders.only('order', 'OrderLine', 'sku', 'misc27')
#                 ]
#                 purchase_order.products.set(products_to_add)
#                 purchase_orders.update(po_generated=True)

#                 # Save the changes to the purchase order
#                 purchase_order.save()


#                 result[supplier] = orders_list
#     except Exception as e:
#             message = "Error: {}".format(e)
#             messages.info(request, message)
#             redirect_url = reverse('Order:new_purches_order')
#             return HttpResponseRedirect(redirect_url)
#     message = "Purchase orders created successfully."
#     messages.info(request, message)
#     return redirect('Order:new_purches_order')

def do_false(request):
    products = Products.objects.filter(po_generated=True)
    products.update(po_generated=False)
    return JsonResponse({"message": "Updated successfully."})


def Get_Suppliers(request):
    orders = Order.objects.all()

    for order in orders:
        products_data = order.products.filter(po_generated=False)

        total_cost = 0.0
        misc27_sum = sum(float(product.misc27) for product in products_data)
        total_cost += misc27_sum

        if products_data:  # Check if there are any products to process
            # Create a new purchase order for each order
            primary_supplier = products_data.first().primary_supplier
            purchase_order = PurchaseOrder.objects.create(
                Order=order,
                Supplier=primary_supplier,
                total_cost=total_cost
            )

            # Add all products of the order to the purchase order
            purchase_order.products.add(*products_data)

            # Mark all products in the order as processed by setting po_generated to True
            products_data.update(po_generated=True)

    return redirect('Order:letest_supplier')


def Lestest_Suppliers(request):
    # Ensuring to get current date and time according to timezone
    today = timezone.now().date()
    # Ensure that date_created is a DateTimeField
    purchase_orders = PurchaseOrder.objects.filter(date_created__gte=today)

    latest_suppliers = {}
    for purchase_order in purchase_orders:
        supplier = purchase_order.Supplier
        if supplier not in latest_suppliers:
            latest_suppliers[supplier] = []

        latest_suppliers[supplier].append(purchase_order)

    context = {
        'latest_suppliers': latest_suppliers
    }
    return render(request, 'dashboard_temp/get_suppliers.html', context)


def Order_list(request, su_name):
    supplier_orders_list = {}
    purchase_orders = PurchaseOrder.objects.filter(Supplier=su_name)

    for purchase_order in purchase_orders:
        order = purchase_order.Order

        if purchase_order.Supplier in supplier_orders_list:
            supplier_orders_list[purchase_order.Supplier].append(order)
        else:
            supplier_orders_list[purchase_order.Supplier] = [order]

    context = {
        "supplier_orders": supplier_orders_list
    }
    return render(request, 'dashboard_temp/Orderlist.html', context)


def Order_PO(request):
    orderid = request.GET.get('orderid')
    purchase_order = get_object_or_404(PurchaseOrder, Order__OrderID=orderid)
    
    products = purchase_order.products.all()
    
    context = {
        "purchase_order": purchase_order,
        "products":products
    
    }
    return render(request, 'dashboard_temp/Order_po.html', context)


def PO_Stock_Update(request):
    if request.method == 'POST':
        order_line_ids = request.POST.getlist('OrderLineID')
        quantities_received = request.POST.getlist('quantities_received')

        for order_line_id, quantity_received in zip(order_line_ids, quantities_received):
            order_line = OrderLine.objects.get(OrderLineID=order_line_id)
            if quantity_received:
                order_line.quantities_received = int(quantity_received)
            else:
                order_line.quantities_received = 0
            order_line.save()

    context = {}
    today = date.today()
    purchase_orders = PurchaseOrder.objects.filter(date_created__date=today)

    latest_suppliers = {}
    for purchase_order in purchase_orders:
        latest_suppliers[purchase_order.PurchaseOrderID] = purchase_order.Supplier

    first_Purchase_id = next(iter(latest_suppliers.keys()), None)
    Purchase_id = request.GET.get('Purchase_id')
    global PO_id
    if Purchase_id:
        try:
            purchase_order = PurchaseOrder.objects.get(
                PurchaseOrderID=Purchase_id)
            PO_id = Purchase_id
        except:
            messages.info(request, "Pourches Order not available.")
            return redirect('Order:new_purches_order')

    else:
        try:
            purchase_order = PurchaseOrder.objects.get(
                PurchaseOrderID=first_Purchase_id)
            PO_id = first_Purchase_id
        except:
            messages.info(request, "Pourches Order not available.")
            return redirect('Order:new_purches_order')

    if purchase_order:
        PO_Details = {
            'PurchaseOrderID': purchase_order.PurchaseOrderID,
            'Alias': purchase_order.Alias,
            'Supplier': purchase_order.Supplier,
            'date_created': purchase_order.date_created,
            'tracking_id': purchase_order.tracking_id,
            'courier': purchase_order.courier,
            'total_cost': purchase_order.total_cost,
        }
        PO_Orders = purchase_order.products.all()
        context = {
            "latest_suppliers": latest_suppliers,
            "PO_Orders": PO_Orders,
            "PO_Details": PO_Details,
            "purchase_order_id": PO_id,
        }
    return render(request, 'dashboard_temp/PO_Stock_Update.html', context)


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
