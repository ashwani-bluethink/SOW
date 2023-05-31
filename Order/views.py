from django.shortcuts import render
from django.http import JsonResponse
import json
import requests
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.shortcuts import render
from .models import Order, OrderLine, Products
from django.db.models import Q


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





# def product_insert_db(request):
#     skus_and_orders = OrderLine.objects.only('SKU', 'Order', 'OrderLineID')
#     api_fields = ['SKU', 'PrimarySupplier', 'DefaultPrice', 'SupplierId', 'Misc27']

#     for sku in skus_and_orders:
#         product_info = api_product_response(
#             {'SKU': sku.SKU},
#             api_fields,
#             None
#         )
#         try:
#             order = Order.objects.get(OrderID=sku.Order)
#         except Order.DoesNotExist:
#             continue
#         try:
#             order_line = OrderLine.objects.get(OrderLineID=sku.OrderLineID)
#         except OrderLine.DoesNotExist:
#             continue
        
#         product_defaults = {
#             'order': order,
#             'OrderLine': order_line,
#             'sku': sku.SKU,
#             'misc27': product_info['Item'][0]['Misc27'],
#             'primary_supplier': product_info['Item'][0]['PrimarySupplier'],
#             'inventory_id': product_info['Item'][0]['InventoryID'],
#             'default_price': float(product_info['Item'][0]['DefaultPrice']),
#             'ack': product_info["Ack"],
#         }
        
#         # Check if the product already exists in the table
#         existing_product = Products.objects.filter(
#             Q(order=order) & Q(OrderLine=order_line) & Q(sku=sku.SKU)
#         )

        
#         if existing_product:
#             # Update existing product information
#             existing_product.update(**product_defaults)
#         else:
#             # Create a new product entry
#             Products.objects.create(**product_defaults)

#     return JsonResponse({'message': 'Product information stored successfully.'})
