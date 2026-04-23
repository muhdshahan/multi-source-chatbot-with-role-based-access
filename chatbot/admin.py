from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("part_no", "price", "source")
    search_fields = ("part_no", "description")