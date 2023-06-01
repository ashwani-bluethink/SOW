from django.shortcuts import render
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
    dict_filter = { 'DatePlacedFrom': "2022-06-01 00:00:00",
    'OrderStatus': ['New Backorder','Pending Pickup']}
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
    api_fields = ['SKU', 'PrimarySupplier', 'DefaultPrice', 'SupplierId', 'Misc27']

    # Fetch all products and put them in a dictionary for fast lookups
    existing_products = {product.sku: product for product in Products.objects.all()}

    for orderline_instance in   skus_and_orders:
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




def get_suppliers(request):
    suppliers = Products.objects.values('primary_supplier').distinct().order_by('primary_supplier')
    unique_suppliers = [item['primary_supplier'] for item in suppliers]
    result = {}
    for supplier in unique_suppliers:
        purchase_orders = Products.objects.select_related('order', 'OrderLine').filter(
            primary_supplier=supplier,
            po_generated=False
        )
        if purchase_orders.exists():  # Check if there are any purchase orders to create
            orders_list = []
            total_cost = 0.0
            for order in purchase_orders:
                misc27_sum = sum(float(product.misc27) for product in order.order.products.all())
                total_cost += misc27_sum
                orders_list.append({
                    "OrderID": order.order.OrderID,
                    "OrderLineID": order.OrderLine.OrderLineID,
                    "SKU": order.sku,
                    "Misc27": order.misc27,
                    "PrimarySupplier": order.primary_supplier,
                    "InventoryID": order.inventory_id,
                    "DefaultPrice": order.default_price,
                    "Ack": order.ack,
                    "QuantitiesReceived": order.quantities_received,
                    "TotalMisc27": misc27_sum
                })
            
            # Save purchase order data in the PurchaseOrder model
            purchase_order = PurchaseOrder.objects.create(
                Supplier=supplier,
                total_cost=total_cost
            )
            
            
            
            # Bulk insertion of products
            products_to_add = [
                product for product in purchase_orders.only('order', 'OrderLine', 'sku', 'misc27')
            ]
            purchase_order.products.set(products_to_add)
            purchase_orders.update(po_generated=True)
            
            # Save the changes to the purchase order
            purchase_order.save()
            

            result[supplier] = orders_list

    return JsonResponse({"Purchase Order": result})






def do_false(request):
    products = Products.objects.filter(po_generated=True)
    products.update(po_generated=False)
    return JsonResponse({"message": "Updated successfully."})