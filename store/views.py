from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.http import JsonResponse
import json
import datetime
from django.contrib.auth import login, authenticate, logout
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate

from .models import *
from .utils import cookieCart, cartData, guestOrder
from .forms import *


def store(request):

    data = cartData(request)
    cartItems = data['cartItems']
    products = Product.objects.all()
    
    context = {'products':products,'cartItems':cartItems}
    return render(request, 'store/store.html', context)


def cart(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    
    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    
    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/checkout.html', context)


@require_http_methods(["POST"])
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    order = Order.objects.get(customer=customer, complete=False)

    return JsonResponse({
        'message':'Item was added', 
        'orderItemQuantity':orderItem.quantity, 
        'orderTotal':order.total,
        'orderItems':order.items
    }, safe=False)


@require_http_methods(["POST"])
def processOrder(request):
    transactionId = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

        
    total = float(data['form']['total'])
    order.transaction_id = transactionId

    if total == order.total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer = customer, 
            order = order, 
            address = data['shipping']['address'],
            city = data['shipping']['city'],
            state = data['shipping']['state'],
            zipcode = data['shipping']['zipcode'],
        )

    return JsonResponse('Payment completed', safe=False)


@require_http_methods(["GET", "POST"])
def signin(request):
    
    if request.user.is_authenticated:
        return redirect('store')

    if request.method == 'POST':

        form = LoginForm(request.POST)
       
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])

            if user is not None:
                login(request, user)
                
                if request.GET.get('next', None):
                    return redirect(request.GET.get('next', None))

                return redirect('store')
    else:
        form = LoginForm()

    return render(request, 'store/login.html', {'form':form})


@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect('store')

    
    if request.POST:
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            Customer.objects.create(user=user, name=user.username, email=user.email)

            login(request, user)

            return redirect('store')
    else:
        form = RegistrationForm()

    return render(request, 'store/register.html', context={'form':form})



@require_http_methods(["POST"])
@login_required
def signout(request):
    logout(request)
    return redirect('store')
