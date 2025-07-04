from django.contrib import admin

from under.models import Item, Category, StockIn, StockOut, Department
# Register your models here.    
admin.site.register(Item)   
admin.site.register(Category)
admin.site.register(StockIn)
admin.site.register(StockOut)
admin.site.register(Department)