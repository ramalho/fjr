from django.contrib import admin
from .models import Brand, RollingStock


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['flag', 'name']
    list_display_links = ['name']
    search_fields = ['name']


@admin.register(RollingStock)
class RollingStockAdmin(admin.ModelAdmin):
    list_display = ['brand', 'code', 'type', 'description', 'era', 'dcc_address', 'quantity']
    list_display_links = ['code', 'description']
    list_filter = ['type', 'brand', 'era']
    search_fields = ['code', 'description', 'prototype']
    fieldsets = [
        (None, {
            'fields': ['type', 'brand', 'code', 'description', 'quantity', 'unit_price', 'era', 'acquired', 'prototype', 'product_url', 'notes'],
        }),
        ('DCC', {
            'classes': ['collapse'],
            'fields': ['dcc_address'],
        }),
    ]
