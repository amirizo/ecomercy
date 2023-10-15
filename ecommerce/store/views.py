from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth import authenticate, login,logout
import datetime
from .models import *
from . utils import cookieCart, cartData
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from .forms import CreationUserForm
# Create your views here.

def registerPage(request):
    forms = CreationUserForm

    if request.method == 'GET':
        forms = CreationUserForm(request.GET)
        if forms.is_valid():
            forms.save()
            user = forms.cleaned_data.get('username')
            messages.success(request, 'account was created for'  + user)
            return redirect('login')


            
    context = {'forms':forms}
    return render(request, ("store/register.html"), context)


def loginPage(request):
    if request.method == 'GET':
        username = request.GET.get('usernmae')
        username = request.GET.get('password')

    user = authenticate(request, usename=username, password=password)
    context = {}
    return render(request, ("store/login.html"))

















def store(request):
    data = cartData(request)
    cartItem = data['cartItem']

    products = Product.objects.all()
    context = {'products': products, 'cartItem': cartItem}
    return render(request, ("store/store.html"), context)


def cart(request):
    data = cartData(request)
    cartItem = data['cartItem']
    order = data['order']
    items = data['items']


    context = {'items': items,  'order': order, 'cartItem': cartItem}
    return render(request, ("store/cart.html"), context)


def checkout(request):
   
    
    data = cartData(request)
    cartItem = data['cartItem']
    order = data['order']
    items = data['items']


    context = {'items': items,  'order': order, 'cartItem': cartItem}
    return render(request, ("store/checkout.html"), context)


def updateItem(request):
    if request.method == "GET":
        productId = request.GET.get("productId")
        action = request.GET.get("action")

        print('action:', action)
        print('productId:', productId)
        
        if request.user.is_authenticated:
            customer = request.user.customer
        else:
            customer = ''
       
        product = Product.objects.get(id=productId)
        order, created = Order.objects.get_or_create(customer=customer ,complete=False)
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)


        if action == 'add':
            orderItem.quantity = (orderItem.quantity + 1)

        elif action == 'remove':
            orderItem.quantity = (orderItem.quantity - 1)
            
        orderItem.save()

        if orderItem.quantity <= 0:
            orderItem.delete()
    return JsonResponse(('item was added'), safe=False)

def processOrder(request):
    if request.method == "GET":
        form_data = request.GET.get("form")
        shipping_data = request.GET.get("shipping")

        form_data_dict = json.loads(form_data)
        shipping_data_dict = json.loads(shipping_data)

        transaction_id = datetime.datetime.now().timestamp()

        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            total = float(form_data_dict['total'])
            order.transaction_id = transaction_id

        if total == float(order.get_cart_total):
            order.complete = True
        order.save()

        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=shipping_data_dict['address'],
                city=shipping_data_dict['city'],
                state=shipping_data_dict['state'],
                zipcode=shipping_data_dict['zipcode'],
                country=shipping_data_dict['country'],
            )
    else:
        print('user is not logged in')

        print('COOKIES:', request.COOKIES)
        name = form_data_dict['name']
        email = form_data_dict['email']

        cookieData = cookieCart(request)
        items = cookieData['items']

        customer, created = Customer.objects.get_or_create(
            email=email,
        )
        customer.name = name
        customer.save()

        order = Order.objects.create(
            customer=customer,
            complete=False,
        )
        for item in items:
            product = Product.objects.get(id=item['product']['id'])

            orderItem = OrderItem.objects.create(
                product=product,
                order=order,
                quantity=item['quantity']
            )

    total = float(form_data_dict['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=shipping_data_dict['address'],
            city=shipping_data_dict['city'],
            state=shipping_data_dict['state'],
            zipcode=shipping_data_dict['zipcode'],
            country=shipping_data_dict['country'],
        )
    return JsonResponse(('payment subbmitted..'), safe=False)


from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

def success(request):
    template = render_to_string(("store/email_template.html"), {"name":request.user.customer})
    email = EmailMessage(
        'Ahsante kwa kujiunga on amir first project trainee',
        template,
        settings.EMAIL_HOST_USER,
        [request.user.customer.email],
    )
    email.fail_silently=False
    email.send()
    context = {}
    return render(request, (), context)