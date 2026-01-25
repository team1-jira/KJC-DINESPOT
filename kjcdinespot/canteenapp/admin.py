from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Item, CartItem, Reviews, Payment
from django.db import models

# Admin customization for the Item model
class ItemAdmin(admin.ModelAdmin):
    fieldsets = [
        ("General Information", {'fields': ['title', 'description', 'price', 'pieces', 'category', 'instructions', 'image', 'labels']}),
        ("Canteen", {'fields': ['canteen']}),
    ]
    list_display = ('id', 'title', 'description', 'price', 'pieces', 'category', 'labels', 'canteen')
    search_fields = ('title', 'description', 'canteen__name')


class ReviewsAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'rating', 'posted_on')  # Columns shown in the admin panel
    list_filter = ('rating', 'posted_on')  # Filters in the sidebar
    search_fields = ('user__name', 'item__title', 'review')  # Searchable fields
    ordering = ('-posted_on',)  # Order reviews by latest first

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'quantity', 'status')
    
    def get_queryset(self, request):
        """Filter out cart items belonging to caterers."""
        qs = super().get_queryset(request)
        return qs.filter(user__role='user')  # Only show users' cart items

admin.site.register(CartItem, CartItemAdmin)
# # Admin customization for the Reviews model
# class ReviewsAdmin(admin.ModelAdmin):
#     list_display = ('user', 'item', 'canteen', 'rating', 'posted_on')
#     list_filter = ('rating', 'posted_on', 'canteen')
#     search_fields = ('user__name', 'item__title', 'canteen__name')

# # Register the models with the admin site
admin.site.register(Item, ItemAdmin)
admin.site.register(Reviews, ReviewsAdmin)
admin.site.register(Payment)
