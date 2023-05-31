from django.shortcuts import render
from django.http import JsonResponse
import json
import requests
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.shortcuts import render
from .models import Order, OrderLine, Products
from django.core.paginator import Paginator


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

    for sku in skus_and_orders:
        product_info = api_product_response(
            {'SKU': sku.SKU},
            api_fields,
            None
        )
        try:
            order = Order.objects.get(OrderID=sku.Order)
        except Order.DoesNotExist:
            continue
        product = Products(
            order=order,
            sku=sku.SKU,
            misc27=product_info['Item'][0]['Misc27'],
            primary_supplier=product_info['Item'][0]['PrimarySupplier'],
            inventory_id=product_info['Item'][0]['InventoryID'],
            default_price=float(product_info['Item'][0]['DefaultPrice']),
            ack = product_info["Ack"],
        )
        product.save()

    return JsonResponse({'message': 'Product information stored successfully.'})



from django.db.models import Prefetch

# Assuming you have already imported the required models

# def get_suppliers_and_products(request):
#     # Retrieve all suppliers with their related products using Prefetch
#     suppliers = Products.objects.select_related('order').prefetch_related(
#         Prefetch('order__order_lines', queryset=OrderLine.objects.select_related('Order')),
#     )
    
#     supplier_products = {}
    
#     for supplier in suppliers:
#         supplier_name = supplier.primary_supplier
        
#         # Create an entry for the supplier if it doesn't exist
#         if supplier_name not in supplier_products:
#             supplier_products[supplier_name] = []
        
#         # Retrieve the products related to the supplier
#         products = supplier.order.products.all()
#         supplier_products[supplier_name].extend(products)
    
   

#     # Iterate over the supplier_products dictionary
#     for supplier, products in supplier_products.items():
#         print(f"Supplier: {supplier}")
        
#         for product in products:
#             print(f"Product SKU: {product.sku}")
#             # Print other product details if needed


import json
from django.http import JsonResponse
from django.db.models import Prefetch
from Order.models import OrderLine

def get_suppliers_and_products(request):
    # Retrieve all suppliers with their related products using Prefetch
    suppliers = Products.objects.select_related('order').prefetch_related(
        Prefetch('order__order_lines', queryset=OrderLine.objects.select_related('Order')),
    )
    
    supplier_products = {}
    
    for supplier in suppliers:
        supplier_name = supplier.primary_supplier
        
        # Create an entry for the supplier if it doesn't exist
        if supplier_name not in supplier_products:
            supplier_products[supplier_name] = []
        
        # Retrieve the products related to the supplier
        products = supplier.order.products.filter(order__OrderStatus='New Backorder')
        supplier_products[supplier_name].extend(products)
    
    # Prepare the response data
    response_data = {
        'suppliers': []
    }
    
    # Iterate over the supplier_products dictionary
    for supplier, products in supplier_products.items():
        supplier_data = {
            'name': supplier,
            'products': []
        }
        
        for product in products:
            try:
                order_line = OrderLine.objects.get(Order=product.order, SKU=product.sku)
                quantity = order_line.Quantity
            except OrderLine.DoesNotExist:
                quantity = None
            
            product_data = {
                'sku': product.sku,
                'misc27': product.misc27,
                'primary_supplier': product.primary_supplier,
                'inventory_id': product.inventory_id,
                'default_price': product.default_price,
                'ack': product.ack,
                'order_id': product.order.OrderID,
                'quantity': quantity
            }
            
            supplier_data['products'].append(product_data)
        
        response_data['suppliers'].append(supplier_data)

    # Return the response as JSON
    return JsonResponse(response_data)


def get_supplier_names(request):
    suppliers = Products.objects.values_list('primary_supplier', flat=True).distinct()
    return list(suppliers)


    

#################################################################### test apis ##################################################


# def index(request):
#     return render(request, 'index.html')


# def api_order_response(dict_filter, List_of_OutputSelector=None, new_headers=None):
#     url = "https://www.findsports.com.au/do/WS/NetoAPI"
#     parent_dict = {}
#     dict_export_status = {}
#     dict_filter = dict_filter.copy()
#     dict_filter['OutputSelector'] = List_of_OutputSelector
#     dict_export_status["ExportStatus"] = "Exported"
#     dict_filter["UpdateResults"] = dict_export_status
#     parent_dict['Filter'] = dict_filter
#     payload = json.dumps(parent_dict)
#     product_headers_order = {
#         'NETOAPI_ACTION': "GetOrder",
#         'NETOAPI_USERNAME': "API-User-Product",
#         'NETOAPI_KEY': "v0fmsHHYPqfq99lFnPJ1kQbIgynkbLJq",
#         'Accept': "application/json",
#         'Content-Type': "application/javascript",
#         'cache-control': "no-cache",
#         'Postman-Token': "2473156a-3bcc-4a64-8079-04c3a395b5ea"
#     }
#     if new_headers is None:
#         header = product_headers_order
#         response = requests.request("POST", url, data=payload, headers=header)
#         json1_data = json.loads(response.text)
#     return json1_data


# def order_view(request):
#     dict_filter = {
#         'OrderStatus': ['Pending Pickup', 'Pending Dispatch', 'On Hold', 'Backorder Approved', 'Pack', 'New Backorder', 'New', 'Pick', 'Uncommitted']
#     }
#     # output_selector = ['Email','OrderID', 'OrderStatus', 'ShippingOption', 'SalesChannel', 'OrderLine', 'DatePlaced', 'OrderLine.ItemNotes', 'InternalOrderNotes', 'Supplier', 'CustomerRef3', 'CustomerRef4', 'CustomerRef5', 'CustomerRef6', 'CustomerRef7']
#     output_selector= [
#       "ShippingOption",
#       "DeliveryInstruction",
#       "Username",
#       "Email",
#       "ShipAddress",
#       "BillAddress",
#       "CustomerRef1",
#       "CustomerRef2",
#       "CustomerRef3",
#       "CustomerRef4",
#       "SalesChannel",
#       "GrandTotal",
#       "ShippingTotal",
#       "ShippingDiscount",
#       "OrderType",
#       "OrderStatus",
#       "OrderPayment",
#       "OrderPayment.PaymentType",
#       "OrderPayment.DatePaid",
#       "DatePlaced",
#       "DateRequired",
#       "DateInvoiced",
#       "DatePaid",
#       "OrderLine",
#       "OrderLine.ProductName",
#       "OrderLine.PickQuantity",
#       "OrderLine.BackorderQuantity",
#       "OrderLine.UnitPrice",
#       "OrderLine.WarehouseID",
#       "OrderLine.WarehouseName",
#       "OrderLine.WarehouseReference",
#       "OrderLine.Quantity",
#       "OrderLine.PercentDiscount",
#       "OrderLine.ProductDiscount",
#       "OrderLine.CostPrice",
#       "OrderLine.ShippingMethod",
#       "OrderLine.ShippingTracking",
#       "ShippingSignature",
#       "eBay.eBayUsername",
#       "eBay.eBayStoreName",
#       "OrderLine.eBay.eBayTransactionID",
#       "OrderLine.eBay.eBayAuctionID",
#       "OrderLine.eBay.ListingType",
#       "OrderLine.eBay.DateCreated",
#       "OrderLine.eBay.DatePaid"
#     ]

#     order_data = api_order_response(dict_filter, output_selector)
#     # order_data = order_data['Order']
#     # total_orders = len(order_data)

#     # paginator = Paginator(order_data, 10) # Show 10 orders per page

#     # page_number = request.GET.get('page')
#     # page_obj = paginator.get_page(page_number)
#     return JsonResponse({'order_data': order_data,})

#     # return render(request, 'index.html', {'total_orders':total_orders, 'page_obj': page_obj})

# def Order_parameter_to_get_data():
#     dict_filter = {
#         'OrderStatus': ['Pending Pickup', 'Pending Dispatch', 'On Hold', 'Backorder Approved', 'Pack', 'New Backorder', 'New', 'Pick', 'Uncommitted']
#     }
#     output_selector = ['OrderID', 'OrderStatus', 'ShippingOption', 'SalesChannel', 'OrderLine', 'DatePlaced', 'OrderLine.ItemNotes', 'InternalOrderNotes', 'Supplier', 'CustomerRef3', 'CustomerRef4', 'CustomerRef5', 'CustomerRef6', 'CustomerRef7']
#     order_data = api_order_response(dict_filter, output_selector)
#     return order_data


# def insert_order_data(request):
#     order_data = Order_parameter_to_get_data()
#     orders = order_data['Order']
#     for order_info in orders:
#         order_lines_data = order_info.pop('OrderLine', [])
#         order_id = order_info['OrderID']

#         order, created = Order.objects.update_or_create(OrderID=order_id, defaults=order_info)

#         for order_line_data in order_lines_data:
#             order_line_id = order_line_data['OrderLineID']

#             # Add the order reference to the order line data
#             order_line_data['Order'] = order

#             order_line, created = OrderLine.objects.update_or_create(OrderLineID=order_line_id, defaults=order_line_data)

#     return JsonResponse({'message': 'Data inserted successfully'})


# def Fiter_order_view(request):
#     dict_filter = {
#         'DatePlacedFrom': "2022-06-01 00:00:00",
#         'OrderStatus': ['Pending Pickup', 'Pending Dispatch', 'On Hold', 'Backorder Approved', 'Pack', 'New Backorder', 'New', 'Pick', 'Uncommitted']
#     }
#     if request.method == "POST":
#         if request.POST.get('DatePlacedFrom'):
#             DatePlacedFrom = request.POST.get('DatePlacedFrom')
#             dict_filter['DatePlacedFrom'] = DatePlacedFrom
#         if request.POST.get('OrderStatus'):
#             OrderStatus = request.POST.get('OrderStatus')
#             dict_filter['OrderStatus'] = OrderStatus

#     output_selector = ['OrderID', 'OrderStatus', 'ShippingOption', 'SalesChannel', 'OrderLine', 'DatePlaced', 'OrderLine.ItemNotes', 'InternalOrderNotes', 'Supplier', 'CustomerRef3', 'CustomerRef4', 'CustomerRef5', 'CustomerRef6', 'CustomerRef7']
#     order_data = api_order_response(dict_filter, output_selector)
#     order_data = order_data['Order']

#     return render(request, 'order.html', {'order_data': order_data})


# # API Headers
# product_headers_products = {
#     'NETOAPI_ACTION': "GetItem",
#     'NETOAPI_USERNAME': "API-User-Product",
#     'NETOAPI_KEY': "v0fmsHHYPqfq99lFnPJ1kQbIgynkbLJq",
#     'Accept': "application/json",
#     'Content-Type': "application/javascript",
#     'cache-control': "no-cache",
#     'Postman-Token': "2473156a-3bcc-4a64-8079-04c3a395b5ea"
# }

# Function to call API
# def api_product_response(dict_filter, List_of_OutputSelector=None, new_headers=None):
#     url = "https://www.findsports.com.au/do/WS/NetoAPI"
#     parent_dict = {}
#     dict_export_status = {}
#     dict_filter['OutputSelector'] = List_of_OutputSelector
#     dict_export_status["ExportStatus"] = "Exported"
#     dict_filter["UpdateResults"] = dict_export_status
#     parent_dict['Filter'] = dict_filter
#     payload = json.dumps(parent_dict)

#     if new_headers is None:
#         header = product_headers_products

#     response = requests.request("POST", url, data=payload, headers=header)
#     json_data = response.json()

#     return json_data

# @csrf_exempt
# def product_info_api(request):
#     if request.method == "POST":
#         # data = json.loads(request.body)
#         # sku = data.get("sku")

#         # Call the API function to get product information
#         product_info = api_product_response(
#             {'SKU': 415245143},
#             ['SKU', 'PrimarySupplier', 'DefaultPrice','SupplierId'],
#             None
#         )

#         return JsonResponse(product_info)

#     return JsonResponse({"error": "Invalid request method."})


# def insert_order_data(order_data):
#     # Create an Order instance
#     order = Order.objects.create(
#         ShippingOption=order_data['ShippingOption'],
#         CustomerRef4=order_data['CustomerRef4'],
#         SalesChannel=order_data['SalesChannel'],
#         InternalOrderNotes=order_data['InternalOrderNotes'],
#         OrderID=order_data['OrderID'],
#         CustomerRef6=order_data['CustomerRef6'],
#         CustomerRef3=order_data['CustomerRef3'],
#         DatePlaced=order_data['DatePlaced'],
#         OrderStatus=order_data['OrderStatus'],
#         CustomerRef5=order_data['CustomerRef5'],
#         CustomerRef7=order_data['CustomerRef7'],
#     )

#     # Create OrderLine instances
#     order_lines_data = order_data['OrderLine']
#     order_lines = []
#     for order_line_data in order_lines_data:
#         order_line = OrderLine(
#             Quantity=order_line_data['Quantity'],
#             SKU=order_line_data['SKU'],
#             OrderLineID=order_line_data['OrderLineID'],
#             ItemNotes=order_line_data['ItemNotes'],
#             Order=order,  # Associate the OrderLine with the Order instance
#         )
#         order_lines.append(order_line)

#     OrderLine.objects.bulk_create(order_lines)


# # Example usage
# order_data = {
#     # your order data here
# }

# insert_order_data(order_data)
