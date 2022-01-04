import json
from .models import *
from django.http.response import HttpResponse

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    items = []
    order = {'total':0,'items':0, 'shipping':False}

    for i in cart:
        try:

            product = Product.objects.get(id=i)
            total = (product.price*cart[i]['quantity'])

            order['total'] += total
            order['items'] += cart[i]['quantity']

            item = {
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'imageURL':product.imageURL
                },
                'quantity':cart[i]['quantity'],
                'total':total
            }

            items.append(item)

            if product.digital == False:
                order['shipping']=True
        except:
            pass
    
    return {'order':order, 'items':items, 'cartItems': order['items']}
    

def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.items
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
        cartItems = cookieData['cartItems']

    return {'order':order, 'items':items, 'cartItems':cartItems}


def guestOrder(request, data):
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(
            email=email 
        )
    customer.name = name
    customer.save()

    order = Order.objects.create(customer=customer, complete=False)

    for item in items:
        product = Product.objects.get(id=item['product']['id'])
        orderItem = OrderItem.objects.create(
            product=product, order=order, quantity=item['quantity']
        )
    
    return customer, order