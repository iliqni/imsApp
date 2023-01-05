from email import message
from unicodedata import category
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from ims_django.settings import MEDIA_ROOT, MEDIA_URL
import json
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from imsApp.forms import SaveStock, UserRegistration, UpdateProfile, UpdatePasswords, SaveCategory, SaveProduct, SaveInvoice, SaveInvoiceItem
from imsApp.models import Category, Product, Stock, Invoice, Invoice_Item
from cryptography.fernet import Fernet
from django.conf import settings
import base64

context = {
    'page_title' : 'File Management System',
}
#login
def login_user(request):
    logout(request)
    resp = {"status":'failed','msg':''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status']='success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp),content_type='application/json')

#Logout
def logoutuser(request):
    logout(request)
    return redirect('/')

@login_required
def home(request):
    context['page_title'] = 'Home'
    context['categories'] = Category.objects.count()
    context['products'] = Product.objects.count()
    context['sales'] = Invoice.objects.count()
    return render(request, 'home.html',context)

def registerUser(request):
    user = request.user
    if user.is_authenticated:
        return redirect('home-page')
    context['page_title'] = "Register User"
    if request.method == 'POST':
        data = request.POST
        form = UserRegistration(data)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            pwd = form.cleaned_data.get('password1')
            loginUser = authenticate(username= username, password = pwd)
            login(request, loginUser)
            return redirect('home-page')
        else:
            context['reg_form'] = form

    return render(request,'register.html',context)

@login_required
def update_profile(request):
    context['page_title'] = 'Update Profile'
    user = User.objects.get(id = request.user.id)
    if not request.method == 'POST':
        form = UpdateProfile(instance=user)
        context['form'] = form
        print(form)
    else:
        form = UpdateProfile(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile has been updated")
            return redirect("profile")
        else:
            context['form'] = form
            
    return render(request, 'manage_profile.html',context)


@login_required
def update_password(request):
    context['page_title'] = "Update Password"
    if request.method == 'POST':
        form = UpdatePasswords(user = request.user, data= request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Your Account Password has been updated successfully")
            update_session_auth_hash(request, form.user)
            return redirect("profile")
        else:
            context['form'] = form
    else:
        form = UpdatePasswords(request.POST)
        context['form'] = form
    return render(request,'update_password.html',context)


@login_required
def profile(request):
    context['page_title'] = 'Profile'
    return render(request, 'profile.html',context)


# Category
@login_required
def category_mgt(request):
    context['page_title'] = "Product Categories"
    categories = Category.objects.all()
    context['categories'] = categories

    return render(request, 'category_mgt.html', context)

@login_required
def save_category(request):
    resp = {'status':'failed','msg':''}
    if request.method == 'POST':
        if (request.POST['id']).isnumeric():
            category = Category.objects.get(pk=request.POST['id'])
        else:
            category = None
        if category is None:
            form = SaveCategory(request.POST)
        else:
            form = SaveCategory(request.POST, instance= category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category has been saved successfully.')
            resp['status'] = 'success'
        else:
            for fields in form:
                for error in fields.errors:
                    resp['msg'] += str(error + "<br>")
    else:
        resp['msg'] = 'No data has been sent.'
    return HttpResponse(json.dumps(resp), content_type = 'application/json')

@login_required
def manage_category(request, pk=None):
    context['page_title'] = "Manage Category"
    if not pk is None:
        category = Category.objects.get(id = pk)
        context['category'] = category
    else:
        context['category'] = {}

    return render(request, 'manage_category.html', context)

@login_required
def delete_category(request):
    resp = {'status':'failed', 'msg':''}

    if request.method == 'POST':
        try:
            category = Category.objects.get(id = request.POST['id'])
            category.delete()
            messages.success(request, 'Category has been deleted successfully')
            resp['status'] = 'success'
        except Exception as err:
            resp['msg'] = 'Category has failed to delete'
            print(err)

    else:
        resp['msg'] = 'Category has failed to delete'
    
    return HttpResponse(json.dumps(resp), content_type="application/json")
        
# product
@login_required
def product_mgt(request):
    context['page_title'] = "Product List"
    products = Product.objects.all()
    context['products'] = products

    return render(request, 'product_mgt.html', context)

@login_required
def save_product(request):
    resp = {'status':'failed','msg':''}
    if request.method == 'POST':
        if (request.POST['id']).isnumeric():
            product = Product.objects.get(pk=request.POST['id'])
        else:
            product = None
        if product is None:
            form = SaveProduct(request.POST)
        else:
            form = SaveProduct(request.POST, instance= product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product has been saved successfully.')
            resp['status'] = 'success'
        else:
            for fields in form:
                for error in fields.errors:
                    resp['msg'] += str(error + "<br>")
    else:
        resp['msg'] = 'No data has been sent.'
    return HttpResponse(json.dumps(resp), content_type = 'application/json')

@login_required
def manage_product(request, pk=None):
    context['page_title'] = "Manage Product"
    if not pk is None:
        product = Product.objects.get(id = pk)
        context['product'] = product
    else:
        context['product'] = {}

    return render(request, 'manage_product.html', context)

@login_required
def delete_product(request):
    resp = {'status':'failed', 'msg':''}

    if request.method == 'POST':
        try:
            product = Product.objects.get(id = request.POST['id'])
            product.delete()
            messages.success(request, 'Product has been deleted successfully')
            resp['status'] = 'success'
        except Exception as err:
            resp['msg'] = 'Product has failed to delete'
            print(err)

    else:
        resp['msg'] = 'Product has failed to delete'
    
    return HttpResponse(json.dumps(resp), content_type="application/json")

#Inventory
@login_required
def inventory(request):
    context['page_title'] = 'Inventory'

    products = Product.objects.all()
    context['products'] = products

    return render(request, 'inventory.html', context)

#Inventory History
@login_required
def inv_history(request, pk= None):
    context['page_title'] = 'Inventory History'
    if pk is None:
        messages.error(request, "Product ID is not recognized")
        return redirect('inventory-page')
    else:
        product = Product.objects.get(id = pk)
        stocks = Stock.objects.filter(product = product).all()
        context['product'] = product
        context['stocks'] = stocks

        return render(request, 'inventory-history.html', context )

#Stock Form
@login_required
def manage_stock(request,pid = None ,pk = None):
    if pid is None:
        messages.error(request, "Product ID is not recognized")
        return redirect('inventory-page')
    context['pid'] = pid
    if pk is None:
        context['page_title'] = "Add New Stock"
        context['stock'] = {}
    else:
        context['page_title'] = "Manage New Stock"
        stock = Stock.objects.get(id = pk)
        context['stock'] = stock
    
    return render(request, 'manage_stock.html', context )

@login_required
def save_stock(request):
    resp = {'status':'failed','msg':''}
    if request.method == 'POST':
        if (request.POST['id']).isnumeric():
            stock = Stock.objects.get(pk=request.POST['id'])
        else:
            stock = None
        if stock is None:
            form = SaveStock(request.POST)
        else:
            form = SaveStock(request.POST, instance= stock)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock has been saved successfully.')
            resp['status'] = 'success'
        else:
            for fields in form:
                for error in fields.errors:
                    resp['msg'] += str(error + "<br>")
    else:
        resp['msg'] = 'No data has been sent.'
    return HttpResponse(json.dumps(resp), content_type = 'application/json')

@login_required
def delete_stock(request):
    resp = {'status':'failed', 'msg':''}

    if request.method == 'POST':
        try:
            stock = Stock.objects.get(id = request.POST['id'])
            stock.delete()
            messages.success(request, 'Stock has been deleted successfully')
            resp['status'] = 'success'
        except Exception as err:
            resp['msg'] = 'Stock has failed to delete'
            print(err)

    else:
        resp['msg'] = 'Stock has failed to delete'
    
    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def sales_mgt(request):
    context['page_title'] = 'Sales'
    products = Product.objects.filter(status = 1).all()
    context['products'] = products
    return render(request,'sales.html', context)


def get_product(request,pk = None):
    resp = {'status':'failed','data':{},'msg':''}
    if pk is None:
        resp['msg'] = 'Product ID is not recognized'
    else:
        product = Product.objects.get(id = pk)
        resp['data']['product'] = str(product.code + " - " + product.name)
        resp['data']['id'] = product.id
        resp['data']['price'] = product.price
        resp['status'] = 'success'
    
    return HttpResponse(json.dumps(resp),content_type="application/json")


def save_sales(request):
    resp = {'status':'failed', 'msg' : ''}
    id = 2
    if request.method == 'POST':
        pids = request.POST.getlist('pid[]')
        invoice_form = SaveInvoice(request.POST)
        if invoice_form.is_valid():
            invoice_form.save()
            invoice = Invoice.objects.last()
            for pid in pids:
                data = {
                    'invoice':invoice.id,
                    'product':pid,
                    'quantity':request.POST['quantity['+str(pid)+']'],
                    'price':request.POST['price['+str(pid)+']'],
                }
                print(data)
                ii_form = SaveInvoiceItem(data=data)
                # print(ii_form.data)
                if ii_form.is_valid():
                    ii_form.save()
                else:
                    for fields in ii_form:
                        for error in fields.errors:
                            resp['msg'] += str(error + "<br>")
                    break
            messages.success(request, "Sale Transaction has been saved.")
            resp['status'] = 'success'
            # invoice.delete()
        else:
            for fields in invoice_form:
                for error in fields.errors:
                    resp['msg'] += str(error + "<br>")

    return HttpResponse(json.dumps(resp),content_type="application/json")

@login_required
def invoices(request):
    invoice =  Invoice.objects.all()
    context['page_title'] = 'Invoices'
    context['invoices'] = invoice

    return render(request, 'invoices.html', context)

@login_required
def delete_invoice(request):
    resp = {'status':'failed', 'msg':''}

    if request.method == 'POST':
        try:
            invoice = Invoice.objects.get(id = request.POST['id'])
            invoice.delete()
            messages.success(request, 'Invoice has been deleted successfully')
            resp['status'] = 'success'
        except Exception as err:
            resp['msg'] = 'Invoice has failed to delete'
            print(err)

    else:
        resp['msg'] = 'Invoice has failed to delete'
    
    return HttpResponse(json.dumps(resp), content_type="application/json")
    