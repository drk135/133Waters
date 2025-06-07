from django.contrib import admin

from .models import Costprice, Warehouse, Product, Customer,Sale, Quatation,Expense,MarketPrice

admin.site.register(Costprice)
admin.site.register(Warehouse)
admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Sale)
admin.site.register(Quatation)
admin.site.register(Expense)
admin.site.register(MarketPrice)
