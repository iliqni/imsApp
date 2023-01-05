from django.contrib import admin
from imsApp.models import Category, Product, Stock, Invoice, Invoice_Item
# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Stock)
admin.site.register(Invoice)
admin.site.register(Invoice_Item)
